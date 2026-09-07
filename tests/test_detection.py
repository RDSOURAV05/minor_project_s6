import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "implementation", "src")))

from embedding.dwt_svd import DWTSVDWatermarker
from detection.detector import WatermarkIntegrityDetector, AudioAuthenticityClassifier
from data.dataset_manager import generate_synthetic_speech_signal


def test_detector_authentic_vs_fake():
    watermarker = DWTSVDWatermarker(alpha=0.05)
    detector = WatermarkIntegrityDetector(watermarker)

    # Clean authentic speech
    sig = generate_synthetic_speech_signal(duration=1.5, sr=16000, f0=130.0, seed=10)
    watermark = DWTSVDWatermarker.generate_watermark(45, key=123)
    wm_sig, meta = watermarker.embed_signal(sig, watermark)

    res_auth = detector.verify_authenticity(wm_sig, watermark, meta)
    assert res_auth.is_authentic is True
    assert res_auth.confidence_score > 0.90
    assert res_auth.label == "AUTHENTIC_WATERMARKED"

    # Unwatermarked / spoofed speech
    fake_sig = generate_synthetic_speech_signal(duration=1.5, sr=16000, f0=220.0, seed=99)
    res_fake = detector.verify_authenticity(fake_sig, watermark, meta)
    assert res_fake.is_authentic is False
    assert res_fake.confidence_score < 0.20
    assert res_fake.label == "AI_GENERATED_OR_UNWATERMARKED"


def test_classifier_training_and_roc():
    watermarker = DWTSVDWatermarker(alpha=0.05)
    watermark = DWTSVDWatermarker.generate_watermark(45, key=456)

    # Generate small feature dataset
    X = []
    y = []

    for i in range(5):
        # Positives (Authentic)
        sig = generate_synthetic_speech_signal(1.0, seed=i)
        wm_sig, meta = watermarker.embed_signal(sig, watermark)
        feat_pos = AudioAuthenticityClassifier.extract_features(wm_sig, watermark, meta, watermarker)
        X.append(feat_pos)
        y.append(1)

        # Negatives (Unwatermarked Fake)
        fake = generate_synthetic_speech_signal(1.0, f0=180.0, seed=i + 50)
        feat_neg = AudioAuthenticityClassifier.extract_features(fake, watermark, meta, watermarker)
        X.append(feat_neg)
        y.append(0)

    clf = AudioAuthenticityClassifier(model_type='rf')
    clf.train(X, y)
    eval_res = clf.evaluate(X, y)

    assert eval_res['auc'] >= 0.85
    assert 0.0 <= eval_res['eer'] <= 0.25
