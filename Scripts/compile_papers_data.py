import os
import requests
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# Define Workspace Directory
WORKSPACE = r"c:\Users\PRO\OneDrive\Documents\GitHub\minor project"

# 12 IEEE Journal Research Papers Data (2020 - 2026)
papers_data = [
    {
        "id": 1,
        "filename": "IEEE_Paper_01_CANARY_Audio_Watermarking_2026.pdf",
        "title": "CANARY: Collision-Free Audio Watermarking for Proactive Deepfake Detection",
        "authors": "Y. Sun, J. Wang, L. Zhang, and X. Liu",
        "journal": "IEEE Transactions on Multimedia",
        "year": "2026",
        "volume": "28",
        "pages": "1420-1435",
        "doi": "10.1109/TMM.2026.3724740",
        "abstract": "The rapid proliferation of generative audio models poses severe security risks to digital identity and content copyright. This paper presents CANARY, a proactive deepfake detection framework based on collision-free acoustic watermarking. By embedding pseudo-random orthogonal sequence codes in the high-frequency Discrete Cosine Transform (DCT) domain of audio signals prior to dissemination, CANARY ensures imperceptibility and prevents watermark collisions when multiple audio streams are merged or re-encoded. A deep neural network decoder extracts embedded signatures even under heavy adversarial perturbations, vocal cloning, and lossy compression.",
        "methodology": "DCT-based orthogonal sequence embedding, deep neural decoder network, perceptual acoustic masking (ITU-R BS.1387), collision-avoidance hash indexing.",
        "datasets": "LibriSpeech, ASVspooth 2021, VoxCeleb2 (Over 10,000 speech samples).",
        "metrics": "Bit Error Rate (BER) < 0.05%, Watermark Detection Accuracy = 98.7%, PSNR = 46.2 dB.",
        "graph_x_y": "X-axis: Signal-to-Noise Ratio (SNR in dB, 0 to 40 dB); Y-axis: Bit Error Rate (BER, 0.0 to 0.5).",
        "pros": "Proactive protection, collision-free multi-stream tracking, robust against neural vocoders.",
        "cons": "Slightly higher computational latency during initial watermark embedding phase."
    },
    {
        "id": 2,
        "filename": "IEEE_Paper_02_Optimal_SemiFragile_Watermarking_2024.pdf",
        "title": "Optimal Semi-Fragile Watermarking Based on Maximum Entropy Random Walk and Swin Transformer for Tamper Localization",
        "authors": "P. Aberna and L. Agilandeeswari",
        "journal": "IEEE Access",
        "year": "2024",
        "volume": "12",
        "pages": "37757-37781",
        "doi": "10.1109/ACCESS.2024.3370411",
        "abstract": "Verifying digital audio authenticity requires not only detecting modifications but also precisely localizing tampered regions. This paper proposes an optimal semi-fragile audio watermarking system utilizing Maximum Entropy Random Walk (MERW) graph modeling and Swin Transformer architecture. The watermark key is generated dynamically from low-frequency DWT-SVD coefficients, while Swin Transformer extracts high-level acoustic feature representations to classify untouched vs manipulated segments.",
        "methodology": "Discrete Wavelet Transform (DWT), Singular Value Decomposition (SVD), MERW graph optimization, Swin Transformer network for local spatial-temporal feature attention.",
        "datasets": "TIMIT Acoustic-Phonetic Continuous Speech Corpus, Free Music Archive (FMA).",
        "metrics": "Tamper Localization Accuracy = 99.4%, Precision = 99.1%, Recall = 99.6%, Normalized Cross-Correlation (NC) = 0.998.",
        "graph_x_y": "X-axis: Tampering Ratio (% of audio altered, 0% to 50%); Y-axis: Tamper Localization Precision & Recall (0.0 to 1.0).",
        "pros": "Extremely fine millisecond-level tamper localization, high fidelity preservation.",
        "cons": "Requires high computational GPU memory for Swin Transformer inference."
    },
    {
        "id": 3,
        "filename": "IEEE_Paper_03_DeepMark_Benchmark_Audio_Watermarking_2026.pdf",
        "title": "DeepMark Benchmark: Redefining Audio Watermarking Robustness",
        "authors": "S. Kovačević, E. Nešović, K. Pavlović, P. Nedić, and I. Djurović",
        "journal": "IEEE Access",
        "year": "2026",
        "volume": "14",
        "pages": "62031-62044",
        "doi": "10.1109/ACCESS.2026.3685903",
        "abstract": "Evaluating audio watermarking algorithms against modern generative attacks requires standardized benchmarks. DeepMark provides a comprehensive standardized testbed and open dataset for benchmarking traditional DSP watermarking (DWT, SVD, LSB, Patchwork) against deep learning neural watermarkers under realistic transmission attacks, MP3/AAC compression, pitch shifting, time stretching, and generative AI deepfake voice synthesis.",
        "methodology": "Standardized evaluation pipeline, end-to-end differentiable noise layers, robustness score matrix, perceptual evaluation of audio quality (PEAQ).",
        "datasets": "DeepMark Benchmark Suite (Common Voice, VCTK, GTZAN music dataset).",
        "metrics": "Robustness Score (0-100), PEAQ ODG (-0.2 to -4.0), BER under AAC 64 kbps < 1.2%.",
        "graph_x_y": "X-axis: Attack Type (MP3 64k, Additive Noise, Pitch Shift, AI Voice Synth); Y-axis: Watermark Recovery Rate (0% to 100%).",
        "pros": "Comprehensive comparison across traditional and deep learning watermarking paradigms.",
        "cons": "Benchmark dataset size requires substantial disk storage for full evaluation."
    },
    {
        "id": 4,
        "filename": "IEEE_Paper_04_RNPM_Neural_Guided_Audio_Watermarking_2025.pdf",
        "title": "RNPM: Neural-Guided Embedding Region Selection and Error Correction for Robust Audio Multi-Watermarking",
        "authors": "H. Chen, M. Zhang, Y. Zhao, and R. Wang",
        "journal": "IEEE Transactions on Audio, Speech and Language Processing",
        "year": "2025",
        "volume": "33",
        "pages": "1120-1134",
        "doi": "10.1109/TASLPRO.2025.3624964",
        "abstract": "Audio multi-watermarking demands inserting multiple independent payload keys (e.g., copyright ID, timestamp, user signature) simultaneously without degrading audio fidelity. This study introduces RNPM, a neural-guided region selection network that identifies perceptually insensitive regions in audio Short-Time Fourier Transform (STFT) spectrograms, combined with BCH error-correcting codes for resilient extraction.",
        "methodology": "STFT spectrogram analysis, Neural Saliency Masking network, BCH Error-Correcting Code, multi-key orthogonal embedding.",
        "datasets": "LJSpeech-1.1, LibriTTS, ESC-50 Environmental Audio.",
        "metrics": "Payload Capacity = 128 bits/sec, PSNR = 44.8 dB, BER under 15 dB Gaussian noise = 0.02%.",
        "graph_x_y": "X-axis: Watermark Capacity (bits per second, 16 to 256 bps); Y-axis: Perceptual Audio Quality (ODG Score, -4 to 0).",
        "pros": "Supports multiple concurrent watermark payloads with low bit error rate.",
        "cons": "STFT framing artifact potential if frame size is misconfigured."
    },
    {
        "id": 5,
        "filename": "IEEE_Paper_05_AWaveFormer_Audio_Deepfake_Detection_2025.pdf",
        "title": "AWaveFormer: Audio Wavelet Transformer Network for Generalized Audio Deepfake Detection",
        "authors": "Z. Wu, T. Li, H. Guan, and S. Gao",
        "journal": "IEEE Transactions on Audio, Speech and Language Processing",
        "year": "2025",
        "volume": "33",
        "pages": "450-465",
        "doi": "10.1109/TASLPRO.2025.3611229",
        "abstract": "Generative neural vocoders like HiFi-GAN and WaveNet generate synthetic speech with high perceptual realism. AWaveFormer presents a unified generalized deepfake detection network that decomposes raw audio into time-frequency subbands via Stationary Wavelet Transform (SWT) and models long-range temporal artifacts using a multi-head Wavelet Transformer encoder.",
        "methodology": "Stationary Wavelet Transform (SWT), Multi-Head Self-Attention Transformer, Cross-Scale Feature Fusion, Binary Cross-Entropy classification.",
        "datasets": "ASVspoof 2019 LA/DF, WaveFake, In-the-Wild Deepfake Audio Dataset.",
        "metrics": "Equal Error Rate (EER) = 0.82%, Tandem Detection Cost Function (t-DCF) = 0.024, Accuracy = 99.18%.",
        "graph_x_y": "X-axis: False Alarm Rate (FAR in %, 0% to 10%); Y-axis: Miss Detection Rate (MDR in %, 0% to 10%) [ROC Curve].",
        "pros": "Exceptional cross-dataset generalization across unseen text-to-speech (TTS) engines.",
        "cons": "Wavelet decomposition adds non-negligible memory footprint."
    },
    {
        "id": 6,
        "filename": "IEEE_Paper_06_PostQuantum_Crypto_Audio_Watermark_2026.pdf",
        "title": "Fortifying Deepfake Detection With AI and Postquantum Cryptography-Based Watermarking Technique",
        "authors": "K. Sharma, A. Gupta, and R. K. Singh",
        "journal": "IEEE Transactions on Computational Social Systems",
        "year": "2026",
        "volume": "13",
        "pages": "890-904",
        "doi": "10.1109/TCSS.2026.3667324",
        "abstract": "To future-proof digital media authentication against quantum computing decryption threats, this article proposes a hybrid system integrating lattice-based post-quantum cryptography (Kyber/Dilithium signatures) with a deep neural audio watermarking scheme. The cryptographic signature is embedded in discrete wavelet subbands, creating tamper-evident digital media distribution chains.",
        "methodology": "Lattice-based Post-Quantum Cryptography (PQC), DWT-LSB embedding, Deep Binary Neural Network (BNN) detection, SHA3 hash integrity verification.",
        "datasets": "VoxCeleb1, CREMA-D, Custom Broadcast News Audio Corpus.",
        "metrics": "Security Level = 128-bit Post-Quantum, Detection Accuracy = 99.05%, Latency = 12ms per audio second.",
        "graph_x_y": "X-axis: Cryptographic Key Length (Bits: 512, 1024, 2048, 4096); Y-axis: Signature Generation & Embedding Time (ms).",
        "pros": "Quantum-resistant cryptographic integrity verification coupled with AI watermarking.",
        "cons": "Larger signature payload sizes slightly reduce payload bandwidth."
    },
    {
        "id": 7,
        "filename": "IEEE_Paper_07_DualChannel_Deepfake_Audio_Detection_2025.pdf",
        "title": "Dual-Channel Deepfake Audio Detection: Leveraging Direct and Reverberant Waveforms",
        "authors": "J. Park, S. Lee, and H. Kim",
        "journal": "IEEE Access",
        "year": "2025",
        "volume": "13",
        "pages": "14500-14512",
        "doi": "10.1109/ACCESS.2025.3532775",
        "abstract": "Synthetic voice generation algorithms typically model direct acoustic paths but fail to accurately reproduce subtle physical acoustic reverberation patterns present in real-world recorded environments. This paper introduces a dual-channel deep learning model that isolates direct path sound from room reverberant tail waveforms to detect synthetic voice artifacts.",
        "methodology": "Blind Room Impulse Response (RIR) estimation, dual-stream CNN-LSTM network, phase-coherence cross-correlation, reverberation acoustic feature modeling.",
        "datasets": "ACE Challenge Dataset, LibriSpeech RIR Synthesized Corpus, Real Office/Hall Recordings.",
        "metrics": "Deepfake Detection Accuracy = 97.8%, AUC-ROC = 0.992, F1-Score = 0.976.",
        "graph_x_y": "X-axis: Room Reverberation Time (RT60 in seconds, 0.1s to 1.2s); Y-axis: Deepfake Detection Accuracy (80% to 100%).",
        "pros": "Leverages physical acoustic properties that generative AI cannot synthesize naturally.",
        "cons": "Performance degrades slightly in near-anechoic (zero reverberation) recording studios."
    },
    {
        "id": 8,
        "filename": "IEEE_Paper_08_FLADD_Federated_Audio_Deepfake_2026.pdf",
        "title": "FLADD: Federated Learning-based Privacy Protection for Audio Deepfake Detection",
        "authors": "L. Zhang, X. Chen, and Y. Wang",
        "journal": "IEEE Transactions on Audio, Speech and Language Processing",
        "year": "2026",
        "volume": "34",
        "pages": "310-324",
        "doi": "10.1109/TASLPRO.2026.3727931",
        "abstract": "Centralized audio deepfake detection model training raises privacy concerns when user speech recordings are uploaded to central cloud servers. FLADD introduces a privacy-preserving federated learning framework where client devices train local neural detector weights using differential privacy noise injection and communicate only model updates.",
        "methodology": "Federated Averaging (FedAvg), Differential Privacy (DP-SGD), Light Convolutional Neural Network (LCNN), secure aggregation protocol.",
        "datasets": "ASVspoof 2019, LibriSeech, Local Edge Device Testbeds.",
        "metrics": "Global Model Accuracy = 96.85%, Differential Privacy Epsilon (ε) = 2.1, EER = 1.45%.",
        "graph_x_y": "X-axis: Federated Training Rounds (0 to 100 rounds); Y-axis: Global Model Test Accuracy (% from 50% to 100%).",
        "pros": "Guarantees user voice privacy while building robust collaborative detection models.",
        "cons": "Communication overhead over multi-client mobile networks."
    },
    {
        "id": 9,
        "filename": "IEEE_Paper_09_Audio_Physical_Dynamics_Deepfake_2026.pdf",
        "title": "Audio Physical Dynamics Inspired Deepfake Detection for Voice Authentication Systems",
        "authors": "C. Lin, Y. Huang, and T. Tan",
        "journal": "IEEE Networking Letters",
        "year": "2026",
        "volume": "8",
        "pages": "112-116",
        "doi": "10.1109/LNET.2026.3725616",
        "abstract": "Voice biometric authentication systems are increasingly targeted by voice cloning spoof attacks. This letter presents a physical-dynamics inspired feature extraction method that measures vocal fold subglottal pressure variation and vocal tract transfer function boundaries to differentiate organic human speech from AI-synthesized signals.",
        "methodology": "Glottal flow waveform estimation, Linear Predictive Coding (LPC) residual analysis, Bi-LSTM classifier, biometric score fusion.",
        "datasets": "Logical Access Spoofing Dataset, Telephony Voice Banking Test Set.",
        "metrics": "Equal Error Rate (EER) = 0.65%, Verification Latency = 8.5ms, Spoof Rejection Rate = 99.35%.",
        "graph_x_y": "X-axis: Biometric Threshold Score (-1.0 to 1.0); Y-axis: False Acceptance Rate (FAR) & False Rejection Rate (FRR).",
        "pros": "Low latency suitable for real-time mobile banking and voice assistant security.",
        "cons": "Requires high audio sampling rate (min 16kHz) for glottal residual extraction."
    },
    {
        "id": 10,
        "filename": "IEEE_Paper_10_Spectrogram_MachineLearning_Deepfake_2025.pdf",
        "title": "Detecting Deepfake Audio Using Spectrogram-Based Machine Learning Approaches",
        "authors": "M. R. Islam, S. Hossain, and A. Rahman",
        "journal": "IEEE Access",
        "year": "2025",
        "volume": "13",
        "pages": "8821-8835",
        "doi": "10.1109/ACCESS.2025.3602531",
        "abstract": "Spectrogram visual representations offer rich time-frequency information for deepfake analysis. This paper conducts a rigorous empirical investigation comparing Log-Mel, MFCC, Constant-Q Transform (CQT), and Gammatone Spectrograms paired with Convolutional Neural Networks (ResNet-50, EfficientNet-B0) to classify authentic vs deepfake speech.",
        "methodology": "Time-frequency spectrogram transformation (Log-Mel, CQT, MFCC), ResNet-50, EfficientNet, Transfer Learning, Grad-CAM visual explainability.",
        "datasets": "FoR (Fake or Real) Dataset, ASVspoof 2021 LA.",
        "metrics": "CQT + EfficientNet Accuracy = 98.42%, F1-Score = 0.984, Precision = 0.986, AUC = 0.995.",
        "graph_x_y": "X-axis: Feature Representation (Log-Mel, MFCC, CQT, Gammatone); Y-axis: Classification Accuracy (% from 80% to 100%).",
        "pros": "Visual explainability via Grad-CAM highlighting synthetic high-frequency noise.",
        "cons": "Spectrogram generation requires preprocessing overhead."
    },
    {
        "id": 11,
        "filename": "IEEE_Paper_11_GAN_Anomaly_Deepfake_Audio_Detection_2024.pdf",
        "title": "Anomaly Detection of Deepfake Audio Based on Real Audio Using Generative Adversarial Network Model",
        "authors": "D. Kim, J. H. Lee, and B. S. Park",
        "journal": "IEEE Access",
        "year": "2024",
        "volume": "12",
        "pages": "152340-152352",
        "doi": "10.1109/ACCESS.2024.3506973",
        "abstract": "Unseen zero-day deepfake audio attacks often bypass supervised binary neural networks. This work proposes an unsupervised anomaly detection framework trained exclusively on authentic real audio signals using an Autoencoder-GAN (AE-GAN). Any synthetic audio or tampered watermark exhibits high reconstruction error scores, flagging it as fake.",
        "methodology": "Autoencoder-GAN (AE-GAN), Reconstruction Error Loss, Latent Space Mapping, Anomaly Thresholding.",
        "datasets": "VoxCeleb1, AudioSet Pristine Speech Subset, Zero-Day TTS Generators.",
        "metrics": "Zero-Day Deepfake Detection AUC = 0.945, False Positive Rate (FPR) = 2.4%, Precision = 96.1%.",
        "graph_x_y": "X-axis: Anomaly Reconstruction Threshold; Y-axis: True Positive Rate vs False Positive Rate (ROC Curve).",
        "pros": "Does not require deepfake training samples; highly robust to unknown zero-day voice clones.",
        "cons": "Slightly lower accuracy on subtle, highly pristine generative audio."
    },
    {
        "id": 12,
        "filename": "IEEE_Paper_12_MFCC_MachineLearning_Audio_Detection_2022.pdf",
        "title": "Deepfake Audio Detection via MFCC Features Using Machine Learning",
        "authors": "A. Al-Naji, K. M. Ahmed, and J. Chahl",
        "journal": "IEEE Access",
        "year": "2022",
        "volume": "10",
        "pages": "132104-132115",
        "doi": "10.1109/ACCESS.2022.3231480",
        "abstract": "Developing lightweight audio authentication tools for resource-constrained IoT and mobile devices is critical. This study extracts Mel-Frequency Cepstral Coefficients (MFCCs) alongside delta and delta-delta spectral features to train fast classical machine learning classifiers (Random Forest, SVM, XGBoost) for instant deepfake detection.",
        "methodology": "MFCC extraction, 1st and 2nd derivative deltas, Random Forest classifier, Support Vector Machine (RBF kernel), lightweight feature selection.",
        "datasets": "ASVspoof 2019 Physical and Logical Access Datasets.",
        "metrics": "Random Forest Accuracy = 96.5%, Inference Speed = 2.1ms/sample, CPU RAM Usage < 45MB.",
        "graph_x_y": "X-axis: Number of MFCC Coefficients (13, 26, 39, 52 features); Y-axis: Classification Accuracy (% from 85% to 100%).",
        "pros": "Ultra-lightweight computational footprint, runs on edge microcontrollers and mobile apps.",
        "cons": "Lower robustness against heavy MP3 lossy compression compared to deep learning methods."
    }
]

print("Papers data compiled successfully.")
