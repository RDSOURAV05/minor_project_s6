import React from 'react';
import { Binary, CheckCircle2, AlertTriangle } from 'lucide-react';

export default function BitMapViewer({ bits = [] }) {
  if (!bits || bits.length === 0) {
    return (
      <div style={{ color: 'var(--text-muted)', fontSize: '0.8125rem', padding: '12px 0' }}>
        No bit comparison data available yet.
      </div>
    );
  }

  const matches = bits.filter((b) => b.match).length;
  const errors = bits.length - matches;
  const accuracy = ((matches / bits.length) * 100).toFixed(1);

  return (
    <div>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '10px',
          fontSize: '0.8125rem',
          flexWrap: 'wrap',
          gap: '8px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              color: 'var(--success)',
              fontWeight: 600,
            }}
          >
            <CheckCircle2 size={14} /> Matched: {matches}
          </span>
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              color: errors > 0 ? 'var(--danger)' : 'var(--text-muted)',
              fontWeight: 600,
            }}
          >
            <AlertTriangle size={14} /> Errors: {errors}
          </span>
          <span style={{ color: 'var(--text-muted)', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
            <Binary size={13} /> {bits.length} bits
          </span>
        </div>

        <div
          style={{
            fontWeight: 700,
            fontSize: '0.8125rem',
            color: 'var(--text-main)',
            background: 'rgba(255, 255, 255, 0.05)',
            padding: '3px 10px',
            borderRadius: '9999px',
            border: '1px solid var(--border-glass)',
          }}
        >
          Bit Recovery: <span style={{ color: 'var(--accent-cyan)' }}>{accuracy}%</span>
        </div>
      </div>

      <div className="bit-matrix">
        {bits.map((b) => (
          <div
            key={b.index}
            className={`bit-chip ${b.match ? 'bit-chip-match' : 'bit-chip-error'}`}
            title={`Bit #${b.index}\nOriginal: ${b.original}\nExtracted: ${b.extracted}\nStatus: ${b.match ? 'MATCH' : 'ERROR'}`}
          >
            {b.extracted}
          </div>
        ))}
      </div>

      <div
        style={{
          fontSize: '0.72rem',
          color: 'var(--text-subtle)',
          marginTop: '8px',
          display: 'flex',
          justifyContent: 'space-between',
        }}
      >
        <span>Green = Exact bit recovery &bull; Red = Channel distortion</span>
        <span>Hover chip for bit index &amp; verification details</span>
      </div>
    </div>
  );
}
