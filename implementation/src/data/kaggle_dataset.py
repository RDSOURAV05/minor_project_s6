"""
Kaggle Speech Dataset Loader & Preprocessing Module.
Dataset: Speech Dataset of Human and AI-Generated Voices (kambingbersayaphitam).

Capabilities:
- Automatic directory discovery (handles nested 'Fake/Fake' and 'Real/Real' layouts)
- Conversion to mono 16 kHz floating-point numpy signals
- Amplitude normalization
- Uniform segmentation/chunking into fixed length (default 3.0s = 48,000 samples)
- Stratified sampling by speaker / recording ID (default ~200 clips per class)
- Speaker-independent Train/Test splitting to prevent acoustic leakage
- Fast local caching in data/kaggle_cache/
"""

import os
import re
import glob
import json
import hashlib
from typing import List, Dict, Tuple, Optional, Any
import numpy as np
import soundfile as sf
import librosa
from tqdm import tqdm


class KaggleAudioSample:
    """Represents a preprocessed audio clip from the Kaggle dataset."""
    def __init__(self, audio: np.ndarray, label: str, speaker_id: str, source_file: str, clip_idx: int, sr: int = 16000):
        self.audio = audio.astype(np.float32)
        self.label = label.lower()  # 'real' (human) or 'fake' (ai)
        self.is_ai = bool(self.label == 'fake')
        self.speaker_id = str(speaker_id)
        self.source_file = source_file
        self.clip_idx = clip_idx
        self.sr = sr

    @property
    def duration(self) -> float:
        return len(self.audio) / self.sr


class KaggleDatasetLoader:
    def __init__(
        self,
        data_dir: str = "data/kaggle_dataset",
        cache_dir: str = "data/kaggle_cache",
        target_sr: int = 16000,
        clip_duration: float = 3.0,
        n_per_class: int = 200,
        seed: int = 42
    ):
        self.data_dir = os.path.abspath(data_dir)
        self.cache_dir = os.path.abspath(cache_dir)
        self.target_sr = target_sr
        self.clip_duration = clip_duration
        self.target_samples = int(clip_duration * target_sr)
        self.n_per_class = n_per_class
        self.seed = seed

    def find_class_files(self) -> Dict[str, List[str]]:
        """Find audio files for Real and Fake classes handling nested folder layouts."""
        files_by_class = {'real': [], 'fake': []}

        if not os.path.exists(self.data_dir):
            raise FileNotFoundError(f"Kaggle dataset directory not found at: {self.data_dir}")

        for root, _, files in os.walk(self.data_dir):
            for f in files:
                if f.lower().endswith(('.wav', '.flac', '.mp3')):
                    full_path = os.path.join(root, f)
                    lower_path = full_path.lower()
                    if 'real' in lower_path:
                        files_by_class['real'].append(full_path)
                    elif 'fake' in lower_path:
                        files_by_class['fake'].append(full_path)

        # Sort for deterministic order
        files_by_class['real'].sort()
        files_by_class['fake'].sort()
        return files_by_class

    def get_dataset_summary(self) -> Dict[str, Any]:
        """Print and return summary statistics of the raw dataset."""
        files_by_class = self.find_class_files()
        summary = {}

        for cls_name in ['real', 'fake']:
            file_list = files_by_class[cls_name]
            total_dur = 0.0
            srs = set()
            channels = set()
            durations = []

            for fp in file_list:
                try:
                    info = sf.info(fp)
                    srs.add(info.samplerate)
                    channels.add(info.channels)
                    durations.append(info.duration)
                    total_dur += info.duration
                except Exception:
                    pass

            summary[cls_name] = {
                'file_count': len(file_list),
                'sample_rates': list(srs),
                'channels': list(channels),
                'total_duration_sec': round(total_dur, 2),
                'total_hours': round(total_dur / 3600, 2),
                'min_duration': round(min(durations), 2) if durations else 0,
                'mean_duration': round(sum(durations) / len(durations), 2) if durations else 0,
                'max_duration': round(max(durations), 2) if durations else 0,
            }

        return summary

    @staticmethod
    def extract_speaker_id(filepath: str) -> str:
        """Extract recording/speaker ID from filename, e.g. 'Recording (5).wav' -> 'speaker_05'."""
        base = os.path.basename(filepath)
        match = re.search(r'\((\d+)\)', base)
        if match:
            return f"speaker_{int(match.group(1)):02d}"
        clean_name = os.path.splitext(base)[0]
        return clean_name

    def _preprocess_audio_file(self, filepath: str) -> List[np.ndarray]:
        """Load audio, convert to mono 16 kHz, normalize, and segment into fixed length chunks."""
        try:
            # Load with soundfile first for speed
            data, sr = sf.read(filepath, dtype='float32')
            if data.ndim > 1:
                data = np.mean(data, axis=1)
            if sr != self.target_sr:
                data = librosa.resample(data, orig_sr=sr, target_sr=self.target_sr)
        except Exception:
            data, sr = librosa.load(filepath, sr=self.target_sr, mono=True)

        # Normalize
        peak = np.max(np.abs(data))
        if peak > 0:
            data = (data / peak) * 0.95

        # Segment into target_samples chunks
        chunks = []
        hop = self.target_samples
        total_samples = len(data)

        for start in range(0, total_samples, hop):
            chunk = data[start:start + self.target_samples]
            if len(chunk) == self.target_samples:
                # Discard near-silent chunks
                rms = np.sqrt(np.mean(chunk ** 2))
                if rms > 0.01:
                    chunks.append(chunk.astype(np.float32))
            elif len(chunk) >= self.target_samples // 2:
                # Pad short trailing chunk
                padded = np.pad(chunk, (0, self.target_samples - len(chunk)), 'constant')
                rms = np.sqrt(np.mean(padded ** 2))
                if rms > 0.01:
                    chunks.append(padded.astype(np.float32))

        return chunks

    def load_subsampled_dataset(self) -> Tuple[List[KaggleAudioSample], List[KaggleAudioSample]]:
        """
        Load a seeded stratified subsample of the dataset (~n_per_class for real and fake).
        Uses local disk caching for instant subsequent loads.
        Returns: (human_samples, ai_samples)
        """
        cache_id = f"subsample_n{self.n_per_class}_dur{self.clip_duration}_sr{self.target_sr}_seed{self.seed}"
        cache_file = os.path.join(self.cache_dir, f"{cache_id}.npz")
        meta_file = os.path.join(self.cache_dir, f"{cache_id}_meta.json")

        if os.path.exists(cache_file) and os.path.exists(meta_file):
            print(f"[KaggleLoader] Loading cached preprocessed dataset from {cache_file}...")
            npz = np.load(cache_file, allow_pickle=True)
            with open(meta_file, 'r') as f:
                meta = json.load(f)

            human_samples = []
            for item in meta['human']:
                audio = npz[f"human_{item['idx']}"]
                human_samples.append(KaggleAudioSample(
                    audio=audio,
                    label='real',
                    speaker_id=item['speaker_id'],
                    source_file=item['source_file'],
                    clip_idx=item['clip_idx'],
                    sr=self.target_sr
                ))

            ai_samples = []
            for item in meta['ai']:
                audio = npz[f"ai_{item['idx']}"]
                ai_samples.append(KaggleAudioSample(
                    audio=audio,
                    label='fake',
                    speaker_id=item['speaker_id'],
                    source_file=item['source_file'],
                    clip_idx=item['clip_idx'],
                    sr=self.target_sr
                ))

            return human_samples, ai_samples

        print("[KaggleLoader] Preprocessing and extracting stratified audio clips...")
        os.makedirs(self.cache_dir, exist_ok=True)
        files_by_class = self.find_class_files()
        rng = np.random.RandomState(self.seed)

        def extract_stratified(file_list: List[str], target_count: int, label: str) -> List[KaggleAudioSample]:
            samples_per_file: Dict[str, List[np.ndarray]] = {}
            for fp in file_list:
                chunks = self._preprocess_audio_file(fp)
                if chunks:
                    samples_per_file[fp] = chunks

            if not samples_per_file:
                return []

            # Stratified round-robin selection across files
            selected_samples: List[KaggleAudioSample] = []
            file_keys = list(samples_per_file.keys())
            file_indices = {fp: list(range(len(samples_per_file[fp]))) for fp in file_keys}
            for fp in file_keys:
                rng.shuffle(file_indices[fp])

            round_num = 0
            while len(selected_samples) < target_count:
                progress = False
                for fp in file_keys:
                    if file_indices[fp]:
                        c_idx = file_indices[fp].pop(0)
                        chunk = samples_per_file[fp][c_idx]
                        spk_id = self.extract_speaker_id(fp)
                        selected_samples.append(KaggleAudioSample(
                            audio=chunk,
                            label=label,
                            speaker_id=spk_id,
                            source_file=os.path.basename(fp),
                            clip_idx=c_idx,
                            sr=self.target_sr
                        ))
                        progress = True
                        if len(selected_samples) >= target_count:
                            break
                if not progress:
                    break

            return selected_samples

        human_samples = extract_stratified(files_by_class['real'], self.n_per_class, 'real')
        ai_samples = extract_stratified(files_by_class['fake'], self.n_per_class, 'fake')

        print(f"[KaggleLoader] Selected {len(human_samples)} Human clips and {len(ai_samples)} AI clips.")

        # Save to disk cache
        npz_dict = {}
        meta_dict = {'human': [], 'ai': []}

        for i, s in enumerate(human_samples):
            npz_dict[f"human_{i}"] = s.audio
            meta_dict['human'].append({
                'idx': i,
                'speaker_id': s.speaker_id,
                'source_file': s.source_file,
                'clip_idx': s.clip_idx
            })

        for i, s in enumerate(ai_samples):
            npz_dict[f"ai_{i}"] = s.audio
            meta_dict['ai'].append({
                'idx': i,
                'speaker_id': s.speaker_id,
                'source_file': s.source_file,
                'clip_idx': s.clip_idx
            })

        np.savez_compressed(cache_file, **npz_dict)
        with open(meta_file, 'w') as f:
            json.dump(meta_dict, f, indent=2)

        print(f"[KaggleLoader] Successfully cached {len(human_samples) + len(ai_samples)} clips to {cache_file}.")
        return human_samples, ai_samples

    @staticmethod
    def split_by_speaker(
        samples: List[KaggleAudioSample],
        train_ratio: float = 0.7,
        seed: int = 42
    ) -> Tuple[List[KaggleAudioSample], List[KaggleAudioSample]]:
        """Split clips into Train and Test partitions strictly by speaker/recording ID."""
        speakers = sorted(list(set(s.speaker_id for s in samples)))
        rng = np.random.RandomState(seed)
        rng.shuffle(speakers)

        n_train = max(1, int(round(len(speakers) * train_ratio)))
        train_speakers = set(speakers[:n_train])

        train_samples = [s for s in samples if s.speaker_id in train_speakers]
        test_samples = [s for s in samples if s.speaker_id not in train_speakers]
        return train_samples, test_samples


def main_inspection_summary(data_dir: str = "data/kaggle_dataset") -> Dict[str, Any]:
    """Inspect folder structure and print formatted summary."""
    loader = KaggleDatasetLoader(data_dir=data_dir)
    print("=" * 70)
    print("KAGGLE DATASET INSPECTION SUMMARY (Human vs AI-Generated Voices)")
    print(f"Path: {loader.data_dir}")
    print("=" * 70)
    summary = loader.get_dataset_summary()
    for cls_name, info in summary.items():
        print(f"\n[Class: {cls_name.upper()}]")
        print(f"  * Audio File Count : {info['file_count']} recordings")
        print(f"  * Format / Codec   : WAV (PCM_16)")
        print(f"  * Sample Rates     : {info['sample_rates']} Hz")
        print(f"  * Channels         : {info['channels']}")
        print(f"  * Total Duration   : {info['total_duration_sec']:.1f} s ({info['total_hours']:.2f} hours)")
        print(f"  * Min / Mean / Max : {info['min_duration']:.1f}s / {info['mean_duration']:.1f}s / {info['max_duration']:.1f}s")
    print("=" * 70)
    return summary


if __name__ == "__main__":
    main_inspection_summary()

