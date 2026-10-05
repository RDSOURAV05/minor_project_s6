"""
Data Management & Synthetic Audio Generation Module.
"""

from .dataset_manager import (
    generate_synthetic_speech_signal,
    create_test_audio_dataset,
    load_audio_file,
    save_audio_file,
    AudioDatasetManager
)

__all__ = [
    'generate_synthetic_speech_signal',
    'create_test_audio_dataset',
    'load_audio_file',
    'save_audio_file',
    'AudioDatasetManager'
]
