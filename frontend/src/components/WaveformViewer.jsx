import React, { useId } from 'react';
import { Activity } from 'lucide-react';

export default function WaveformViewer({
  points = [],
  color = '#38bdf8',
  label = 'Signal Waveform',
  duration = 3.0,
}) {
  const gradientId = useId().replace(/:/g, '');

  if (!points || points.length === 0) {
    return (
      <div
        style={{
          height: '110px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '6px',
          background: 'rgba(15, 23, 42, 0.4)',
          borderRadius: '12px',
          border: '1px dashed var(--border-glass)',
          color: 'var(--text-subtle)',
          fontSize: '0.8125rem',
        }}
      >
        <Activity size={18} style={{ opacity: 0.5 }} />
        <span>No waveform data available</span>
      </div>
    );
  }

  const height = 96;
  const width = 640;
  const midY = height / 2;
  const maxAmp = Math.max(0.08, ...points.map((p) => Math.abs(p)));
  const scaleY = (midY - 8) / maxAmp;
  const stepX = width / Math.max(1, points.length - 1);

  // Line path
  let pathD = `M 0 ${midY}`;
  points.forEach((pt, idx) => {
    const x = idx * stepX;
    const y = midY - pt * scaleY;
    pathD += ` L ${x.toFixed(1)} ${y.toFixed(1)}`;
  });

  // Area path for gradient fill under the line
  let areaD = `M 0 ${midY}`;
  points.forEach((pt, idx) => {
    const x = idx * stepX;
    const y = midY - pt * scaleY;
    areaD += ` L ${x.toFixed(1)} ${y.toFixed(1)}`;
  });
  areaD += ` L ${width} ${midY} Z`;

  return (
    <div style={{ margin: '10px 0' }}>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontSize: '0.75rem',
          color: 'var(--text-muted)',
          marginBottom: '6px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 600 }}>
          <Activity size={13} style={{ color }} />
          <span style={{ color: 'var(--text-main)' }}>{label}</span>
        </div>
        <div style={{ display: 'flex', gap: '10px', fontFamily: 'var(--font-mono)' }}>
          <span>{duration}s</span>
          <span style={{ opacity: 0.6 }}>&bull; 16 kHz mono</span>
        </div>
      </div>

      <div
        style={{
          background: 'rgba(8, 12, 20, 0.7)',
          border: '1px solid var(--border-glass)',
          borderRadius: '12px',
          padding: '8px 12px',
          position: 'relative',
          boxShadow: 'inset 0 1px 8px rgba(0, 0, 0, 0.4)',
          overflow: 'hidden',
        }}
      >
        <svg
          viewBox={`0 0 ${width} ${height}`}
          style={{ width: '100%', height: '88px', display: 'block' }}
        >
          <defs>
            <linearGradient id={`grad-${gradientId}`} x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor={color} stopOpacity="0.35" />
              <stop offset="50%" stopColor={color} stopOpacity="0.08" />
              <stop offset="100%" stopColor={color} stopOpacity="0.0" />
            </linearGradient>
            <filter id={`glow-${gradientId}`} x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="2" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* Grid reference guide */}
          <line
            x1="0"
            y1={midY}
            x2={width}
            y2={midY}
            stroke="var(--border-glass)"
            strokeDasharray="4 4"
            strokeWidth="1"
          />

          {/* Gradient area under waveform */}
          <path d={areaD} fill={`url(#grad-${gradientId})`} />

          {/* Waveform line with glowing stroke */}
          <path
            d={pathD}
            fill="none"
            stroke={color}
            strokeWidth="1.75"
            strokeLinecap="round"
            strokeLinejoin="round"
            filter={`url(#glow-${gradientId})`}
          />
        </svg>
      </div>
    </div>
  );
}
