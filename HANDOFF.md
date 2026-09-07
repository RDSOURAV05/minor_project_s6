# Minor Project S6 — Handoff Document

> **Topic**: Audio Watermarking using DWT-SVD for AI-Generated Audio Detection  
> **Base Paper**: *DeepMark Benchmark: Redefining Audio Watermarking Robustness* (IEEE Access 2026)  
> **Branch**: `main`  
> **Last Updated**: September 2026  

---

## 1. What Has Been Done

### Phase 1 — Research & Literature Survey (Complete)
- Collected and organized **12 IEEE research papers** on audio watermarking, deepfake detection, and DWT-SVD methods.
- Summarized all papers into `Documentation/IEEE_Papers_Summary.docx` and `IEEE_Research_Papers/Summaries/`.
- Created an **Overleaf LaTeX presentation** (`Overleaf_Presentation/`) and `First_Review/` folder covering problem statement, related work, and baseline comparisons.
- Established **DeepMark Benchmark (IEEE Access 2026)** as Paper #1 Base Paper.

### Phase 2 — Core Implementation & Benchmark Framework (Complete)

| Module | Location | Status | What It Does |
|--------|----------|--------|--------------|
| **Embedding** | `implementation/src/embedding/dwt_svd.py` | Complete | 3-Level DWT + SVD watermarking; supports In-Memory signals, Orthonormal Projection (0% clean BER), QIM (Semi-Blind), and Block-Based Tamper Localization |
| **Evaluation** | `implementation/src/evaluation/metrics.py` | Complete | Fidelity (SNR, PSNR, SegSNR, LSD), Watermark Recovery (BER, NCC, Bit Accuracy), and Detection (ROC, AUC, EER, Confusion Matrix) |
| **Attacks** | `implementation/src/attacks/audio_attacks.py` | Complete | DeepMark-aligned suite: AWGN noise (0–40 dB), Lowpass/Highpass/Bandpass filters, Resampling (8 kHz), Amplitude scaling, Cropping, MP3 compression simulation, AI Vocoder re-synthesis |
| **Data** | `implementation/src/data/dataset_manager.py` | Complete | Formant synthetic speech synthesis (standalone testing), test dataset generation, and audio loader utilities |
| **Detection** | `implementation/src/detection/detector.py` | Complete | `WatermarkIntegrityDetector` (confidence scoring, authenticity verdict, tamper localization) and `AudioAuthenticityClassifier` (supervised ML feature classifier) |
| **Pipeline & CLI** | `implementation/src/pipeline/` & `run_pipeline.py` | Complete | End-to-end benchmark execution, publication-grade graph generation, and single-command demo runner |
| **Automated Tests**| `tests/` | Complete | 15 comprehensive unit & integration tests covering watermarking, attacks, detection, and metrics |

---

## 2. System Architecture & Methodology

```
Original Audio ---> 3-Level DWT ---> LL Sub-band (cA3)
                                            |
                                     Reshape to Matrix
                                            |
                                      SVD: U, S, Vt
                                            |
                           Embed: S' = S + alpha * watermark_bits
                                            |
                         Reconstruct: cA3' = U . diag(S') . Vt
                                            |
                            IDWT ---> Watermarked Audio
                                            |
       +------------------------------------+------------------------------------+
       |                                                                         |
[Transmission / Attacks]                                                [Receiver & Detector]
(AWGN, MP3, Filters, Cropping)                                          Extract Watermark
       |                                                                         |
       +----------------------------> Verify Integrity <------------------------+
                                            |
                       +--------------------+--------------------+
                       |                                         |
             Confidence >= 85%                        Confidence < 30%
           [AUTHENTIC WATERMARKED]               [AI-GENERATED / SPOOFED]
```

### Orthonormal Projection Extraction (Zero-Error Non-Blind):
$$S_{\text{proj}} = \text{diag}(U^T \cdot A' \cdot V)$$
$$\text{Watermark Bits} = \text{sign}\left(\frac{S_{\text{proj}} - S}{\alpha}\right)$$
*Eliminates singular value sorting/permutation errors inherent in textbook SVD reconstruction.*

---

## 3. How to Run / Demo for Teachers & Reviews

### 1. Setup Environment
```powershell
# Sync local virtual environment using uv
uv sync
```

### 2. Run Interactive Streamlit Web GUI (Frontend)
```powershell
uv run streamlit run app.py
```
*Launches the full interactive web application in your browser: live embedding studio, attack stress test simulator, AI deepfake detector with color-coded bit maps, and benchmark analytics.*

### 3. Run Interactive CLI Demo
```powershell
uv run python run_pipeline.py --demo
```
*Outputs speech synthesis, embedding, SNR/PSNR verification, attack simulation, confidence scores, and rejection of spoofed AI voice.*

### 4. Run Full DeepMark Empirical Benchmark & Update Graphs
```powershell
uv run python run_pipeline.py --benchmark
```
*Executes full stress test across all attacks, computes ROC-AUC / EER, writes `benchmark_results/benchmark_results.json`, and automatically saves updated high-resolution graphs in:*
- `benchmark_results/metrics_graph.png`
- `First_Review/Presentation/metrics_graph.png`
- `Overleaf_Presentation/metrics_graph.png`

### 4. Run Automated Test Suite
```powershell
uv run pytest tests/ -v
```
*(All 15 tests pass in ~3.5s).*

---

## 4. Key Empirical Benchmark Results

- **Noiseless Reconstruction**: $\text{BER} = 0.0000$, $\text{NCC} = 1.0000$
- **Audio Fidelity**: $\text{SNR} = 38.60\text{ dB}$, $\text{PSNR} = 53.97\text{ dB}$ (imperceptible degradation)
- **Deepfake AI Detection**: $\text{ROC-AUC} = 0.9170$, $\text{Equal Error Rate (EER)} = 14.29\%$
- **Attack Robustness**:
  - AWGN Noise 25 dB: $\text{BER} = 0.0000$ (100% confidence)
  - AWGN Noise 15 dB: $\text{BER} = 0.0667$ (86.7% confidence)
  - MP3 Compression 128 kbps: $\text{BER} = 0.0667$ (86.7% confidence)
  - Unwatermarked AI Audio: $\text{BER} = 0.6444 \implies \text{Flagged as AI-Generated (0.0\% confidence)}$

---

## 5. Next Steps for Phase 3 (Final Review Preparation)

1. **Hardware / Real-Time Evaluation**: Measure inference latency (ms/sec of audio) for real-time streaming detection.
2. **Multi-Key Payload**: Embed payload metadata (speaker ID hash + timestamp) rather than fixed sequence.
3. **External Real Datasets**: Run batch benchmarks on large subsets of LibriSpeech and In-The-Wild Deepfake Audio dataset.
4. **GUI / Web Interface**: Build a lightweight interactive demonstration dashboard (e.g. Streamlit or web UI) for the final project presentation.
