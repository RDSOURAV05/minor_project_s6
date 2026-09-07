"""
Audio Watermarking & Deepfake Detection Evaluation Metrics.

Provides:
- Audio Fidelity Metrics: SNR, PSNR, Segmental SNR (SegSNR), Log-Spectral Distance (LSD)
- Watermark Quality Metrics: Bit Error Rate (BER), Normalized Cross-Correlation (NCC), Bit Accuracy (%)
- Binary Detection & Classification Metrics: Accuracy, Precision, Recall, F1-Score, ROC-AUC, Equal Error Rate (EER)
"""

import math
import numpy as np


# =============================================================================
# Audio Fidelity & Perceptual Quality Metrics
# =============================================================================

def calculate_snr(original_signal, modified_signal):
    """
    Calculate the global Signal-to-Noise Ratio (SNR) in decibels (dB).
    """
    min_len = min(len(original_signal), len(modified_signal))
    orig = np.asarray(original_signal[:min_len], dtype=np.float64)
    mod = np.asarray(modified_signal[:min_len], dtype=np.float64)

    signal_power = np.sum(orig ** 2)
    noise_power = np.sum((orig - mod) ** 2)

    if noise_power == 0:
        return float('inf')
    if signal_power == 0:
        return 0.0

    return float(10.0 * math.log10(signal_power / noise_power))


def calculate_psnr(original_signal, modified_signal, max_val=1.0):
    """
    Calculate the Peak Signal-to-Noise Ratio (PSNR) in dB.
    """
    min_len = min(len(original_signal), len(modified_signal))
    orig = np.asarray(original_signal[:min_len], dtype=np.float64)
    mod = np.asarray(modified_signal[:min_len], dtype=np.float64)

    mse = np.mean((orig - mod) ** 2)
    if mse == 0:
        return float('inf')

    return float(20.0 * math.log10(max_val / math.sqrt(mse)))


def calculate_seg_snr(original_signal, modified_signal, frame_len=512, overlap=256):
    """
    Calculate Segmental Signal-to-Noise Ratio (SegSNR) in dB.
    Captures local time-varying perceptual distortions much better than global SNR.
    """
    min_len = min(len(original_signal), len(modified_signal))
    orig = np.asarray(original_signal[:min_len], dtype=np.float64)
    mod = np.asarray(modified_signal[:min_len], dtype=np.float64)

    hop = frame_len - overlap
    num_frames = max(1, (min_len - frame_len) // hop + 1)
    frame_snrs = []

    for i in range(num_frames):
        start = i * hop
        end = start + frame_len
        f_orig = orig[start:end]
        f_mod = mod[start:end]

        s_pow = np.sum(f_orig ** 2)
        n_pow = np.sum((f_orig - f_mod) ** 2)

        if n_pow > 1e-10 and s_pow > 1e-10:
            snr_val = 10.0 * math.log10(s_pow / n_pow)
            # Clip between standard -10 dB and 35 dB to prevent silence domination
            snr_val = max(-10.0, min(35.0, snr_val))
            frame_snrs.append(snr_val)

    return float(np.mean(frame_snrs)) if frame_snrs else calculate_snr(orig, mod)


def calculate_lsd(original_signal, modified_signal, n_fft=512, hop_length=256):
    """
    Calculate Log-Spectral Distance (LSD) in dB between two audio signals.
    Lower LSD indicates higher spectral fidelity.
    """
    min_len = min(len(original_signal), len(modified_signal))
    orig = np.asarray(original_signal[:min_len], dtype=np.float64)
    mod = np.asarray(modified_signal[:min_len], dtype=np.float64)

    # Compute short-time Fourier magnitudes
    window = np.hanning(n_fft)
    num_frames = max(1, (min_len - n_fft) // hop_length + 1)
    frame_lsd = []

    for i in range(num_frames):
        start = i * hop_length
        end = start + n_fft
        f_orig = orig[start:end] * window
        f_mod = mod[start:end] * window

        spec_orig = np.abs(np.fft.rfft(f_orig)) + 1e-12
        spec_mod = np.abs(np.fft.rfft(f_mod)) + 1e-12

        log_ratio = np.log10(spec_orig / spec_mod)
        lsd = np.sqrt(np.mean(log_ratio ** 2))
        frame_lsd.append(lsd)

    return float(np.mean(frame_lsd)) if frame_lsd else 0.0


# =============================================================================
# Watermark Integrity & Error Metrics
# =============================================================================

def calculate_ber(original_watermark, extracted_watermark):
    """
    Calculate Bit Error Rate (BER) between original and extracted watermark bits.
    Range: [0.0, 1.0]. Lower is better. 0.0 = perfect recovery.
    """
    o_w = np.asarray(original_watermark, dtype=np.int32)
    e_w = np.asarray(extracted_watermark, dtype=np.int32)
    min_len = min(len(o_w), len(e_w))
    if min_len == 0:
        return 1.0

    errors = np.sum(o_w[:min_len] != e_w[:min_len])
    return float(errors / min_len)


def calculate_bit_accuracy(original_watermark, extracted_watermark):
    """
    Calculate Bit Recovery Accuracy percentage.
    Range: [0.0%, 100.0%].
    """
    ber = calculate_ber(original_watermark, extracted_watermark)
    return float((1.0 - ber) * 100.0)


def calculate_ncc(original_watermark, extracted_watermark):
    """
    Calculate Normalized Cross-Correlation (NCC).
    Range: [-1.0, 1.0]. Closer to 1.0 indicates higher correlation.
    """
    o_w = np.asarray(original_watermark, dtype=np.float64)
    e_w = np.asarray(extracted_watermark, dtype=np.float64)
    min_len = min(len(o_w), len(e_w))
    if min_len == 0:
        return 0.0

    o_sub = o_w[:min_len]
    e_sub = e_w[:min_len]

    num = np.sum(o_sub * e_sub)
    den = np.sqrt(np.sum(o_sub ** 2)) * np.sqrt(np.sum(e_sub ** 2))

    if den == 0:
        return 0.0
    return float(num / den)


# =============================================================================
# Detection, ROC-AUC & Equal Error Rate (EER) Metrics
# =============================================================================

def calculate_roc_and_auc(y_true, y_scores, num_thresholds=200):
    """
    Calculate False Positive Rate (FPR), True Positive Rate (TPR), and Area Under Curve (AUC).
    
    :param y_true: Ground truth binary labels (1 = positive / authentic, 0 = negative / fake)
    :param y_scores: Continuous decision scores / confidence [0, 1]
    :return: (fpr, tpr, thresholds, auc)
    """
    y_true = np.asarray(y_true, dtype=np.int32)
    y_scores = np.asarray(y_scores, dtype=np.float64)

    positives = np.sum(y_true == 1)
    negatives = np.sum(y_true == 0)

    if positives == 0 or negatives == 0:
        return np.array([0.0, 1.0]), np.array([0.0, 1.0]), np.array([0.0, 1.0]), 0.5

    try:
        from sklearn.metrics import roc_curve, auc as sk_auc
        fpr, tpr, thresholds = roc_curve(y_true, y_scores)
        auc = float(sk_auc(fpr, tpr))
        return fpr, tpr, thresholds, auc
    except ImportError:
        thresholds = np.unique(np.concatenate([[0.0, 1.0], y_scores]))
        thresholds = np.sort(thresholds)[::-1]
        tpr_list = []
        fpr_list = []

        for th in thresholds:
            preds = (y_scores >= th).astype(np.int32)
            tp = np.sum((preds == 1) & (y_true == 1))
            fp = np.sum((preds == 1) & (y_true == 0))
            tpr_list.append(tp / positives)
            fpr_list.append(fp / negatives)

        sorted_indices = np.argsort(fpr_list)
        fpr_sorted = np.array(fpr_list)[sorted_indices]
        tpr_sorted = np.array(tpr_list)[sorted_indices]

        if hasattr(np, 'trapezoid'):
            auc = float(np.trapezoid(tpr_sorted, fpr_sorted))
        elif hasattr(np, 'trapz'):
            auc = float(np.trapz(tpr_sorted, fpr_sorted))
        else:
            from scipy import integrate
            auc = float(integrate.trapezoid(tpr_sorted, fpr_sorted))
        auc = max(0.0, min(1.0, auc))
        return fpr_sorted, tpr_sorted, thresholds[sorted_indices], auc


def calculate_eer(fpr, tpr):
    """
    Calculate Equal Error Rate (EER) where FPR == FNR (1 - TPR).
    Key benchmark metric used in DeepMark and ASVspoof.
    """
    fnr = 1.0 - np.asarray(tpr)
    fpr = np.asarray(fpr)

    # Find the index where |FPR - FNR| is minimal
    idx = np.nanargmin(np.abs(fpr - fnr))
    eer = (fpr[idx] + fnr[idx]) / 2.0
    return float(eer)


def calculate_classification_metrics(y_true, y_pred):
    """
    Calculate standard classification metrics: Accuracy, Precision, Recall, F1.
    """
    y_true = np.asarray(y_true, dtype=np.int32)
    y_pred = np.asarray(y_pred, dtype=np.int32)

    tp = int(np.sum((y_pred == 1) & (y_true == 1)))
    fp = int(np.sum((y_pred == 1) & (y_true == 0)))
    fn = int(np.sum((y_pred == 0) & (y_true == 1)))
    tn = int(np.sum((y_pred == 0) & (y_true == 0)))

    total = max(1, len(y_true))
    accuracy = (tp + tn) / total
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        'accuracy': float(accuracy),
        'precision': float(precision),
        'recall': float(recall),
        'f1_score': float(f1),
        'tp': tp,
        'fp': fp,
        'fn': fn,
        'tn': tn
    }
