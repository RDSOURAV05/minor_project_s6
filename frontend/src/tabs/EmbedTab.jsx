import React, { useState, useEffect } from 'react';
import WaveformViewer from '../components/WaveformViewer';

export default function EmbedTab({ apiBase, session, setSession, samples = [] }) {
  const [selectedSample, setSelectedSample] = useState(samples.length > 0 ? samples[0].id : '');
  const [uploadFile, setUploadFile] = useState(null);
  const [alpha, setAlpha] = useState(0.05);
  const [mode, setMode] = useState('SVD');
  const [keySeed, setKeySeed] = useState(12345);
  const [watermarkLen, setWatermarkLen] = useState(45);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (samples.length > 0 && !selectedSample) {
      setSelectedSample(samples[0].id);
    }
  }, [samples]);

  const handleEmbed = async () => {
    setLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      if (uploadFile) {
        formData.append('file', uploadFile);
      } else if (selectedSample) {
        formData.append('sample_id', selectedSample);
      } else {
        throw new Error('Please select a sample audio or upload a WAV file.');
      }
      formData.append('alpha', alpha.toString());
      formData.append('mode', mode);
      formData.append('key_seed', keySeed.toString());
      formData.append('watermark_len', watermarkLen.toString());

      const res = await fetch(`${apiBase}/api/embed`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Server error: ${res.status}`);
      }

      const data = await res.json();
      setSession(data);
    } catch (err) {
      setError(err.message || 'Watermark embedding failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="tab-content">
      <div className="grid-2">
        {/* Left Column: Input and Parameters */}
        <div className="card">
          <h2 className="card-title">1. Audio Source & Embedding Parameters</h2>

          {/* Sample Picker */}
          <div className="form-group">
            <label className="form-label">
              <span>Select Academic Speech Sample</span>
              <span style={{ color: 'var(--text-subtle)' }}>Preset 16 kHz Mono</span>
            </label>
            <select
              className="form-select"
              value={selectedSample}
              onChange={(e) => {
                setSelectedSample(e.target.value);
                setUploadFile(null);
              }}
              disabled={!!uploadFile}
            >
              {samples.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name} ({s.duration}s)
                </option>
              ))}
            </select>
          </div>

          {/* File Upload */}
          <div className="form-group">
            <label className="form-label">
              <span>Or Upload Custom WAV Audio</span>
              {uploadFile && (
                <span
                  style={{ color: 'var(--primary)', cursor: 'pointer' }}
                  onClick={() => setUploadFile(null)}
                >
                  Clear File
                </span>
              )}
            </label>
            <input
              type="file"
              accept=".wav,.flac,.mp3"
              className="form-input"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  setUploadFile(e.target.files[0]);
                }
              }}
            />
          </div>

          {/* Alpha Slider */}
          <div className="form-group">
            <div className="form-label">
              <span>Watermark Strength (Alpha)</span>
              <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{alpha.toFixed(3)}</span>
            </div>
            <input
              type="range"
              min="0.01"
              max="0.20"
              step="0.005"
              value={alpha}
              className="range-slider"
              onChange={(e) => setAlpha(parseFloat(e.target.value))}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: 'var(--text-subtle)', marginTop: '2px' }}>
              <span>0.01 (High Fidelity)</span>
              <span>0.05 (Balanced)</span>
              <span>0.20 (Robust)</span>
            </div>
          </div>

          {/* Mode & Key Seed */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div className="form-group">
              <label className="form-label">Watermarking Mode</label>
              <select className="form-select" value={mode} onChange={(e) => setMode(e.target.value)}>
                <option value="SVD">SVD (Orthonormal Projection)</option>
                <option value="QIM">QIM (Quantization Modulation)</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Watermark Key / PRNG Seed</label>
              <input
                type="number"
                className="form-input"
                value={keySeed}
                onChange={(e) => setKeySeed(parseInt(e.target.value) || 0)}
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Payload Length (Bits)</label>
            <input
              type="number"
              className="form-input"
              value={watermarkLen}
              onChange={(e) => setWatermarkLen(parseInt(e.target.value) || 32)}
              min="8"
              max="128"
            />
          </div>

          <button
            className="btn btn-primary"
            style={{ width: '100%', marginTop: '8px' }}
            onClick={handleEmbed}
            disabled={loading}
          >
            {loading ? 'Embedding DWT-SVD Watermark...' : 'Embed Watermark'}
          </button>

          {error && (
            <div style={{ marginTop: '12px', padding: '10px', background: 'var(--danger-bg)', border: '1px solid var(--danger-border)', borderRadius: '6px', color: 'var(--danger)', fontSize: '0.8125rem' }}>
              {error}
            </div>
          )}
        </div>

        {/* Right Column: Fidelity Results & Waveforms */}
        <div className="card">
          <h2 className="card-title">2. Audio Fidelity & Waveform Comparison</h2>

          {session ? (
            <div>
              {/* 2x2 Metric Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px' }}>
                <div className="metric-box">
                  <div className="metric-label">Signal-to-Noise Ratio (SNR)</div>
                  <div className="metric-value">{session.snr} dB</div>
                  <div className="metric-desc">Target &gt; 35 dB (Imperceptible)</div>
                </div>
                <div className="metric-box">
                  <div className="metric-label">Peak SNR (PSNR)</div>
                  <div className="metric-value">{session.psnr} dB</div>
                  <div className="metric-desc">Target &gt; 50 dB</div>
                </div>
                <div className="metric-box">
                  <div className="metric-label">Segmental SNR (SegSNR)</div>
                  <div className="metric-value">{session.seg_snr} dB</div>
                  <div className="metric-desc">Frame-level perceptual metric</div>
                </div>
                <div className="metric-box">
                  <div className="metric-label">Log-Spectral Distance (LSD)</div>
                  <div className="metric-value">{session.lsd} dB</div>
                  <div className="metric-desc">Target &lt; 1.0 dB</div>
                </div>
              </div>

              {/* Waveform Comparisons */}
              <WaveformViewer
                points={session.waveform_original}
                color="#0284c7"
                label="Original Speech Signal"
                duration={session.duration}
              />
              <div className="audio-player-wrapper">
                <audio controls src={session.original_audio} />
              </div>

              <div style={{ marginTop: '14px' }}>
                <WaveformViewer
                  points={session.waveform_watermarked}
                  color="#10b981"
                  label="DWT-SVD Watermarked Signal"
                  duration={session.duration}
                />
                <div className="audio-player-wrapper">
                  <audio controls src={session.watermarked_audio} />
                </div>
              </div>
            </div>
          ) : (
            <div style={{
              padding: '60px 20px',
              textAlign: 'center',
              color: 'var(--text-muted)',
              fontSize: '0.875rem'
            }}>
              Configure parameters on the left and click "Embed Watermark" to evaluate audio fidelity and view side-by-side waveforms.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
