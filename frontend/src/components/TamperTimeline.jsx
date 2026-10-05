import React from 'react';

export default function TamperTimeline({ segments = [], totalDuration = 3.0 }) {
  if (!segments || segments.length === 0) {
    return (
      <div style={{ padding: '16px', background: 'var(--bg-surface-alt)', borderRadius: '6px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.8125rem' }}>
        No tamper segmentation data available. Verify audio to perform block-level localization.
      </div>
    );
  }

  const tamperedCount = segments.filter(s => s.is_tampered || (s.ber !== undefined && s.ber > 0.20)).length;
  const tamperPercent = ((tamperedCount / segments.length) * 100).toFixed(1);

  return (
    <div style={{ marginTop: '14px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px', fontSize: '0.8125rem' }}>
        <span style={{ fontWeight: 600 }}>Tamper Localization Timeline (4096-sample blocks)</span>
        <span style={{ color: tamperedCount > 0 ? 'var(--danger)' : 'var(--success)', fontWeight: 600 }}>
          {tamperedCount > 0 ? `${tamperedCount} / ${segments.length} Blocks Tampered (${tamperPercent}%)` : 'All Blocks Intact (0% Tampered)'}
        </span>
      </div>

      {/* Visual Timeline Bar */}
      <div style={{
        display: 'flex',
        height: '28px',
        borderRadius: '6px',
        overflow: 'hidden',
        border: '1px solid var(--border-color)',
        background: 'var(--bg-surface-alt)'
      }}>
        {segments.map((seg, idx) => {
          const isTampered = seg.is_tampered || (seg.ber !== undefined && seg.ber > 0.20);
          const bg = isTampered ? '#ef4444' : '#10b981';
          return (
            <div
              key={idx}
              style={{
                flex: 1,
                backgroundColor: bg,
                borderRight: '1px solid rgba(0,0,0,0.15)',
                position: 'relative',
                cursor: 'pointer',
                transition: 'opacity 0.15s ease'
              }}
              title={`Block ${seg.block_idx !== undefined ? seg.block_idx : idx}\nTime: ${seg.start_time_sec}s - ${seg.end_time_sec}s\nBER: ${seg.ber}\nStatus: ${isTampered ? 'TAMPERED / MANIPULATED' : 'AUTHENTIC'}`}
            />
          );
        })}
      </div>

      {/* Timeline Labels */}
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-subtle)', marginTop: '4px' }}>
        <span>0.0s</span>
        <span>{(totalDuration / 2).toFixed(1)}s</span>
        <span>{totalDuration}s</span>
      </div>

      {/* Legend & Tampered Intervals List */}
      <div style={{ display: 'flex', gap: '16px', marginTop: '12px', fontSize: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <div style={{ width: '12px', height: '12px', borderRadius: '3px', background: '#10b981' }} />
          <span>Authentic Region</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <div style={{ width: '12px', height: '12px', borderRadius: '3px', background: '#ef4444' }} />
          <span>Tampered / Cropped / AI Infilled Region</span>
        </div>
      </div>
    </div>
  );
}
