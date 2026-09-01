# Summary: Paper 9 - Audio Physical Dynamics Inspired Deepfake Detection for Voice Authentication Systems

**Authors:** C. Lin, Y. Huang, and T. Tan  
**Journal:** IEEE Networking Letters (2026)  
**Volume:** 8 | **Pages:** 112-116  
**DOI:** https://doi.org/10.1109/LNET.2026.3725616  
**PDF File:** `IEEE_Research_Papers/Papers/IEEE_Paper_09_Audio_Physical_Dynamics_Deepfake_2026.pdf`  

---

### Abstract
Voice biometric authentication systems are increasingly targeted by voice cloning spoof attacks. This letter presents a physical-dynamics inspired feature extraction method that measures vocal fold subglottal pressure variation.

### Key Methodology & Architecture
Glottal flow waveform estimation, Linear Predictive Coding (LPC) residual analysis, Bi-LSTM classifier.

### Datasets & Benchmarks
Logical Access Spoofing Dataset, Telephony Voice Banking Test Set.

### Performance Metrics & Experimental Results
- **Reported Results:** Equal Error Rate (EER) = 0.65%, Verification Latency = 8.5ms, Spoof Rejection Rate = 99.35%.
- **Graph Parameter Mapping:** X-axis: Biometric Threshold Score (-1.0 to 1.0); Y-axis: False Acceptance Rate (FAR) & False Rejection Rate (FRR).

### Comparative Analysis
- **Pros:** Low latency suitable for real-time mobile banking and voice assistant security.
- **Cons:** Requires high audio sampling rate (min 16kHz) for glottal residual extraction.

### IEEE Citation
`C. Lin, Y. Huang, and T. Tan, "Audio Physical Dynamics Inspired Deepfake Detection for Voice Authentication Systems," IEEE Networking Letters, vol. 8, pp. 112-116, 2026, doi: 10.1109/LNET.2026.3725616.`
