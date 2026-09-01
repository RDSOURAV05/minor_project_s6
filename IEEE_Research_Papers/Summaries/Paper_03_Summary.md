# Summary: Paper 3 - CANARY: Collision-Free Audio Watermarking for Proactive Deepfake Detection

**Authors:** Y. Sun, J. Wang, L. Zhang, and X. Liu  
**Journal:** IEEE Transactions on Multimedia (2026)  
**Volume:** 28 | **Pages:** 1420-1435  
**DOI:** https://doi.org/10.1109/TMM.2026.3724740  
**PDF File:** `IEEE_Research_Papers/Papers/IEEE_Paper_03_CANARY_Audio_Watermarking_2026.pdf`  

---

### Abstract
The rapid proliferation of generative audio models poses severe security risks to digital identity and content copyright. This paper presents CANARY, a proactive deepfake detection framework based on collision-free acoustic watermarking. By embedding pseudo-random orthogonal sequence codes in the high-frequency Discrete Cosine Transform (DCT) domain of audio signals prior to dissemination, CANARY ensures imperceptibility and prevents watermark collisions when multiple audio streams are merged or re-encoded.

### Key Methodology & Architecture
DCT-based orthogonal sequence embedding, deep neural decoder network, perceptual acoustic masking (ITU-R BS.1387), collision-avoidance hash indexing.

### Datasets & Benchmarks
LibriSpeech, ASVspoof 2021, VoxCeleb2 (Over 10,000 speech samples).

### Performance Metrics & Experimental Results
- **Reported Results:** Bit Error Rate (BER) < 0.05%, Watermark Detection Accuracy = 98.7%, PSNR = 46.2 dB.
- **Graph Parameter Mapping:** X-axis: Signal-to-Noise Ratio (SNR in dB, 0 to 40 dB); Y-axis: Bit Error Rate (BER, 0.0 to 0.5).

### Comparative Analysis
- **Pros:** Proactive protection, collision-free multi-stream tracking, robust against neural vocoders.
- **Cons:** Slightly higher computational latency during initial watermark embedding phase.

### IEEE Citation
`Y. Sun, J. Wang, L. Zhang, and X. Liu, "CANARY: Collision-Free Audio Watermarking for Proactive Deepfake Detection," IEEE Transactions on Multimedia, vol. 28, pp. 1420-1435, 2026, doi: 10.1109/TMM.2026.3724740.`
