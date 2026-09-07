"""
Audio Attack Simulation Suite.

Implements standard digital signal processing and transmission attacks
aligned with the DeepMark Benchmark (IEEE Access 2026):
1. Additive White Gaussian Noise (AWGN) at specified SNR (0 to 40 dB)
2. Butterworth Lowpass, Highpass, and Bandpass Filtering
3. Resampling Attack (Downsampling / Upsampling)
4. Amplitude / Gain Scaling
5. Time-Domain Cropping / Zero-Padding
6. Lossy Compression Simulation (MP3/AAC Psychoacoustic Quantization)
7. Generative Re-synthesis / Neural Vocoder Perturbation Attack
"""

import math
import numpy as np
from scipy import signal as sp_signal


def add_awgn_noise(signal, snr_db):
    """
    Add Additive White Gaussian Noise (AWGN) to achieve a specified SNR in dB.
    
    :param signal: 1D numpy array of audio samples
    :param snr_db: Target Signal-to-Noise Ratio in dB (e.g., 0, 10, 20, 30 dB)
    :return: 1D numpy array of noisy audio samples
    """
    signal = np.asarray(signal, dtype=np.float64)
    signal_power = np.mean(signal ** 2)
    if signal_power == 0:
        return signal.copy()

    # SNR = 10 * log10(P_signal / P_noise) => P_noise = P_signal / (10^(SNR/10))
    noise_power = signal_power / (10.0 ** (snr_db / 10.0))
    noise = np.random.normal(0.0, np.sqrt(noise_power), size=len(signal))

    noisy_signal = signal + noise
    return np.clip(noisy_signal, -1.0, 1.0).astype(np.float32)


def apply_lowpass_filter(signal, sr=16000, cutoff=4000, order=5):
    """
    Apply a Butterworth low-pass filter to attenuate high-frequency components.
    
    :param signal: 1D numpy array
    :param sr: Sampling rate in Hz
    :param cutoff: Cutoff frequency in Hz
    :param order: Filter order
    :return: Filtered audio signal
    """
    nyquist = 0.5 * sr
    normal_cutoff = min(cutoff / nyquist, 0.99)
    b, a = sp_signal.butter(order, normal_cutoff, btype='low', analog=False)
    filtered = sp_signal.filtfilt(b, a, signal)
    return np.clip(filtered, -1.0, 1.0).astype(np.float32)


def apply_highpass_filter(signal, sr=16000, cutoff=300, order=5):
    """
    Apply a Butterworth high-pass filter to attenuate low-frequency components.
    
    :param signal: 1D numpy array
    :param sr: Sampling rate in Hz
    :param cutoff: Cutoff frequency in Hz
    :param order: Filter order
    :return: Filtered audio signal
    """
    nyquist = 0.5 * sr
    normal_cutoff = max(cutoff / nyquist, 0.01)
    b, a = sp_signal.butter(order, normal_cutoff, btype='high', analog=False)
    filtered = sp_signal.filtfilt(b, a, signal)
    return np.clip(filtered, -1.0, 1.0).astype(np.float32)


def apply_bandpass_filter(signal, sr=16000, lowcut=300, highcut=3400, order=5):
    """
    Apply a Butterworth band-pass filter (simulates narrow-band telephony/cellular channels).
    
    :param signal: 1D numpy array
    :param sr: Sampling rate in Hz
    :param lowcut: Lower cutoff in Hz
    :param highcut: Upper cutoff in Hz
    :param order: Filter order
    :return: Filtered audio signal
    """
    nyquist = 0.5 * sr
    low = max(lowcut / nyquist, 0.01)
    high = min(highcut / nyquist, 0.99)
    b, a = sp_signal.butter(order, [low, high], btype='band', analog=False)
    filtered = sp_signal.filtfilt(b, a, signal)
    return np.clip(filtered, -1.0, 1.0).astype(np.float32)


def apply_resampling_attack(signal, orig_sr=16000, target_sr=8000):
    """
    Simulate resampling attack by downsampling to target_sr and reconstructing back to orig_sr.
    
    :param signal: 1D numpy array
    :param orig_sr: Original sampling rate in Hz
    :param target_sr: Intermediate attack sampling rate (e.g. 8000 Hz)
    :return: Resampled signal of exact original length
    """
    orig_len = len(signal)
    num_downsampled = int(round(orig_len * target_sr / orig_sr))
    downsampled = sp_signal.resample(signal, max(1, num_downsampled))
    reconstructed = sp_signal.resample(downsampled, orig_len)
    return np.clip(reconstructed, -1.0, 1.0).astype(np.float32)


def apply_amplitude_scaling(signal, factor=0.8):
    """
    Scale the signal amplitude by a gain factor (simulates volume change / attenuation / boosting).
    
    :param signal: 1D numpy array
    :param factor: Scaling multiplier
    :return: Scaled audio signal
    """
    scaled = signal * factor
    return np.clip(scaled, -1.0, 1.0).astype(np.float32)


def apply_cropping_attack(signal, crop_ratio=0.1, location='middle'):
    """
    Zero-out or crop a segment of the audio signal (tampering / packet loss attack).
    
    :param signal: 1D numpy array
    :param crop_ratio: Fraction of audio to zero-out (0.0 to 1.0)
    :param location: 'start', 'middle', or 'end'
    :return: Attacked audio signal with identical length
    """
    signal_copy = np.copy(signal)
    crop_len = int(len(signal_copy) * crop_ratio)

    if location == 'start':
        signal_copy[:crop_len] = 0.0
    elif location == 'end':
        signal_copy[-crop_len:] = 0.0
    else:  # middle
        start = (len(signal_copy) - crop_len) // 2
        signal_copy[start:start + crop_len] = 0.0

    return signal_copy.astype(np.float32)


def apply_compression_simulation(signal, sr=16000, bitrate=64):
    """
    Simulate lossy audio compression (MP3/AAC) via psychoacoustic subband quantization
    and high-frequency roll-off corresponding to the given bitrate.
    
    :param signal: 1D numpy array
    :param sr: Sampling rate in Hz
    :param bitrate: Bitrate in kbps (32, 64, 128, 192, 256, 320)
    :return: Compressed-like audio signal
    """
    # Lower bitrates impose stricter low-pass cutoff (MP3 standard practice)
    # 32k: ~8kHz cutoff, 64k: ~11kHz, 128k: ~15kHz, >=192k: ~Nyquist
    nyquist = 0.5 * sr
    if bitrate <= 32:
        cutoff = min(4000.0, nyquist * 0.5)
        quant_levels = 32
    elif bitrate <= 64:
        cutoff = min(6000.0, nyquist * 0.7)
        quant_levels = 64
    elif bitrate <= 128:
        cutoff = min(7500.0, nyquist * 0.9)
        quant_levels = 128
    else:
        cutoff = nyquist * 0.98
        quant_levels = 256

    # 1. High-frequency roll-off
    filtered = apply_lowpass_filter(signal, sr=sr, cutoff=cutoff, order=4)

    # 2. Spectral STFT quantization (simulates subband MDCT bit-budget allocation)
    n_fft = 512
    hop = 256
    window = np.hanning(n_fft)
    stft = []
    num_frames = max(1, (len(filtered) - n_fft) // hop + 1)

    for i in range(num_frames):
        start = i * hop
        frame = filtered[start:start + n_fft] * window
        stft.append(np.fft.rfft(frame))

    if stft:
        stft_matrix = np.array(stft)
        mag = np.abs(stft_matrix)
        phase = np.angle(stft_matrix)

        # Quantize magnitudes
        max_mag = np.max(mag) + 1e-8
        norm_mag = mag / max_mag
        quant_mag = np.round(norm_mag * quant_levels) / quant_levels * max_mag

        reconstructed_stft = quant_mag * np.exp(1j * phase)

        # Overlap-add reconstruction
        out = np.zeros(len(filtered), dtype=np.float64)
        norm_weights = np.zeros(len(filtered), dtype=np.float64)

        for i in range(num_frames):
            start = i * hop
            reconstructed_frame = np.fft.irfft(reconstructed_stft[i]) * window
            out[start:start + n_fft] += reconstructed_frame
            norm_weights[start:start + n_fft] += window ** 2

        norm_weights[norm_weights < 1e-6] = 1.0
        out = out / norm_weights
        return np.clip(out, -1.0, 1.0).astype(np.float32)

    return filtered.astype(np.float32)


def apply_resynthesis_attack(signal, noise_level=0.03):
    """
    Simulate neural vocoder re-synthesis attack (e.g. HiFi-GAN / WaveGlow / VITS pass-through)
    where speech is regenerated, perturbing subtle phase and singular value distributions.
    
    :param signal: 1D numpy array
    :param noise_level: Amplitude of harmonic/phase perturbation
    :return: Perturbed audio signal
    """
    # Perturb phases in the frequency domain while keeping envelope intact
    n_fft = 512
    hop = 256
    window = np.hanning(n_fft)
    num_frames = max(1, (len(signal) - n_fft) // hop + 1)
    out = np.zeros(len(signal), dtype=np.float64)
    norm_weights = np.zeros(len(signal), dtype=np.float64)

    for i in range(num_frames):
        start = i * hop
        frame = signal[start:start + n_fft] * window
        spec = np.fft.rfft(frame)
        mag = np.abs(spec)
        phase = np.angle(spec)

        # Add subtle phase jitter
        phase_jitter = np.random.uniform(-noise_level * np.pi, noise_level * np.pi, size=len(phase))
        spec_perturbed = mag * np.exp(1j * (phase + phase_jitter))

        rec_frame = np.fft.irfft(spec_perturbed) * window
        out[start:start + n_fft] += rec_frame
        norm_weights[start:start + n_fft] += window ** 2

    norm_weights[norm_weights < 1e-6] = 1.0
    out = out / norm_weights
    return np.clip(out, -1.0, 1.0).astype(np.float32)


# =============================================================================
# Attack Suite Orchestrator
# =============================================================================

class AttackSuite:
    """
    Orchestrates standardized attacks for benchmark evaluation.
    """
    @staticmethod
    def get_standard_attacks(sr=16000):
        """
        Returns a dictionary of named attack functions.
        """
        return {
            'No Attack (Clean)': lambda sig: sig,
            'AWGN Noise (30 dB)': lambda sig: add_awgn_noise(sig, snr_db=30),
            'AWGN Noise (20 dB)': lambda sig: add_awgn_noise(sig, snr_db=20),
            'AWGN Noise (10 dB)': lambda sig: add_awgn_noise(sig, snr_db=10),
            'Lowpass Filter (4 kHz)': lambda sig: apply_lowpass_filter(sig, sr=sr, cutoff=4000),
            'Highpass Filter (300 Hz)': lambda sig: apply_highpass_filter(sig, sr=sr, cutoff=300),
            'Resampling (8 kHz)': lambda sig: apply_resampling_attack(sig, orig_sr=sr, target_sr=8000),
            'Volume Scaling (0.8x)': lambda sig: apply_amplitude_scaling(sig, factor=0.8),
            'Volume Scaling (1.2x)': lambda sig: apply_amplitude_scaling(sig, factor=1.2),
            'Cropping Attack (10%)': lambda sig: apply_cropping_attack(sig, crop_ratio=0.1),
            'MP3 128 kbps Sim': lambda sig: apply_compression_simulation(sig, sr=sr, bitrate=128),
            'MP3 64 kbps Sim': lambda sig: apply_compression_simulation(sig, sr=sr, bitrate=64),
            'MP3 32 kbps Sim': lambda sig: apply_compression_simulation(sig, sr=sr, bitrate=32),
            'AI Vocoder Re-synth': lambda sig: apply_resynthesis_attack(sig, noise_level=0.03),
        }
