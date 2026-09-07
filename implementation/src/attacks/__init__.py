"""
Audio Attack Simulation Suite for Robustness Benchmarking.
Aligned with DeepMark Benchmark (IEEE Access 2026).
"""

from .audio_attacks import (
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

__all__ = [
    'add_awgn_noise',
    'apply_lowpass_filter',
    'apply_highpass_filter',
    'apply_bandpass_filter',
    'apply_resampling_attack',
    'apply_amplitude_scaling',
    'apply_cropping_attack',
    'apply_compression_simulation',
    'apply_resynthesis_attack',
    'AttackSuite'
]
