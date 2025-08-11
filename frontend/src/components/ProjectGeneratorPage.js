import React, { useState } from 'react';
import axios from 'axios';
import { apiConfig } from '../config/apiConfig.js';

export default function ProjectGeneratorPage() {
  const [projectInputs, setProjectInputs] = useState({
    aemVersion: 'cloud',
    archetypeVersion: '42',
    appTitle: 'My AEM Project',
    appId: 'myapp',
    groupId: 'com.mycompany',
    artifactId: 'myapp-project',
    package: 'com.mycompany.myapp',
    version: '0.0.1-SNAPSHOT'
  });

  const [result, setResult] = useState('');

  const handleGenerateProject = async () => {
    const res = await axios.post(apiConfig.getFullUrl(apiConfig.endpoints.generateProject), projectInputs);
    setResult(`✅ Project generated at: ${res.data.outputDir}`);
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>AEM Project Generator</h2>

      {Object.keys(projectInputs).map(key => (
        <div key={key} style={{ marginBottom: 10 }}>
          <label style={{ width: 150, display: 'inline-block' }}>{key}: </label>
          <input
            type="text"
            value={projectInputs[key]}
            onChange={e => setProjectInputs({ ...projectInputs, [key]: e.target.value })}
            style={{ width: '50%' }}
          />
        </div>
      ))}

      <button onClick={handleGenerateProject}>Generate Project</button>

      {result && <div style={{ marginTop: 20 }}>{result}</div>}
    </div>
  );
}
