import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "implementation", "src")))

from evaluation.metrics import (
    calculate_snr,
    calculate_psnr,
    calculate_seg_snr,
    calculate_lsd,
    calculate_ber,
    calculate_bit_accuracy,
    calculate_ncc,
    calculate_roc_and_auc,
    calculate_eer,
    calculate_classification_metrics
)


def test_audio_fidelity_metrics():
    orig = np.sin(np.linspace(0, 50, 8000))
    mod = orig + 0.001 * np.random.normal(size=8000)

    snr = calculate_snr(orig, mod)
    psnr = calculate_psnr(orig, mod)
    seg_snr = calculate_seg_snr(orig, mod)
    lsd = calculate_lsd(orig, mod)

    assert snr > 40.0
    assert psnr > 50.0
    assert seg_snr > 20.0
    assert lsd >= 0.0


def test_watermark_metrics():
    w1 = np.array([1, 0, 1, 1, 0, 0, 1, 0])
    w2 = np.array([1, 0, 1, 1, 0, 0, 1, 0])  # Identical
    w3 = np.array([0, 1, 0, 0, 1, 1, 0, 1])  # Inverted

    assert calculate_ber(w1, w2) == 0.0
    assert calculate_bit_accuracy(w1, w2) == 100.0
    assert pytest.approx(calculate_ncc(w1, w2), 0.001) == 1.0

    assert calculate_ber(w1, w3) == 1.0
    assert calculate_bit_accuracy(w1, w3) == 0.0


def test_roc_auc_and_eer():
    y_true = np.array([1, 1, 1, 1, 1, 0, 0, 0, 0, 0])
    y_scores = np.array([0.95, 0.88, 0.92, 0.79, 0.85, 0.12, 0.25, 0.08, 0.15, 0.30])

    fpr, tpr, thresholds, auc = calculate_roc_and_auc(y_true, y_scores)
    eer = calculate_eer(fpr, tpr)

    assert auc >= 0.99
    assert eer <= 0.10


def test_classification_metrics():
    y_true = np.array([1, 1, 1, 0, 0])
    y_pred = np.array([1, 1, 0, 0, 0])

    m = calculate_classification_metrics(y_true, y_pred)
    assert m['accuracy'] == 0.8
    assert m['precision'] == 1.0
    assert pytest.approx(m['recall'], 0.01) == 0.6667
