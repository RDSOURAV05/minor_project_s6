# Summary: Paper 3 - DeepMark Benchmark: Redefining Audio Watermarking Robustness

**Authors:** S. Kovačević, E. Nešović, K. Pavlović, P. Nedić, and I. Djurović  
**Journal:** IEEE Access (2026)  
**Volume:** 14 | **Pages:** 62031-62044  
**DOI:** https://doi.org/10.1109/ACCESS.2026.3685903  
**PDF File:** `IEEE_Research_Papers/Papers/IEEE_Paper_03_DeepMark_Benchmark_Audio_Watermarking_2026.pdf`  

---

### Abstract
Evaluating audio watermarking algorithms against modern generative attacks requires standardized benchmarks. DeepMark provides a comprehensive standardized testbed and open dataset for benchmarking traditional DSP watermarking (DWT, SVD, LSB, Patchwork) against deep learning neural watermarkers under realistic transmission attacks, MP3/AAC compression, pitch shifting, time stretching, and generative AI deepfake voice synthesis.

### Key Methodology & Architecture
Standardized evaluation pipeline, end-to-end differentiable noise layers, robustness score matrix, perceptual evaluation of audio quality (PEAQ).

### Datasets & Benchmarks
DeepMark Benchmark Suite (Common Voice, VCTK, GTZAN music dataset).

### Performance Metrics & Experimental Results
- **Reported Results:** Robustness Score (0-100), PEAQ ODG (-0.2 to -4.0), BER under AAC 64 kbps < 1.2%.
- **Graph X-Axis:** X-axis: Attack Type (MP3 64k, Additive Noise, Pitch Shift, AI Voice Synth)
- **Graph Y-Axis:**  Y-axis: Watermark Recovery Rate (0% to 100%).

### Comparative Analysis
- **Pros:** Comprehensive comparison across traditional and deep learning watermarking paradigms.
- **Cons:** Benchmark dataset size requires substantial disk storage for full evaluation.

### IEEE Citation
`S. Kovačević, E. Nešović, K. Pavlović, P. Nedić, and I. Djurović, "DeepMark Benchmark: Redefining Audio Watermarking Robustness," IEEE Access, vol. 14, pp. 62031-62044, 2026, doi: 10.1109/ACCESS.2026.3685903.`
