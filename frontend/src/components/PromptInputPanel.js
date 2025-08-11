import React, { useState } from 'react';
import axios from 'axios';
import { apiConfig } from '../config/apiConfig.js';

export default function PromptInputPanel({ setOutput }) {
  const [prompt, setPrompt] = useState('');
  const [appId, setAppId] = useState('myapp'); // 🔥 default appId
  const [pkg, setPkg] = useState('com.mycompany.myapp'); // 🔥 default package

  const handleGenerate = async () => {
    try {
      const payload = {
        componentDesc: prompt,
        appId: appId,
        package: pkg
      };

      const res = await axios.post(apiConfig.getFullUrl(apiConfig.endpoints.generateComponent), payload);
      setOutput(res.data.aiOutput);

    } catch (err) {
      console.error("❌ Component generation failed:", err);
      setOutput({ htl: '', slingModel: '', dialog: '', error: err.message });
    }
  };

  return (
    <div style={{ flex: 1, padding: 20, borderRight: '1px solid #ccc' }}>
      <h2>Component Generator</h2>

      <div style={{ marginBottom: 10 }}>
        <label style={{ display: 'block', fontWeight: 'bold' }}>App ID:</label>
        <input
          type="text"
          value={appId}
          onChange={e => setAppId(e.target.value)}
          style={{ width: '100%' }}
          placeholder="e.g. myapp"
        />
      </div>

      <div style={{ marginBottom: 10 }}>
        <label style={{ display: 'block', fontWeight: 'bold' }}>Package:</label>
        <input
          type="text"
          value={pkg}
          onChange={e => setPkg(e.target.value)}
          style={{ width: '100%' }}
          placeholder="e.g. com.mycompany.myapp"
        />
      </div>

      <div style={{ marginBottom: 10 }}>
        <label style={{ display: 'block', fontWeight: 'bold' }}>Component Prompt:</label>
        <textarea
          value={prompt}
          onChange={e => setPrompt(e.target.value)}
          rows={8}
          style={{ width: '100%' }}
          placeholder="Describe your component requirements here..."
        />
      </div>

      <button onClick={handleGenerate}>Generate Component</button>
    </div>
  );
}
