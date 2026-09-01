# Summary: Paper 1 **(BASE PAPER)** - DeepMark Benchmark: Redefining Audio Watermarking Robustness (Base Paper)

**Authors:** S. Kovačević, E. Nešović, K. Pavlović, P. Nedić, and I. Djurović  
**Journal:** IEEE Access (2026)  
**Volume:** 14 | **Pages:** 62031-62044  
**DOI:** https://doi.org/10.1109/ACCESS.2026.3685903  
**PDF File:** `IEEE_Research_Papers/Papers/IEEE_Paper_01_BasePaper_DeepMark_Benchmark_2026.pdf`  

---

### Abstract
This paper introduces DeepMark Benchmark, a comprehensive and extensible framework for evaluating the robustness of audio watermarking algorithms. The benchmark enables systematic evaluation of watermarking methods against a diverse range of attacks, including audio editing operations, distortion and desynchronization attacks, end-to-end transmission scenarios, and deep learning-based transformations leveraging generative models and neural audio processing. Using this framework, we benchmark several state-of-the-art audio watermarking models and provide a comparative analysis of their robustness across attack categories. In addition, we introduce Process Disruption Attacks, which occur when multiple watermarking models are applied to the same audio signal.

### Key Methodology & Architecture
Standardized evaluation pipeline, end-to-end differentiable noise layers, Process Disruption Attacks, plugin-based architecture (BaseModel, BaseAttack), perceptual evaluation of audio quality (PEAQ, STOI).

### Datasets & Benchmarks
DeepMark Benchmark Suite (Common Voice, VCTK, GTZAN music dataset, Aachen AIR impulse response database).

### Performance Metrics & Experimental Results
- **Reported Results:** Robustness Score Matrix (0-100), PEAQ ODG (-0.2 to -4.0), STOI Score (0.0 to 1.0), BER under AAC 64 kbps < 1.2%.
- **Graph Parameter Mapping:** X-axis: Attack Category (Process Disruption, Audio Editing, Audio Distortion, Desynchronization, AI Attacks, Transmission); Y-axis: Watermark Detection Accuracy (% / Bit Accuracy 0% to 100%).

### Comparative Analysis
- **Pros:** Comprehensive open-source benchmark, evaluates 6 SOTA models against 40 attacks, introduces Process Disruption Attacks.
- **Cons:** AI-based attacks require high GPU computational memory and execution time.

### IEEE Citation
`S. Kovačević, E. Nešović, K. Pavlović, P. Nedić, and I. Djurović, "DeepMark Benchmark: Redefining Audio Watermarking Robustness (Base Paper)," IEEE Access, vol. 14, pp. 62031-62044, 2026, doi: 10.1109/ACCESS.2026.3685903.`
