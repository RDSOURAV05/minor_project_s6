# Summary: Paper 11 - Anomaly Detection of Deepfake Audio Based on Real Audio Using Generative Adversarial Network Model

**Authors:** D. Kim, J. H. Lee, and B. S. Park  
**Journal:** IEEE Access (2024)  
**Volume:** 12 | **Pages:** 152340-152352  
**DOI:** https://doi.org/10.1109/ACCESS.2024.3506973  
**PDF File:** `IEEE_Research_Papers/Papers/IEEE_Paper_11_GAN_Anomaly_Deepfake_Audio_Detection_2024.pdf`  

---

### Abstract
Unseen zero-day deepfake audio attacks often bypass supervised binary neural networks. This work proposes an unsupervised anomaly detection framework trained exclusively on authentic real audio signals using an Autoencoder-GAN.

### Key Methodology & Architecture
Autoencoder-GAN (AE-GAN), Reconstruction Error Loss, Latent Space Mapping, Anomaly Thresholding.

### Datasets & Benchmarks
VoxCeleb1, AudioSet Pristine Speech Subset, Zero-Day TTS Generators.

### Performance Metrics & Experimental Results
- **Reported Results:** Zero-Day Deepfake Detection AUC = 0.945, False Positive Rate (FPR) = 2.4%, Precision = 96.1%.
- **Graph Parameter Mapping:** X-axis: Anomaly Reconstruction Threshold; Y-axis: True Positive Rate vs False Positive Rate (ROC Curve).

### Comparative Analysis
- **Pros:** Does not require deepfake training samples; highly robust to unknown zero-day voice clones.
- **Cons:** Slightly lower accuracy on subtle, highly pristine generative audio.

### IEEE Citation
`D. Kim, J. H. Lee, and B. S. Park, "Anomaly Detection of Deepfake Audio Based on Real Audio Using Generative Adversarial Network Model," IEEE Access, vol. 12, pp. 152340-152352, 2024, doi: 10.1109/ACCESS.2024.3506973.`
