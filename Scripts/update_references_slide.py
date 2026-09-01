import os

WORKSPACE = r"c:\Users\PRO\OneDrive\Documents\GitHub\minor project"
BEAMER_FILE = os.path.join(WORKSPACE, "Overleaf_Presentation", "beamer_presentation.tex")
MAIN_FILE = os.path.join(WORKSPACE, "Overleaf_Presentation", "main.tex")

ref_slide_code = r"""%=====================================================
% SLIDE 15: References
%=====================================================
\section{References}
\begin{frame}{References}
  \fontsize{5.5pt}{7pt}\selectfont
  \setlength{\leftmargini}{1.2em}
  \begin{enumerate}
    \setlength{\itemsep}{1.5pt}
    \setlength{\parskip}{0pt}
    \item S. Kova\v{c}evi\'c et al., ``DeepMark Benchmark: Redefining Audio Watermarking Robustness \textbf{(Base Paper)},'' \textit{IEEE Access}, vol. 14, pp. 62031--62044, 2026.
    \item P. Aberna and L. Agilandeeswari, ``Optimal Semi-Fragile Watermarking Based on Maximum Entropy Random Walk and Swin Transformer for Tamper Localization,'' \textit{IEEE Access}, vol. 12, pp. 37757--37781, 2024.
    \item Y. Sun et al., ``CANARY: Collision-Free Audio Watermarking for Proactive Deepfake Detection,'' \textit{IEEE Trans. Multimedia}, vol. 28, pp. 1420--1435, 2026.
    \item H. Chen et al., ``RNPM: Neural-Guided Embedding Region Selection and Error Correction for Robust Audio Multi-Watermarking,'' \textit{IEEE Trans. Audio, Speech, Lang. Process.}, vol. 33, pp. 1120--1134, 2025.
    \item Z. Wu et al., ``AWaveFormer: Audio Wavelet Transformer Network for Generalized Audio Deepfake Detection,'' \textit{IEEE Trans. Audio, Speech, Lang. Process.}, vol. 33, pp. 450--465, 2025.
    \item K. Sharma et al., ``Fortifying Deepfake Detection With AI and Postquantum Cryptography-Based Watermarking Technique,'' \textit{IEEE Trans. Comput. Soc. Syst.}, vol. 13, pp. 890--904, 2026.
    \item J. Park et al., ``Dual-Channel Deepfake Audio Detection: Leveraging Direct and Reverberant Waveforms,'' \textit{IEEE Access}, vol. 13, pp. 14500--14512, 2025.
    \item L. Zhang et al., ``FLADD: Federated Learning-based Privacy Protection for Audio Deepfake Detection,'' \textit{IEEE Trans. Audio, Speech, Lang. Process.}, vol. 34, pp. 310--324, 2026.
    \item C. Lin et al., ``Audio Physical Dynamics Inspired Deepfake Detection for Voice Authentication Systems,'' \textit{IEEE Netw. Lett.}, vol. 8, pp. 112--116, 2026.
    \item M. R. Islam et al., ``Detecting Deepfake Audio Using Spectrogram-Based Machine Learning Approaches,'' \textit{IEEE Access}, vol. 13, pp. 8821--8835, 2025.
    \item D. Kim et al., ``Anomaly Detection of Deepfake Audio Based on Real Audio Using Generative Adversarial Network Model,'' \textit{IEEE Access}, vol. 12, pp. 152340--152352, 2024.
    \item A. Al-Naji et al., ``Deepfake Audio Detection via MFCC Features Using Machine Learning,'' \textit{IEEE Access}, vol. 10, pp. 132104--132115, 2022.
  \end{enumerate}
\end{frame}

\end{document}
"""

with open(BEAMER_FILE, "r", encoding="utf-8") as f:
    content = f.read()

idx = content.find(r"\section{References}")
if idx != -1:
    new_content = content[:idx] + ref_slide_code
    with open(BEAMER_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)
    with open(MAIN_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Successfully updated References slide!")
