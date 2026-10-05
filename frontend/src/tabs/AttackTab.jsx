import React, { useState } from 'react';
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
        {/* Left Column: Attack Selector & Parameters */}
        <div className="card">
          <h2 className="card-title">1. Channel Distortion & Manipulation Attack</h2>

          {!session && (
            <div style={{ marginBottom: '14px', padding: '10px 14px', background: 'var(--warning-bg)', border: '1px solid var(--warning-border)', borderRadius: '6px', fontSize: '0.8125rem', color: 'var(--warning)' }}>
              Note: Watermark has not been embedded yet. Please embed first in Tab 1.
            </div>
          )}

          <div className="form-group">
            <label className="form-label">Attack Type (DeepMark Suite)</label>
            <select
              className="form-select"
              value={attackType}
              onChange={(e) => setAttackType(e.target.value)}
            >
              <option value="awgn">Additive White Gaussian Noise (AWGN)</option>
              <option value="mp3">Lossy Compression (MP3 Simulation)</option>
              <option value="lowpass">Butterworth Lowpass Filter</option>
              <option value="highpass">Butterworth Highpass Filter</option>
              <option value="bandpass">Telephony Bandpass Filter (300 - 3400 Hz)</option>
              <option value="resample">Resampling Attack (16 kHz -&gt; 8 kHz -&gt; 16 kHz)</option>
              <option value="scale">Amplitude / Gain Scaling</option>
              <option value="crop">Time-Domain Cropping / Packet Loss</option>
              <option value="vocoder">Neural Vocoder Re-synthesis Perturbation</option>
            </select>
          </div>

          {/* Dynamic Attack Controls */}
          {attackType === 'awgn' && (
            <div className="form-group">
              <div className="form-label">
                <span>Signal-to-Noise Ratio (SNR)</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{awgnSnr} dB</span>
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
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: 'var(--text-subtle)', marginTop: '2px' }}>
                <span>0 dB (Extreme Noise)</span>
                <span>20 dB (Moderate)</span>
                <span>40 dB (Light)</span>
              </div>
            </div>
          )}

          {attackType === 'mp3' && (
            <div className="form-group">
              <label className="form-label">Target Bitrate</label>
              <select
                className="form-select"
                value={mp3Bitrate}
                onChange={(e) => setMp3Bitrate(parseInt(e.target.value))}
              >
                <option value="32">32 kbps (Heavy Compression)</option>
                <option value="64">64 kbps (Standard Mobile)</option>
                <option value="128">128 kbps (Standard Streaming)</option>
                <option value="192">192 kbps (High Quality)</option>
                <option value="256">256 kbps</option>
                <option value="320">320 kbps (Near Lossless)</option>
              </select>
            </div>
          )}

          {attackType === 'lowpass' && (
            <div className="form-group">
              <div className="form-label">
                <span>Cutoff Frequency</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{lowpassCutoff} Hz</span>
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
                <span>Cutoff Frequency</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{highpassCutoff} Hz</span>
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
                <span>Scaling Factor</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{scaleFactor.toFixed(2)}x</span>
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
                  <span>Crop / Zero-out Ratio</span>
                  <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{(cropRatio * 100).toFixed(0)}%</span>
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
                <label className="form-label">Cropping Location</label>
                <select
                  className="form-select"
                  value={cropLocation}
                  onChange={(e) => setCropLocation(e.target.value)}
                >
                  <option value="start">Beginning of signal</option>
                  <option value="middle">Middle segment</option>
                  <option value="end">End of signal</option>
                </select>
              </div>
            </>
          )}

          {attackType === 'vocoder' && (
            <div className="form-group">
              <div className="form-label">
                <span>Phase Jitter Level</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{vocoderJitter.toFixed(3)}</span>
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
            className="btn btn-primary"
            style={{ width: '100%', marginTop: '12px' }}
            onClick={handleRunAttack}
            disabled={loading || !session}
          >
            {loading ? 'Simulating Attack & Extracting...' : 'Apply Attack & Verify Robustness'}
          </button>

          {error && (
            <div style={{ marginTop: '12px', padding: '10px', background: 'var(--danger-bg)', border: '1px solid var(--danger-border)', borderRadius: '6px', color: 'var(--danger)', fontSize: '0.8125rem' }}>
              {error}
            </div>
          )}
        </div>

        {/* Right Column: Robustness Metrics & Bit Map */}
        <div className="card">
          <h2 className="card-title">2. Watermark Recovery & Bit Comparison</h2>

          {attackResult ? (
            <div>
              {/* Metric Cards */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px' }}>
                <div className="metric-box">
                  <div className="metric-label">Bit Error Rate (BER)</div>
                  <div className="metric-value" style={{ color: attackResult.ber <= 0.15 ? 'var(--success)' : attackResult.ber <= 0.35 ? 'var(--warning)' : 'var(--danger)' }}>
                    {attackResult.ber}
                  </div>
                  <div className="metric-desc">Target &lt;= 0.15 for certified authenticity</div>
                </div>

                <div className="metric-box">
                  <div className="metric-label">Normalized Correlation (NCC)</div>
                  <div className="metric-value" style={{ color: attackResult.ncc >= 0.70 ? 'var(--success)' : 'var(--warning)' }}>
                    {attackResult.ncc}
                  </div>
                  <div className="metric-desc">Target &gt;= 0.70 under attack</div>
                </div>
              </div>

              {/* Bit Comparison Map */}
              <div style={{ background: 'var(--bg-surface-alt)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '14px', marginBottom: '16px' }}>
                <BitMapViewer bits={attackResult.bit_comparison} />
              </div>

              {/* Attacked Audio Player & Waveform */}
              <WaveformViewer
                points={attackResult.waveform_attacked}
                color="#f59e0b"
                label={`Distorted Audio (${attackResult.attack_type.toUpperCase()})`}
                duration={attackResult.duration}
              />
              <div className="audio-player-wrapper">
                <audio controls src={attackResult.attacked_audio} />
              </div>
            </div>
          ) : (
            <div style={{
              padding: '60px 20px',
              textAlign: 'center',
              color: 'var(--text-muted)',
              fontSize: '0.875rem'
            }}>
              Choose an attack scenario from the DeepMark suite and click "Apply Attack & Verify Robustness" to inspect BER, NCC, and bit error map.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
