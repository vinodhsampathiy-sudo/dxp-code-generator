import React, { useState, useEffect } from 'react';
import './AEMCoreComponentsPanel.css';

const AEMCoreComponentsPanel = () => {
  const [config, setConfig] = useState(null);
  const [components, setComponents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedComponent, setSelectedComponent] = useState(null);
  const [componentDetails, setComponentDetails] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchConfig();
    fetchComponents();
  }, []);

  const fetchConfig = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/aem/core-components/config');
      const data = await response.json();
      setConfig(data);
    } catch (error) {
      console.error('Error fetching config:', error);
      setError('Failed to fetch configuration');
    }
  };

  const fetchComponents = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:5001/api/aem/core-components/components');
      const data = await response.json();
      
      if (data.success) {
        setComponents(data.components);
      } else {
        setError('Failed to fetch components');
      }
    } catch (error) {
      console.error('Error fetching components:', error);
      setError('Failed to fetch components');
    } finally {
      setLoading(false);
    }
  };

  const fetchComponentDetails = async (componentName) => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:5001/api/aem/core-components/components/${componentName}`);
      const data = await response.json();
      
      if (data.success) {
        setComponentDetails(data.component);
        setSelectedComponent(componentName);
      } else {
        setError('Failed to fetch component details');
      }
    } catch (error) {
      console.error('Error fetching component details:', error);
      setError('Failed to fetch component details');
    } finally {
      setLoading(false);
    }
  };

  const clearCache = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/aem/core-components/clear-cache', {
        method: 'POST'
      });
      const data = await response.json();
      
      if (data.success) {
        alert('Cache cleared successfully');
        fetchComponents(); // Refresh components list
      } else {
        alert('Failed to clear cache');
      }
    } catch (error) {
      console.error('Error clearing cache:', error);
      alert('Failed to clear cache');
    }
  };

  const filteredComponents = components.filter(component =>
    component.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    component.category.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getComponentsByCategory = () => {
    const grouped = {};
    filteredComponents.forEach(component => {
      if (!grouped[component.category]) {
        grouped[component.category] = [];
      }
      grouped[component.category].push(component);
    });
    return grouped;
  };

  if (loading && components.length === 0) {
    return (
      <div className="aem-core-panel">
        <div className="loading-indicator">
          <div className="spinner"></div>
          <p>Loading AEM Core Components...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="aem-core-panel">
      <div className="panel-header">
        <h3>🧩 AEM Core Components</h3>
        <p>Enhanced AI generation with Adobe's official components</p>
      </div>

      {config && (
        <div className="config-status">
          <div className={`status-indicator ${config.configured ? 'connected' : 'disconnected'}`}>
            {config.configured ? '✅ Connected' : '❌ Not Configured'}
          </div>
          <div className="config-details">
            <p><strong>Repository:</strong> {config.repo_info.owner}/{config.repo_info.name}</p>
            <p><strong>GitHub Token:</strong> {config.github_token_available ? 'Available' : 'Missing'}</p>
            <button onClick={clearCache} className="btn-secondary">Clear Cache</button>
          </div>
        </div>
      )}

      {error && (
        <div className="error-message">
          <p>⚠️ {error}</p>
        </div>
      )}

      <div className="components-section">
        <div className="search-bar">
          <input
            type="text"
            placeholder="Search components..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>

        <div className="components-overview">
          <h4>Available Components ({filteredComponents.length})</h4>
          <p className="enhancement-info">
            🚀 These components are automatically analyzed and used to enhance AI generation with real patterns from Adobe's core components.
          </p>
        </div>

        <div className="components-grid">
          {Object.entries(getComponentsByCategory()).map(([category, categoryComponents]) => (
            <div key={category} className="category-group">
              <h5 className="category-title">{category}</h5>
              <div className="components-list">
                {categoryComponents.map((component) => (
                  <div
                    key={component.name}
                    className={`component-card ${selectedComponent === component.name ? 'selected' : ''}`}
                    onClick={() => fetchComponentDetails(component.name)}
                  >
                    <div className="component-name">{component.name}</div>
                    <div className="component-category">{component.category}</div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {componentDetails && (
          <div className="component-details">
            <div className="details-header">
              <h4>📋 {selectedComponent} Details</h4>
              <button onClick={() => {setSelectedComponent(null); setComponentDetails(null);}} className="close-btn">×</button>
            </div>
            <div className="details-content">
              {componentDetails.htl_template && (
                <div className="code-section">
                  <h5>HTL Template</h5>
                  <pre><code>{componentDetails.htl_template.substring(0, 500)}...</code></pre>
                </div>
              )}
              {componentDetails.sling_model && (
                <div className="code-section">
                  <h5>Sling Model</h5>
                  <pre><code>{componentDetails.sling_model.substring(0, 500)}...</code></pre>
                </div>
              )}
              {componentDetails.dialog && (
                <div className="code-section">
                  <h5>Dialog Configuration</h5>
                  <pre><code>{componentDetails.dialog.substring(0, 500)}...</code></pre>
                </div>
              )}
              {componentDetails.readme && (
                <div className="readme-section">
                  <h5>Documentation</h5>
                  <p>{componentDetails.readme.substring(0, 300)}...</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AEMCoreComponentsPanel;
