import React, { useState, useEffect } from 'react';
import {
  Layers,
  Flame,
  ScanLine,
  BarChart3,
  Sun,
  Moon,
  Info,
  CheckCircle,
  AlertTriangle,
  XCircle,
  X
} from 'lucide-react';
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
  
  // Toast Notification State
  const [toast, setToast] = useState({ show: false, message: '', type: 'info' });

  const showToast = (message, type = 'info') => {
    setToast({ show: true, message, type });
    setTimeout(() => {
      setToast(prev => ({ ...prev, show: false }));
    }, 4000);
  };

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
      } catch {
        // Handled gracefully
      }
    };

    checkApi();
    loadSamples();
  }, []);

  // Helper for toast icons
  const getToastIcon = () => {
    switch(toast.type) {
      case 'success': return <CheckCircle size={18} className="text-success" />;
      case 'warning': return <AlertTriangle size={18} className="text-warning" />;
      case 'error': return <XCircle size={18} className="text-danger" />;
      default: return <Info size={18} className="text-accent-cyan" />;
    }
  };

  return (
    <>
      {/* Toast Notification Overlay */}
      <div className={`toast-container ${toast.show ? 'show' : ''}`}>
        <div className={`toast-message toast-${toast.type}`}>
          {getToastIcon()}
          <span>{toast.message}</span>
          <button className="toast-close" onClick={() => setToast({ ...toast, show: false })}>
            <X size={14} />
          </button>
        </div>
      </div>

      {/* Aceternity Grid / Dot Pattern Background & Ambient Auroras */}
      <div className="aceternity-bg" />
      <div className="aurora-glow-1" />
      <div className="aurora-glow-2" />

      <div className="app-container">
        {/* Aceternity Hero Header */}
        <header className="hero-header">
          <div className="hero-top-row">
            <div>
              <h1 className="hero-title">Audio Watermarking &amp; AI Detection System</h1>
              <p className="hero-subtitle">
                Dual-layer orthonormal wavelet watermarking for proactive deepfake attribution,
                tamper localization, and Kaggle acoustic validation.
              </p>
            </div>

            <div className="header-actions">
              {/* API Connection Indicator */}
              <div className="status-pill">
                <div className={`status-dot ${apiConnected ? '' : 'offline'}`} />
                <span>{apiConnected ? 'API Connected' : 'API Offline (8000)'}</span>
              </div>

              {/* Theme Toggle Button */}
              <button
                className="btn btn-secondary"
                onClick={() => setDarkMode(!darkMode)}
                title="Toggle Theme"
                style={{ padding: '7px 14px', fontSize: '0.8125rem' }}
              >
                {darkMode ? <Sun size={15} /> : <Moon size={15} />}
                <span>{darkMode ? 'Light' : 'Dark'}</span>
              </button>
            </div>
          </div>
        </header>

        {/* Floating Pill Nav Tabs (Aceternity Floating Dock Style) */}
        <div className="nav-tabs-wrapper">
          <nav className="nav-tabs">
            <button
              className={`nav-tab-btn ${activeTab === 'embed' ? 'active' : ''}`}
              onClick={() => setActiveTab('embed')}
            >
              <Layers size={15} />
              <span>1. Embed &amp; Fidelity</span>
            </button>
            <button
              className={`nav-tab-btn ${activeTab === 'attacks' ? 'active' : ''}`}
              onClick={() => setActiveTab('attacks')}
            >
              <Flame size={15} />
              <span>2. Attacks &amp; Robustness</span>
            </button>
            <button
              className={`nav-tab-btn ${activeTab === 'detect' ? 'active' : ''}`}
              onClick={() => setActiveTab('detect')}
            >
              <ScanLine size={15} />
              <span>3. Detection &amp; Authenticity</span>
            </button>
            <button
              className={`nav-tab-btn ${activeTab === 'benchmarks' ? 'active' : ''}`}
              onClick={() => setActiveTab('benchmarks')}
            >
              <BarChart3 size={15} />
              <span>4. Benchmarks &amp; Kaggle</span>
            </button>
          </nav>
        </div>

        {/* Tab Panels */}
        <main>
          {activeTab === 'embed' && (
            <EmbedTab
              apiBase={API_BASE}
              session={session}
              setSession={setSession}
              samples={samples}
              showToast={showToast}
            />
          )}

          {activeTab === 'attacks' && (
            <AttackTab
              apiBase={API_BASE}
              session={session}
              showToast={showToast}
            />
          )}

          {activeTab === 'detect' && (
            <DetectTab
              apiBase={API_BASE}
              session={session}
              samples={samples}
              showToast={showToast}
            />
          )}

          {activeTab === 'benchmarks' && (
            <BenchmarkTab
              apiBase={API_BASE}
              showToast={showToast}
            />
          )}
        </main>
      </div>
    </>
  );
}
