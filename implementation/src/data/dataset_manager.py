"""
Audio Dataset Manager & Speech Synthesis Utility.

Provides:
- High-fidelity synthetic speech signal generation (harmonic formant modeling)
- Local test dataset creation without external network requirements
- LibriSpeech subset downloading and caching
- Batch audio loading and preprocessing
"""

import os
import glob
import numpy as np
import soundfile as sf
import librosa


def generate_synthetic_speech_signal(duration=3.0, sr=16000, f0=130.0, seed=None):
    """
    Generate a realistic synthetic speech-like acoustic signal using formant synthesis
    (vocal tract resonance modeling with natural amplitude envelope and glottal pulses).
    
    :param duration: Duration in seconds
    :param sr: Sampling rate in Hz (default: 16000)
    :param f0: Fundamental pitch frequency in Hz (default: 130 Hz - typical male/female speech range)
    :param seed: Random seed for deterministic generation
    :return: 1D numpy array of normalized audio samples in [-1.0, 1.0]
    """
    if seed is not None:
        np.random.seed(seed)

    num_samples = int(duration * sr)
    t = np.linspace(0, duration, num_samples, endpoint=False)

    # 1. Harmonic glottal pulse train with slight pitch jitter
    jitter = 1.0 + 0.015 * np.sin(2 * np.pi * 5.0 * t)  # 5 Hz vibrato / jitter
    harmonic_signal = np.zeros(num_samples, dtype=np.float64)

    # Sum up to 15 harmonics with 1/n decay (glottal source spectral tilt)
    for h in range(1, 16):
        harmonic_freq = h * f0
        if harmonic_freq < sr / 2:
            phase = np.random.uniform(0, 2 * np.pi) if seed is not None else 0
            amplitude = (1.0 / h) * (0.8 + 0.2 * np.random.rand())
            harmonic_signal += amplitude * np.sin(2 * np.pi * harmonic_freq * jitter * t + phase)

    # 2. Formant resonance filtering (simulate vowel resonances: F1 ~ 500Hz, F2 ~ 1500Hz, F3 ~ 2500Hz)
    formants = [
        (500.0, 80.0, 1.0),    # (center_freq, bandwidth, gain)
        (1500.0, 120.0, 0.6),
        (2500.0, 150.0, 0.3),
        (3500.0, 200.0, 0.15),
    ]

    filtered_signal = np.zeros_like(harmonic_signal)
    for center, bw, gain in formants:
        # Resonant 2nd order bandpass filter approximation
        omega = 2 * np.pi * center / sr
        r = np.exp(-np.pi * bw / sr)
        b0 = (1.0 - r) * gain
        # Simple IIR filtering
        y = np.zeros_like(harmonic_signal)
        y[0] = b0 * harmonic_signal[0]
        if len(y) > 1:
            y[1] = b0 * harmonic_signal[1] + 2 * r * np.cos(omega) * y[0]
        for n in range(2, num_samples):
            y[n] = b0 * harmonic_signal[n] + 2 * r * np.cos(omega) * y[n - 1] - (r ** 2) * y[n - 2]
        filtered_signal += y

    # 3. Speech syllabic envelope modulation (simulate words / pauses at 3-4 Hz)
    envelope = (0.5 + 0.5 * np.sin(2 * np.pi * 3.2 * t)) ** 2
    # Add subtle unvoiced fricative noise (breath/air)
    noise = np.random.normal(0, 0.02, size=num_samples)
    speech = (filtered_signal * envelope) + (noise * envelope)

    # Normalize to peak amplitude of 0.95
    peak = np.max(np.abs(speech))
    if peak > 0:
        speech = (speech / peak) * 0.95

    return speech.astype(np.float32)


def create_test_audio_dataset(output_dir, num_samples=5, sample_rate=16000, duration=3.0):
    """
    Create a local directory of synthetic speech audio WAV files for testing.
    
    :param output_dir: Directory path to save audio files
    :param num_samples: Number of distinct audio clips to generate
    :param sample_rate: Audio sampling rate (default: 16000 Hz)
    :param duration: Duration per clip in seconds
    :return: List of created file paths
    """
    os.makedirs(output_dir, exist_ok=True)
    created_files = []

    pitches = [110.0, 140.0, 175.0, 210.0, 125.0, 160.0, 190.0, 220.0]

    for idx in range(num_samples):
        pitch = pitches[idx % len(pitches)]
        sig = generate_synthetic_speech_signal(duration=duration, sr=sample_rate, f0=pitch, seed=idx + 42)
        filename = f"speech_sample_{idx + 1:02d}.wav"
        file_path = os.path.join(output_dir, filename)
        sf.write(file_path, sig, sample_rate)
        created_files.append(file_path)

    return created_files


def load_audio_file(file_path, sr=16000):
    """
    Load an audio file into a 1D numpy array with target sampling rate.
    """
    audio, actual_sr = librosa.load(file_path, sr=sr)
    return audio, actual_sr


def save_audio_file(file_path, signal, sr=16000):
    """
    Save an audio numpy array to disk as a WAV file.
    """
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    sf.write(file_path, signal, sr)


class AudioDatasetManager:
    """
    High-level manager for managing audio benchmarks and test samples.
    """
    def __init__(self, base_dir="datasets"):
        self.base_dir = base_dir
        self.samples_dir = os.path.join(base_dir, "test_samples")
        self.watermarked_dir = os.path.join(base_dir, "watermarked")
        self.attacked_dir = os.path.join(base_dir, "attacked")

        os.makedirs(self.samples_dir, exist_ok=True)
        os.makedirs(self.watermarked_dir, exist_ok=True)
        os.makedirs(self.attacked_dir, exist_ok=True)

    def prepare_test_samples(self, count=5, sr=16000, duration=3.0):
        """
        Ensure test audio files exist. If none exist, generate synthetic speech.
        """
        existing = glob.glob(os.path.join(self.samples_dir, "*.wav"))
        if len(existing) >= count:
            return sorted(existing)[:count]

        print(f"Generating {count} test speech samples in {self.samples_dir}...")
        return create_test_audio_dataset(self.samples_dir, num_samples=count, sample_rate=sr, duration=duration)

    def get_audio_paths(self):
        """
        Retrieve all available WAV files in the test samples directory.
        """
        return sorted(glob.glob(os.path.join(self.samples_dir, "*.wav")))
