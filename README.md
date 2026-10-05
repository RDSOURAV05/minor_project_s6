# Minor Project S6 — Audio Watermarking using DWT-SVD for AI-Generated Audio Detection

> **Base Paper**: *DeepMark Benchmark: Redefining Audio Watermarking Robustness* (IEEE Access 2026)  
> **Repository**: Minor Project S6 — Academic Evaluation Testbed & Full-Stack System  
> **Status**: Phase 3 Complete (React Frontend + Kaggle Dataset Empirical Benchmark)

---

## 1. System Overview

This system provides a proactive defense against unauthorized AI audio deepfakes and speech tampering. By embedding imperceptible, cryptographic watermark signatures into the singular values of the 3-level Discrete Wavelet Transform (DWT-SVD) approximation sub-band, genuine speech can be authenticated, tampering can be localized across time, and unwatermarked or spoofed AI voices are reliably detected.

### Key Capabilities
- **High Audio Fidelity**: Imperceptible degradation ($\text{SNR} \ge 37.5\text{ dB}$, $\text{PSNR} \ge 53.9\text{ dB}$, $\text{LSD} < 0.2\text{ dB}$).
- **DeepMark Robustness Suite**: Resilient against Additive White Gaussian Noise (0–40 dB), MP3 compression (32–320 kbps), lowpass/highpass/bandpass filters, 8 kHz resampling, volume scaling, cropping, and neural vocoder re-synthesis.
- **Proactive Provenance Detection**: Distinguishes authentic audio from unwatermarked deepfakes with $\text{ROC-AUC} \ge 0.99$, outperforming passive post-hoc classifiers.
- **Temporal Tamper Localization**: Identifies cropped, zeroed, or infilled audio intervals using block-based watermark verification.

---

## 2. Architecture & Components

```
minor_project_s6/
├── api/                          # FastAPI REST Backend
│   └── main.py                   # REST endpoints for embed, attack, detect, and benchmark
├── frontend/                     # Vite + React Frontend
│   ├── src/
│   │   ├── components/           # WaveformViewer (SVG), BitMapViewer, TamperTimeline
│   │   ├── tabs/                 # EmbedTab, AttackTab, DetectTab, BenchmarkTab
│   │   ├── App.jsx               # Navigation, light/dark mode toggle
│   │   └── index.css             # Academic typography & CSS design system
│   ├── package.json
│   └── vite.config.js
├── implementation/src/           # Core Signal Processing & Pipeline Engine
│   ├── embedding/dwt_svd.py      # 3-Level DWT + SVD Watermarking Engine
│   ├── attacks/audio_attacks.py  # DeepMark Attack Suite Orchestrator
│   ├── data/kaggle_dataset.py    # Kaggle dataset loader, preprocessor & caching
│   ├── detection/detector.py     # WatermarkIntegrityDetector & AudioAuthenticityClassifier
│   ├── evaluation/metrics.py     # SNR, PSNR, SegSNR, LSD, BER, NCC, ROC-AUC, EER
│   └── pipeline/kaggle_evaluator.py # Kaggle evaluation runner & figure generator
├── benchmark_results/            # Empirical benchmarks, 300 DPI plots, and CSV reports
├── legacy/                       # Preserved Streamlit Application
│   └── app.py
├── samples/                      # Sample 16 kHz audio files for instant testing
├── tests/                        # 22 Automated Unit & Integration Tests (100% Passing)
└── run_pipeline.py               # Unified CLI runner for demo, benchmarks & servers
```

---

## 3. Quick Start & Run Instructions

### Prerequisites
- Python 3.10+ (managed via `uv` or standard virtual environment)
- Node.js 18+ and `npm`

```bash
# 1. Sync Python dependencies
uv sync

# 2. Install frontend dependencies
cd frontend
npm install
cd ..
```

---

### Option A: Run Full-Stack Web Application (Recommended)

Start both the FastAPI backend and Vite React frontend concurrently with a single command:

```powershell
uv run python run_pipeline.py --serve
```

- **Frontend Application**: [http://localhost:5173](http://localhost:5173)
- **FastAPI Backend**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

#### Running Services Separately
If preferred, you can run the backend and frontend in separate terminals:

```powershell
# Terminal 1 — Backend
uvicorn api.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
npm run dev
```

---

### Option B: Kaggle Dataset Real-World Evaluation

Dataset: [Speech Dataset of Human and AI-Generated Voices](https://www.kaggle.com/datasets/kambingbersayaphitam/speech-dataset-of-human-and-ai-generated-voices) (`kambingbersayaphitam`)

To run the complete evaluation protocol on the dataset:
```powershell
uv run python run_pipeline.py --kaggle [--data-dir data/kaggle_dataset] [--n-per-class 200]
```

This outputs:
- `benchmark_results/kaggle_results.json`
- `benchmark_results/kaggle_fidelity.csv`
- `benchmark_results/kaggle_robustness.csv`
- `benchmark_results/kaggle_detection.csv`
- `benchmark_results/kaggle_alpha_sweep.csv`
- 300 DPI plots:
  - `benchmark_results/kaggle_roc_curves.png`
  - `benchmark_results/kaggle_ber_vs_attack.png`
  - `benchmark_results/kaggle_alpha_tradeoff.png`
  - `benchmark_results/kaggle_fidelity_distribution.png`
- `results_summary.md` (detailed discussion of results and limitations)

#### Kaggle Credentials Setup
To download datasets using the Kaggle API:
1. Obtain `kaggle.json` from your Kaggle account (Account Settings &rarr; API &rarr; Create New Token).
2. Place the token in `~/.kaggle/kaggle.json` (Windows: `C:\Users\<Username>\.kaggle\kaggle.json`).
3. Or pass `--data-dir PATH` to point to a local directory containing the unzipped dataset.

---

### Option C: Interactive CLI Demonstration
```powershell
uv run python run_pipeline.py --demo
```
Runs a single-clip speech synthesis, DWT-SVD embedding, SNR verification, attack simulation, and verification against an unwatermarked spoof.

---

### Option D: Synthetic DeepMark Benchmark
```powershell
uv run python run_pipeline.py --benchmark
```
Runs the synthetic benchmark suite and updates empirical plots in `benchmark_results/`.

---

### Option E: Run Automated Test Suite
```powershell
uv run pytest tests/ -v
```
Executes all 22 unit and integration tests covering:
- Watermarking (embedding, noiseless extraction, QIM mode, block embedding)
- Attack suite (AWGN, filters, resampling, scaling, compression, resynthesis)
- Detection engine (integrity detector, Random Forest classifier, ROC-AUC, EER)
- Metrics (SNR, PSNR, SegSNR, LSD, BER, NCC, classification metrics)
- API backend endpoints (`/api/health`, `/api/samples`, `/api/embed`, `/api/attack`, `/api/detect`)
- Kaggle dataset loader, speaker splitting, and evaluation protocol

---

### Option F: Legacy Streamlit Web GUI
The previous Streamlit interface has been preserved in `legacy/app.py`:
```powershell
uv run streamlit run legacy/app.py
```
