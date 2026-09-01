# Summary: Paper 8 - FLADD: Federated Learning-based Privacy Protection for Audio Deepfake Detection

**Authors:** L. Zhang, X. Chen, and Y. Wang  
**Journal:** IEEE Transactions on Audio, Speech and Language Processing (2026)  
**Volume:** 34 | **Pages:** 310-324  
**DOI:** https://doi.org/10.1109/TASLPRO.2026.3727931  
**PDF File:** `IEEE_Research_Papers/Papers/IEEE_Paper_08_FLADD_Federated_Audio_Deepfake_2026.pdf`  

---

### Abstract
Centralized audio deepfake detection model training raises privacy concerns when user speech recordings are uploaded to central cloud servers. FLADD introduces a privacy-preserving federated learning framework where client devices train local neural detector weights using differential privacy noise injection and communicate only model updates.

### Key Methodology & Architecture
Federated Averaging (FedAvg), Differential Privacy (DP-SGD), Light Convolutional Neural Network (LCNN), secure aggregation protocol.

### Datasets & Benchmarks
ASVspoof 2019, LibriSeech, Local Edge Device Testbeds.

### Performance Metrics & Experimental Results
- **Reported Results:** Global Model Accuracy = 96.85%, Differential Privacy Epsilon (ε) = 2.1, EER = 1.45%.
- **Graph X-Axis:** X-axis: Federated Training Rounds (0 to 100 rounds)
- **Graph Y-Axis:**  Y-axis: Global Model Test Accuracy (% from 50% to 100%).

### Comparative Analysis
- **Pros:** Guarantees user voice privacy while building robust collaborative detection models.
- **Cons:** Communication overhead over multi-client mobile networks.

### IEEE Citation
`L. Zhang, X. Chen, and Y. Wang, "FLADD: Federated Learning-based Privacy Protection for Audio Deepfake Detection," IEEE Transactions on Audio, Speech and Language Processing, vol. 34, pp. 310-324, 2026, doi: 10.1109/TASLPRO.2026.3727931.`
