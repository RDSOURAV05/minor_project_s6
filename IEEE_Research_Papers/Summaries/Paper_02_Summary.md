# Summary: Paper 2 - Optimal Semi-Fragile Watermarking Based on Maximum Entropy Random Walk and Swin Transformer for Tamper Localization

**Authors:** P. Aberna and L. Agilandeeswari  
**Journal:** IEEE Access (2024)  
**Volume:** 12 | **Pages:** 37757-37781  
**DOI:** https://doi.org/10.1109/ACCESS.2024.3370411  
**PDF File:** `IEEE_Research_Papers/Papers/IEEE_Paper_02_Optimal_SemiFragile_Watermarking_2024.pdf`  

---

### Abstract
Verifying digital audio authenticity requires not only detecting modifications but also precisely localizing tampered regions. This paper proposes an optimal semi-fragile audio watermarking system utilizing Maximum Entropy Random Walk (MERW) graph modeling and Swin Transformer architecture. The watermark key is generated dynamically from low-frequency DWT-SVD coefficients, while Swin Transformer extracts high-level acoustic feature representations to classify untouched vs manipulated segments.

### Key Methodology & Architecture
Discrete Wavelet Transform (DWT), Singular Value Decomposition (SVD), MERW graph optimization, Swin Transformer network for local spatial-temporal feature attention.

### Datasets & Benchmarks
TIMIT Acoustic-Phonetic Continuous Speech Corpus, Free Music Archive (FMA).

### Performance Metrics & Experimental Results
- **Reported Results:** Tamper Localization Accuracy = 99.4%, Precision = 99.1%, Recall = 99.6%, Normalized Cross-Correlation (NC) = 0.998.
- **Graph X-Axis:** X-axis: Tampering Ratio (% of audio altered, 0% to 50%)
- **Graph Y-Axis:**  Y-axis: Tamper Localization Precision & Recall (0.0 to 1.0).

### Comparative Analysis
- **Pros:** Extremely fine millisecond-level tamper localization, high fidelity preservation.
- **Cons:** Requires high computational GPU memory for Swin Transformer inference.

### IEEE Citation
`P. Aberna and L. Agilandeeswari, "Optimal Semi-Fragile Watermarking Based on Maximum Entropy Random Walk and Swin Transformer for Tamper Localization," IEEE Access, vol. 12, pp. 37757-37781, 2024, doi: 10.1109/ACCESS.2024.3370411.`
