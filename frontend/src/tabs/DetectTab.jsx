import React, { useState, useEffect } from 'react';
import {
  ScanLine,
  ShieldCheck,
  ShieldAlert,
  ShieldX,
  UploadCloud,
  CheckCircle2,
  AlertCircle,
  FileAudio,
  Radio,
  Sparkles,
} from 'lucide-react';
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
        {/* Left Column: Detector Configuration in Bento Card */}
        <div className="bento-card">
          <h2 className="card-title">
            <span className="card-title-icon">
              <ScanLine size={18} style={{ color: 'var(--accent-cyan)' }} />
              1. Detection &amp; Verification Protocol
            </span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', fontWeight: 500 }}>
              Proactive Attribution
            </span>
          </h2>

          <div className="form-group">
            <label className="form-label">
              <span>Candidate Audio Source</span>
              <span style={{ color: 'var(--text-subtle)' }}>Select Origin</span>
            </label>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  fontSize: '0.8125rem',
                  padding: '10px 12px',
                  borderRadius: '10px',
                  background: sourceType === 'session_watermarked' ? 'rgba(56, 189, 248, 0.08)' : 'rgba(255, 255, 255, 0.02)',
                  border: `1px solid ${sourceType === 'session_watermarked' ? 'var(--accent-cyan)' : 'var(--border-glass)'}`,
                  cursor: session ? 'pointer' : 'not-allowed',
                  opacity: session ? 1 : 0.5,
                  transition: 'all 0.2s ease',
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
                  gap: '10px',
                  fontSize: '0.8125rem',
                  padding: '10px 12px',
                  borderRadius: '10px',
                  background: sourceType === 'session_attacked' ? 'rgba(56, 189, 248, 0.08)' : 'rgba(255, 255, 255, 0.02)',
                  border: `1px solid ${sourceType === 'session_attacked' ? 'var(--accent-cyan)' : 'var(--border-glass)'}`,
                  cursor: session && session.attacked_signal ? 'pointer' : 'not-allowed',
                  opacity: session ? 1 : 0.5,
                  transition: 'all 0.2s ease',
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

              <label
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  fontSize: '0.8125rem',
                  padding: '10px 12px',
                  borderRadius: '10px',
                  background: sourceType === 'custom' ? 'rgba(56, 189, 248, 0.08)' : 'rgba(255, 255, 255, 0.02)',
                  border: `1px solid ${sourceType === 'custom' ? 'var(--accent-cyan)' : 'var(--border-glass)'}`,
                  cursor: 'pointer',
                  fontWeight: 600,
                  transition: 'all 0.2s ease',
                }}
              >
                <input
                  type="radio"
                  name="sourceType"
                  value="custom"
                  checked={sourceType === 'custom'}
                  onChange={(e) => setSourceType(e.target.value)}
                />
                <span>Upload External / Suspect Audio (e.g., Deepfake or WAV)</span>
              </label>
            </div>
          </div>

          {/* Custom File or Preset Sample Section */}
          {sourceType === 'custom' && (
            <div
              style={{
                background: 'rgba(8, 12, 20, 0.7)',
                border: '1px solid var(--border-glass)',
                borderRadius: '12px',
                padding: '16px',
                marginBottom: '16px',
              }}
            >
              {/* Preset Sample Picker */}
              {samples.length > 0 && (
                <div className="form-group" style={{ marginBottom: '14px' }}>
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

              {/* File Uploader Dropzone */}
              <div className="form-group" style={{ marginBottom: 0 }}>
                <div className="form-label">
                  <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                    <UploadCloud size={14} /> Upload Audio File
                  </span>
                  {customFile && (
                    <span
                      style={{ color: 'var(--danger)', cursor: 'pointer', fontWeight: 600 }}
                      onClick={() => setCustomFile(null)}
                    >
                      Remove File
                    </span>
                  )}
                </div>

                <div
                  className="dropzone-box"
                  style={{
                    padding: '18px',
                    borderColor: customFile ? 'var(--accent-cyan)' : undefined,
                    background: customFile ? 'rgba(56, 189, 248, 0.08)' : undefined,
                  }}
                  onClick={() => document.getElementById('detect-file-upload').click()}
                >
                  <input
                    id="detect-file-upload"
                    type="file"
                    accept=".wav,.flac,.mp3,audio/*"
                    style={{ display: 'none' }}
                    onChange={(e) => {
                      if (e.target.files && e.target.files[0]) {
                        setCustomFile(e.target.files[0]);
                        setSelectedSample('');
                      }
                    }}
                  />
                  <UploadCloud size={24} style={{ color: 'var(--accent-cyan)', margin: '0 auto 6px auto' }} />
                  <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-main)' }}>
                    {customFile ? customFile.name : 'Click to select or drag suspect audio file'}
                  </div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-subtle)', marginTop: '2px' }}>
                    {customFile
                      ? `${(customFile.size / 1024).toFixed(1)} KB loaded`
                      : 'Supports WAV, MP3, FLAC formats'}
                  </div>
                </div>

                {/* Selected File Details & Audio Preview */}
                {customFile && filePreviewUrl && (
                  <div className="audio-player-wrapper" style={{ marginTop: '10px' }}>
                    <audio controls src={filePreviewUrl} style={{ width: '100%', height: '34px' }} />
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Verification Parameters */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginTop: '14px' }}>
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
                <option value="SVD">SVD (Orthonormal)</option>
                <option value="QIM">QIM (Quantization)</option>
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
            className="btn btn-shimmer"
            style={{ width: '100%', marginTop: '10px' }}
            onClick={handleDetect}
            disabled={isButtonDisabled()}
          >
            <Sparkles size={16} />
            <span>
              {loading
                ? 'Evaluating Wavelet Integrity & Tampering...'
                : 'Run Authenticity & Deepfake Detection'}
            </span>
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

        {/* Right Column: Verdict Card & Tamper Timeline in Bento Card */}
        <div className="bento-card">
          <h2 className="card-title">
            <span className="card-title-icon">
              <ShieldCheck size={18} style={{ color: 'var(--accent-cyan)' }} />
              2. Security Verdict &amp; Tamper Localization
            </span>
            {detectionResult && (
              <span
                style={{
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  color: detectionResult.is_authentic ? 'var(--success)' : 'var(--danger)',
                  background: detectionResult.is_authentic ? 'var(--success-bg)' : 'var(--danger-bg)',
                  border: `1px solid ${detectionResult.is_authentic ? 'var(--success-border)' : 'var(--danger-border)'}`,
                  padding: '2px 8px',
                  borderRadius: '9999px',
                }}
              >
                {detectionResult.is_authentic ? 'VERIFIED AUTHENTIC' : 'UNAUTHENTIC / SUSPECT'}
              </span>
            )}
          </h2>

          {detectionResult ? (
            <div>
              {/* Aceternity Glowing Verdict Banner */}
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
                  <div
                    style={{
                      fontSize: '1.15rem',
                      fontWeight: 800,
                      letterSpacing: '-0.01em',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                    }}
                  >
                    {detectionResult.verdict === 'AUTHENTIC_WATERMARKED' && (
                      <>
                        <ShieldCheck size={20} style={{ color: 'var(--success)' }} />
                        <span>AUTHENTIC WATERMARKED AUDIO</span>
                      </>
                    )}
                    {detectionResult.verdict === 'TAMPERED_AUDIO' && (
                      <>
                        <ShieldAlert size={20} style={{ color: 'var(--warning)' }} />
                        <span>TAMPERED AUDIO DETECTED</span>
                      </>
                    )}
                    {detectionResult.verdict === 'AI_GENERATED_OR_UNWATERMARKED' && (
                      <>
                        <ShieldX size={20} style={{ color: 'var(--danger)' }} />
                        <span>AI-GENERATED / UNWATERMARKED AUDIO</span>
                      </>
                    )}
                  </div>
                  <div style={{ fontSize: '0.8125rem', opacity: 0.88, marginTop: '4px' }}>
                    {detectionResult.verdict === 'AUTHENTIC_WATERMARKED' &&
                      'Cryptographic watermark matches registered signature. Audio integrity certified.'}
                    {detectionResult.verdict === 'TAMPERED_AUDIO' &&
                      'Watermark detected but localized regions exhibit high BER indicating partial tampering.'}
                    {detectionResult.verdict === 'AI_GENERATED_OR_UNWATERMARKED' &&
                      'No valid watermark detected (BER ~ 0.50). Flagged as unauthorized or synthetic voice.'}
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
                    color: '#ffffff',
                    boxShadow:
                      detectionResult.verdict === 'AUTHENTIC_WATERMARKED'
                        ? '0 0 12px rgba(16, 185, 129, 0.5)'
                        : '0 0 12px rgba(239, 68, 68, 0.5)',
                  }}
                >
                  {(detectionResult.confidence * 100).toFixed(1)}% Conf
                </div>
              </div>

              {/* Confidence Meter Bar */}
              <div style={{ marginBottom: '16px' }}>
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    fontSize: '0.75rem',
                    color: 'var(--text-muted)',
                    marginBottom: '6px',
                  }}
                >
                  <span>Authenticity Confidence Score</span>
                  <span style={{ fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
                    {(detectionResult.confidence * 100).toFixed(1)}%
                  </span>
                </div>
                <div
                  style={{
                    height: '8px',
                    background: 'rgba(8, 12, 20, 0.7)',
                    borderRadius: '4px',
                    overflow: 'hidden',
                    border: '1px solid var(--border-glass)',
                  }}
                >
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
                      transition: 'width 0.4s ease',
                      boxShadow: '0 0 10px rgba(56, 189, 248, 0.5)',
                    }}
                  />
                </div>
              </div>

              {/* Diagnostics Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px' }}>
                <div className="metric-box">
                  <div className="metric-box-accent" />
                  <div className="metric-label">Extracted BER</div>
                  <div className="metric-value">{detectionResult.ber}</div>
                  <div className="metric-desc">Authentic: &le; 0.15 | Fake: ~0.50</div>
                </div>
                <div className="metric-box">
                  <div className="metric-box-accent" />
                  <div className="metric-label">Extracted NCC</div>
                  <div className="metric-value">{detectionResult.ncc}</div>
                  <div className="metric-desc">Authentic: ~1.00 | Fake: ~0.00</div>
                </div>
              </div>

              {/* Waveform & Audio Player of Evaluated Audio */}
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
              <ShieldCheck size={32} style={{ color: 'var(--text-subtle)', margin: '0 auto 12px auto' }} />
              <div style={{ fontWeight: 600, color: 'var(--text-main)', marginBottom: '4px' }}>
                Awaiting Verification Scan
              </div>
              <div>
                Select or upload candidate audio on the left and click{' '}
                <strong>"Run Authenticity &amp; Deepfake Detection"</strong> to examine cryptographic
                integrity and tamper localization.
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
