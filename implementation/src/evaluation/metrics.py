import numpy as np
import math

def calculate_snr(original_signal, modified_signal):
    """
    Calculate the Signal-to-Noise Ratio (SNR) between original and modified audio.
    """
    # Ensure they are the same length
    min_len = min(len(original_signal), len(modified_signal))
    original_signal = original_signal[:min_len]
    modified_signal = modified_signal[:min_len]
    
    signal_power = np.sum(original_signal ** 2)
    noise_power = np.sum((original_signal - modified_signal) ** 2)
    
    if noise_power == 0:
        return float('inf')
        
    snr = 10 * math.log10(signal_power / noise_power)
    return snr

def calculate_psnr(original_signal, modified_signal, max_val=1.0):
    """
    Calculate the Peak Signal-to-Noise Ratio (PSNR).
    Audio is usually normalized between -1.0 and 1.0, so max_val=1.0 or 2.0 depending on convention.
    We'll use max_val=1.0 for normalized audio.
    """
    min_len = min(len(original_signal), len(modified_signal))
    original_signal = original_signal[:min_len]
    modified_signal = modified_signal[:min_len]
    
    mse = np.mean((original_signal - modified_signal) ** 2)
    if mse == 0:
        return float('inf')
        
    psnr = 20 * math.log10(max_val / math.sqrt(mse))
    return psnr

def calculate_ber(original_watermark, extracted_watermark):
    """
    Calculate Bit Error Rate (BER) between original and extracted watermark.
    """
    min_len = min(len(original_watermark), len(extracted_watermark))
    original_watermark = original_watermark[:min_len]
    extracted_watermark = extracted_watermark[:min_len]
    
    errors = np.sum(original_watermark != extracted_watermark)
    ber = errors / min_len
    return ber

def calculate_ncc(original_watermark, extracted_watermark):
    """
    Calculate Normalized Cross-Correlation (NCC).
    """
    min_len = min(len(original_watermark), len(extracted_watermark))
    o_w = original_watermark[:min_len]
    e_w = extracted_watermark[:min_len]
    
    numerator = np.sum(o_w * e_w)
    denominator = np.sqrt(np.sum(o_w ** 2)) * np.sqrt(np.sum(e_w ** 2))
    
    if denominator == 0:
        return 0
    return numerator / denominator
