# Summary: Paper 10 - Detecting Deepfake Audio Using Spectrogram-Based Machine Learning Approaches

**Authors:** M. R. Islam, S. Hossain, and A. Rahman  
**Journal:** IEEE Access (2025)  
**Volume:** 13 | **Pages:** 8821-8835  
**DOI:** https://doi.org/10.1109/ACCESS.2025.3602531  
**PDF File:** `IEEE_Research_Papers/Papers/IEEE_Paper_10_Spectrogram_MachineLearning_Deepfake_2025.pdf`  

---

### Abstract
Spectrogram visual representations offer rich time-frequency information for deepfake analysis. This paper conducts a rigorous empirical investigation comparing Log-Mel, MFCC, and CQT spectrograms.

### Key Methodology & Architecture
Time-frequency spectrogram transformation (Log-Mel, CQT, MFCC), ResNet-50, EfficientNet, Transfer Learning.

### Datasets & Benchmarks
FoR (Fake or Real) Dataset, ASVspoof 2021 LA.

### Performance Metrics & Experimental Results
- **Reported Results:** CQT + EfficientNet Accuracy = 98.42%, F1-Score = 0.984, Precision = 0.986, AUC = 0.995.
- **Graph Parameter Mapping:** X-axis: Feature Representation (Log-Mel, MFCC, CQT); Y-axis: Classification Accuracy (% from 80% to 100%).

### Comparative Analysis
- **Pros:** Visual explainability via Grad-CAM highlighting synthetic high-frequency noise.
- **Cons:** Spectrogram generation requires preprocessing overhead.

### IEEE Citation
`M. R. Islam, S. Hossain, and A. Rahman, "Detecting Deepfake Audio Using Spectrogram-Based Machine Learning Approaches," IEEE Access, vol. 13, pp. 8821-8835, 2025, doi: 10.1109/ACCESS.2025.3602531.`
