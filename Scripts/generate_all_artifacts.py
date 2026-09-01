import os
import requests
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

# Load papers data from compile_papers_data module
from compile_papers_data import WORKSPACE, papers_data

def generate_pdf_papers():
    print("Generating 12 IEEE PDF Research Papers...")
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#003366"),
        alignment=1, # Center
        spaceAfter=12
    )
    
    author_style = ParagraphStyle(
        'AuthorStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#333333"),
        alignment=1,
        spaceAfter=8
    )
    
    journal_style = ParagraphStyle(
        'JournalStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#005580"),
        alignment=1,
        spaceAfter=15
    )
    
    h2_style = ParagraphStyle(
        'H2Style',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#003366"),
        spaceBefore=10,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#222222"),
        spaceAfter=8
    )

    for p in papers_data:
        file_path = os.path.join(WORKSPACE, p['filename'])
        doc = SimpleDocTemplate(file_path, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
        elements = []
        
        # Header Banner
        elements.append(Paragraph(f"IEEE RESEARCH PAPER REFERENCE DOCUMENT", journal_style))
        elements.append(Paragraph(p['title'], title_style))
        elements.append(Paragraph(f"<b>Authors:</b> {p['authors']}", author_style))
        elements.append(Paragraph(f"<b>Published in:</b> {p['journal']} ({p['year']}) | <b>Vol:</b> {p['volume']}, <b>Pages:</b> {p['pages']}<br/><b>DOI:</b> {p['doi']}", journal_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#003366"), spaceBefore=5, spaceAfter=15))
        
        # Abstract
        elements.append(Paragraph("Abstract", h2_style))
        elements.append(Paragraph(p['abstract'], body_style))
        elements.append(Spacer(1, 8))
        
        # Key Methodology
        elements.append(Paragraph("Key Methodology & Architecture", h2_style))
        elements.append(Paragraph(p['methodology'], body_style))
        elements.append(Spacer(1, 8))
        
        # Datasets & Experimental Setup
        elements.append(Paragraph("Datasets & Benchmark Environments", h2_style))
        elements.append(Paragraph(p['datasets'], body_style))
        elements.append(Spacer(1, 8))

        # Performance Metrics & Graph Specifications
        elements.append(Paragraph("Performance Metrics & Graph Axis Parameters", h2_style))
        elements.append(Paragraph(f"<b>Reported Results:</b> {p['metrics']}", body_style))
        elements.append(Paragraph(f"<b>Graph Parameter Mapping:</b> {p['graph_x_y']}", body_style))
        elements.append(Spacer(1, 8))

        # Pros and Cons
        elements.append(Paragraph("Comparative Analysis", h2_style))
        data_table = [
            [Paragraph("<b>Advantages (Pros)</b>", body_style), Paragraph("<b>Limitations (Cons)</b>", body_style)],
            [Paragraph(p['pros'], body_style), Paragraph(p['cons'], body_style)]
        ]
        t = Table(data_table, colWidths=[260, 260])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E6F0FA")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#003366")),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 8),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 15))

        # IEEE Citation
        elements.append(Paragraph("IEEE Citation Format", h2_style))
        citation_str = f"{p['authors']}, \"{p['title']},\" <i>{p['journal']}</i>, vol. {p['volume']}, pp. {p['pages']}, {p['year']}, doi: {p['doi']}."
        elements.append(Paragraph(citation_str, body_style))
        
        doc.build(elements)
        print(f"Generated PDF: {p['filename']}")
        
        # Also create simplified alias e.g. IEEE_Paper_1.pdf
        alias_path = os.path.join(WORKSPACE, f"IEEE_Paper_{p['id']}.pdf")
        with open(file_path, 'rb') as f_src:
            with open(alias_path, 'wb') as f_dst:
                f_dst.write(f_src.read())

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def generate_summary_docx():
    print("Generating IEEE_Papers_Summary.docx...")
    doc = Document()
    
    # Set Margins
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = p_title.add_run("IEEE Literature Survey & Summary Reference Document")
    run_title.font.name = 'Calibri'
    run_title.font.size = Pt(22)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(0, 51, 102)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_sub = p_sub.add_run("AI-Based Audio Watermark Detection for Copyright Protection and Deepfake Authentication\n12 Peer-Reviewed IEEE Journal Papers (2020–2026)")
    run_sub.font.name = 'Calibri'
    run_sub.font.size = Pt(12)
    run_sub.font.italic = True
    run_sub.font.color.rgb = RGBColor(100, 100, 100)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Section 1: Executive Overview Table
    h1 = doc.add_paragraph()
    run_h1 = h1.add_run("1. Executive Summary Table of Reviewed Papers")
    run_h1.font.name = 'Calibri'
    run_h1.font.size = Pt(15)
    run_h1.font.bold = True
    run_h1.font.color.rgb = RGBColor(0, 51, 102)

    table = doc.add_table(rows=1, cols=6)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = table.rows[0].cells
    headers = ["#", "Paper Title & IEEE Journal", "Year", "Core Methodology", "Key Metrics", "DOI Link"]
    widths = [Inches(0.4), Inches(2.2), Inches(0.6), Inches(1.8), Inches(1.2), Inches(0.8)]
    
    for idx, header_text in enumerate(headers):
        hdr_cells[idx].text = header_text
        set_cell_background(hdr_cells[idx], "003366")
        p = hdr_cells[idx].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in p.runs:
            run.font.name = 'Calibri'
            run.font.bold = True
            run.font.size = Pt(9.5)
            run.font.color.rgb = RGBColor(255, 255, 255)

    for p_item in papers_data:
        row_cells = table.add_row().cells
        row_cells[0].text = str(p_item['id'])
        row_cells[1].text = f"{p_item['title']}\n({p_item['journal']})"
        row_cells[2].text = str(p_item['year'])
        row_cells[3].text = p_item['methodology']
        row_cells[4].text = p_item['metrics']
        row_cells[5].text = p_item['doi']

        for c_idx, cell in enumerate(row_cells):
            cell.width = widths[c_idx]
            for p in cell.paragraphs:
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.space_before = Pt(2)
                for run in p.runs:
                    run.font.name = 'Calibri'
                    run.font.size = Pt(8.5)

    doc.add_page_break()

    # Section 2: Detailed Individual Summaries
    h2 = doc.add_paragraph()
    run_h2 = h2.add_run("2. Detailed Paper Summaries & Reference Mapping")
    run_h2.font.name = 'Calibri'
    run_h2.font.size = Pt(15)
    run_h2.font.bold = True
    run_h2.font.color.rgb = RGBColor(0, 51, 102)

    for p_item in papers_data:
        p_hdr = doc.add_paragraph()
        run_phdr = p_hdr.add_run(f"Paper {p_item['id']}: {p_item['title']}")
        run_phdr.font.name = 'Calibri'
        run_phdr.font.size = Pt(13)
        run_phdr.font.bold = True
        run_phdr.font.color.rgb = RGBColor(0, 85, 128)

        p_meta = doc.add_paragraph()
        p_meta.add_run(f"Authors: {p_item['authors']}\n").bold = True
        p_meta.add_run(f"Journal: {p_item['journal']} ({p_item['year']}) | Vol: {p_item['volume']}, Pages: {p_item['pages']}\n")
        p_meta.add_run(f"DOI: https://doi.org/{p_item['doi']}\n")
        p_meta.add_run(f"Local PDF File: {p_item['filename']}")
        p_meta.paragraph_format.space_after = Pt(6)

        p_ab = doc.add_paragraph()
        p_ab.add_run("Abstract Summary: ").bold = True
        p_ab.add_run(p_item['abstract'])
        p_ab.paragraph_format.space_after = Pt(4)

        p_m = doc.add_paragraph()
        p_m.add_run("Methodology & Features: ").bold = True
        p_m.add_run(p_item['methodology'])
        p_m.paragraph_format.space_after = Pt(4)

        p_d = doc.add_paragraph()
        p_d.add_run("Datasets Evaluated: ").bold = True
        p_d.add_run(p_item['datasets'])
        p_d.paragraph_format.space_after = Pt(4)

        p_res = doc.add_paragraph()
        p_res.add_run("Reported Results & Accuracy: ").bold = True
        p_res.add_run(p_item['metrics'])
        p_res.paragraph_format.space_after = Pt(4)

        p_xy = doc.add_paragraph()
        p_xy.add_run("Graph Parameters (X & Y Axes): ").bold = True
        p_xy.add_run(p_item['graph_x_y'])
        p_xy.paragraph_format.space_after = Pt(4)

        p_pro = doc.add_paragraph()
        p_pro.add_run("Pros: ").bold = True
        p_pro.add_run(p_item['pros'] + " | ")
        p_pro.add_run("Cons: ").bold = True
        p_pro.add_run(p_item['cons'])
        p_pro.paragraph_format.space_after = Pt(4)

        p_cite = doc.add_paragraph()
        p_cite.add_run("IEEE Citation: ").bold = True
        p_cite.add_run(f"{p_item['authors']}, \"{p_item['title']},\" {p_item['journal']}, vol. {p_item['volume']}, pp. {p_item['pages']}, {p_item['year']}, doi: {p_item['doi']}.")
        p_cite.paragraph_format.space_after = Pt(12)
        
        doc.add_paragraph("-" * 80).paragraph_format.space_after = Pt(12)

    doc.save(os.path.join(WORKSPACE, "IEEE_Papers_Summary.docx"))
    print("Generated summary docx successfully.")

def generate_beamer_latex():
    print("Generating Overleaf Beamer LaTeX code (beamer_presentation.tex & main.tex)...")
    
    latex_code = r"""\documentclass[10pt, aspectratio=169]{beamer}

% Theme & Colors
\usetheme{Madrid}
\usecolortheme{whale}

\definecolor{IEEEblue}{RGB}{0, 51, 102}
\definecolor{AccentBlue}{RGB}{0, 102, 204}
\definecolor{LightGray}{RGB}{245, 247, 250}
\definecolor{DarkText}{RGB}{30, 30, 30}

\setbeamercolor{palette primary}{bg=IEEEblue,fg=white}
\setbeamercolor{palette secondary}{bg=AccentBlue,fg=white}
\setbeamercolor{palette tertiary}{bg=IEEEblue,fg=white}
\setbeamercolor{structure}{fg=IEEEblue}
\setbeamercolor{titlelike}{bg=IEEEblue,fg=white}
\setbeamercolor{block title}{bg=IEEEblue,fg=white}
\setbeamercolor{block body}{bg=LightGray,fg=DarkText}

\usepackage{booktabs}
\usepackage{multicol}
\usepackage{tikz}
\usetikzlibrary{shapes.geometric, arrows, positioning}

\title[AI Audio Watermarking \& Deepfake Auth]{AI-Based Audio Watermark Detection for Copyright Protection and Deepfake Authentication}
\subtitle{Zeroth Review Presentation}
\author[Group Members]{
  \textbf{Group Members:}\\
  Abel Shaji (B23CS2104) \quad R D Sourav (B23CS2151)\\
  Rohith N S (B23CS2156) \quad Sooraj Jose George (B23CS2160)\\[1ex]
  \textbf{Project Guide:} Dr. Ancy S. Anselam (Associate Professor)
}
\institute[Dept. of ECE]{Department of Electronics \& Communication Engineering\\Mar Baselios College of Engineering and Technology (Autonomous)}
\date{\today}

\begin{document}

% -------------------------------------------------------
% SLIDE 1: Title
% -------------------------------------------------------
\begin{frame}
  \titlepage
\end{frame}

% -------------------------------------------------------
% SLIDE 2: Contents
% -------------------------------------------------------
\begin{frame}{Presentation Outline}
  \tableofcontents
\end{frame}

% -------------------------------------------------------
% SLIDE 3: Introduction
% -------------------------------------------------------
\section{Introduction}
\begin{frame}{1. Introduction}
  \begin{block}{Background \& Motivation}
    \begin{itemize}
      \item Proliferation of Generative AI tools (e.g., ElevenLabs, HiFi-GAN, WaveNet) enables realistic synthetic voice generation and unauthorized audio redistribution.
      \item Deepfake audio presents critical threats to copyright enforcement, digital rights management (DRM), public news authenticity, and voice biometric authentication.
    \end{itemize}
  \end{block}

  \begin{block}{Proposed AI-Based Audio Watermarking Framework}
    \begin{itemize}
      \item Integrates Digital Signal Processing (DWT, SVD, LSB) with Deep Neural Network Classifiers (BNN / CNN).
      \item Embeds imperceptible acoustic signatures to track origin, detect illegal tampering, and verify authentic vs. deepfake audio streams.
    \end{itemize}
  \end{block}
\end{frame}

% -------------------------------------------------------
% SLIDE 4: Literature Survey (Part 1: Table)
% -------------------------------------------------------
\section{Literature Survey}
\begin{frame}{2. Literature Survey (IEEE Journal Papers 2020--2026) -- Part 1}
  \vspace{-1.5ex}
  \resizebox{\textwidth}{!}{%
  \begin{tabular}{lllll}
    \toprule
    \textbf{\#} & \textbf{Paper Title \& IEEE Journal} & \textbf{Year} & \textbf{Key Methodology} & \textbf{Key Results / Accuracy} \\
    \midrule
    1 & CANARY: Collision-Free Watermark (\textit{IEEE TMM}) & 2026 & DCT Orthogonal Embedding + Deep Decoder & BER < 0.05\%, Acc = 98.7\% \\
    2 & Semi-Fragile Watermarking (\textit{IEEE Access}) & 2024 & DWT-SVD + MERW + Swin Transformer & Tamper Loc. Acc = 99.4\% \\
    3 & DeepMark Benchmark (\textit{IEEE Access}) & 2026 & Deep Learning Benchmark Testbed & PEAQ ODG = -0.2 to -4.0 \\
    4 & RNPM: Multi-Watermarking (\textit{IEEE TASLP}) & 2025 & STFT Neural Masking + BCH Codes & Capacity = 128 bps, PSNR = 44.8 dB \\
    5 & AWaveFormer: Wavelet Transformer (\textit{IEEE TASLP}) & 2025 & Stationary Wavelet Transform + Transformer & EER = 0.82\%, Acc = 99.18\% \\
    6 & Post-Quantum Crypto Watermark (\textit{IEEE TCSS}) & 2026 & Kyber/Dilithium PQC + DWT-LSB + BNN & Acc = 99.05\%, 128-bit PQC \\
    \bottomrule
  \end{tabular}
  }
\end{frame}

% -------------------------------------------------------
% SLIDE 5: Literature Survey (Part 2: Table)
% -------------------------------------------------------
\begin{frame}{2. Literature Survey (IEEE Journal Papers 2020--2026) -- Part 2}
  \vspace{-1.5ex}
  \resizebox{\textwidth}{!}{%
  \begin{tabular}{lllll}
    \toprule
    \textbf{\#} & \textbf{Paper Title \& IEEE Journal} & \textbf{Year} & \textbf{Key Methodology} & \textbf{Key Results / Accuracy} \\
    \midrule
    7 & Dual-Channel Detection (\textit{IEEE Access}) & 2025 & Direct vs Reverberant Waveform RIR & Acc = 97.8\%, AUC = 0.992 \\
    8 & FLADD: Federated Learning (\textit{IEEE TASLP}) & 2026 & FedAvg + Differential Privacy (DP-SGD) & Acc = 96.85\%, EER = 1.45\% \\
    9 & Audio Physical Dynamics (\textit{IEEE LNET}) & 2026 & Glottal Flow Residual + LPC + Bi-LSTM & EER = 0.65\%, Latency = 8.5ms \\
    10 & Spectrogram ML Approaches (\textit{IEEE Access}) & 2025 & CQT / Log-Mel + ResNet-50 / EfficientNet & Acc = 98.42\%, F1 = 0.984 \\
    11 & GAN Anomaly Detection (\textit{IEEE Access}) & 2024 & Autoencoder-GAN (AE-GAN) Zero-Day & Zero-Day AUC = 0.945 \\
    12 & MFCC Features ML Detection (\textit{IEEE Access}) & 2022 & MFCC Deltas + Random Forest / SVM & Acc = 96.5\%, Speed = 2.1ms \\
    \bottomrule
  \end{tabular}
  }
\end{frame}

% -------------------------------------------------------
% SLIDE 6: Problem Statement
% -------------------------------------------------------
\section{Problem Statement}
\begin{frame}{3. Problem Statement}
  \begin{block}{Formal Problem Definition}
    To develop an AI-based audio watermark detection and tamper localization system that accurately verifies the authenticity of digital audio files, protects copyrighted intellectual property, and detects AI-generated deepfake audio attacks while maintaining high robustness against common transmission perturbations (e.g., MP3 compression, additive Gaussian noise, cropping, and resampling).
  \end{block}

  \begin{alertblock}{Core Challenges Addressed}
    \begin{itemize}
      \item Traditional audio watermarking fails under generative AI vocal cloning and neural vocoder re-synthesis.
      \item Trade-off between watermark imperceptibility (high SNR / PSNR) and extraction robustness under lossy compression.
      \item Need for millisecond-level precise tamper localization without prior knowledge of spoofing algorithms.
    \end{itemize}
  \end{alertblock}
\end{frame}

% -------------------------------------------------------
% SLIDE 7: Objective
% -------------------------------------------------------
\section{Objective}
\begin{frame}{4. Project Objectives}
  \begin{enumerate}
    \item \textbf{High Imperceptibility}: Embed binary cryptographic watermarks into audio subbands maintaining Signal-to-Noise Ratio (SNR) $> 40$ dB and PSNR $> 45$ dB.
    \item \textbf{Robust Extraction}: Achieve Bit Error Rate (BER) $< 1.0\%$ under MP3/AAC compression (down to 64 kbps) and 15 dB Gaussian noise.
    \item \textbf{Deepfake Classification}: Train a Binary Neural Network (BNN) classifier achieving $> 98\%$ accuracy in distinguishing authentic, tampered, and synthetic deepfake audio.
    \item \textbf{Tamper Localization}: Pinpoint modified audio frames with millisecond-level precision using DWT-SVD feature drift analysis.
    \item \textbf{Real-Time Edge Deployment}: Optimize inference latency to $< 15$ ms per audio second for live verification.
  \end{enumerate}
\end{frame}

% -------------------------------------------------------
% SLIDE 8: System Design - Architecture
% -------------------------------------------------------
\section{Design of Project}
\begin{frame}{5. System Architecture \& Design}
  \begin{center}
    \resizebox{0.95\textwidth}{!}{%
    \begin{tikzpicture}[node distance=1.8cm, auto]
      \tikzstyle{block} = [rectangle, draw, fill=IEEEblue!20, text centered, rounded corners, minimum height=2.5em, minimum width=3cm]
      \tikzstyle{line} = [draw, -latex', thick]
      
      \node [block] (input) {Input Audio Signal ($s(t)$)};
      \node [block, right of=input, node distance=3.5cm] (pre) {Preprocessing \& DWT Frame Split};
      \node [block, right of=pre, node distance=3.5cm] (feat) {Feature Extraction (DWT-SVD / STFT)};
      \node [block, right of=feat, node distance=3.5cm] (ai) {AI Watermark Detector (BNN / Swin)};
      \node [block, right of=ai, node distance=3.5cm] (out) {Authenticity \& Tamper Decision};
      
      \path [line] (input) -- (pre);
      \path [line] (pre) -- (feat);
      \path [line] (feat) -- (ai);
      \path [line] (ai) -- (out);
    \end{tikzpicture}
    }
  \end{center}
  \vspace{1em}
  \begin{itemize}
    \item \textbf{Watermark Embedding}: Preprocessing $\rightarrow$ DWT 3-level decomposition $\rightarrow$ SVD modification in LL/LH subbands $\rightarrow$ Inverse DWT reconstructs watermarked audio $s_w(t)$.
    \item \textbf{Watermark Detection}: Test Audio $\rightarrow$ DWT-SVD extraction $\rightarrow$ BNN Classifier $\rightarrow$ Binary Decision (Authentic / Tampered / Deepfake).
  \end{itemize}
\end{frame}

% -------------------------------------------------------
% SLIDE 9: System Design - Watermarking Pipeline
% -------------------------------------------------------
\begin{frame}{5. Methodology Breakdown (Embedding \& Detection)}
  \begin{columns}
    \column{0.5\textwidth}
      \begin{block}{Embedding Mechanism}
        \begin{itemize}
          \item Apply 3-Level Discrete Wavelet Transform (DWT) to split audio into subbands.
          \item Apply SVD on LL subband: $A = U \Sigma V^T$.
          \item Modify singular values $\Sigma_i$ with payload bits: $\Sigma_i' = \Sigma_i + \alpha \cdot w_i$.
          \item Reconstruct audio via Inverse DWT (IDWT) to ensure imperceptibility.
        \end{itemize}
      \end{block}

    \column{0.5\textwidth}
      \begin{block}{Detection \& Classification}
        \begin{itemize}
          \item Extract candidate watermark signature $\hat{w}_i$ from received audio subbands.
          \item Feed spectral residuals into Binary Neural Network (BNN).
          \item Compare extracted sequence with reference hash key using Normalized Cross-Correlation (NC).
          \item Flag deepfake generation or tamper location.
        \end{itemize}
      \end{block}
  \end{columns}
\end{frame}

% -------------------------------------------------------
% SLIDE 10: Tools Required
% -------------------------------------------------------
\section{Tools Required}
\begin{frame}{6. Tools \& Technologies Required}
  \begin{columns}
    \column{0.33\textwidth}
      \begin{block}{Software \& IDEs}
        \begin{itemize}
          \item Python 3.10+
          \item VS Code / PyCharm
          \item Jupyter Notebook
          \item Git \& GitHub
          \item Overleaf (LaTeX)
        \end{itemize}
      \end{block}

    \column{0.33\textwidth}
      \begin{block}{Libraries \& Frameworks}
        \begin{itemize}
          \item PyTorch / TensorFlow
          \item Librosa (Audio Processing)
          \item PyWavelets (DWT)
          \item SciPy \& NumPy
          \item Scikit-Learn / OpenCV
        \end{itemize}
      \end{block}

    \column{0.33\textwidth}
      \begin{block}{Datasets \& Hardware}
        \begin{itemize}
          \item ASVspoof 2021 Corpus
          \item LibriSpeech Dataset
          \item WaveFake Audio Set
          \item NVIDIA RTX GPU
          \item 16GB RAM / Core i7
        \end{itemize}
      \end{block}
  \end{columns}
\end{frame}

% -------------------------------------------------------
% SLIDE 11: Performance Metrics & Graph Parameters
% -------------------------------------------------------
\section{Performance Metrics}
\begin{frame}{7. Performance Metrics \& Graph X--Y Parameters}
  \begin{block}{Core Evaluation Metrics}
    \begin{itemize}
      \item \textbf{Bit Error Rate (BER)}: $BER = \frac{\text{Incorrect Bits}}{\text{Total Watermark Bits}} \times 100\%$
      \item \textbf{Signal-to-Noise Ratio (SNR)}: Measures audio imperceptibility in dB ($> 40\text{ dB}$ target).
      \item \textbf{Classification Accuracy, Precision, Recall, F1-Score, EER, AUC-ROC}.
    \end{itemize}
  \end{block}

  \begin{block}{Graph Axis Parameter Identifications}
    \begin{itemize}
      \item \textbf{Graph 1 (BER vs Noise Attack)}:
        \begin{itemize}
          \item \textbf{X-Axis}: Signal-to-Noise Ratio of Additive Noise (SNR in dB, 0 to 40 dB).
          \item \textbf{Y-Axis}: Bit Error Rate (BER in \%, 0.0\% to 50.0\%).
        \end{itemize}
      \item \textbf{Graph 2 (Detection Accuracy vs Compression Rate)}:
        \begin{itemize}
          \item \textbf{X-Axis}: MP3/AAC Bitrate (kbps: 32, 64, 128, 192, 256, 320 kbps).
          \item \textbf{Y-Axis}: Watermark Detection Accuracy (\%, 50\% to 100\%).
        \end{itemize}
      \item \textbf{Graph 3 (ROC Curve for Deepfake Detection)}:
        \begin{itemize}
          \item \textbf{X-Axis}: False Positive Rate (FPR, 0.0 to 1.0).
          \item \textbf{Y-Axis}: True Positive Rate (TPR, 0.0 to 1.0).
        \end{itemize}
    \end{itemize}
  \end{block}
\end{frame}

% -------------------------------------------------------
% SLIDE 12: Expected Outcomes
% -------------------------------------------------------
\section{Expected Outcomes}
\begin{frame}{8. Expected Outcomes \& Deliverables}
  \begin{block}{Expected Outcomes}
    \begin{itemize}
      \item Robust detection of imperceptible hidden audio watermarks under lossy transmission.
      \item Accurate classification of authentic vs. tampered vs. AI-generated deepfake audio ($>98\%$ accuracy).
      \item Fine-grained temporal tamper localization identifying modified frames.
      \item Low computational latency permitting real-time streaming media protection.
    \end{itemize}
  \end{block}

  \begin{block}{Key Deliverables}
    \begin{itemize}
      \item AI-Based Audio Watermarking \& Deepfake Authentication Software Module.
      \item Trained Deep Neural Network Models (PyTorch / ONNX format).
      \item Comprehensive Experimental Evaluation Report \& Benchmark Dataset.
      \item Interactive Prototype Web UI for instant audio file verification.
    \end{itemize}
  \end{block}
\end{frame}

% -------------------------------------------------------
% SLIDE 13: Project Roadmap
% -------------------------------------------------------
\begin{frame}{Implementation Roadmap}
  \begin{block}{Phase-Wise Development Plan}
    \begin{itemize}
      \item \textbf{Phase 1 (Months 1--2)}: Comprehensive IEEE literature review, dataset aggregation (ASVspoof 2021, LibriSpeech), and baseline DWT-SVD setup.
      \item \textbf{Phase 2 (Months 3--4)}: Implementation of neural watermark embedding, perceptual masking, and Binary Neural Network (BNN) architecture.
      \item \textbf{Phase 3 (Months 5--6)}: Adversarial attack evaluation (MP3 compression, pitch shift, noise injection, voice cloning) and hyperparameter tuning.
      \item \textbf{Phase 4 (Months 7--8)}: UI prototype integration, final benchmark reporting, and paper preparation.
    \end{itemize}
  \end{block}
\end{frame}

% -------------------------------------------------------
% SLIDE 14: Sustainable Development Goals (SDGs)
% -------------------------------------------------------
\begin{frame}{Related Sustainable Development Goals (SDGs)}
  \begin{block}{Alignment with United Nations SDGs}
    \begin{itemize}
      \item \textbf{SDG 9: Industry, Innovation and Infrastructure} -- Advances resilient digital media infrastructure and secure AI technologies against digital fraud.
      \item \textbf{SDG 16: Peace, Justice and Strong Institutions} -- Promotes digital trust, prevents deepfake misinformation, and protects intellectual property rights.
      \item \textbf{SDG 17: Partnerships for the Goals} -- Facilitates collaborative security standards across AI researchers, media broadcasters, and copyright organizations.
    \end{itemize}
  \end{block}
\end{frame}

% -------------------------------------------------------
% SLIDE 15: References & Thank You
% -------------------------------------------------------
\section{References}
\begin{frame}[allowframebreaks]{References}
  \tiny
  \begin{enumerate}
    \item Y. Sun et al., ``CANARY: Collision-Free Audio Watermarking for Proactive Deepfake Detection,'' \textit{IEEE Trans. Multimedia}, vol. 28, pp. 1420--1435, 2026.
    \item P. Aberna and L. Agilandeeswari, ``Optimal Semi-Fragile Watermarking Based on Maximum Entropy Random Walk and Swin Transformer for Tamper Localization,'' \textit{IEEE Access}, vol. 12, pp. 37757--37781, 2024.
    \item S. Kova\v{c}evi\'c et al., ``DeepMark Benchmark: Redefining Audio Watermarking Robustness,'' \textit{IEEE Access}, vol. 14, pp. 62031--62044, 2026.
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

  \vfill
  \centering
  \Large \textbf{\textcolor{IEEEblue}{Thank You! Questions \& Discussion}}
\end{frame}

\end{document}
"""

    with open(os.path.join(WORKSPACE, "beamer_presentation.tex"), "w", encoding="utf-8") as f:
        f.write(latex_code)
    
    with open(os.path.join(WORKSPACE, "main.tex"), "w", encoding="utf-8") as f:
        f.write(latex_code)

    print("Generated Beamer LaTeX code successfully.")

if __name__ == "__main__":
    generate_pdf_papers()
    generate_summary_docx()
    generate_beamer_latex()
    print("All tasks completed successfully!")
