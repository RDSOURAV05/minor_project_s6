import requests
import json
import os
import time

query_terms = [
    "audio watermarking IEEE Access",
    "audio deepfake watermark IEEE",
    "audio tamper localization IEEE",
    "robust audio watermarking neural network IEEE",
    "acoustic watermarking IEEE",
    "deepfake audio authentication IEEE"
]

papers = []
seen_dois = set()

# Pre-selected high-impact IEEE journal papers (2020-2026) in Audio Watermarking & Deepfake Authentication
selected_candidates = [
    {
        "title": "Optimal Semi-Fragile Watermarking Based on Maximum Entropy Random Walk and Swin Transformer for Tamper Localization",
        "authors": "P. Aberna, L. Agilandeeswari",
        "journal": "IEEE Access",
        "year": "2024",
        "volume": "12",
        "pages": "37757-37781",
        "doi": "10.1109/ACCESS.2024.3370411",
        "pdf_url": "https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=10453965",
        "direct_pdf": "https://ieeexplore.ieee.org/ielx7/6287639/10380310/10453965.pdf"
    },
    {
        "title": "DeepMark Benchmark: Redefining Audio Watermarking Robustness",
        "authors": "S. Kovačević, E. Nešović, K. Pavlović, P. Nedić, I. Djurović",
        "journal": "IEEE Access",
        "year": "2024",
        "volume": "12",
        "pages": "62031-62044",
        "doi": "10.1109/ACCESS.2024.3395123",
        "pdf_url": "https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=10510523",
        "direct_pdf": "https://ieeexplore.ieee.org/ielx7/6287639/10380310/10510523.pdf"
    }
]

print("Script template created.")
