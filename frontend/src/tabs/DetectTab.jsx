import React, { useState, useEffect } from 'react';
import TamperTimeline from '../components/TamperTimeline';
import WaveformViewer from '../components/WaveformViewer';

export default function DetectTab({ apiBase, session, samples = [] }) {
  // If no session exists yet, default directly to custom upload
  const [sourceType, setSourceType] = useState(session ? 'session_watermarked' : 'custom');
  const [customFile, setCustomFile] = useState(null);
  const [selectedSample, setSelectedSample] = useState('');
  const [filePreviewUrl, setFilePreviewUrl] = useState(null);
  const [keySeed, setKeySeed] = useState(session?.key_seed || 12345);
  const [watermarkLen, setWatermarkLen] = useState(session?.watermark_len || 45);
  const [alpha, setAlpha] = useState(session?.alpha || 0.05);
  const [mode, setMode] = useState(session?.mode || 'SVD');
  const [loading, setLoading] = useState(false);
  const [detectionResult, setDetectionResult] = useState(null);
  const [error, setError] = useState(null);

  // Sync state when session becomes available
  useEffect(() => {
    if (session) {
      if (sourceType !== 'custom') {
        setSourceType('session_watermarked');
      }
      if (session.key_seed) setKeySeed(session.key_seed);
      if (session.watermark_len) setWatermarkLen(session.watermark_len);
      if (session.alpha) setAlpha(session.alpha);
      if (session.mode) setMode(session.mode);
    }
  }, [session]);

  // Manage object URL for file preview
  useEffect(() => {
    if (customFile) {
      const url = URL.createObjectURL(customFile);
      setFilePreviewUrl(url);
      return () => URL.revokeObjectURL(url);
    } else {
      setFilePreviewUrl(null);
    }
  }, [customFile]);

  const handleDetect = async () => {
    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('key_seed', keySeed.toString());
      formData.append('watermark_len', watermarkLen.toString());
      formData.append('alpha', alpha.toString());
      formData.append('mode', mode);

      if (sourceType === 'custom') {
        if (customFile) {
          formData.append('file', customFile);
        } else if (selectedSample) {
          formData.append('sample_id', selectedSample);
        } else {
          throw new Error('Please select an audio file to upload or choose a preset sample.');
        }

        // If an active session exists, include session_id so server can cross-reference registered metadata
        if (session && session.session_id) {
          formData.append('session_id', session.session_id);
        }
      } else if (session && session.session_id) {
        formData.append('session_id', session.session_id);
        formData.append('use_attacked', sourceType === 'session_attacked' ? 'true' : 'false');
      } else {
        throw new Error('No active session available. Please upload an audio file or select a sample.');
      }

      const res = await fetch(`${apiBase}/api/detect`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Detection error (Status ${res.status})`);
      }

      const data = await res.json();
      setDetectionResult(data);
    } catch (err) {
      setError(err.message || 'Authenticity detection failed.');
    } finally {
      setLoading(false);
    }
  };

  const isButtonDisabled = () => {
    if (loading) return true;
    if (sourceType === 'custom') {
      return !customFile && !selectedSample;
    }
    return !session;
  };

  return (
    <div className="tab-content">
      <div className="grid-2">
        {/* Left Column: Detector Configuration */}
        <div className="card">
          <h2 className="card-title">1. Detection &amp; Verification Setup</h2>

          <div className="form-group">
            <label className="form-label">Audio Candidate to Authenticate</label>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <label
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  fontSize: '0.875rem',
                  cursor: session ? 'pointer' : 'not-allowed',
                  opacity: session ? 1 : 0.6,
                }}
              >
                <input
                  type="radio"
                  name="sourceType"
                  value="session_watermarked"
                  checked={sourceType === 'session_watermarked'}
                  onChange={(e) => setSourceType(e.target.value)}
                  disabled={!session}
                />
                <span>Active Watermarked Audio (From Session Tab 1)</span>
              </label>

              <label
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  fontSize: '0.875rem',
                  cursor: session && session.attacked_signal ? 'pointer' : 'not-allowed',
                  opacity: session ? 1 : 0.6,
                }}
              >
                <input
                  type="radio"
                  name="sourceType"
                  value="session_attacked"
                  checked={sourceType === 'session_attacked'}
                  onChange={(e) => setSourceType(e.target.value)}
                  disabled={!session}
                />
                <span>Distorted / Attacked Audio (From Session Tab 2)</span>
              </label>

              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.875rem', cursor: 'pointer' }}>
                <input
                  type="radio"
                  name="sourceType"
                  value="custom"
                  checked={sourceType === 'custom'}
                  onChange={(e) => setSourceType(e.target.value)}
                />
                <span style={{ fontWeight: 600 }}>Upload External / Suspect Audio (e.g., Deepfake or WAV)</span>
              </label>
            </div>
          </div>

          {/* Custom File or Preset Sample Section */}
          {sourceType === 'custom' && (
            <div style={{ background: 'var(--bg-surface-alt)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '14px', marginBottom: '16px' }}>
              {/* Preset Sample Picker */}
              {samples.length > 0 && (
                <div className="form-group" style={{ marginBottom: '12px' }}>
                  <label className="form-label">
                    <span>Quick Select Sample Audio</span>
                    <span style={{ color: 'var(--text-subtle)' }}>Preset Fixtures</span>
                  </label>
                  <select
                    className="form-select"
                    value={selectedSample}
                    onChange={(e) => {
                      setSelectedSample(e.target.value);
                      setCustomFile(null);
                    }}
                  >
                    <option value="">-- Choose a test sample --</option>
                    {samples.map((s) => (
                      <option key={s.id} value={s.id}>
                        {s.name} ({s.duration}s)
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* File Uploader */}
              <div className="form-group" style={{ marginBottom: 0 }}>
                <div className="form-label">
                  <span>Upload Local Audio (WAV / MP3 / FLAC)</span>
                  {customFile && (
                    <span
                      style={{ color: 'var(--danger)', cursor: 'pointer', fontWeight: 600 }}
                      onClick={() => setCustomFile(null)}
                    >
                      Remove File
                    </span>
                  )}
                </div>
                <input
                  type="file"
                  accept=".wav,.flac,.mp3,audio/*"
                  className="form-input"
                  onChange={(e) => {
                    if (e.target.files && e.target.files[0]) {
                      setCustomFile(e.target.files[0]);
                      setSelectedSample('');
                    }
                  }}
                />

                {/* Selected File Details & Audio Preview */}
                {customFile && (
                  <div style={{ marginTop: '10px' }}>
                    <div style={{ fontSize: '0.8125rem', color: 'var(--text-main)', fontWeight: 500 }}>
                      Selected: {customFile.name} ({(customFile.size / 1024).toFixed(1)} KB)
                    </div>
                    {filePreviewUrl && (
                      <div className="audio-player-wrapper" style={{ marginTop: '6px' }}>
                        <audio controls src={filePreviewUrl} style={{ width: '100%', height: '34px' }} />
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Verification Parameters */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginTop: '12px' }}>
            <div className="form-group">
              <label className="form-label">Registered Key / Seed</label>
              <input
                type="number"
                className="form-input"
                value={keySeed}
                onChange={(e) => setKeySeed(parseInt(e.target.value) || 0)}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Watermark Length</label>
              <input
                type="number"
                className="form-input"
                value={watermarkLen}
                onChange={(e) => setWatermarkLen(parseInt(e.target.value) || 32)}
              />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div className="form-group">
              <label className="form-label">Watermarking Mode</label>
              <select className="form-select" value={mode} onChange={(e) => setMode(e.target.value)}>
                <option value="SVD">SVD (Orthonormal Projection)</option>
                <option value="QIM">QIM (Quantization Modulation)</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Embedding Alpha</label>
              <input
                type="number"
                step="0.01"
                min="0.01"
                max="0.5"
                className="form-input"
                value={alpha}
                onChange={(e) => setAlpha(parseFloat(e.target.value) || 0.05)}
              />
            </div>
          </div>

          <button
            className="btn btn-primary"
            style={{ width: '100%', marginTop: '14px' }}
            onClick={handleDetect}
            disabled={isButtonDisabled()}
          >
            {loading ? 'Evaluating Integrity & Wavelet Correlation...' : 'Run Authenticity & Deepfake Detection'}
          </button>

          {error && (
            <div style={{ marginTop: '12px', padding: '10px', background: 'var(--danger-bg)', border: '1px solid var(--danger-border)', borderRadius: '6px', color: 'var(--danger)', fontSize: '0.8125rem' }}>
              {error}
            </div>
          )}
        </div>

        {/* Right Column: Verdict Card & Tamper Timeline */}
        <div className="card">
          <h2 className="card-title">2. Authenticity Verdict &amp; Tamper Localization</h2>

          {detectionResult ? (
            <div>
              {/* Verdict Banner */}
              <div
                className={`verdict-banner ${
                  detectionResult.verdict === 'AUTHENTIC_WATERMARKED'
                    ? 'verdict-authentic'
                    : detectionResult.verdict === 'TAMPERED_AUDIO'
                    ? 'verdict-tampered'
                    : 'verdict-fake'
                }`}
              >
                <div>
                  <div style={{ fontSize: '1.15rem', fontWeight: 700, letterSpacing: '0.01em' }}>
                    {detectionResult.verdict === 'AUTHENTIC_WATERMARKED' && 'AUTHENTIC WATERMARKED AUDIO'}
                    {detectionResult.verdict === 'TAMPERED_AUDIO' && 'TAMPERED AUDIO DETECTED'}
                    {detectionResult.verdict === 'AI_GENERATED_OR_UNWATERMARKED' && 'AI-GENERATED / UNWATERMARKED AUDIO'}
                  </div>
                  <div style={{ fontSize: '0.8125rem', opacity: 0.9, marginTop: '3px' }}>
                    {detectionResult.verdict === 'AUTHENTIC_WATERMARKED' && 'Cryptographic watermark matches registered signature. Audio integrity certified.'}
                    {detectionResult.verdict === 'TAMPERED_AUDIO' && 'Watermark detected but localized regions exhibit high BER indicating partial tampering.'}
                    {detectionResult.verdict === 'AI_GENERATED_OR_UNWATERMARKED' && 'No valid watermark detected (BER ~ 0.50). Flagged as unauthorized or synthetic voice.'}
                  </div>
                </div>

                <div
                  className="verdict-badge"
                  style={{
                    backgroundColor:
                      detectionResult.verdict === 'AUTHENTIC_WATERMARKED'
                        ? '#10b981'
                        : detectionResult.verdict === 'TAMPERED_AUDIO'
                        ? '#f59e0b'
                        : '#ef4444',
                    color: '#ffffff'
                  }}
                >
                  {(detectionResult.confidence * 100).toFixed(1)}% Conf
                </div>
              </div>

              {/* Confidence Meter Bar */}
              <div style={{ marginBottom: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
                  <span>Authenticity Confidence Score</span>
                  <span style={{ fontWeight: 600 }}>{(detectionResult.confidence * 100).toFixed(1)}%</span>
                </div>
                <div style={{ height: '8px', background: 'var(--bg-surface-alt)', borderRadius: '4px', overflow: 'hidden' }}>
                  <div
                    style={{
                      height: '100%',
                      width: `${(detectionResult.confidence * 100).toFixed(1)}%`,
                      backgroundColor:
                        detectionResult.confidence >= 0.8
                          ? 'var(--success)'
                          : detectionResult.confidence >= 0.4
                          ? 'var(--warning)'
                          : 'var(--danger)',
                      transition: 'width 0.4s ease'
                    }}
                  />
                </div>
              </div>

              {/* Diagnostics Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px' }}>
                <div className="metric-box">
                  <div className="metric-label">Extracted BER</div>
                  <div className="metric-value">{detectionResult.ber}</div>
                  <div className="metric-desc">Authentic: &le; 0.15 | Fake: ~0.50</div>
                </div>
                <div className="metric-box">
                  <div className="metric-label">Extracted NCC</div>
                  <div className="metric-value">{detectionResult.ncc}</div>
                  <div className="metric-desc">Authentic: ~1.00 | Fake: ~0.00</div>
                </div>
              </div>

              {/* Waveform & Audio Player of the Evaluated Audio */}
              {detectionResult.waveform && (
                <div style={{ marginBottom: '16px' }}>
                  <WaveformViewer
                    points={detectionResult.waveform}
                    color={detectionResult.is_authentic ? '#10b981' : '#ef4444'}
                    label={`Evaluated Signal (${detectionResult.verdict.replace(/_/g, ' ')})`}
                    duration={detectionResult.duration}
                  />
                  {detectionResult.audio_url && (
                    <div className="audio-player-wrapper">
                      <audio controls src={detectionResult.audio_url} />
                    </div>
                  )}
                </div>
              )}

              {/* Tamper Timeline */}
              <TamperTimeline
                segments={detectionResult.tamper_segments}
                totalDuration={detectionResult.duration}
              />
            </div>
          ) : (
            <div style={{
              padding: '60px 20px',
              textAlign: 'center',
              color: 'var(--text-muted)',
              fontSize: '0.875rem'
            }}>
              Select or upload suspect audio and click "Run Authenticity &amp; Deepfake Detection" to view the security verdict, confidence percentage, and temporal tamper segmentation.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
