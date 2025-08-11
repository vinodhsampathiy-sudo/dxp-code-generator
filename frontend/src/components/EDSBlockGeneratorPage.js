import React, { useState } from 'react';
import axios from 'axios';
import { Buffer } from 'buffer';
import { apiConfig } from '../config/apiConfig.js';

export default function EDSBlockGeneratorPage() {
  const [formData, setFormData] = useState({
    description: ''
  });

  const [loading, setLoading] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const [cssPreview, setCssPreview] = useState('');
  const [jsPreview, setJsPreview] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name === 'description' && value.length > 300) return;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setCssPreview('');
    setJsPreview('');
    setDownloadUrl(null);

    try {
      const res = await axios.post(apiConfig.getFullUrl(apiConfig.endpoints.generateEdsBlock), formData);

      const { zip_base64, css, js, file_name } = res.data;
      const blob = new Blob([Uint8Array.from(Buffer.from(zip_base64, 'hex'))], {
        type: 'application/zip'
      });

      const zipUrl = window.URL.createObjectURL(blob);
      setDownloadUrl({ url: zipUrl, name: file_name });
      setCssPreview(css);
      setJsPreview(js);
    } catch (err) {
        console.log('Error generating block', err)
        alert('Error generating block');
    }
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', padding: '2rem', fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ fontSize: '1.8rem', fontWeight: 'bold', marginBottom: '1rem' }}>EDS Block Generator</h1>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <textarea
          name="description"
          placeholder="Describe the purpose and layout of the block (max 300 chars)"
          value={formData.description}
          onChange={handleChange}
          required
          rows={4}
          style={{ padding: '0.5rem', borderRadius: '5px', border: '1px solid #ccc', resize: 'vertical' }}
        />
        <button
          type="submit"
          disabled={loading}
          style={{
            backgroundColor: '#007bff',
            color: 'white',
            padding: '0.6rem 1.2rem',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer',
            fontWeight: 'bold'
          }}
        >
          {loading ? 'Generating...' : 'Generate Block'}
        </button>
      </form>

      {cssPreview && (
        <div style={{ marginTop: '2rem' }}>
          <h2 style={{ fontWeight: '600', marginBottom: '0.5rem' }}>🧩 CSS Preview</h2>
          <textarea
            readOnly
            value={cssPreview}
            style={{
              width: '100%',
              height: '160px',
              fontFamily: 'monospace',
              fontSize: '0.9rem',
              padding: '0.5rem',
              borderRadius: '5px',
              border: '1px solid #ccc'
            }}
          />
        </div>
      )}

      {jsPreview && (
        <div style={{ marginTop: '1.5rem' }}>
          <h2 style={{ fontWeight: '600', marginBottom: '0.5rem' }}>📜 JS Preview</h2>
          <textarea
            readOnly
            value={jsPreview}
            style={{
              width: '100%',
              height: '160px',
              fontFamily: 'monospace',
              fontSize: '0.9rem',
              padding: '0.5rem',
              borderRadius: '5px',
              border: '1px solid #ccc'
            }}
          />
        </div>
      )}

      {downloadUrl && (
        <div style={{ paddingTop: '1.5rem' }}>
          <a
            href={downloadUrl.url}
            download={downloadUrl.name}
            style={{ color: '#007bff', textDecoration: 'underline' }}
          >
            ⬇ Download ZIP
          </a>
        </div>
      )}
    </div>
  );
}
