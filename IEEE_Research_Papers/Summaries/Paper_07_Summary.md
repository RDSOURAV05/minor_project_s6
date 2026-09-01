# Summary: Paper 7 - Dual-Channel Deepfake Audio Detection: Leveraging Direct and Reverberant Waveforms

**Authors:** J. Park, S. Lee, and H. Kim  
**Journal:** IEEE Access (2025)  
**Volume:** 13 | **Pages:** 14500-14512  
**DOI:** https://doi.org/10.1109/ACCESS.2025.3532775  
**PDF File:** `IEEE_Research_Papers/Papers/IEEE_Paper_07_DualChannel_Deepfake_Audio_Detection_2025.pdf`  

---

### Abstract
Synthetic voice generation algorithms typically model direct acoustic paths but fail to accurately reproduce subtle physical acoustic reverberation patterns present in real-world recorded environments. This paper introduces a dual-channel deep learning model that isolates direct path sound from room reverberant tail waveforms to detect synthetic voice artifacts.

### Key Methodology & Architecture
Blind Room Impulse Response (RIR) estimation, dual-stream CNN-LSTM network, phase-coherence cross-correlation, reverberation acoustic feature modeling.

### Datasets & Benchmarks
ACE Challenge Dataset, LibriSpeech RIR Synthesized Corpus, Real Office/Hall Recordings.

### Performance Metrics & Experimental Results
- **Reported Results:** Deepfake Detection Accuracy = 97.8%, AUC-ROC = 0.992, F1-Score = 0.976.
- **Graph X-Axis:** X-axis: Room Reverberation Time (RT60 in seconds, 0.1s to 1.2s)
- **Graph Y-Axis:**  Y-axis: Deepfake Detection Accuracy (80% to 100%).

### Comparative Analysis
- **Pros:** Leverages physical acoustic properties that generative AI cannot synthesize naturally.
- **Cons:** Performance degrades slightly in near-anechoic (zero reverberation) recording studios.

### IEEE Citation
`J. Park, S. Lee, and H. Kim, "Dual-Channel Deepfake Audio Detection: Leveraging Direct and Reverberant Waveforms," IEEE Access, vol. 13, pp. 14500-14512, 2025, doi: 10.1109/ACCESS.2025.3532775.`
