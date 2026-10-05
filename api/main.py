"""
FastAPI Backend for Audio Watermarking & AI Deepfake Detection System.
Provides RESTful APIs for Embedding, Attacks, Detection, and Benchmarks.
"""

import os
import sys
import io
import json
import uuid
import base64
import threading
from typing import Optional, List, Dict, Any

import numpy as np
import soundfile as sf
import librosa
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Ensure implementation/src is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "implementation", "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from embedding.dwt_svd import DWTSVDWatermarker
from evaluation.metrics import (
    calculate_snr,
    calculate_psnr,
    calculate_seg_snr,
    calculate_lsd,
    calculate_ber,
    calculate_ncc,
)
from attacks.audio_attacks import (
    add_awgn_noise,
    apply_lowpass_filter,
    apply_highpass_filter,
    apply_bandpass_filter,
    apply_resampling_attack,
    apply_amplitude_scaling,
    apply_cropping_attack,
    apply_compression_simulation,
    apply_resynthesis_attack,
)
from detection.detector import WatermarkIntegrityDetector
from pipeline.benchmark_runner import BenchmarkRunner

app = FastAPI(
    title="Audio Watermarking API",
    description="DWT-SVD Watermarking and AI Deepfake Detection API",
    version="1.0.0"
)

# Enable CORS for Vite dev server and standard frontend hosts
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store for caching audio signals & metadata
SESSIONS: Dict[str, Dict[str, Any]] = {}

# Background benchmark state
BENCHMARK_STATUS: Dict[str, Any] = {
    "status": "idle",
    "progress": 0,
    "message": "No benchmark running"
}


def _downsample_waveform(signal: np.ndarray, num_points: int = 300) -> List[float]:
    """Downsample a 1D audio signal to a fixed number of representative points for frontend plotting."""
    if len(signal) == 0:
        return []
    if len(signal) <= num_points:
        return [float(round(v, 4)) for v in signal]
    
    chunk_size = len(signal) / num_points
    downsampled = []
    for i in range(num_points):
        start = int(i * chunk_size)
        end = int((i + 1) * chunk_size)
        chunk = signal[start:end]
        if len(chunk) > 0:
            # Keep the peak with correct sign
            max_idx = np.argmax(np.abs(chunk))
            val = float(chunk[max_idx])
        else:
            val = 0.0
        downsampled.append(round(val, 4))
    return downsampled


def _audio_to_base64_wav(signal: np.ndarray, sr: int = 16000) -> str:
    """Encode a 1D float numpy audio array as a data:audio/wav;base64 string."""
    buffer = io.BytesIO()
    # Normalize signal to avoid clipping in int16 representation
    max_val = np.max(np.abs(signal))
    norm_sig = signal if max_val <= 1.0 else signal / max_val
    sf.write(buffer, norm_sig.astype(np.float32), sr, format='WAV', subtype='PCM_16')
    buffer.seek(0)
    encoded = base64.b64encode(buffer.read()).decode('utf-8')
    return f"data:audio/wav;base64,{encoded}"


def _load_audio_bytes(file_bytes: bytes, target_sr: int = 16000) -> np.ndarray:
    """Load audio bytes into mono 1D float32 numpy array at target_sr."""
    buffer = io.BytesIO(file_bytes)
    try:
        data, sr = sf.read(buffer, dtype='float32')
        if data.ndim > 1:
            data = np.mean(data, axis=1)
        if sr != target_sr:
            data = librosa.resample(data, orig_sr=sr, target_sr=target_sr)
    except Exception:
        # Fallback to librosa with temp buffer
        buffer.seek(0)
        data, sr = librosa.load(buffer, sr=target_sr, mono=True)
    return data.astype(np.float32)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": "minor-project-s6-watermarking"}


@app.get("/api/samples")
def get_sample_list():
    """List sample audio files available in the samples/ folder."""
    samples_dir = os.path.join(BASE_DIR, "samples")
    result = []
    if os.path.exists(samples_dir):
        for f in os.listdir(samples_dir):
            if f.lower().endswith(".wav"):
                path = os.path.join(samples_dir, f)
                try:
                    data, sr = sf.read(path, dtype='float32')
                    if data.ndim > 1:
                        data = np.mean(data, axis=1)
                    duration = len(data) / sr
                    result.append({
                        "id": f,
                        "name": f.replace(".wav", "").replace("_", " ").title(),
                        "duration": round(duration, 2),
                        "sample_rate": sr,
                        "waveform": _downsample_waveform(data, 100),
                        "audio_url": _audio_to_base64_wav(data, sr)
                    })
                except Exception as e:
                    continue
    return {"samples": result}


@app.post("/api/embed")
async def embed_watermark(
    file: Optional[UploadFile] = File(None),
    sample_id: Optional[str] = Form(None),
    alpha: float = Form(0.05),
    mode: str = Form("SVD"),
    key_seed: int = Form(12345),
    watermark_len: int = Form(45)
):
    """
    Embed watermark into audio signal.
    Accepts uploaded audio file or sample_id from samples/ folder.
    Returns watermarked WAV, fidelity metrics (SNR, PSNR, SegSNR, LSD), waveforms, and session_id.
    """
    signal = None
    target_sr = 16000

    if file is not None and len(await file.read()) > 0:
        await file.seek(0)
        content = await file.read()
        signal = _load_audio_bytes(content, target_sr=target_sr)
    elif sample_id:
        sample_path = os.path.join(BASE_DIR, "samples", sample_id if sample_id.endswith(".wav") else f"{sample_id}.wav")
        if os.path.exists(sample_path):
            with open(sample_path, "rb") as f:
                signal = _load_audio_bytes(f.read(), target_sr=target_sr)

    if signal is None or len(signal) == 0:
        raise HTTPException(status_code=400, detail="No valid audio file or sample provided.")

    # Generate watermark
    watermark = DWTSVDWatermarker.generate_watermark(watermark_len, key=key_seed)

    # Watermarking engine
    wm_mode = 'qim' if mode.upper() == 'QIM' else 'non_blind'
    watermarker = DWTSVDWatermarker(wavelet='db4', level=3, alpha=alpha, mode=wm_mode)
    
    # Embed
    wm_signal, metadata = watermarker.embed_signal(signal, watermark)

    # Compute fidelity metrics
    snr = float(calculate_snr(signal, wm_signal))
    psnr = float(calculate_psnr(signal, wm_signal))
    seg_snr = float(calculate_seg_snr(signal, wm_signal))
    lsd = float(calculate_lsd(signal, wm_signal))

    # Also compute block metadata for tamper localization
    try:
        wm_blocks, block_metadata = watermarker.embed_blocks(signal, watermark, block_size=4096)
    except Exception:
        block_metadata = []

    # Store session
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = {
        "original_signal": signal,
        "watermarked_signal": wm_signal,
        "metadata": metadata,
        "block_metadata": block_metadata,
        "watermark": watermark,
        "alpha": alpha,
        "mode": wm_mode,
        "key_seed": key_seed,
        "watermark_len": watermark_len,
        "sr": target_sr
    }

    return {
        "session_id": session_id,
        "snr": round(snr, 2),
        "psnr": round(psnr, 2),
        "seg_snr": round(seg_snr, 2),
        "lsd": round(lsd, 3),
        "duration": round(len(signal) / target_sr, 2),
        "sample_rate": target_sr,
        "watermark_length": watermark_len,
        "watermark_bits": watermark.tolist(),
        "waveform_original": _downsample_waveform(signal, 300),
        "waveform_watermarked": _downsample_waveform(wm_signal, 300),
        "original_audio": _audio_to_base64_wav(signal, target_sr),
        "watermarked_audio": _audio_to_base64_wav(wm_signal, target_sr)
    }


@app.post("/api/attack")
async def attack_watermark(
    file: Optional[UploadFile] = File(None),
    session_id: Optional[str] = Form(None),
    attack_type: str = Form("awgn"),
    params: Optional[str] = Form("{}"),
    key_seed: int = Form(12345),
    watermark_len: int = Form(45),
    alpha: float = Form(0.05),
    mode: str = Form("SVD")
):
    """
    Apply channel distortion or manipulation attack to watermarked audio.
    Computes extracted watermark, BER, NCC, bit-level comparison array, and attacked waveform.
    """
    signal = None
    metadata = None
    expected_watermark = None
    sr = 16000

    if session_id and session_id in SESSIONS:
        sess = SESSIONS[session_id]
        signal = sess["watermarked_signal"]
        metadata = sess["metadata"]
        expected_watermark = sess["watermark"]
        sr = sess["sr"]
        alpha = sess["alpha"]
        mode = sess["mode"]
        watermark_len = sess["watermark_len"]
        key_seed = sess["key_seed"]

    if file is not None and len(await file.read()) > 0:
        await file.seek(0)
        signal = _load_audio_bytes(await file.read(), target_sr=sr)

    if signal is None:
        raise HTTPException(status_code=400, detail="No audio provided for attack.")

    if expected_watermark is None:
        expected_watermark = DWTSVDWatermarker.generate_watermark(watermark_len, key=key_seed)

    # Parse attack parameters
    try:
        p = json.loads(params) if params else {}
    except Exception:
        p = {}

    att = attack_type.lower()
    attacked_signal = signal.copy()

    if "awgn" in att:
        snr_db = float(p.get("snr_db", 20.0))
        attacked_signal = add_awgn_noise(signal, snr_db=snr_db)
    elif "mp3" in att or "compression" in att:
        bitrate = int(p.get("bitrate", 64))
        attacked_signal = apply_compression_simulation(signal, sr=sr, bitrate=bitrate)
    elif "lowpass" in att:
        cutoff = float(p.get("cutoff", 4000.0))
        attacked_signal = apply_lowpass_filter(signal, sr=sr, cutoff=cutoff)
    elif "highpass" in att:
        cutoff = float(p.get("cutoff", 300.0))
        attacked_signal = apply_highpass_filter(signal, sr=sr, cutoff=cutoff)
    elif "bandpass" in att:
        lowcut = float(p.get("lowcut", 300.0))
        highcut = float(p.get("highcut", 3400.0))
        attacked_signal = apply_bandpass_filter(signal, sr=sr, lowcut=lowcut, highcut=highcut)
    elif "resample" in att:
        target_sr = int(p.get("target_sr", 8000))
        attacked_signal = apply_resampling_attack(signal, orig_sr=sr, target_sr=target_sr)
    elif "scale" in att:
        factor = float(p.get("factor", 0.8))
        attacked_signal = apply_amplitude_scaling(signal, factor=factor)
    elif "crop" in att:
        crop_ratio = float(p.get("crop_ratio", 0.1))
        location = str(p.get("location", "middle"))
        attacked_signal = apply_cropping_attack(signal, crop_ratio=crop_ratio, location=location)
    elif "vocoder" in att or "resynthesis" in att:
        noise_level = float(p.get("noise_level", 0.03))
        attacked_signal = apply_resynthesis_attack(signal, noise_level=noise_level)

    # Watermark Extraction
    wm_mode = 'qim' if str(mode).upper() == 'QIM' or mode == 'qim' else 'non_blind'
    watermarker = DWTSVDWatermarker(wavelet='db4', level=3, alpha=alpha, mode=wm_mode)
    extracted = watermarker.extract_signal(attacked_signal, metadata, watermark_len=len(expected_watermark))

    ber = float(calculate_ber(expected_watermark, extracted))
    ncc = float(calculate_ncc(expected_watermark, extracted))

    # Bit comparison array for visual chip rendering
    bit_comparison = []
    for i in range(len(expected_watermark)):
        orig_bit = int(expected_watermark[i])
        ext_bit = int(extracted[i]) if i < len(extracted) else 0
        bit_comparison.append({
            "index": i,
            "original": orig_bit,
            "extracted": ext_bit,
            "match": bool(orig_bit == ext_bit)
        })

    # Update session with attacked audio if available
    if session_id and session_id in SESSIONS:
        SESSIONS[session_id]["attacked_signal"] = attacked_signal

    return {
        "attack_type": attack_type,
        "ber": round(ber, 4),
        "ncc": round(ncc, 4),
        "bit_comparison": bit_comparison,
        "attacked_audio": _audio_to_base64_wav(attacked_signal, sr),
        "waveform_attacked": _downsample_waveform(attacked_signal, 300),
        "duration": round(len(attacked_signal) / sr, 2)
    }


@app.post("/api/detect")
async def detect_authenticity(
    file: Optional[UploadFile] = File(None),
    session_id: Optional[str] = Form(None),
    use_attacked: bool = Form(False),
    key_seed: int = Form(12345),
    watermark_len: int = Form(45),
    alpha: float = Form(0.05),
    mode: str = Form("SVD")
):
    """
    Authenticate audio and evaluate deepfake / tampering integrity.
    Returns verdict, confidence, BER, NCC, and tamper localization segments.
    """
    signal = None
    metadata = None
    block_metadata = None
    sr = 16000

    if session_id and session_id in SESSIONS:
        sess = SESSIONS[session_id]
        if use_attacked and "attacked_signal" in sess:
            signal = sess["attacked_signal"]
        else:
            signal = sess["watermarked_signal"]
        metadata = sess["metadata"]
        block_metadata = sess.get("block_metadata")
        sr = sess["sr"]
        alpha = sess["alpha"]
        mode = sess["mode"]
        key_seed = sess["key_seed"]
        watermark_len = sess["watermark_len"]

    if file is not None and len(await file.read()) > 0:
        await file.seek(0)
        signal = _load_audio_bytes(await file.read(), target_sr=sr)

    if signal is None:
        raise HTTPException(status_code=400, detail="No audio provided for detection.")

    expected_watermark = DWTSVDWatermarker.generate_watermark(watermark_len, key=key_seed)
    wm_mode = 'qim' if str(mode).upper() == 'QIM' or mode == 'qim' else 'non_blind'
    watermarker = DWTSVDWatermarker(wavelet='db4', level=3, alpha=alpha, mode=wm_mode)
    detector = WatermarkIntegrityDetector(watermarker)

    # 1. Holistic verification
    det_result = detector.verify_authenticity(signal, expected_watermark, metadata)

    # 2. Tamper localization if block metadata exists or block partitioning
    tamper_segments = []
    block_size = 4096
    num_blocks = len(signal) // block_size

    if block_metadata and len(block_metadata) > 0:
        loc_res = detector.localize_tampering(signal, block_metadata, block_size=block_size, sr=sr)
        if loc_res.tampered_intervals:
            tamper_segments = loc_res.tampered_intervals
    else:
        # Segment-by-segment check
        for i in range(num_blocks):
            start = i * block_size
            end = start + block_size
            chunk = signal[start:end]
            t_start = round(start / sr, 3)
            t_end = round(end / sr, 3)
            
            # Sub-block extraction
            sub_wm = watermarker.extract_signal(chunk, metadata, watermark_len=min(16, watermark_len))
            sub_expected = expected_watermark[:len(sub_wm)]
            sub_ber = float(calculate_ber(sub_expected, sub_wm)) if len(sub_expected) > 0 else 0.5
            is_tampered = sub_ber > 0.20
            
            tamper_segments.append({
                "block_idx": i,
                "start_time_sec": t_start,
                "end_time_sec": t_end,
                "ber": round(sub_ber, 4),
                "is_tampered": is_tampered
            })

    return {
        "verdict": det_result.label,
        "is_authentic": det_result.is_authentic,
        "confidence": round(det_result.confidence_score, 4),
        "ber": round(det_result.ber, 4),
        "ncc": round(det_result.ncc, 4),
        "tamper_segments": tamper_segments,
        "duration": round(len(signal) / sr, 2),
        "sample_rate": sr
    }


@app.get("/api/benchmark")
def get_benchmark_results():
    """Retrieve synthetic benchmark results."""
    json_path = os.path.join(BASE_DIR, "benchmark_results", "benchmark_results.json")
    if not os.path.exists(json_path):
        raise HTTPException(status_code=404, detail="Benchmark results not found. Run benchmark first.")
    with open(json_path, "r") as f:
        data = json.load(f)
    return data


def _execute_benchmark_worker(num_samples: int = 5):
    global BENCHMARK_STATUS
    BENCHMARK_STATUS["status"] = "running"
    BENCHMARK_STATUS["progress"] = 10
    BENCHMARK_STATUS["message"] = "Starting DeepMark benchmark suite..."

    try:
        runner = BenchmarkRunner()
        BENCHMARK_STATUS["progress"] = 30
        BENCHMARK_STATUS["message"] = "Running synthetic speech embedding and attack stress tests..."
        results = runner.run_comprehensive_benchmark(num_samples=num_samples, duration=2.5)
        BENCHMARK_STATUS["progress"] = 80
        BENCHMARK_STATUS["message"] = "Generating empirical plots and saving metrics..."
        
        from pipeline.plot_empirical_results import EmpiricalResultsPlotter
        plotter = EmpiricalResultsPlotter()
        plotter.generate_presentation_metrics_figure(data=results)

        BENCHMARK_STATUS["progress"] = 100
        BENCHMARK_STATUS["status"] = "completed"
        BENCHMARK_STATUS["message"] = "Benchmark completed successfully."
    except Exception as e:
        BENCHMARK_STATUS["status"] = "failed"
        BENCHMARK_STATUS["message"] = str(e)


@app.post("/api/benchmark/run")
def trigger_benchmark(background_tasks: BackgroundTasks, num_samples: int = 5):
    """Trigger the synthetic benchmark runner in the background."""
    global BENCHMARK_STATUS
    if BENCHMARK_STATUS["status"] == "running":
        return {"status": "already_running", "message": "Benchmark is currently executing."}
    
    thread = threading.Thread(target=_execute_benchmark_worker, args=(num_samples,))
    thread.daemon = True
    thread.start()
    return {"status": "started", "message": f"Benchmark launched with {num_samples} samples."}


@app.get("/api/benchmark/status")
def get_benchmark_status():
    """Check status of running benchmark."""
    return BENCHMARK_STATUS


@app.get("/api/dataset/results")
def get_dataset_results():
    """Retrieve Kaggle real-world dataset evaluation results."""
    json_path = os.path.join(BASE_DIR, "benchmark_results", "kaggle_results.json")
    if not os.path.exists(json_path):
        raise HTTPException(
            status_code=404,
            detail="Kaggle dataset evaluation results not found. Run dataset evaluation first."
        )
    with open(json_path, "r") as f:
        data = json.load(f)
    return data
