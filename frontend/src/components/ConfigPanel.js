import React, { useState, useEffect } from 'react';
import { apiConfig, updateApiBaseUrl, getApiConfig } from '../config/apiConfig.js';

const ConfigPanel = () => {
  const [config, setConfig] = useState(getApiConfig());
  const [newBaseUrl, setNewBaseUrl] = useState('');
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Show config panel in development mode or when accessed via keyboard shortcut
    const showConfigPanel = () => {
      if (process.env.NODE_ENV === 'development' || localStorage.getItem('showConfigPanel')) {
        setIsVisible(true);
      }
    };

    // Keyboard shortcut: Ctrl + Shift + C
    const handleKeyPress = (e) => {
      if (e.ctrlKey && e.shiftKey && e.key === 'C') {
        setIsVisible(!isVisible);
        localStorage.setItem('showConfigPanel', isVisible ? 'false' : 'true');
      }
    };

    showConfigPanel();
    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [isVisible]);

  const handleUpdateUrl = () => {
    if (newBaseUrl.trim()) {
      updateApiBaseUrl(newBaseUrl.trim());
    }
  };

  const resetToDefault = () => {
    localStorage.removeItem('API_BASE_URL');
    window.location.reload();
  };

  if (!isVisible) {
    return null;
  }

  return (
    <div style={{
      position: 'fixed',
      top: '10px',
      right: '10px',
      background: '#f0f0f0',
      border: '1px solid #ccc',
      borderRadius: '8px',
      padding: '15px',
      minWidth: '300px',
      zIndex: 9999,
      boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
      fontSize: '12px'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
        <strong>API Configuration</strong>
        <button 
          onClick={() => setIsVisible(false)}
          style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '16px' }}
        >
          ×
        </button>
      </div>
      
      <div style={{ marginBottom: '10px' }}>
        <div><strong>Current Base URL:</strong> {config.baseUrl}</div>
        <div><strong>AEM Builder URL:</strong> {config.aemBuilderUrl}</div>
      </div>

      <div style={{ marginBottom: '10px' }}>
        <input
          type="text"
          placeholder="Enter new base URL (e.g., http://localhost:5001)"
          value={newBaseUrl}
          onChange={(e) => setNewBaseUrl(e.target.value)}
          style={{ width: '100%', padding: '5px', marginBottom: '5px' }}
        />
        <div style={{ display: 'flex', gap: '5px' }}>
          <button onClick={handleUpdateUrl} style={{ padding: '5px 10px', cursor: 'pointer' }}>
            Update URL
          </button>
          <button onClick={resetToDefault} style={{ padding: '5px 10px', cursor: 'pointer' }}>
            Reset to Default
          </button>
        </div>
      </div>

      <div style={{ fontSize: '10px', color: '#666' }}>
        <div>Press Ctrl+Shift+C to toggle this panel</div>
        <div>Current environment: {process.env.NODE_ENV || 'development'}</div>
      </div>
    </div>
  );
};

export default ConfigPanel;
