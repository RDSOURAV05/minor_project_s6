"""
Unit Tests for Kaggle Dataset Loader and Evaluation Protocol.
Uses isolated temporary synthetic directory fixtures so tests run fast without external data.
"""

import os
import sys
import tempfile
import pytest
import numpy as np
import soundfile as sf

# Ensure implementation/src is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "implementation", "src")))

from data.kaggle_dataset import KaggleDatasetLoader, KaggleAudioSample
from pipeline.kaggle_evaluator import KaggleBenchmarkEvaluator
from data.dataset_manager import generate_synthetic_speech_signal


@pytest.fixture
def fake_kaggle_dir(tmp_path):
    """Creates a tiny mock Kaggle dataset with nested Real/Real and Fake/Fake directories."""
    data_dir = tmp_path / "fake_kaggle"
    real_dir = data_dir / "Real" / "Real"
    fake_dir = data_dir / "Fake" / "Fake"
    real_dir.mkdir(parents=True)
    fake_dir.mkdir(parents=True)

    sr = 44100
    # Generate 3 fake recordings and 3 real recordings
    for i in range(1, 4):
        # 1.5s audio
        sig_real = generate_synthetic_speech_signal(duration=1.5, sr=sr, f0=120.0 + i * 15, seed=i)
        # Stereo for real
        stereo_real = np.column_stack([sig_real, sig_real])
        sf.write(str(real_dir / f"Recording ({i}).wav"), stereo_real, sr)

        # Mono for fake
        sig_fake = generate_synthetic_speech_signal(duration=1.5, sr=sr, f0=200.0 + i * 20, seed=100 + i)
        sf.write(str(fake_dir / f"Recording ({i}).wav"), sig_fake, sr)

    return str(data_dir)


def test_kaggle_loader_discovery_and_summary(fake_kaggle_dir):
    loader = KaggleDatasetLoader(data_dir=fake_kaggle_dir, n_per_class=4)
    summary = loader.get_dataset_summary()

    assert "real" in summary
    assert "fake" in summary
    assert summary["real"]["file_count"] == 3
    assert summary["fake"]["file_count"] == 3
    assert 44100 in summary["real"]["sample_rates"]
    assert 2 in summary["real"]["channels"]
    assert 1 in summary["fake"]["channels"]


def test_kaggle_subsampling_and_caching(fake_kaggle_dir, tmp_path):
    cache_dir = tmp_path / "cache"
    loader = KaggleDatasetLoader(
        data_dir=fake_kaggle_dir,
        cache_dir=str(cache_dir),
        clip_duration=0.5,
        target_sr=16000,
        n_per_class=4,
        seed=42
    )

    human, ai = loader.load_subsampled_dataset()
    assert len(human) > 0
    assert len(ai) > 0
    for s in human:
        assert s.label == "real"
        assert len(s.audio) == int(0.5 * 16000)
        assert s.sr == 16000
    for s in ai:
        assert s.label == "fake"
        assert len(s.audio) == int(0.5 * 16000)
        assert s.sr == 16000

    # Verify cache files created
    cache_files = os.listdir(str(cache_dir))
    assert any(f.endswith(".npz") for f in cache_files)
    assert any(f.endswith("_meta.json") for f in cache_files)


def test_speaker_disjoint_splitting(fake_kaggle_dir, tmp_path):
    cache_dir = tmp_path / "cache_split"
    loader = KaggleDatasetLoader(
        data_dir=fake_kaggle_dir,
        cache_dir=str(cache_dir),
        clip_duration=0.5,
        target_sr=16000,
        n_per_class=6,
        seed=42
    )
    human, ai = loader.load_subsampled_dataset()

    train_h, test_h = loader.split_by_speaker(human, train_ratio=0.6, seed=42)
    train_speakers = set(s.speaker_id for s in train_h)
    test_speakers = set(s.speaker_id for s in test_h)

    # Disjoint check
    assert len(train_speakers.intersection(test_speakers)) == 0


def test_kaggle_evaluator_pipeline_integration(fake_kaggle_dir, tmp_path):
    out_dir = str(tmp_path / "results")
    evaluator = KaggleBenchmarkEvaluator(
        data_dir=fake_kaggle_dir,
        output_dir=out_dir,
        n_per_class=4,
        alpha=0.05,
        watermark_len=16,
        seed=42
    )

    # Run full evaluation pipeline on the mock dataset
    results = evaluator.run_full_evaluation()

    assert "fidelity" in results
    assert "human" in results["fidelity"]
    assert results["fidelity"]["human"]["snr_mean"] > 25.0

    assert "clean_extraction" in results
    assert results["clean_extraction"]["human"]["ber_mean"] == 0.0

    assert "detection" in results
    assert results["detection"]["watermark_auc"] >= 0.80

    assert "baseline" in results
    assert "passive_rf_auc" in results["baseline"]

    assert "tamper_localization" in results
    assert results["tamper_localization"]["accuracy"] >= 0.50

    # Verify output artifacts exist
    assert os.path.exists(os.path.join(out_dir, "kaggle_results.json"))
    assert os.path.exists(os.path.join(out_dir, "kaggle_fidelity.csv"))
    assert os.path.exists(os.path.join(out_dir, "kaggle_roc_curves.png"))
    assert os.path.exists(os.path.join(out_dir, "kaggle_ber_vs_attack.png"))
