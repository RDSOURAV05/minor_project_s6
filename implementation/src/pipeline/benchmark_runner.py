"""
Comprehensive Benchmark Runner for Audio Watermarking & AI Detection.
Aligned with DeepMark Benchmark Suite (IEEE Access 2026).
"""

import os
import json
import time
import numpy as np
from typing import Dict, Any, List

try:
    from embedding.dwt_svd import DWTSVDWatermarker
    from evaluation.metrics import (
        calculate_snr,
        calculate_psnr,
        calculate_seg_snr,
        calculate_lsd,
        calculate_ber,
        calculate_bit_accuracy,
        calculate_ncc,
        calculate_roc_and_auc,
        calculate_eer
    )
    from attacks.audio_attacks import (
        add_awgn_noise,
        apply_lowpass_filter,
        apply_highpass_filter,
        apply_bandpass_filter,
        apply_resampling_attack,
        apply_amplitude_scaling,
        apply_cropping_attack,
        apply_compression_simulation,
        apply_resynthesis_attack,
        AttackSuite
    )
    from data.dataset_manager import (
        generate_synthetic_speech_signal,
        AudioDatasetManager
    )
    from detection.detector import WatermarkIntegrityDetector
except (ImportError, ValueError):
    from ..embedding.dwt_svd import DWTSVDWatermarker
    from ..evaluation.metrics import (
        calculate_snr,
        calculate_psnr,
        calculate_seg_snr,
        calculate_lsd,
        calculate_ber,
        calculate_bit_accuracy,
        calculate_ncc,
        calculate_roc_and_auc,
        calculate_eer
    )
    from ..attacks.audio_attacks import (
        add_awgn_noise,
        apply_lowpass_filter,
        apply_highpass_filter,
        apply_bandpass_filter,
        apply_resampling_attack,
        apply_amplitude_scaling,
        apply_cropping_attack,
        apply_compression_simulation,
        apply_resynthesis_attack,
        AttackSuite
    )
    from ..data.dataset_manager import (
        generate_synthetic_speech_signal,
        AudioDatasetManager
    )
    from ..detection.detector import WatermarkIntegrityDetector


class BenchmarkRunner:
    def __init__(self, output_dir="benchmark_results", sr=16000, default_alpha=0.05):
        self.output_dir = output_dir
        self.sr = sr
        self.default_alpha = default_alpha
        os.makedirs(self.output_dir, exist_ok=True)

    def run_comprehensive_benchmark(self, num_samples=5, duration=2.5, watermark_len=45):
        """
        Execute full benchmark across fidelity, attack robustness, and AI detection.
        """
        print(f"=== Starting Audio Watermarking & AI Detection Benchmark ===")
        print(f"Test samples: {num_samples} | Duration: {duration}s | Sample Rate: {self.sr} Hz")
        start_time = time.time()

        # 1. Prepare clean audio signals
        clean_signals = []
        pitches = [110.0, 135.0, 160.0, 185.0, 215.0]
        for i in range(num_samples):
            sig = generate_synthetic_speech_signal(duration=duration, sr=self.sr, f0=pitches[i % len(pitches)], seed=i + 100)
            clean_signals.append(sig)

        # 2. Test Alpha vs Audio Fidelity Trade-off
        print("\n[1/4] Evaluating Fidelity across Embedding Strengths (Alpha)...")
        alpha_values = [0.01, 0.03, 0.05, 0.08, 0.1, 0.15, 0.2]
        fidelity_results = {str(a): {'snr': [], 'psnr': [], 'seg_snr': [], 'lsd': []} for a in alpha_values}

        watermark = DWTSVDWatermarker.generate_watermark(watermark_len, key=42)

        for alpha in alpha_values:
            wm_obj = DWTSVDWatermarker(alpha=alpha)
            for sig in clean_signals:
                wm_sig, meta = wm_obj.embed_signal(sig, watermark)
                fidelity_results[str(alpha)]['snr'].append(calculate_snr(sig, wm_sig))
                fidelity_results[str(alpha)]['psnr'].append(calculate_psnr(sig, wm_sig))
                fidelity_results[str(alpha)]['seg_snr'].append(calculate_seg_snr(sig, wm_sig))
                fidelity_results[str(alpha)]['lsd'].append(calculate_lsd(sig, wm_sig))

        avg_fidelity = {
            a: {k: float(np.mean(v)) for k, v in metrics.items()}
            for a, metrics in fidelity_results.items()
        }

        # 3. Robustness Evaluation: Additive Noise Sweep (BER vs SNR)
        print("\n[2/4] Evaluating Noise Robustness (AWGN 0 to 40 dB)...")
        wm_obj = DWTSVDWatermarker(alpha=self.default_alpha)
        detector = WatermarkIntegrityDetector(wm_obj)

        noise_snrs = [0, 5, 10, 15, 20, 25, 30, 35, 40]
        noise_results = {snr: {'ber': [], 'bit_acc': [], 'ncc': []} for snr in noise_snrs}

        for sig in clean_signals:
            wm_sig, meta = wm_obj.embed_signal(sig, watermark)
            for snr_val in noise_snrs:
                attacked = add_awgn_noise(wm_sig, snr_db=snr_val)
                ext = wm_obj.extract_signal(attacked, meta, watermark_len=watermark_len)
                ber = calculate_ber(watermark, ext)
                noise_results[snr_val]['ber'].append(ber)
                noise_results[snr_val]['bit_acc'].append(calculate_bit_accuracy(watermark, ext))
                noise_results[snr_val]['ncc'].append(calculate_ncc(watermark, ext))

        avg_noise = {
            int(snr): {k: float(np.mean(v)) for k, v in metrics.items()}
            for snr, metrics in noise_results.items()
        }

        # 4. Robustness Evaluation: MP3 / Lossy Compression Sweep
        print("\n[3/4] Evaluating Lossy Compression Robustness (32 to 320 kbps)...")
        bitrates = [32, 64, 128, 192, 256, 320]
        compression_results = {b: {'ber': [], 'bit_acc': [], 'ncc': []} for b in bitrates}

        for sig in clean_signals:
            wm_sig, meta = wm_obj.embed_signal(sig, watermark)
            for br in bitrates:
                attacked = apply_compression_simulation(wm_sig, sr=self.sr, bitrate=br)
                ext = wm_obj.extract_signal(attacked, meta, watermark_len=watermark_len)
                ber = calculate_ber(watermark, ext)
                compression_results[br]['ber'].append(ber)
                compression_results[br]['bit_acc'].append(calculate_bit_accuracy(watermark, ext))
                compression_results[br]['ncc'].append(calculate_ncc(watermark, ext))

        avg_compression = {
            int(b): {k: float(np.mean(v)) for k, v in metrics.items()}
            for b, metrics in compression_results.items()
        }

        # 5. Full Standard Attack Suite Evaluation
        print("\n[4/4] Evaluating DeepMark Standard Attack Suite & AI Detection...")
        standard_attacks = AttackSuite.get_standard_attacks(sr=self.sr)
        attack_summary = {}

        y_true = []
        y_scores = []

        for att_name, att_fn in standard_attacks.items():
            ber_list = []
            acc_list = []
            correct_auth = 0

            for sig in clean_signals:
                wm_sig, meta = wm_obj.embed_signal(sig, watermark)
                attacked = att_fn(wm_sig)

                # Detection
                res = detector.verify_authenticity(attacked, watermark, meta)
                ber_list.append(res.ber)
                acc_list.append((1.0 - res.ber) * 100.0)
                if res.is_authentic:
                    correct_auth += 1

                # Collect detection scores for ROC
                y_true.append(1)  # Genuine watermarked
                y_scores.append(res.confidence_score)

            attack_summary[att_name] = {
                'mean_ber': float(np.mean(ber_list)),
                'mean_bit_acc': float(np.mean(acc_list)),
                'detection_rate': float(correct_auth / len(clean_signals) * 100.0)
            }

        # Generate negative (unwatermarked AI / deepfake) samples for ROC evaluation
        for i in range(len(clean_signals) * len(standard_attacks)):
            fake_sig = generate_synthetic_speech_signal(duration=duration, sr=self.sr, f0=np.random.uniform(90, 300), seed=i + 500)
            # Dummy metadata from authentic watermark
            res_fake = detector.verify_authenticity(fake_sig, watermark, meta)
            y_true.append(0)  # Unwatermarked / Fake
            y_scores.append(res_fake.confidence_score)

        fpr, tpr, thresholds, auc = calculate_roc_and_auc(y_true, y_scores)
        eer = calculate_eer(fpr, tpr)

        detection_metrics = {
            'auc': float(auc),
            'eer': float(eer),
            'total_evaluated': len(y_true),
            'fpr': [float(x) for x in fpr],
            'tpr': [float(x) for x in tpr]
        }

        elapsed = time.time() - start_time
        print(f"\n=== Benchmark Complete in {elapsed:.2f}s ===")
        print(f"Overall Detection ROC-AUC: {auc:.4f} | EER: {eer:.4f}")

        results_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'parameters': {
                'num_samples': num_samples,
                'duration_sec': duration,
                'sample_rate': self.sr,
                'default_alpha': self.default_alpha,
                'watermark_length': watermark_len
            },
            'fidelity_vs_alpha': avg_fidelity,
            'noise_robustness': avg_noise,
            'compression_robustness': avg_compression,
            'standard_attacks': attack_summary,
            'detection_performance': detection_metrics
        }

        # Save JSON results
        json_path = os.path.join(self.output_dir, "benchmark_results.json")
        with open(json_path, 'w') as f:
            json.dump(results_data, f, indent=2)
        print(f"Saved benchmark results: {json_path}")

        return results_data
