import React from 'react';
import { ShieldAlert, ShieldCheck, Clock } from 'lucide-react';

export default function TamperTimeline({ segments = [], totalDuration = 3.0 }) {
  if (!segments || segments.length === 0) {
    return (
      <div
        style={{
          padding: '16px',
          background: 'rgba(15, 23, 42, 0.4)',
          borderRadius: '12px',
          textAlign: 'center',
          color: 'var(--text-muted)',
          fontSize: '0.8125rem',
          border: '1px dashed var(--border-glass)',
        }}
      >
        No tamper segmentation data available. Verify audio to perform block-level localization.
      </div>
    );
  }

  const tamperedCount = segments.filter(
    (s) => s.is_tampered || (s.ber !== undefined && s.ber > 0.2)
  ).length;
  const tamperPercent = ((tamperedCount / segments.length) * 100).toFixed(1);
  const isIntact = tamperedCount === 0;

  return (
    <div style={{ marginTop: '16px' }}>
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
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 600 }}>
          <Clock size={14} style={{ color: 'var(--accent-cyan)' }} />
          <span>Tamper Localization Timeline (4096-Sample Windows)</span>
        </div>
        <span
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            color: isIntact ? 'var(--success)' : 'var(--danger)',
            fontWeight: 700,
            background: isIntact ? 'var(--success-bg)' : 'var(--danger-bg)',
            border: `1px solid ${isIntact ? 'var(--success-border)' : 'var(--danger-border)'}`,
            padding: '3px 10px',
            borderRadius: '9999px',
          }}
        >
          {isIntact ? (
            <>
              <ShieldCheck size={13} /> All Blocks Intact (0% Tampered)
            </>
          ) : (
            <>
              <ShieldAlert size={13} /> {tamperedCount} / {segments.length} Blocks Tampered ({tamperPercent}%)
            </>
          )}
        </span>
      </div>

      {/* Visual Timeline Bar */}
      <div
        style={{
          display: 'flex',
          height: '28px',
          borderRadius: '10px',
          overflow: 'hidden',
          border: '1px solid var(--border-glass)',
          background: 'rgba(8, 12, 20, 0.8)',
          boxShadow: 'inset 0 1px 6px rgba(0, 0, 0, 0.4)',
          padding: '2px',
          gap: '2px',
        }}
      >
        {segments.map((seg, idx) => {
          const isTampered = seg.is_tampered || (seg.ber !== undefined && seg.ber > 0.2);
          const bg = isTampered ? '#ef4444' : '#10b981';
          return (
            <div
              key={idx}
              style={{
                flex: 1,
                backgroundColor: bg,
                borderRadius: '4px',
                position: 'relative',
                cursor: 'pointer',
                transition: 'opacity 0.15s ease, transform 0.15s ease',
                boxShadow: isTampered ? '0 0 8px rgba(239, 68, 68, 0.4)' : '0 0 6px rgba(16, 185, 129, 0.2)',
              }}
              title={`Block ${seg.block_idx !== undefined ? seg.block_idx : idx}\nTime: ${seg.start_time_sec}s - ${seg.end_time_sec}s\nBER: ${seg.ber}\nStatus: ${isTampered ? 'TAMPERED / MANIPULATED' : 'AUTHENTIC'}`}
            />
          );
        })}
      </div>

      {/* Timeline Labels */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          fontSize: '0.72rem',
          color: 'var(--text-subtle)',
          marginTop: '6px',
          fontFamily: 'var(--font-mono)',
        }}
      >
        <span>0.0s</span>
        <span>{(totalDuration / 2).toFixed(1)}s</span>
        <span>{totalDuration}s</span>
      </div>

      {/* Legend & Tampered Intervals List */}
      <div style={{ display: 'flex', gap: '20px', marginTop: '12px', fontSize: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <div
            style={{
              width: '10px',
              height: '10px',
              borderRadius: '3px',
              background: '#10b981',
              boxShadow: '0 0 6px rgba(16, 185, 129, 0.5)',
            }}
          />
          <span style={{ color: 'var(--text-muted)' }}>Authentic Region</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <div
            style={{
              width: '10px',
              height: '10px',
              borderRadius: '3px',
              background: '#ef4444',
              boxShadow: '0 0 6px rgba(239, 68, 68, 0.5)',
            }}
          />
          <span style={{ color: 'var(--text-muted)' }}>Tampered / Cropped / Infilled Region</span>
        </div>
      </div>
    </div>
  );
}
