import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "implementation", "src")))

from embedding.dwt_svd import DWTSVDWatermarker
from evaluation.metrics import calculate_snr, calculate_ber, calculate_ncc
from data.dataset_manager import generate_synthetic_speech_signal


def test_watermark_generation():
    wm = DWTSVDWatermarker.generate_watermark(64, key=42)
    assert len(wm) == 64
    assert set(np.unique(wm)).issubset({0, 1})
    # Reproducibility
    wm2 = DWTSVDWatermarker.generate_watermark(64, key=42)
    np.testing.assert_array_equal(wm, wm2)


def test_noiseless_embedding_and_extraction():
    sr = 16000
    signal = generate_synthetic_speech_signal(duration=1.5, sr=sr, seed=123)
    watermarker = DWTSVDWatermarker(wavelet='db4', level=3, alpha=0.05)

    watermark = DWTSVDWatermarker.generate_watermark(45, key=999)
    wm_signal, metadata = watermarker.embed_signal(signal, watermark)

    # Length preservation
    assert len(wm_signal) == len(signal)

    # High fidelity check
    snr = calculate_snr(signal, wm_signal)
    assert snr > 30.0, f"SNR too low: {snr} dB"

    # Perfect recovery in noiseless channel
    extracted = watermarker.extract_signal(wm_signal, metadata, watermark_len=len(watermark))
    ber = calculate_ber(watermark, extracted)
    ncc = calculate_ncc(watermark, extracted)

    assert ber == 0.0, f"Expected 0 BER, got {ber}"
    assert pytest.approx(ncc, rel=1e-5) == 1.0


def test_qim_mode():
    signal = generate_synthetic_speech_signal(duration=1.0, sr=16000, seed=456)
    watermarker = DWTSVDWatermarker(wavelet='db4', level=3, mode='qim', qim_step=0.1)

    watermark = DWTSVDWatermarker.generate_watermark(30, key=777)
    wm_signal, metadata = watermarker.embed_signal(signal, watermark)

    # Extraction without original S (semi-blind)
    extracted = watermarker.extract_signal(wm_signal, metadata, watermark_len=len(watermark))
    ber = calculate_ber(watermark, extracted)
    assert ber <= 0.20, f"QIM BER too high: {ber}"


def test_block_based_embedding():
    signal = generate_synthetic_speech_signal(duration=2.0, sr=16000, seed=555)
    watermarker = DWTSVDWatermarker(alpha=0.08)
    watermark = DWTSVDWatermarker.generate_watermark(32, key=111)

    wm_signal, block_meta = watermarker.embed_blocks(signal, watermark, block_size=4096)
    assert len(wm_signal) == len(signal)
    assert len(block_meta) > 0

    extracted_bits, block_results = watermarker.extract_blocks(wm_signal, block_meta, block_size=4096)
    assert len(block_results) == len(block_meta)
    for b in block_results:
        assert b['is_tampered'] is False
