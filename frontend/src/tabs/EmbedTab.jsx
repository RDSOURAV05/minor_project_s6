import React, { useState, useEffect } from 'react';
import {
  Sliders,
  Sparkles,
  UploadCloud,
  Music,
  CheckCircle2,
  AlertCircle,
  KeyRound,
  Binary,
} from 'lucide-react';
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
        {/* Left Column: Input and Parameters in Bento Card */}
        <div className="bento-card">
          <h2 className="card-title">
            <span className="card-title-icon">
              <Sliders size={18} style={{ color: 'var(--accent-cyan)' }} />
              1. Audio Source &amp; Wavelet Parameters
            </span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', fontWeight: 500 }}>
              DWT-SVD Engine
            </span>
          </h2>

          {/* Sample Picker */}
          <div className="form-group">
            <label className="form-label">
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                <Music size={14} /> Academic Speech Preset
              </span>
              <span style={{ color: 'var(--text-subtle)' }}>16 kHz Mono Standard</span>
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

          {/* File Upload Dropzone Style */}
          <div className="form-group">
            <div className="form-label">
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                <UploadCloud size={14} /> Custom Audio Upload
              </span>
              {uploadFile && (
                <span
                  style={{ color: 'var(--danger)', cursor: 'pointer', fontWeight: 600 }}
                  onClick={() => setUploadFile(null)}
                >
                  Clear File
                </span>
              )}
            </div>

            <div
              className="dropzone-box"
              style={{
                borderColor: uploadFile ? 'var(--accent-cyan)' : undefined,
                background: uploadFile ? 'rgba(56, 189, 248, 0.08)' : undefined,
                padding: '16px',
              }}
              onClick={() => document.getElementById('audio-upload-input').click()}
            >
              <input
                id="audio-upload-input"
                type="file"
                accept=".wav,.flac,.mp3"
                style={{ display: 'none' }}
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    setUploadFile(e.target.files[0]);
                  }
                }}
              />
              <UploadCloud size={24} style={{ color: 'var(--accent-cyan)', margin: '0 auto 6px auto' }} />
              <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-main)' }}>
                {uploadFile ? uploadFile.name : 'Click to select or drag WAV / FLAC audio file'}
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-subtle)', marginTop: '2px' }}>
                {uploadFile
                  ? `${(uploadFile.size / 1024).toFixed(1)} KB loaded`
                  : 'Automatic resampling to 16 kHz mono'}
              </div>
            </div>
          </div>

          {/* Alpha Slider with glowing thumb */}
          <div className="form-group">
            <div className="form-label">
              <span>Watermark Strength Factor (&alpha;)</span>
              <span
                style={{
                  fontFamily: 'var(--font-mono)',
                  fontWeight: 700,
                  color: 'var(--accent-cyan)',
                  background: 'rgba(56, 189, 248, 0.1)',
                  padding: '2px 8px',
                  borderRadius: '6px',
                }}
              >
                {alpha.toFixed(3)}
              </span>
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
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                fontSize: '0.7rem',
                color: 'var(--text-subtle)',
                marginTop: '2px',
              }}
            >
              <span>0.01 (Transparent / High SNR)</span>
              <span>0.05 (DeepMark Recommended)</span>
              <span>0.20 (Robust / Heavy)</span>
            </div>
          </div>

          {/* Mode & Key Seed */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div className="form-group">
              <label className="form-label">
                <span>Transform Mode</span>
              </label>
              <select className="form-select" value={mode} onChange={(e) => setMode(e.target.value)}>
                <option value="SVD">SVD (Singular Vectors)</option>
                <option value="QIM">QIM (Quantization)</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">
                <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                  <KeyRound size={13} /> Crypto Seed
                </span>
              </label>
              <input
                type="number"
                className="form-input"
                value={keySeed}
                onChange={(e) => setKeySeed(parseInt(e.target.value) || 0)}
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                <Binary size={13} /> Payload Length (Bits)
              </span>
              <span style={{ color: 'var(--text-subtle)' }}>Pseudo-Random Binary Sequence</span>
            </label>
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
            className="btn btn-shimmer"
            style={{ width: '100%', marginTop: '6px' }}
            onClick={handleEmbed}
            disabled={loading}
          >
            <Sparkles size={16} />
            <span>{loading ? 'Embedding DWT-SVD Watermark...' : 'Embed Watermark'}</span>
          </button>

          {error && (
            <div
              style={{
                marginTop: '14px',
                padding: '12px',
                background: 'var(--danger-bg)',
                border: '1px solid var(--danger-border)',
                borderRadius: '8px',
                color: 'var(--danger)',
                fontSize: '0.8125rem',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          )}
        </div>

        {/* Right Column: Fidelity Results & Waveforms in Bento Card */}
        <div className="bento-card">
          <h2 className="card-title">
            <span className="card-title-icon">
              <Sparkles size={18} style={{ color: 'var(--success)' }} />
              2. Acoustic Fidelity &amp; Waveforms
            </span>
            {session && (
              <span
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  fontSize: '0.75rem',
                  color: 'var(--success)',
                  background: 'var(--success-bg)',
                  border: '1px solid var(--success-border)',
                  padding: '2px 8px',
                  borderRadius: '9999px',
                }}
              >
                <CheckCircle2 size={12} /> Active Session
              </span>
            )}
          </h2>

          {session ? (
            <div>
              {/* 2x2 Bento Metric Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px' }}>
                <div className="metric-box">
                  <div className="metric-box-accent" />
                  <div className="metric-label">Signal-to-Noise Ratio (SNR)</div>
                  <div className="metric-value">{session.snr} dB</div>
                  <div className="metric-desc">
                    {session.snr >= 35 ? 'Target > 35 dB (Imperceptible)' : 'Noticeable perturbation'}
                  </div>
                </div>

                <div className="metric-box">
                  <div className="metric-box-accent" />
                  <div className="metric-label">Peak SNR (PSNR)</div>
                  <div className="metric-value">{session.psnr} dB</div>
                  <div className="metric-desc">Target &gt; 50 dB (Near-Lossless)</div>
                </div>

                <div className="metric-box">
                  <div className="metric-box-accent" />
                  <div className="metric-label">Segmental SNR (SegSNR)</div>
                  <div className="metric-value">{session.seg_snr} dB</div>
                  <div className="metric-desc">Frame-level perceptual metric</div>
                </div>

                <div className="metric-box">
                  <div className="metric-box-accent" />
                  <div className="metric-label">Log-Spectral Dist. (LSD)</div>
                  <div className="metric-value">{session.lsd} dB</div>
                  <div className="metric-desc">Target &lt; 1.0 dB spectral diff</div>
                </div>
              </div>

              {/* Waveform Comparisons */}
              <WaveformViewer
                points={session.waveform_original}
                color="#38bdf8"
                label="Original Speech Signal"
                duration={session.duration}
              />
              <div className="audio-player-wrapper">
                <audio controls src={session.original_audio} />
              </div>

              <div style={{ marginTop: '16px' }}>
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
            <div
              style={{
                padding: '70px 20px',
                textAlign: 'center',
                color: 'var(--text-muted)',
                fontSize: '0.875rem',
                border: '1px dashed var(--border-glass)',
                borderRadius: '12px',
                marginTop: '10px',
              }}
            >
              <Music size={32} style={{ color: 'var(--text-subtle)', margin: '0 auto 12px auto' }} />
              <div style={{ fontWeight: 600, color: 'var(--text-main)', marginBottom: '4px' }}>
                Ready to Embed Watermark
              </div>
              <div>
                Configure parameters on the left and click <strong>"Embed Watermark"</strong> to compute
                audio fidelity metrics and render side-by-side wavelet spectrograms.
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
