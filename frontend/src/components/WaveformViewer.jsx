import React from 'react';

export default function WaveformViewer({ points = [], color = '#0284c7', label = 'Waveform', duration = 3.0 }) {
  if (!points || points.length === 0) {
    return (
      <div style={{
        height: '100px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'var(--bg-surface-alt)',
        borderRadius: '6px',
        color: 'var(--text-muted)',
        fontSize: '0.8125rem'
      }}>
        No waveform data available
      </div>
    );
  }

  const height = 90;
  const width = 600;
  const midY = height / 2;
  const maxAmp = Math.max(0.1, ...points.map(p => Math.abs(p)));
  const scaleY = (midY - 6) / maxAmp;
  const stepX = width / Math.max(1, points.length - 1);

  // Build SVG path
  let pathD = `M 0 ${midY}`;
  points.forEach((pt, idx) => {
    const x = idx * stepX;
    const y = midY - pt * scaleY;
    pathD += ` L ${x.toFixed(1)} ${y.toFixed(1)}`;
  });

  return (
    <div style={{ margin: '8px 0' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
        <span style={{ fontWeight: 600 }}>{label}</span>
        <span>{duration}s (16 kHz)</span>
      </div>
      <div style={{
        background: 'var(--bg-surface-alt)',
        border: '1px solid var(--border-color)',
        borderRadius: '6px',
        padding: '6px 8px',
        position: 'relative'
      }}>
        <svg viewBox={`0 0 ${width} ${height}`} style={{ width: '100%', height: '80px', display: 'block' }}>
          {/* Zero center line */}
          <line x1="0" y1={midY} x2={width} y2={midY} stroke="var(--border-subtle)" strokeDasharray="3 3" strokeWidth="1" />
          {/* Waveform line */}
          <path d={pathD} fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </div>
    </div>
  );
}
