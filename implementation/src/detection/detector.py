"""
AI-Generated Audio & Deepfake Detection Engine.

Implements:
1. WatermarkIntegrityDetector:
   - Evaluates watermark extraction correlation and bit error rate against authentic registered keys
   - Computes continuous authenticity confidence scores [0.0, 1.0]
   - Categorizes audio as AUTHENTIC, TAMPERED, or AI_GENERATED_OR_UNWATERMARKED
   - Localizes tampered segments across time
2. AudioAuthenticityClassifier:
   - Feature-based machine learning classifier (Random Forest / Logistic Regression)
   - Evaluates multi-domain features (BER, NCC, DWT wavelet energy ratios, SVD singular values)
   - Computes ROC curve, AUC, Equal Error Rate (EER)
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import pywt

try:
    from embedding.dwt_svd import DWTSVDWatermarker
    from evaluation.metrics import (
        calculate_ber,
        calculate_ncc,
        calculate_roc_and_auc,
        calculate_eer,
        calculate_classification_metrics
    )
except (ImportError, ValueError):
    from ..embedding.dwt_svd import DWTSVDWatermarker
    from ..evaluation.metrics import (
        calculate_ber,
        calculate_ncc,
        calculate_roc_and_auc,
        calculate_eer,
        calculate_classification_metrics
    )


@dataclass
class DetectionResult:
    """Encapsulates detection decision and diagnostic metrics."""
    label: str                     # 'AUTHENTIC_WATERMARKED', 'TAMPERED', 'AI_GENERATED_OR_UNWATERMARKED'
    is_authentic: bool
    confidence_score: float        # [0.0, 1.0]
    ber: float                     # Bit Error Rate
    ncc: float                     # Normalized Cross-Correlation
    tamper_ratio: float = 0.0      # Fraction of blocks detected as tampered
    tampered_intervals: Optional[List[Dict[str, Any]]] = None


class WatermarkIntegrityDetector:
    """
    Proactive authenticity verifier and deepfake detector based on DWT-SVD watermark integrity.
    """
    def __init__(self, watermarker: Optional[DWTSVDWatermarker] = None, ber_authentic_th=0.15, ber_tampered_th=0.35):
        """
        :param watermarker: DWTSVDWatermarker instance
        :param ber_authentic_th: Threshold below which audio is certified authentic (default: 0.15)
        :param ber_tampered_th: Threshold above which audio is deemed unwatermarked/AI-generated (default: 0.35)
        """
        self.watermarker = watermarker or DWTSVDWatermarker()
        self.ber_authentic_th = ber_authentic_th
        self.ber_tampered_th = ber_tampered_th

    def verify_authenticity(self, audio_signal, expected_watermark, metadata_or_S):
        """
        Verify authenticity of an audio signal against an expected watermark key.
        
        :param audio_signal: 1D numpy array of audio samples
        :param expected_watermark: 1D binary array of the registered authentic watermark
        :param metadata_or_S: Original singular values vector S or metadata dictionary
        :return: DetectionResult object
        """
        expected_watermark = np.asarray(expected_watermark, dtype=np.int32)
        extracted = self.watermarker.extract_signal(
            audio_signal,
            metadata_or_S,
            watermark_len=len(expected_watermark)
        )

        ber = calculate_ber(expected_watermark, extracted)
        ncc = calculate_ncc(expected_watermark, extracted)

        # Unwatermarked / random noise audio produces BER ~ 0.50, NCC ~ 0.0
        # Authentic watermarked audio produces BER ~ 0.0, NCC ~ 1.0
        # Map BER [0.0 -> 0.50] to confidence [1.0 -> 0.0]
        confidence = float(max(0.0, min(1.0, 1.0 - 2.0 * ber)))

        if ber <= self.ber_authentic_th:
            label = "AUTHENTIC_WATERMARKED"
            is_authentic = True
        elif ber <= self.ber_tampered_th:
            label = "TAMPERED_AUDIO"
            is_authentic = False
        else:
            label = "AI_GENERATED_OR_UNWATERMARKED"
            is_authentic = False

        return DetectionResult(
            label=label,
            is_authentic=is_authentic,
            confidence_score=confidence,
            ber=float(ber),
            ncc=float(ncc)
        )

    def localize_tampering(self, audio_signal, block_metadata, block_size=4096, sr=16000):
        """
        Localize tampered time regions in the audio signal.
        
        :param audio_signal: 1D numpy array
        :param block_metadata: List of block metadata from embed_blocks
        :param block_size: Block size in samples
        :param sr: Audio sample rate
        :return: DetectionResult with detailed block-level tamper localization
        """
        extracted_bits, block_results = self.watermarker.extract_blocks(
            audio_signal,
            block_metadata,
            block_size=block_size
        )

        tampered_blocks = [b for b in block_results if b['is_tampered']]
        tamper_ratio = len(tampered_blocks) / len(block_results) if block_results else 0.0

        tampered_intervals = []
        for b in tampered_blocks:
            t_start = b['start_sample'] / sr
            t_end = b['end_sample'] / sr
            tampered_intervals.append({
                'block_idx': b['block_idx'],
                'start_time_sec': round(t_start, 3),
                'end_time_sec': round(t_end, 3),
                'ber': round(b['ber'], 4)
            })

        avg_ber = float(np.mean([b['ber'] for b in block_results])) if block_results else 1.0
        confidence = float(max(0.0, min(1.0, 1.0 - tamper_ratio)))

        if tamper_ratio == 0.0:
            label = "AUTHENTIC_WATERMARKED"
            is_authentic = True
        elif tamper_ratio < 0.50:
            label = "TAMPERED_AUDIO"
            is_authentic = False
        else:
            label = "AI_GENERATED_OR_UNWATERMARKED"
            is_authentic = False

        return DetectionResult(
            label=label,
            is_authentic=is_authentic,
            confidence_score=confidence,
            ber=avg_ber,
            ncc=float(1.0 - 2.0 * avg_ber),
            tamper_ratio=float(tamper_ratio),
            tampered_intervals=tampered_intervals
        )


class AudioAuthenticityClassifier:
    """
    Supervised classifier leveraging watermark correlation and multi-scale wavelet features
    to achieve high-accuracy detection and generate ROC/AUC curves.
    """
    def __init__(self, model_type='rf'):
        """
        :param model_type: 'rf' for RandomForestClassifier or 'logistic' for LogisticRegression
        """
        if model_type == 'rf':
            self.model = RandomForestClassifier(n_estimators=50, random_state=42, max_depth=6)
        else:
            self.model = LogisticRegression(random_state=42)
        self.is_fitted = False

    @staticmethod
    def extract_features(audio_signal, expected_watermark, metadata_or_S, watermarker: DWTSVDWatermarker):
        """
        Extract multi-dimensional diagnostic features:
        1. Bit Error Rate (BER)
        2. Normalized Cross Correlation (NCC)
        3. Approximation subband energy ratio
        4. Detail subband energy ratio
        5. SVD singular value deviation
        """
        extracted = watermarker.extract_signal(audio_signal, metadata_or_S, watermark_len=len(expected_watermark))
        ber = calculate_ber(expected_watermark, extracted)
        ncc = calculate_ncc(expected_watermark, extracted)

        # Wavelet subband energy features
        coeffs = pywt.wavedec(audio_signal, watermarker.wavelet, level=watermarker.level)
        cA = coeffs[0]
        cD_energies = [np.sum(d ** 2) for d in coeffs[1:]]

        total_energy = np.sum(audio_signal ** 2) + 1e-10
        cA_energy_ratio = np.sum(cA ** 2) / total_energy
        mean_cD_energy_ratio = float(np.mean(cD_energies)) / total_energy

        return np.array([ber, ncc, cA_energy_ratio, mean_cD_energy_ratio], dtype=np.float64)

    def train(self, X, y):
        """
        Train the classifier on extracted feature matrix X and ground-truth binary labels y.
        y = 1 (Authentic / Watermarked), y = 0 (AI-Generated / Unwatermarked / Severely Attacked)
        """
        X = np.asarray(X)
        y = np.asarray(y, dtype=np.int32)
        self.model.fit(X, y)
        self.is_fitted = True

    def predict_proba(self, X):
        """
        Return predicted probability of being Authentic (class 1).
        """
        X = np.asarray(X)
        if not self.is_fitted:
            # Rule-based fallback if not explicitly trained
            # Feature 0 is BER, Feature 1 is NCC
            ber = X[:, 0]
            confidence = np.clip(1.0 - 2.0 * ber, 0.0, 1.0)
            return confidence
        return self.model.predict_proba(X)[:, 1]

    def evaluate(self, X_test, y_test):
        """
        Evaluate classifier performance: ROC curve, AUC, EER, and classification metrics.
        """
        scores = self.predict_proba(X_test)
        preds = (scores >= 0.5).astype(np.int32)

        fpr, tpr, thresholds, auc = calculate_roc_and_auc(y_test, scores)
        eer = calculate_eer(fpr, tpr)
        metrics_dict = calculate_classification_metrics(y_test, preds)

        metrics_dict['auc'] = auc
        metrics_dict['eer'] = eer
        metrics_dict['fpr'] = fpr.tolist()
        metrics_dict['tpr'] = tpr.tolist()

        return metrics_dict
