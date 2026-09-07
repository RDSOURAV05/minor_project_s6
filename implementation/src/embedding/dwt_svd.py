"""
DWT-SVD Audio Watermarking Module.

Supports:
- 3-Level Discrete Wavelet Transform (DWT) decomposition
- Singular Value Decomposition (SVD) on approximation sub-band (LL / cA3)
- Embedding and extraction in both Non-Blind and QIM (Quantization Index Modulation / Semi-Blind) modes
- Direct in-memory numpy signal processing and file-based I/O
- Full-signal and block-based watermarking for tamper localization
- Cryptographic / PRNG watermark key generation
"""

import math
import numpy as np
import pywt
import librosa
import soundfile as sf


class DWTSVDWatermarker:
    def __init__(self, wavelet='db4', level=3, alpha=0.1, mode='non_blind', qim_step=0.05):
        """
        Initialize the DWT-SVD Watermarker.
        
        :param wavelet: Wavelet type (default: 'db4' Daubechies 4)
        :param level: DWT decomposition level (default: 3)
        :param alpha: Watermark embedding strength for non-blind mode
        :param mode: 'non_blind' (requires original S) or 'qim' (quantization index modulation, semi-blind)
        :param qim_step: Quantization step size Delta for QIM mode
        """
        self.wavelet = wavelet
        self.level = level
        self.alpha = alpha
        self.mode = mode.lower()
        self.qim_step = qim_step

    @staticmethod
    def generate_watermark(length, key=None):
        """
        Generate a binary pseudo-random watermark sequence from an integer key/seed.
        
        :param length: Number of bits to generate
        :param key: Random seed for reproducible cryptographic watermark key
        :return: 1D numpy array of 0s and 1s (dtype=np.int32)
        """
        rng = np.random.RandomState(key)
        return rng.randint(0, 2, size=length, dtype=np.int32)

    # -------------------------------------------------------------------------
    # Core In-Memory Signal Embedding & Extraction
    # -------------------------------------------------------------------------

    def embed_signal(self, audio_signal, watermark):
        """
        Embed binary watermark bits into a 1D audio numpy signal.
        
        :param audio_signal: 1D numpy array of floating-point audio samples
        :param watermark: 1D numpy array of binary watermark bits (0s and 1s)
        :return: (watermarked_signal, original_S_or_metadata)
        """
        watermark = np.asarray(watermark, dtype=np.int32)
        original_len = len(audio_signal)

        # 1. Apply DWT decomposition: [cA3, cD3, cD2, cD1] for level=3
        coeffs = pywt.wavedec(audio_signal, self.wavelet, level=self.level)
        cA = coeffs[0]

        # 2. Reshape cA into a 2D matrix for SVD
        matrix_dim = int(np.ceil(np.sqrt(len(cA))))
        pad_size = matrix_dim * matrix_dim - len(cA)
        cA_padded = np.pad(cA, (0, pad_size), 'constant')
        cA_matrix = cA_padded.reshape((matrix_dim, matrix_dim))

        # 3. Perform SVD on the approximation subband matrix
        U, S, Vt = np.linalg.svd(cA_matrix, full_matrices=False)
        original_S = S.copy()

        # 4. Prepare watermark to match the singular values vector
        if len(watermark) < len(S):
            w_repeated = np.resize(watermark, len(S))
        else:
            w_repeated = watermark[:len(S)]

        if self.mode == 'qim':
            # Quantization Index Modulation (Semi-blind)
            # For bit 0: quantize S to nearest even multiple of Delta
            # For bit 1: quantize S to nearest odd multiple of Delta
            delta = self.qim_step * (np.mean(S) + 1e-6)
            S_prime = np.zeros_like(S)
            for i, (s_val, b) in enumerate(zip(S, w_repeated)):
                k = np.round(s_val / delta)
                if b == 0:
                    if k % 2 != 0:
                        k = k + 1 if (s_val / delta) >= k else k - 1
                else:
                    if k % 2 == 0:
                        k = k + 1 if (s_val / delta) >= k else k - 1
                S_prime[i] = k * delta
        else:
            # Non-blind additive embedding: S' = S + alpha * w_mapped
            w_mapped = np.where(w_repeated == 0, -1.0, 1.0)
            S_prime = S + self.alpha * w_mapped

        # 5. Reconstruct the approximation matrix using modified singular values
        cA_matrix_prime = np.dot(U, np.dot(np.diag(S_prime), Vt))
        cA_prime_padded = cA_matrix_prime.flatten()
        cA_prime = cA_prime_padded[:len(cA)]

        # 6. Reconstruct full audio via IDWT
        coeffs[0] = cA_prime
        watermarked_signal = pywt.waverec(coeffs, self.wavelet)

        # Truncate or pad to preserve original audio length
        if len(watermarked_signal) > original_len:
            watermarked_signal = watermarked_signal[:original_len]
        elif len(watermarked_signal) < original_len:
            watermarked_signal = np.pad(watermarked_signal, (0, original_len - len(watermarked_signal)), 'constant')

        metadata = {
            'original_S': original_S,
            'U': U,
            'Vt': Vt,
            'matrix_dim': matrix_dim,
            'watermark_length': len(watermark),
            'mode': self.mode,
            'alpha': self.alpha,
            'qim_step': self.qim_step,
        }

        return watermarked_signal, metadata

    def extract_signal(self, watermarked_signal, original_S_or_metadata, watermark_len=None):
        """
        Extract the watermark from a 1D audio numpy signal.
        
        :param watermarked_signal: 1D numpy array of watermarked audio samples
        :param original_S_or_metadata: Original S array (for non-blind) or metadata dict
        :param watermark_len: Length of watermark to extract (optional)
        :return: 1D numpy array of extracted binary bits (0s and 1s)
        """
        if isinstance(original_S_or_metadata, dict):
            original_S = original_S_or_metadata.get('original_S')
            U_orig = original_S_or_metadata.get('U')
            Vt_orig = original_S_or_metadata.get('Vt')
            mode = original_S_or_metadata.get('mode', self.mode)
            qim_step = original_S_or_metadata.get('qim_step', self.qim_step)
            if watermark_len is None:
                watermark_len = original_S_or_metadata.get('watermark_length')
        else:
            original_S = np.asarray(original_S_or_metadata)
            U_orig = None
            Vt_orig = None
            mode = self.mode
            qim_step = self.qim_step

        # 1. Apply DWT decomposition
        coeffs = pywt.wavedec(watermarked_signal, self.wavelet, level=self.level)
        cA = coeffs[0]

        # 2. Reshape and pad
        matrix_dim = int(np.ceil(np.sqrt(len(cA))))
        pad_size = matrix_dim * matrix_dim - len(cA)
        cA_padded = np.pad(cA, (0, pad_size), 'constant')
        cA_matrix = cA_padded.reshape((matrix_dim, matrix_dim))

        if mode == 'qim':
            # Semi-blind extraction using quantization step
            U, S_prime, Vt = np.linalg.svd(cA_matrix, full_matrices=False)
            delta = qim_step * (np.mean(S_prime) + 1e-6)
            k = np.round(S_prime / delta).astype(int)
            extracted_w = (k % 2 != 0).astype(np.int32)
        elif U_orig is not None and Vt_orig is not None:
            # Projection onto original orthonormal bases: avoids eigenvalue permutation/sorting errors
            min_dim = min(cA_matrix.shape[0], U_orig.shape[0], Vt_orig.shape[1])
            mat_sub = cA_matrix[:min_dim, :min_dim]
            U_sub = U_orig[:min_dim, :min_dim]
            Vt_sub = Vt_orig[:min_dim, :min_dim]
            S_proj = np.diag(np.dot(U_sub.T, np.dot(mat_sub, Vt_sub.T)))
            comp_len = min(len(S_proj), len(original_S))
            diff = (S_proj[:comp_len] - original_S[:comp_len]) / self.alpha
            extracted_w = np.where(diff > 0, 1, 0).astype(np.int32)
        else:
            # Fallback when only original_S vector is available
            U, S_prime, Vt = np.linalg.svd(cA_matrix, full_matrices=False)
            comp_len = min(len(S_prime), len(original_S))
            diff = (S_prime[:comp_len] - original_S[:comp_len]) / self.alpha
            extracted_w = np.where(diff > 0, 1, 0).astype(np.int32)

        if watermark_len is not None and watermark_len <= len(extracted_w):
            return extracted_w[:watermark_len]
        return extracted_w

    # -------------------------------------------------------------------------
    # Block-Based Embedding & Extraction (For Tamper Localization)
    # -------------------------------------------------------------------------

    def embed_blocks(self, audio_signal, watermark, block_size=4096):
        """
        Embed watermark bits across audio frames/blocks for fine-grained tamper localization.
        
        :param audio_signal: 1D numpy array
        :param watermark: 1D binary array
        :param block_size: Block size in samples (e.g. 4096)
        :return: (watermarked_signal, list_of_block_metadata)
        """
        num_blocks = len(audio_signal) // block_size
        if num_blocks == 0:
            return self.embed_signal(audio_signal, watermark)

        watermarked_signal = np.copy(audio_signal)
        block_metadata = []

        bits_per_block = max(1, len(watermark) // num_blocks)

        for b_idx in range(num_blocks):
            start = b_idx * block_size
            end = start + block_size
            block = audio_signal[start:end]

            w_start = (b_idx * bits_per_block) % len(watermark)
            w_end = w_start + bits_per_block
            block_bits = watermark[w_start:w_end]

            wm_block, meta = self.embed_signal(block, block_bits)
            watermarked_signal[start:end] = wm_block
            meta['block_idx'] = b_idx
            meta['watermark_bits'] = block_bits
            block_metadata.append(meta)

        return watermarked_signal, block_metadata

    def extract_blocks(self, watermarked_signal, block_metadata, block_size=4096):
        """
        Extract watermark from audio blocks and determine tamper status per block.
        
        :param watermarked_signal: 1D numpy array
        :param block_metadata: Metadata list from embed_blocks
        :param block_size: Block size in samples
        :return: (extracted_bits_array, block_results)
        """
        num_blocks = min(len(block_metadata), len(watermarked_signal) // block_size)
        all_extracted = []
        block_results = []

        for b_idx in range(num_blocks):
            start = b_idx * block_size
            end = start + block_size
            block = watermarked_signal[start:end]
            meta = block_metadata[b_idx]

            expected_bits = meta.get('watermark_bits')
            extracted = self.extract_signal(block, meta, watermark_len=len(expected_bits))
            all_extracted.extend(extracted)

            # Block integrity check
            min_len = min(len(expected_bits), len(extracted))
            errors = np.sum(expected_bits[:min_len] != extracted[:min_len])
            ber = errors / min_len if min_len > 0 else 1.0

            block_results.append({
                'block_idx': b_idx,
                'start_sample': start,
                'end_sample': end,
                'ber': float(ber),
                'is_tampered': bool(ber > 0.25)
            })

        return np.array(all_extracted, dtype=np.int32), block_results

    # -------------------------------------------------------------------------
    # Backward-Compatible File-Based Interface
    # -------------------------------------------------------------------------

    def embed_watermark(self, audio_path, watermark, output_path):
        """
        File-based wrapper: Embed a binary watermark into an audio file.
        Preserves backward compatibility with existing project scripts.
        """
        audio, sr = librosa.load(audio_path, sr=None)
        watermarked_audio, metadata = self.embed_signal(audio, watermark)
        sf.write(output_path, watermarked_audio, sr)
        return watermarked_audio, sr, metadata['original_S']

    def extract_watermark(self, watermarked_audio_path, original_S):
        """
        File-based wrapper: Extract watermark from an audio file.
        Preserves backward compatibility with existing project scripts.
        """
        watermarked_audio, sr = librosa.load(watermarked_audio_path, sr=None)
        return self.extract_signal(watermarked_audio, original_S)


if __name__ == "__main__":
    print("DWT-SVD Watermarker module loaded.")
