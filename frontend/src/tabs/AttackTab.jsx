import React, { useState } from 'react';
import {
  Flame,
  ShieldAlert,
  Zap,
  Activity,
  AlertCircle,
  Radio,
  SlidersHorizontal,
} from 'lucide-react';
import WaveformViewer from '../components/WaveformViewer';
import BitMapViewer from '../components/BitMapViewer';

export default function AttackTab({ apiBase, session }) {
  const [attackType, setAttackType] = useState('awgn');
  const [awgnSnr, setAwgnSnr] = useState(20);
  const [mp3Bitrate, setMp3Bitrate] = useState(64);
  const [lowpassCutoff, setLowpassCutoff] = useState(4000);
  const [highpassCutoff, setHighpassCutoff] = useState(300);
  const [scaleFactor, setScaleFactor] = useState(0.8);
  const [cropRatio, setCropRatio] = useState(0.1);
  const [cropLocation, setCropLocation] = useState('middle');
  const [vocoderJitter, setVocoderJitter] = useState(0.03);

  const [loading, setLoading] = useState(false);
  const [attackResult, setAttackResult] = useState(null);
  const [error, setError] = useState(null);

  const handleRunAttack = async () => {
    if (!session || !session.session_id) {
      setError('Please embed a watermark in the "Embed & Fidelity" tab first.');
      return;
    }

    setLoading(true);
    setError(null);

    // Build params JSON
    const params = {};
    if (attackType === 'awgn') params.snr_db = awgnSnr;
    else if (attackType === 'mp3') params.bitrate = mp3Bitrate;
    else if (attackType === 'lowpass') params.cutoff = lowpassCutoff;
    else if (attackType === 'highpass') params.cutoff = highpassCutoff;
    else if (attackType === 'bandpass') {
      params.lowcut = 300;
      params.highcut = 3400;
    } else if (attackType === 'resample') params.target_sr = 8000;
    else if (attackType === 'scale') params.factor = scaleFactor;
    else if (attackType === 'crop') {
      params.crop_ratio = cropRatio;
      params.location = cropLocation;
    } else if (attackType === 'vocoder') params.noise_level = vocoderJitter;

    try {
      const formData = new FormData();
      formData.append('session_id', session.session_id);
      formData.append('attack_type', attackType);
      formData.append('params', JSON.stringify(params));

      const res = await fetch(`${apiBase}/api/attack`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Attack error: ${res.status}`);
      }

      const data = await res.json();
      setAttackResult(data);
    } catch (err) {
      setError(err.message || 'Attack simulation failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="tab-content">
      <div className="grid-2">
        {/* Left Column: Attack Selector & Controls in Bento Card */}
        <div className="bento-card">
          <h2 className="card-title">
            <span className="card-title-icon">
              <Flame size={18} style={{ color: 'var(--warning)' }} />
              1. DeepMark Acoustic Stress Test Suite
            </span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', fontWeight: 500 }}>
              Adversarial Attacks
            </span>
          </h2>

          {!session && (
            <div
              style={{
                marginBottom: '16px',
                padding: '12px',
                background: 'var(--warning-bg)',
                border: '1px solid var(--warning-border)',
                borderRadius: '8px',
                fontSize: '0.8125rem',
                color: 'var(--warning)',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              <AlertCircle size={16} />
              <span>Note: Active watermark session required. Please embed in Tab 1 first.</span>
            </div>
          )}

          <div className="form-group">
            <label className="form-label">
              <span>Select Attack Distortion Type</span>
              <span style={{ color: 'var(--text-subtle)' }}>IEEE Suite</span>
            </label>
            <select
              className="form-select"
              value={attackType}
              onChange={(e) => setAttackType(e.target.value)}
            >
              <option value="awgn">Additive White Gaussian Noise (AWGN)</option>
              <option value="mp3">Lossy MP3 Compression (Perceptual Coding)</option>
              <option value="lowpass">Butterworth Lowpass Filter (Spectral Attenuation)</option>
              <option value="highpass">Butterworth Highpass Filter</option>
              <option value="bandpass">Telephony Bandpass Filter (300 - 3400 Hz)</option>
              <option value="resample">Resampling Attack (16 kHz -&gt; 8 kHz -&gt; 16 kHz)</option>
              <option value="scale">Amplitude / Gain Dynamic Scaling</option>
              <option value="crop">Time-Domain Cropping / Zero-out Packet Loss</option>
              <option value="vocoder">Neural Vocoder Re-synthesis Perturbation</option>
            </select>
          </div>

          {/* Dynamic Attack Parameter Sliders */}
          {attackType === 'awgn' && (
            <div className="form-group">
              <div className="form-label">
                <span>Signal-to-Noise Ratio (SNR)</span>
                <span
                  style={{
                    fontFamily: 'var(--font-mono)',
                    fontWeight: 700,
                    color: 'var(--warning)',
                    background: 'rgba(245, 158, 11, 0.1)',
                    padding: '2px 8px',
                    borderRadius: '6px',
                  }}
                >
                  {awgnSnr} dB
                </span>
              </div>
              <input
                type="range"
                min="0"
                max="40"
                step="5"
                value={awgnSnr}
                className="range-slider"
                onChange={(e) => setAwgnSnr(parseInt(e.target.value))}
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
                <span>0 dB (Extreme Distortion)</span>
                <span>20 dB (Standard Noise)</span>
                <span>40 dB (Subtle Ambient)</span>
              </div>
            </div>
          )}

          {attackType === 'mp3' && (
            <div className="form-group">
              <label className="form-label">Target Lossy Bitrate</label>
              <select
                className="form-select"
                value={mp3Bitrate}
                onChange={(e) => setMp3Bitrate(parseInt(e.target.value))}
              >
                <option value="32">32 kbps (Extreme Mobile Compression)</option>
                <option value="64">64 kbps (Standard Mobile Quality)</option>
                <option value="128">128 kbps (Standard Streaming Quality)</option>
                <option value="192">192 kbps (High Quality)</option>
                <option value="256">256 kbps</option>
                <option value="320">320 kbps (Transparent Near-Lossless)</option>
              </select>
            </div>
          )}

          {attackType === 'lowpass' && (
            <div className="form-group">
              <div className="form-label">
                <span>Lowpass Cutoff Frequency</span>
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
                  {lowpassCutoff} Hz
                </span>
              </div>
              <input
                type="range"
                min="1000"
                max="7500"
                step="500"
                value={lowpassCutoff}
                className="range-slider"
                onChange={(e) => setLowpassCutoff(parseInt(e.target.value))}
              />
            </div>
          )}

          {attackType === 'highpass' && (
            <div className="form-group">
              <div className="form-label">
                <span>Highpass Cutoff Frequency</span>
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
                  {highpassCutoff} Hz
                </span>
              </div>
              <input
                type="range"
                min="100"
                max="1000"
                step="50"
                value={highpassCutoff}
                className="range-slider"
                onChange={(e) => setHighpassCutoff(parseInt(e.target.value))}
              />
            </div>
          )}

          {attackType === 'scale' && (
            <div className="form-group">
              <div className="form-label">
                <span>Gain Scaling Factor</span>
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
                  {scaleFactor.toFixed(2)}x
                </span>
              </div>
              <input
                type="range"
                min="0.5"
                max="1.5"
                step="0.05"
                value={scaleFactor}
                className="range-slider"
                onChange={(e) => setScaleFactor(parseFloat(e.target.value))}
              />
            </div>
          )}

          {attackType === 'crop' && (
            <>
              <div className="form-group">
                <div className="form-label">
                  <span>Zero-Out Cropping Ratio</span>
                  <span
                    style={{
                      fontFamily: 'var(--font-mono)',
                      fontWeight: 700,
                      color: 'var(--danger)',
                      background: 'rgba(239, 68, 68, 0.1)',
                      padding: '2px 8px',
                      borderRadius: '6px',
                    }}
                  >
                    {(cropRatio * 100).toFixed(0)}%
                  </span>
                </div>
                <input
                  type="range"
                  min="0.05"
                  max="0.50"
                  step="0.05"
                  value={cropRatio}
                  className="range-slider"
                  onChange={(e) => setCropRatio(parseFloat(e.target.value))}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Temporal Segment Location</label>
                <select
                  className="form-select"
                  value={cropLocation}
                  onChange={(e) => setCropLocation(e.target.value)}
                >
                  <option value="start">Beginning of signal</option>
                  <option value="middle">Center speech segment</option>
                  <option value="end">End of audio file</option>
                </select>
              </div>
            </>
          )}

          {attackType === 'vocoder' && (
            <div className="form-group">
              <div className="form-label">
                <span>Phase Jitter Perturbation</span>
                <span
                  style={{
                    fontFamily: 'var(--font-mono)',
                    fontWeight: 700,
                    color: 'var(--accent-purple)',
                    background: 'rgba(168, 85, 247, 0.1)',
                    padding: '2px 8px',
                    borderRadius: '6px',
                  }}
                >
                  {vocoderJitter.toFixed(3)}
                </span>
              </div>
              <input
                type="range"
                min="0.01"
                max="0.10"
                step="0.005"
                value={vocoderJitter}
                className="range-slider"
                onChange={(e) => setVocoderJitter(parseFloat(e.target.value))}
              />
            </div>
          )}

          <button
            className="btn btn-shimmer"
            style={{ width: '100%', marginTop: '10px' }}
            onClick={handleRunAttack}
            disabled={loading || !session}
          >
            <Zap size={16} />
            <span>{loading ? 'Simulating Attack & Extracting...' : 'Apply Attack & Verify Robustness'}</span>
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

        {/* Right Column: Robustness Metrics & Bit Map in Bento Card */}
        <div className="bento-card">
          <h2 className="card-title">
            <span className="card-title-icon">
              <ShieldAlert size={18} style={{ color: 'var(--accent-cyan)' }} />
              2. Watermark Recovery &amp; Bit Accuracy
            </span>
            {attackResult && (
              <span
                style={{
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  color: attackResult.ber <= 0.15 ? 'var(--success)' : 'var(--warning)',
                  background: attackResult.ber <= 0.15 ? 'var(--success-bg)' : 'var(--warning-bg)',
                  border: `1px solid ${attackResult.ber <= 0.15 ? 'var(--success-border)' : 'var(--warning-border)'}`,
                  padding: '2px 8px',
                  borderRadius: '9999px',
                }}
              >
                {attackResult.ber <= 0.15 ? 'AUTHENTIC CERTIFIED' : 'DEGRADED / TAMPERED'}
              </span>
            )}
          </h2>

          {attackResult ? (
            <div>
              {/* Metric Boxes with Top Accents */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px' }}>
                <div className="metric-box">
                  <div className="metric-box-accent" />
                  <div className="metric-label">Bit Error Rate (BER)</div>
                  <div
                    className="metric-value"
                    style={{
                      color:
                        attackResult.ber <= 0.15
                          ? 'var(--success)'
                          : attackResult.ber <= 0.35
                          ? 'var(--warning)'
                          : 'var(--danger)',
                    }}
                  >
                    {attackResult.ber}
                  </div>
                  <div className="metric-desc">
                    {attackResult.ber <= 0.15
                      ? 'Target <= 0.15 met (Intact)'
                      : 'Elevated bit errors from attack'}
                  </div>
                </div>

                <div className="metric-box">
                  <div className="metric-box-accent" />
                  <div className="metric-label">Normalized Corr. (NCC)</div>
                  <div
                    className="metric-value"
                    style={{
                      color: attackResult.ncc >= 0.7 ? 'var(--success)' : 'var(--warning)',
                    }}
                  >
                    {attackResult.ncc}
                  </div>
                  <div className="metric-desc">Target &gt;= 0.70 under attack</div>
                </div>
              </div>

              {/* Bit Comparison Map */}
              <div
                style={{
                  background: 'rgba(8, 12, 20, 0.7)',
                  border: '1px solid var(--border-glass)',
                  borderRadius: '12px',
                  padding: '16px',
                  marginBottom: '16px',
                }}
              >
                <BitMapViewer bits={attackResult.bit_comparison} />
              </div>

              {/* Attacked Audio Player & Waveform */}
              <WaveformViewer
                points={attackResult.waveform_attacked}
                color="#f59e0b"
                label={`Distorted Signal (${attackResult.attack_type.toUpperCase()})`}
                duration={attackResult.duration}
              />
              <div className="audio-player-wrapper">
                <audio controls src={attackResult.attacked_audio} />
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
              <Activity size={32} style={{ color: 'var(--text-subtle)', margin: '0 auto 12px auto' }} />
              <div style={{ fontWeight: 600, color: 'var(--text-main)', marginBottom: '4px' }}>
                Awaiting Stress Test
              </div>
              <div>
                Choose an adversarial distortion scenario on the left and click{' '}
                <strong>"Apply Attack &amp; Verify Robustness"</strong> to inspect bit error rate and
                perceptual degradation.
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
