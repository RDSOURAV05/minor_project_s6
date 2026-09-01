import numpy as np
import pywt
import librosa
import soundfile as sf

class DWTSVDWatermarker:
    def __init__(self, wavelet='db4', level=3, alpha=0.1):
        """
        Initialize the DWT-SVD Watermarker.
        
        :param wavelet: Wavelet type to use (default: Daubechies 4)
        :param level: Decomposition level (default: 3)
        :param alpha: Watermark embedding strength
        """
        self.wavelet = wavelet
        self.level = level
        self.alpha = alpha

    def embed_watermark(self, audio_path, watermark, output_path):
        """
        Embed a binary watermark into the audio using 3-Level DWT and SVD.
        
        :param audio_path: Path to the original audio file
        :param watermark: 1D numpy array of binary watermark bits (0s and 1s)
        :param output_path: Path to save the watermarked audio
        """
        # 1. Load the input audio signal s(t)
        audio, sr = librosa.load(audio_path, sr=None)
        
        # 2. Apply 3-Level DWT decomposition
        # coeffs is a list: [cA3, cD3, cD2, cD1] for level=3
        coeffs = pywt.wavedec(audio, self.wavelet, level=self.level)
        
        # We perform SVD on the LL sub-band (cA3 - the approximation coefficients)
        cA3 = coeffs[0]
        
        # Reshape cA3 into a 2D matrix for SVD
        # Determine matrix dimensions (approx square)
        matrix_dim = int(np.ceil(np.sqrt(len(cA3))))
        pad_size = matrix_dim * matrix_dim - len(cA3)
        
        # Pad cA3 to make it a perfect square
        cA3_padded = np.pad(cA3, (0, pad_size), 'constant')
        cA3_matrix = cA3_padded.reshape((matrix_dim, matrix_dim))
        
        # 3. Perform SVD on the LL sub-band matrix
        U, S, Vt = np.linalg.svd(cA3_matrix, full_matrices=False)
        
        # 4. Embed watermark: Sigma_i_prime = Sigma_i + alpha * w_i
        # We need to make sure the watermark size matches the singular values (S)
        # S is a 1D array of size matrix_dim.
        # We will embed the watermark bits into the singular values.
        
        # Adjust watermark size to match S
        if len(watermark) < len(S):
            # Repeat or pad watermark if it's too short
            w_repeated = np.resize(watermark, len(S))
        else:
            w_repeated = watermark[:len(S)]
            
        # The watermark elements should ideally be mapped to -1 and 1
        w_mapped = np.where(w_repeated == 0, -1, 1)
        
        # Apply embedding equation
        S_prime = S + self.alpha * w_mapped
        
        # 5. Reconstruct the LL matrix using the modified singular values
        cA3_matrix_prime = np.dot(U, np.dot(np.diag(S_prime), Vt))
        
        # Flatten and remove padding to restore original cA3 shape
        cA3_prime_padded = cA3_matrix_prime.flatten()
        cA3_prime = cA3_prime_padded[:len(cA3)]
        
        # Update the coefficients
        coeffs[0] = cA3_prime
        
        # 6. Reconstruct using IDWT and generate watermarked audio sw(t)
        watermarked_audio = pywt.waverec(coeffs, self.wavelet)
        
        # Ensure the length matches the original audio (IDWT might add an extra sample)
        watermarked_audio = watermarked_audio[:len(audio)]
        
        # Save to file
        sf.write(output_path, watermarked_audio, sr)
        
        return watermarked_audio, sr, S

    def extract_watermark(self, watermarked_audio_path, original_S):
        """
        Extract the watermark from the watermarked audio.
        (This requires original singular values in this non-blind approach)
        """
        # Load the watermarked audio
        watermarked_audio, sr = librosa.load(watermarked_audio_path, sr=None)
        
        # Apply 3-Level DWT
        coeffs = pywt.wavedec(watermarked_audio, self.wavelet, level=self.level)
        cA3 = coeffs[0]
        
        # Reshape and pad
        matrix_dim = int(np.ceil(np.sqrt(len(cA3))))
        pad_size = matrix_dim * matrix_dim - len(cA3)
        cA3_padded = np.pad(cA3, (0, pad_size), 'constant')
        cA3_matrix = cA3_padded.reshape((matrix_dim, matrix_dim))
        
        # Perform SVD on the watermarked LL sub-band
        U, S_prime, Vt = np.linalg.svd(cA3_matrix, full_matrices=False)
        
        # Extract watermark: w_i = (Sigma_i_prime - Sigma_i) / alpha
        extracted_w_mapped = (S_prime - original_S) / self.alpha
        
        # Map back to 0 and 1
        extracted_w = np.where(extracted_w_mapped > 0, 1, 0)
        
        return extracted_w

# Example usage (can be removed or moved to a test file)
if __name__ == "__main__":
    print("DWT-SVD Watermarker initialized.")
