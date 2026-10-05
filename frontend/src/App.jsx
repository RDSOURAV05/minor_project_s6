import React, { useState, useEffect } from 'react';
import EmbedTab from './tabs/EmbedTab';
import AttackTab from './tabs/AttackTab';
import DetectTab from './tabs/DetectTab';
import BenchmarkTab from './tabs/BenchmarkTab';

const API_BASE = 'http://localhost:8000';

export default function App() {
  const [activeTab, setActiveTab] = useState('embed');
  const [darkMode, setDarkMode] = useState(true);
  const [session, setSession] = useState(null);
  const [samples, setSamples] = useState([]);
  const [apiConnected, setApiConnected] = useState(false);

  // Apply dark mode class to root document
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  // Load sample audios on startup and check API health
  useEffect(() => {
    const checkApi = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/health`);
        if (res.ok) {
          setApiConnected(true);
        }
      } catch {
        setApiConnected(false);
      }
    };

    const loadSamples = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/samples`);
        if (res.ok) {
          const data = await res.json();
          if (data.samples) {
            setSamples(data.samples);
          }
        }
      } catch (e) {
        // Handled gracefully
      }
    };

    checkApi();
    loadSamples();
  }, []);

  return (
    <div className="app-container">
      {/* Academic Header */}
      <header className="app-header">
        <div>
          <h1 className="brand-title">Audio Watermarking & AI Detection System</h1>
          <p className="brand-subtitle">
            DWT-SVD Multi-Level Watermarking Testbed &bull; Minor Project S6 &bull; DeepMark Aligned
          </p>
        </div>

        <div className="header-actions">
          {/* API Connection Indicator */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '0.75rem',
              color: apiConnected ? 'var(--success)' : 'var(--danger)',
              fontWeight: 600,
              background: 'var(--bg-surface-alt)',
              padding: '6px 10px',
              borderRadius: '6px',
              border: '1px solid var(--border-color)',
            }}
          >
            <div
              style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                background: apiConnected ? 'var(--success)' : 'var(--danger)',
              }}
            />
            {apiConnected ? 'API Connected' : 'API Offline (localhost:8000)'}
          </div>

          {/* Theme Toggle Button */}
          <button
            className="btn btn-secondary"
            onClick={() => setDarkMode(!darkMode)}
            title="Toggle Light / Dark Mode"
            style={{ padding: '6px 12px', fontSize: '0.8125rem' }}
          >
            {darkMode ? 'Light Theme' : 'Dark Theme'}
          </button>
        </div>
      </header>

      {/* Main Tabs Navigation */}
      <nav className="nav-tabs">
        <button
          className={`nav-tab-btn ${activeTab === 'embed' ? 'active' : ''}`}
          onClick={() => setActiveTab('embed')}
        >
          1. Embed &amp; Fidelity
        </button>
        <button
          className={`nav-tab-btn ${activeTab === 'attacks' ? 'active' : ''}`}
          onClick={() => setActiveTab('attacks')}
        >
          2. Attacks &amp; Robustness
        </button>
        <button
          className={`nav-tab-btn ${activeTab === 'detect' ? 'active' : ''}`}
          onClick={() => setActiveTab('detect')}
        >
          3. Detection &amp; Authenticity
        </button>
        <button
          className={`nav-tab-btn ${activeTab === 'benchmarks' ? 'active' : ''}`}
          onClick={() => setActiveTab('benchmarks')}
        >
          4. Benchmarks &amp; Kaggle Dataset
        </button>
      </nav>

      {/* Tab Panels */}
      <main>
        {activeTab === 'embed' && (
          <EmbedTab
            apiBase={API_BASE}
            session={session}
            setSession={setSession}
            samples={samples}
          />
        )}

        {activeTab === 'attacks' && (
          <AttackTab
            apiBase={API_BASE}
            session={session}
          />
        )}

        {activeTab === 'detect' && (
          <DetectTab
            apiBase={API_BASE}
            session={session}
          />
        )}

        {activeTab === 'benchmarks' && (
          <BenchmarkTab
            apiBase={API_BASE}
          />
        )}
      </main>
    </div>
  );
}
