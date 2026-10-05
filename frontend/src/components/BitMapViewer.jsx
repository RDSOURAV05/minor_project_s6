import React from 'react';

export default function BitMapViewer({ bits = [] }) {
  if (!bits || bits.length === 0) {
    return <div style={{ color: 'var(--text-muted)', fontSize: '0.8125rem' }}>No bit comparison data yet.</div>;
  }

  const matches = bits.filter(b => b.match).length;
  const errors = bits.length - matches;
  const accuracy = ((matches / bits.length) * 100).toFixed(1);

  return (
    <div>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '8px',
        fontSize: '0.8125rem'
      }}>
        <div style={{ display: 'flex', gap: '16px' }}>
          <span style={{ color: 'var(--success)', fontWeight: 600 }}>Matched: {matches}</span>
          <span style={{ color: 'var(--danger)', fontWeight: 600 }}>Errors: {errors}</span>
          <span style={{ color: 'var(--text-muted)' }}>Total: {bits.length} bits</span>
        </div>
        <span style={{ fontWeight: 700, color: 'var(--text-main)' }}>Bit Recovery: {accuracy}%</span>
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
      <div style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', marginTop: '6px' }}>
        Green chips denote exact bit matches; red chips denote bit alteration or channel errors. Hover over any chip to inspect the original vs extracted value.
      </div>
    </div>
  );
}
