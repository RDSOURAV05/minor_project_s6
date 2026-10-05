import React, { useState } from 'react';
import TamperTimeline from '../components/TamperTimeline';

export default function DetectTab({ apiBase, session }) {
  const [sourceType, setSourceType] = useState('session_watermarked');
  const [customFile, setCustomFile] = useState(null);
  const [keySeed, setKeySeed] = useState(12345);
  const [watermarkLen, setWatermarkLen] = useState(45);
  const [loading, setLoading] = useState(false);
  const [detectionResult, setDetectionResult] = useState(null);
  const [error, setError] = useState(null);

  const handleDetect = async () => {
    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('key_seed', keySeed.toString());
      formData.append('watermark_len', watermarkLen.toString());

      if (sourceType === 'custom' && customFile) {
        formData.append('file', customFile);
      } else if (session && session.session_id) {
        formData.append('session_id', session.session_id);
        formData.append('use_attacked', sourceType === 'session_attacked' ? 'true' : 'false');
      } else {
        throw new Error('Please select an active session audio or upload an audio file.');
      }

      const res = await fetch(`${apiBase}/api/detect`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Detection error: ${res.status}`);
      }

      const data = await res.json();
      setDetectionResult(data);
    } catch (err) {
      setError(err.message || 'Authenticity detection failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="tab-content">
      <div className="grid-2">
        {/* Left Column: Detector Configuration */}
        <div className="card">
          <h2 className="card-title">1. Detection & Verification Setup</h2>

          <div className="form-group">
            <label className="form-label">Audio Candidate to Authenticate</label>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.875rem', cursor: 'pointer' }}>
                <input
                  type="radio"
                  name="sourceType"
                  value="session_watermarked"
                  checked={sourceType === 'session_watermarked'}
                  onChange={(e) => setSourceType(e.target.value)}
                  disabled={!session}
                />
                <span>Active Watermarked Audio (Session)</span>
              </label>

              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.875rem', cursor: 'pointer' }}>
                <input
                  type="radio"
                  name="sourceType"
                  value="session_attacked"
                  checked={sourceType === 'session_attacked'}
                  onChange={(e) => setSourceType(e.target.value)}
                  disabled={!session}
                />
                <span>Distorted / Attacked Audio (Session)</span>
              </label>

              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.875rem', cursor: 'pointer' }}>
                <input
                  type="radio"
                  name="sourceType"
                  value="custom"
                  checked={sourceType === 'custom'}
                  onChange={(e) => setSourceType(e.target.value)}
                />
                <span>Upload External / Suspect Audio (e.g., Unwatermarked Deepfake)</span>
              </label>
            </div>
          </div>

          {sourceType === 'custom' && (
            <div className="form-group">
              <label className="form-label">Upload WAV / MP3</label>
              <input
                type="file"
                accept=".wav,.flac,.mp3"
                className="form-input"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    setCustomFile(e.target.files[0]);
                  }
                }}
              />
            </div>
          )}

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

          <button
            className="btn btn-primary"
            style={{ width: '100%', marginTop: '14px' }}
            onClick={handleDetect}
            disabled={loading || (sourceType === 'custom' && !customFile) || (sourceType !== 'custom' && !session)}
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
          <h2 className="card-title">2. Authenticity Verdict & Tamper Localization</h2>

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
                  <div className="metric-desc">Authentic: &lt; 0.15 | Fake: ~0.50</div>
                </div>
                <div className="metric-box">
                  <div className="metric-label">Extracted NCC</div>
                  <div className="metric-value">{detectionResult.ncc}</div>
                  <div className="metric-desc">Authentic: ~1.00 | Fake: ~0.00</div>
                </div>
              </div>

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
              Select candidate audio and click "Run Authenticity & Deepfake Detection" to view the security verdict, confidence percentage, and temporal tamper segmentation.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
