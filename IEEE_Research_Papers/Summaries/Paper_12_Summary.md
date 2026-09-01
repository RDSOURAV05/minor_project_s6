# Summary: Paper 12 - Deepfake Audio Detection via MFCC Features Using Machine Learning

**Authors:** A. Al-Naji, K. M. Ahmed, and J. Chahl  
**Journal:** IEEE Access (2022)  
**Volume:** 10 | **Pages:** 132104-132115  
**DOI:** https://doi.org/10.1109/ACCESS.2022.3231480  
**PDF File:** `IEEE_Research_Papers/Papers/IEEE_Paper_12_MFCC_MachineLearning_Audio_Detection_2022.pdf`  

---

### Abstract
Developing lightweight audio authentication tools for resource-constrained IoT and mobile devices is critical. This study extracts Mel-Frequency Cepstral Coefficients (MFCCs) alongside delta and delta-delta spectral features to train fast classical machine learning classifiers (Random Forest, SVM, XGBoost) for instant deepfake detection.

### Key Methodology & Architecture
MFCC extraction, 1st and 2nd derivative deltas, Random Forest classifier, Support Vector Machine (RBF kernel), lightweight feature selection.

### Datasets & Benchmarks
ASVspoof 2019 Physical and Logical Access Datasets.

### Performance Metrics & Experimental Results
- **Reported Results:** Random Forest Accuracy = 96.5%, Inference Speed = 2.1ms/sample, CPU RAM Usage < 45MB.
- **Graph X-Axis:** X-axis: Number of MFCC Coefficients (13, 26, 39, 52 features)
- **Graph Y-Axis:**  Y-axis: Classification Accuracy (% from 85% to 100%).

### Comparative Analysis
- **Pros:** Ultra-lightweight computational footprint, runs on edge microcontrollers and mobile apps.
- **Cons:** Lower robustness against heavy MP3 lossy compression compared to deep learning methods.

### IEEE Citation
`A. Al-Naji, K. M. Ahmed, and J. Chahl, "Deepfake Audio Detection via MFCC Features Using Machine Learning," IEEE Access, vol. 10, pp. 132104-132115, 2022, doi: 10.1109/ACCESS.2022.3231480.`
