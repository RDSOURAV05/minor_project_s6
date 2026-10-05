"""
Proxy module exposing KaggleDatasetLoader and KaggleAudioSample from implementation/src/data/kaggle_dataset.py.
"""

import sys
import os

IMPL_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "implementation", "src"))
if IMPL_SRC not in sys.path:
    sys.path.insert(0, IMPL_SRC)

from data.kaggle_dataset import KaggleDatasetLoader, KaggleAudioSample, main_inspection_summary

if __name__ == "__main__":
    main_inspection_summary()

__all__ = ["KaggleDatasetLoader", "KaggleAudioSample", "main_inspection_summary"]
