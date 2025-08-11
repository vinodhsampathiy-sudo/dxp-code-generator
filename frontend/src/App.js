import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import ComponentGeneratorPage from './components/ComponentGeneratorPage';
import ProjectGeneratorPage from './components/ProjectGeneratorPage';
import EDSBlockGeneratorPage from './components/EDSBlockGeneratorPage'
import DXPComponentGeneratorPage from './components/DXPComponentGeneratorPage';
import Navbar from './components/Navbar';
import ConfigPanel from './components/ConfigPanel';

function App() {
  return (
    <Router>
      <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
        {/* <nav style={{ padding: 10, borderBottom: '1px solid #ccc' }}>
          <Link to="/dxp-code-generator" style={{ marginRight: 10 }}>Component Generator</Link>
          <Link to="/project" style={{ marginRight: 10 }}>Project Generator</Link>
          <Link to="/eds-block-generator">EDS Block Generator</Link>
        </nav> */}

        <div style={{ flex: 1 }}>
          <Routes>
            <Route path="/project" element={<ProjectGeneratorPage />} />
            <Route path="/eds-block-generator" element={<EDSBlockGeneratorPage />} />
            <Route intial path="/" element={<DXPComponentGeneratorPage />}/>
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
