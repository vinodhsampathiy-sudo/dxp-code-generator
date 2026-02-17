import React, { useState, useCallback } from 'react';
import './ImageUploadPanel.css';

const ImageUploadPanel = ({ onImageUpload, onAnalysisComplete }) => {
    const [isDragging, setIsDragging] = useState(false);
    const [uploadedImage, setUploadedImage] = useState(null);
    const [isUploading, setIsUploading] = useState(false);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [designAnalysis, setDesignAnalysis] = useState(null);
    const [error, setError] = useState(null);
    const [figmaUrl, setFigmaUrl] = useState('');

    const handleDragEnter = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
    }, []);

    const handleDragOver = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
    }, []);

    const handleDrop = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);

        const files = e.dataTransfer.files;
        if (files && files.length > 0) {
            handleFileUpload(files[0]);
        }
    }, []);

    const handleFileSelect = (e) => {
        const files = e.target.files;
        if (files && files.length > 0) {
            handleFileUpload(files[0]);
        }
    };

    const handleFileUpload = async (file) => {
        // Validate file type
        const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/svg+xml', 'image/webp'];
        if (!validTypes.includes(file.type)) {
            setError('Invalid file type. Please upload PNG, JPG, SVG, or WebP images.');
            return;
        }

        // Validate file size (10MB max)
        const maxSize = 10 * 1024 * 1024;
        if (file.size > maxSize) {
            setError('File too large. Maximum size is 10MB.');
            return;
        }

        setError(null);
        setIsUploading(true);

        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('analyze', 'true');

            const response = await fetch('http://localhost:5001/api/image/upload', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Upload failed');
            }

            const data = await response.json();
            console.log('Upload response:', data);

            setUploadedImage({
                url: data.imageUrl,
                id: data.imageId,
                fileName: data.fileName,
            });

            if (data.designAnalysis) {
                setDesignAnalysis(data.designAnalysis);
                if (onAnalysisComplete) {
                    onAnalysisComplete(data.designAnalysis);
                }
            }

            if (onImageUpload) {
                onImageUpload(data);
            }
        } catch (err) {
            console.error('Upload error:', err);
            setError('Failed to upload image. Please try again.');
        } finally {
            setIsUploading(false);
        }
    };

    const handleClearImage = () => {
        setUploadedImage(null);
        setDesignAnalysis(null);
        setError(null);
    };

    const handleFigmaUrlSubmit = async () => {
        if (!figmaUrl.trim()) {
            setError('Please enter a Figma URL');
            return;
        }

        if (!figmaUrl.startsWith('https://www.figma.com/')) {
            setError('Invalid Figma URL. Must start with https://www.figma.com/');
            return;
        }

        setError(null);
        setIsAnalyzing(true);

        try {
            // TODO: Implement Figma URL parsing endpoint
            setError('Figma integration coming soon!');
        } catch (err) {
            console.error('Figma error:', err);
            setError('Failed to fetch Figma design. Please try again.');
        } finally {
            setIsAnalyzing(false);
        }
    };

    return (
        <div className="image-upload-panel">
            <h3>Upload Design Image</h3>

            {!uploadedImage ? (
                <>
                    {/* Drag and Drop Area */}
                    <div
                        className={`upload-dropzone ${isDragging ? 'dragging' : ''}`}
                        onDragEnter={handleDragEnter}
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        onDrop={handleDrop}
                    >
                        {isUploading ? (
                            <div className="upload-loading">
                                <div className="spinner"></div>
                                <p>Uploading and analyzing...</p>
                            </div>
                        ) : (
                            <>
                                <svg className="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                                </svg>
                                <p className="upload-text">Drag & drop your design image here</p>
                                <p className="upload-subtext">or</p>
                                <label className="upload-button">
                                    Browse Files
                                    <input
                                        type="file"
                                        accept="image/png,image/jpeg,image/jpg,image/svg+xml,image/webp"
                                        onChange={handleFileSelect}
                                        style={{ display: 'none' }}
                                    />
                                </label>
                                <p className="upload-hint">Supports: PNG, JPG, SVG, WebP (Max 10MB)</p>
                            </>
                        )}
                    </div>

                    {/* Figma URL Input */}
                    <div className="figma-input-section">
                        <p className="section-divider">OR</p>
                        <div className="figma-input-group">
                            <input
                                type="text"
                                className="figma-url-input"
                                placeholder="Paste Figma URL here..."
                                value={figmaUrl}
                                onChange={(e) => setFigmaUrl(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && handleFigmaUrlSubmit()}
                            />
                            <button
                                className="figma-submit-button"
                                onClick={handleFigmaUrlSubmit}
                                disabled={isAnalyzing}
                            >
                                {isAnalyzing ? 'Loading...' : 'Fetch Design'}
                            </button>
                        </div>
                    </div>
                </>
            ) : (
                /* Image Preview */
                <div className="image-preview-section">
                    <div className="image-preview">
                        <img src={uploadedImage.url} alt="Uploaded design" />
                        <button className="clear-image-button" onClick={handleClearImage}>
                            ✕
                        </button>
                    </div>
                    <p className="image-filename">{uploadedImage.fileName}</p>

                    {/* Design Analysis Display */}
                    {designAnalysis && (
                        <div className="design-analysis">
                            <h4>Design Analysis</h4>

                            {designAnalysis.blockType && (
                                <div className="analysis-item">
                                    <strong>Block Type:</strong> {designAnalysis.blockType}
                                </div>
                            )}

                            {designAnalysis.colorPalette && Object.keys(designAnalysis.colorPalette).length > 0 && (
                                <div className="analysis-item">
                                    <strong>Colors:</strong>
                                    <div className="color-palette">
                                        {Object.entries(designAnalysis.colorPalette).map(([name, color]) => (
                                            <div key={name} className="color-swatch">
                                                <div className="color-box" style={{ backgroundColor: color }}></div>
                                                <span className="color-name">{name}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {designAnalysis.interactiveElements && designAnalysis.interactiveElements.length > 0 && (
                                <div className="analysis-item">
                                    <strong>Interactive Elements:</strong>
                                    <div className="element-tags">
                                        {designAnalysis.interactiveElements.map((element, idx) => (
                                            <span key={idx} className="element-tag">{element}</span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {designAnalysis.layoutPattern && (
                                <div className="analysis-item">
                                    <strong>Layout:</strong> {designAnalysis.layoutPattern}
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}

            {/* Error Display */}
            {error && (
                <div className="upload-error">
                    <span className="error-icon">⚠️</span>
                    {error}
                </div>
            )}
        </div>
    );
};

export default ImageUploadPanel;
