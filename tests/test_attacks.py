import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "implementation", "src")))

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
from data.dataset_manager import generate_synthetic_speech_signal


@pytest.fixture
def clean_signal():
    return generate_synthetic_speech_signal(duration=1.0, sr=16000, seed=123)


def test_awgn_noise(clean_signal):
    noisy = add_awgn_noise(clean_signal, snr_db=20)
    assert len(noisy) == len(clean_signal)
    assert not np.isnan(noisy).any()
    assert np.max(np.abs(noisy)) <= 1.0


def test_filters(clean_signal):
    lp = apply_lowpass_filter(clean_signal, sr=16000, cutoff=4000)
    hp = apply_highpass_filter(clean_signal, sr=16000, cutoff=300)
    bp = apply_bandpass_filter(clean_signal, sr=16000, lowcut=300, highcut=3400)

    for f_sig in [lp, hp, bp]:
        assert len(f_sig) == len(clean_signal)
        assert not np.isnan(f_sig).any()


def test_resampling_and_scaling(clean_signal):
    resampled = apply_resampling_attack(clean_signal, orig_sr=16000, target_sr=8000)
    scaled = apply_amplitude_scaling(clean_signal, factor=0.8)

    assert len(resampled) == len(clean_signal)
    assert len(scaled) == len(clean_signal)
    assert not np.isnan(resampled).any()
    assert not np.isnan(scaled).any()


def test_compression_and_resynthesis(clean_signal):
    compressed = apply_compression_simulation(clean_signal, sr=16000, bitrate=64)
    resynth = apply_resynthesis_attack(clean_signal, noise_level=0.02)

    assert len(compressed) == len(clean_signal)
    assert len(resynth) == len(clean_signal)
    assert not np.isnan(compressed).any()
    assert not np.isnan(resynth).any()


def test_attack_suite_orchestration(clean_signal):
    suite = AttackSuite.get_standard_attacks(sr=16000)
    assert len(suite) >= 10

    for name, attack_fn in suite.items():
        attacked = attack_fn(clean_signal)
        assert len(attacked) == len(clean_signal), f"Attack {name} altered signal length"
        assert not np.isnan(attacked).any(), f"Attack {name} introduced NaN"
