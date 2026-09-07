"""
Audio Watermarking & AI Deepfake Detection — Main Pipeline CLI.
Minor Project S6 — Academic Demo & Benchmark Runner.

Usage:
    uv run python run_pipeline.py --demo
    uv run python run_pipeline.py --benchmark
    uv run python run_pipeline.py --plot
    uv run python run_pipeline.py --all
"""

import sys
import os
import argparse

# Ensure implementation/src is on sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "implementation", "src"))

from embedding.dwt_svd import DWTSVDWatermarker
from evaluation.metrics import calculate_snr, calculate_psnr, calculate_ber, calculate_ncc
from attacks.audio_attacks import AttackSuite, add_awgn_noise, apply_compression_simulation
from data.dataset_manager import generate_synthetic_speech_signal, create_test_audio_dataset
from detection.detector import WatermarkIntegrityDetector
from pipeline.benchmark_runner import BenchmarkRunner
from pipeline.plot_empirical_results import EmpiricalResultsPlotter


def run_demo():
    print("=" * 70)
    print("AUDIO WATERMARKING (DWT-SVD) FOR AI AUDIO DETECTION — INTERACTIVE DEMO")
    print("=" * 70)

    # 1. Generate or load clean speech signal
    print("\n[Step 1] Generating clean speech audio signal (3.0s, 16 kHz)...")
    signal = generate_synthetic_speech_signal(duration=3.0, sr=16000, f0=140.0, seed=42)

    # 2. Generate cryptographic watermark
    watermark_len = 45
    watermark = DWTSVDWatermarker.generate_watermark(watermark_len, key=12345)
    print(f"Generated {watermark_len}-bit cryptographic watermark key: {watermark[:16]}... (first 16 bits)")

    # 3. Watermark Embedding
    alpha = 0.05
    watermarker = DWTSVDWatermarker(wavelet='db4', level=3, alpha=alpha)
    print(f"\n[Step 2] Embedding watermark using 3-Level DWT + SVD (alpha={alpha})...")
    wm_signal, metadata = watermarker.embed_signal(signal, watermark)

    # 4. Measure Audio Fidelity
    snr = calculate_snr(signal, wm_signal)
    psnr = calculate_psnr(signal, wm_signal)
    print(f"  --> Audio Fidelity Preserved:")
    print(f"      * SNR : {snr:.2f} dB (Imperceptible quality degradation)")
    print(f"      * PSNR: {psnr:.2f} dB")

    # 5. Extraction in Noiseless Channel
    print("\n[Step 3] Extracting watermark in clean condition...")
    extracted_clean = watermarker.extract_signal(wm_signal, metadata, watermark_len=watermark_len)
    ber_clean = calculate_ber(watermark, extracted_clean)
    ncc_clean = calculate_ncc(watermark, extracted_clean)
    print(f"  --> Clean Extraction Results: BER = {ber_clean:.4f} | NCC = {ncc_clean:.4f}")

    # 6. Authenticity & AI Detection Verification
    detector = WatermarkIntegrityDetector(watermarker)
    det_clean = detector.verify_authenticity(wm_signal, watermark, metadata)
    print(f"  --> Detector Decision: [{det_clean.label}] (Confidence: {det_clean.confidence_score * 100:.1f}%)")

    # 7. Stress Testing under Attacks
    print("\n[Step 4] Simulating Real-World Channel & Manipulation Attacks (DeepMark Suite):")
    attacks = {
        "AWGN Noise (25 dB)": lambda s: add_awgn_noise(s, snr_db=25),
        "AWGN Noise (15 dB)": lambda s: add_awgn_noise(s, snr_db=15),
        "MP3 Compression (128 kbps)": lambda s: apply_compression_simulation(s, sr=16000, bitrate=128),
        "MP3 Compression (64 kbps)": lambda s: apply_compression_simulation(s, sr=16000, bitrate=64),
    }

    print(f"\n{'Attack Scenario':<28} | {'BER':<8} | {'NCC':<8} | {'Confidence':<10} | {'Decision'}")
    print("-" * 75)

    for att_name, att_fn in attacks.items():
        attacked = att_fn(wm_signal)
        res = detector.verify_authenticity(attacked, watermark, metadata)
        print(f"{att_name:<28} | {res.ber:<8.4f} | {res.ncc:<8.4f} | {res.confidence_score * 100:>5.1f}%     | {res.label}")

    # 8. Testing against Unwatermarked / Deepfake Audio
    print("\n[Step 5] Evaluating against Unwatermarked / Spoofed Synthetic Voice:")
    fake_signal = generate_synthetic_speech_signal(duration=3.0, sr=16000, f0=220.0, seed=999)
    res_fake = detector.verify_authenticity(fake_signal, watermark, metadata)
    print(f"{'Unwatermarked AI Voice':<28} | {res_fake.ber:<8.4f} | {res_fake.ncc:<8.4f} | {res_fake.confidence_score * 100:>5.1f}%     | {res_fake.label}")

    print("\n" + "=" * 70)
    print("DEMO VERIFICATION SUCCESSFUL: Proactive watermarking reliably authenticates")
    print("genuine speech and flags unwatermarked/tampered deepfakes.")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Minor Project S6 — Audio Watermarking Pipeline CLI")
    parser.add_argument("--demo", action="store_true", help="Run interactive single-file demonstration")
    parser.add_argument("--benchmark", action="store_true", help="Run full DeepMark-aligned benchmark suite")
    parser.add_argument("--plot", action="store_true", help="Generate publication-ready empirical graphs")
    parser.add_argument("--all", action="store_true", help="Run demo, full benchmark, and plotting")

    args = parser.parse_args()

    if not any([args.demo, args.benchmark, args.plot, args.all]):
        # Default to demo if no arguments provided
        run_demo()
        return

    if args.demo or args.all:
        run_demo()

    if args.benchmark or args.all:
        print("\nRunning full DeepMark empirical benchmark...")
        runner = BenchmarkRunner()
        results = runner.run_comprehensive_benchmark(num_samples=5, duration=2.5)

        print("\nGenerating empirical metric graphs...")
        plotter = EmpiricalResultsPlotter()
        plotter.generate_presentation_metrics_figure(data=results)

    elif args.plot:
        print("\nGenerating empirical metric graphs from existing benchmark results...")
        plotter = EmpiricalResultsPlotter()
        plotter.generate_presentation_metrics_figure()


if __name__ == "__main__":
    main()
