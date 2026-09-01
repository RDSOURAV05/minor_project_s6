# Minor Project S6 — Handoff Document

> **Topic**: Audio Watermarking using DWT-SVD for AI-Generated Audio Detection  
> **Branch**: `main`  
> **Last Updated**: September 2, 2026

---

## What Has Been Done

### Phase 1 — Research & Literature Survey (Complete)
- Collected and organized **12 IEEE research papers** on audio watermarking, deepfake detection, and DWT-SVD methods.
- Summarized all papers into `Documentation/IEEE_Papers_Summary.docx`.
- Created an **Overleaf LaTeX presentation** (`Overleaf_Presentation/`) covering problem statement, related work, and proposed approach.
- Automated paper scraping/fetching scripts in `Scripts/`.

### Phase 2 — Core Implementation (In Progress)

| Module | File | Status | What It Does |
|--------|------|--------|--------------|
| **Embedding** | `src/embedding/dwt_svd.py` | Done | Embeds + extracts binary watermarks using 3-level DWT + SVD |
| **Evaluation** | `src/evaluation/metrics.py` | Done | SNR, PSNR, BER, NCC metric calculations |
| **Data** | `src/data/dataset_manager.py` | Done | Downloads LibriSpeech; placeholder for ASVspoof 2021 |
| **Detection** | `src/detection/` | TODO | Deepfake detection pipeline (not yet implemented) |

---

## How the Algorithm Works

```
Original Audio --> 3-Level DWT --> LL Sub-band (cA3)
                                         |
                                   Reshape to 2D Matrix
                                         |
                                   SVD: U, S, Vt
                                         |
                         Embed: S' = S + alpha * watermark_bits
                                         |
                        Reconstruct: cA3' = U . diag(S') . Vt
                                         |
                          IDWT --> Watermarked Audio
```

**Extraction** (non-blind, requires original singular values S):
```
watermark_bits = sign( (S'_extracted - S_original) / alpha )
```

**Quality Metrics:**
- **SNR / PSNR** — measures audio quality degradation (higher = better)
- **BER** — Bit Error Rate of extracted watermark (lower = better, 0 = perfect)
- **NCC** — Normalized Cross-Correlation (closer to 1 = better)

---

## Project Structure

```
minor_project_s6/
├── Documentation/
│   └── IEEE_Papers_Summary.docx     # Literature survey summary
├── IEEE_Research_Papers/            # 12 reference papers
├── Overleaf_Presentation/           # LaTeX slides for presentation
├── Scripts/                         # Paper fetching/automation scripts
├── implementation/
│   ├── requirements.txt             # Python dependencies
│   └── src/
│       ├── embedding/
│       │   └── dwt_svd.py           # Core algorithm (DWT-SVD)
│       ├── evaluation/
│       │   └── metrics.py           # SNR, PSNR, BER, NCC
│       ├── data/
│       │   └── dataset_manager.py   # Dataset loader
│       └── detection/               # (TODO)
├── .gitignore
└── HANDOFF.md                       # This file
```

---

## How to Run / Demo for Teachers

### 1. Setup Environment
```powershell
# From project root
.\venv\Scripts\Activate.ps1
pip install -r implementation\requirements.txt
```

### 2. Embed & Extract a Watermark
```python
import numpy as np
import sys
sys.path.insert(0, 'implementation/src')
from embedding.dwt_svd import DWTSVDWatermarker

watermarker = DWTSVDWatermarker(wavelet='db4', level=3, alpha=0.1)

watermark_bits = np.array([1, 0, 1, 1, 0, 1, 0, 0])
watermarked, sr, original_S = watermarker.embed_watermark(
    "path/to/input.wav",
    watermark_bits,
    "path/to/output_watermarked.wav"
)

extracted = watermarker.extract_watermark("path/to/output_watermarked.wav", original_S)
print("Original: ", watermark_bits)
print("Extracted:", extracted[:len(watermark_bits)])
```

### 3. Evaluate Quality
```python
from evaluation.metrics import calculate_snr, calculate_ber
snr = calculate_snr(original_audio, watermarked_audio)
ber = calculate_ber(watermark_bits, extracted_bits)
print(f"SNR: {snr:.2f} dB | BER: {ber:.4f}")
```

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `PyWavelets` | DWT/IDWT transforms |
| `librosa` | Audio loading & processing |
| `soundfile` | Writing watermarked .wav files |
| `numpy` / `scipy` | Matrix ops, SVD |
| `torch` / `torchaudio` | Dataset loading (LibriSpeech) |
| `matplotlib` | Plotting (future use) |
| `tqdm` | Progress bars |

---

## What is Left (Next Steps)

1. **Detection module** — classifier to detect AI-generated audio using watermark presence
2. **End-to-end pipeline script** — tie embedding, evaluation, and detection together
3. **Robustness testing** — test watermark survival under MP3 compression, noise, pitch shift
4. **Dataset integration** — download and use ASVspoof 2021 for deepfake detection
5. **Results visualization** — SNR/BER plots across different alpha values

---

## Git Notes

- `venv/` and `.venv/` are in `.gitignore` — never commit these
- Datasets (`.wav`, `.flac`, `.mp3`, `dataset/`) are also excluded
- Branch off `main` for new features

---
