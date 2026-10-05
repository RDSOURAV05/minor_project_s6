"""
Tests for FastAPI Backend Endpoints (api/main.py).
"""

import sys
import os
import pytest
from fastapi.testclient import TestClient

# Ensure root and implementation/src are on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "implementation", "src")))

from api.main import app
from data.dataset_manager import generate_synthetic_speech_signal
import soundfile as sf
import io

client = TestClient(app)


def test_api_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_api_samples():
    response = client.get("/api/samples")
    assert response.status_code == 200
    data = response.json()
    assert "samples" in data
    assert isinstance(data["samples"], list)


def test_api_embed_with_synthetic_audio():
    # Generate 1.0s synthetic audio
    sig = generate_synthetic_speech_signal(duration=1.0, sr=16000, seed=42)
    buf = io.BytesIO()
    sf.write(buf, sig, 16000, format='WAV')
    buf.seek(0)

    files = {"file": ("test.wav", buf.read(), "audio/wav")}
    data = {
        "alpha": "0.05",
        "mode": "SVD",
        "key_seed": "12345",
        "watermark_len": "32"
    }

    response = client.post("/api/embed", files=files, data=data)
    assert response.status_code == 200
    res = response.json()
    assert "session_id" in res
    assert res["snr"] > 25.0
    assert "watermarked_audio" in res
    assert len(res["waveform_original"]) > 0
    assert len(res["waveform_watermarked"]) > 0
    assert len(res["watermark_bits"]) == 32

    session_id = res["session_id"]

    # Test attack endpoint using the session
    attack_res = client.post("/api/attack", data={
        "session_id": session_id,
        "attack_type": "awgn",
        "params": '{"snr_db": 30}',
        "key_seed": "12345",
        "watermark_len": "32",
        "alpha": "0.05",
        "mode": "SVD"
    })
    assert attack_res.status_code == 200
    att_data = attack_res.json()
    assert "ber" in att_data
    assert "ncc" in att_data
    assert "bit_comparison" in att_data
    assert len(att_data["bit_comparison"]) == 32

    # Test detect endpoint
    detect_res = client.post("/api/detect", data={
        "session_id": session_id,
        "key_seed": "12345",
        "watermark_len": "32",
        "alpha": "0.05",
        "mode": "SVD"
    })
    assert detect_res.status_code == 200
    det_data = detect_res.json()
    assert "verdict" in det_data
    assert det_data["verdict"] in ["AUTHENTIC_WATERMARKED", "TAMPERED_AUDIO", "AI_GENERATED_OR_UNWATERMARKED"]
    assert "confidence" in det_data
    assert "tamper_segments" in det_data
