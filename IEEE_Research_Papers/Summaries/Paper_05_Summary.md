# Summary: Paper 5 - AWaveFormer: Audio Wavelet Transformer Network for Generalized Audio Deepfake Detection

**Authors:** Z. Wu, T. Li, H. Guan, and S. Gao  
**Journal:** IEEE Transactions on Audio, Speech and Language Processing (2025)  
**Volume:** 33 | **Pages:** 450-465  
**DOI:** https://doi.org/10.1109/TASLPRO.2025.3611229  
**PDF File:** `IEEE_Research_Papers/Papers/IEEE_Paper_05_AWaveFormer_Audio_Deepfake_Detection_2025.pdf`  

---

### Abstract
Generative neural vocoders like HiFi-GAN and WaveNet generate synthetic speech with high perceptual realism. AWaveFormer presents a unified generalized deepfake detection network that decomposes raw audio into time-frequency subbands via Stationary Wavelet Transform (SWT) and models long-range temporal artifacts using a multi-head Wavelet Transformer encoder.

### Key Methodology & Architecture
Stationary Wavelet Transform (SWT), Multi-Head Self-Attention Transformer, Cross-Scale Feature Fusion, Binary Cross-Entropy classification.

### Datasets & Benchmarks
ASVspoof 2019 LA/DF, WaveFake, In-the-Wild Deepfake Audio Dataset.

### Performance Metrics & Experimental Results
- **Reported Results:** Equal Error Rate (EER) = 0.82%, Tandem Detection Cost Function (t-DCF) = 0.024, Accuracy = 99.18%.
- **Graph Parameter Mapping:** X-axis: False Alarm Rate (FAR in %, 0% to 10%); Y-axis: Miss Detection Rate (MDR in %, 0% to 10%) [ROC Curve].

### Comparative Analysis
- **Pros:** Exceptional cross-dataset generalization across unseen text-to-speech (TTS) engines.
- **Cons:** Wavelet decomposition adds non-negligible memory footprint.

### IEEE Citation
`Z. Wu, T. Li, H. Guan, and S. Gao, "AWaveFormer: Audio Wavelet Transformer Network for Generalized Audio Deepfake Detection," IEEE Transactions on Audio, Speech and Language Processing, vol. 33, pp. 450-465, 2025, doi: 10.1109/TASLPRO.2025.3611229.`
