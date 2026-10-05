"""
Proxy module exposing KaggleBenchmarkEvaluator from implementation/src/pipeline/kaggle_evaluator.py.
"""

import sys
import os

IMPL_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "implementation", "src"))
if IMPL_SRC not in sys.path:
    sys.path.insert(0, IMPL_SRC)

from pipeline.kaggle_evaluator import KaggleBenchmarkEvaluator

__all__ = ["KaggleBenchmarkEvaluator"]
