"""
AI-Generated Audio & Deepfake Detection Engine.
"""

from .detector import (
    WatermarkIntegrityDetector,
    AudioAuthenticityClassifier,
    DetectionResult
)

__all__ = [
    'WatermarkIntegrityDetector',
    'AudioAuthenticityClassifier',
    'DetectionResult'
]
