import React, { useState, useRef, useEffect } from 'react';
import { Sparkles, Upload, Code, Download, Trash2, Image as ImageIcon, Send, X, History, ChevronLeft, ChevronRight } from 'lucide-react';
import { apiConfig } from '../config/apiConfig';
import { downloadZipFromBase64 } from '../utils/zipdownload';
import './EDSBlockBuilder.css';

const EDSBlockBuilder = () => {
    const [blockHistory, setBlockHistory] = useState([]);
    const [selectedBlock, setSelectedBlock] = useState(null);
    const [blockName, setBlockName] = useState('');
    const [description, setDescription] = useState('');
    const [uploadedImage, setUploadedImage] = useState(null);
    const [imageFile, setImageFile] = useState(null);
    const [designAnalysis, setDesignAnalysis] = useState(null);
    const [figmaUrl, setFigmaUrl] = useState('');
    const [isFigmaModalOpen, setIsFigmaModalOpen] = useState(false);
    const [isGenerating, setIsGenerating] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const [isParsingFigma, setIsParsingFigma] = useState(false);
    const [activeTab, setActiveTab] = useState('css');
    const [error, setError] = useState(null);
    const [leftPanelOpen, setLeftPanelOpen] = useState(true);
    const [rightPanelOpen, setRightPanelOpen] = useState(true);
    const messagesEndRef = useRef(null);
    const fileInputRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [blockHistory]);

    const handleImageSelect = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/svg+xml', 'image/webp'];
        if (!validTypes.includes(file.type)) {
            setError('Invalid file type. Please upload PNG, JPG, SVG, or WebP images.');
            return;
        }

        const maxSize = 10 * 1024 * 1024;
        if (file.size > maxSize) {
            setError('File too large. Maximum size is 10MB.');
            return;
        }

        setError(null);
        setIsUploading(true);
        setImageFile(file);

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

            setUploadedImage({
                url: data.imageUrl,
                id: data.imageId,
                fileName: data.fileName,
            });

            if (data.designAnalysis) {
                setDesignAnalysis(data.designAnalysis);
                if (!blockName && data.designAnalysis.blockType) {
                    setBlockName(data.designAnalysis.blockType.toLowerCase().replace(/\s+/g, '-'));
                }
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
        setImageFile(null);
        setDesignAnalysis(null);
        setFigmaUrl('');
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    const handleFigmaImport = async () => {
        if (!figmaUrl.trim() || !figmaUrl.startsWith('https://www.figma.com/')) {
            setError('Please enter a valid Figma URL');
            return;
        }

        setError(null);
        setIsParsingFigma(true);

        try {
            const response = await fetch('http://localhost:5001/api/figma/parse', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ figmaUrl }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to parse Figma URL');
            }

            const data = await response.json();

            setUploadedImage({
                url: data.imageUrl,
                id: data.fileId,
                fileName: data.fileName || 'Figma Design',
                isFigma: true
            });

            if (data.designTokens) {
                setDesignAnalysis(data.designTokens);
            }

            setIsFigmaModalOpen(false);
            if (!blockName && data.fileName) {
                setBlockName(data.fileName.toLowerCase().replace(/\s+/g, '-'));
            }
        } catch (err) {
            console.error('Figma parse error:', err);
            setError(err.message || 'Failed to parse Figma URL. Please check your token and URL.');
        } finally {
            setIsParsingFigma(false);
        }
    };

    const handleGenerateBlock = async () => {
        if (!description.trim()) {
            setError('Please provide a description for your block');
            return;
        }

        setError(null);
        setIsGenerating(true);

        try {
            const payload = {
                description: description,
                userId: 'block-builder-user'
            };

            if (uploadedImage) {
                payload.imageUrl = uploadedImage.url;
            }

            if (designAnalysis) {
                payload.designAnalysis = designAnalysis;
            }

            const response = await fetch(apiConfig.getFullUrl(apiConfig.endpoints.generateEdsBlock), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                throw new Error('Generation failed');
            }

            const data = await response.json();

            const newBlock = {
                id: Date.now(),
                name: data.block_name || blockName || 'generated-block',
                description: description,
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                image: uploadedImage?.url || null,
                code: {
                    css: data.css || '',
                    js: data.js || '',
                    mkd_table: data.mkd_table || '',
                },
                zip_base64: data.zip_base64 || '',
                file_name: data.file_name || 'block.zip'
            };

            setBlockHistory([...blockHistory, newBlock]);
            setSelectedBlock(newBlock);
            setRightPanelOpen(true);

            // Clear inputs
            setBlockName('');
            setDescription('');
            handleClearImage();

        } catch (err) {
            console.error('Generation error:', err);
            setError('Failed to generate block. Please try again.');
        } finally {
            setIsGenerating(false);
        }
    };

    const handleDownload = (block) => {
        if (block?.zip_base64) {
            downloadZipFromBase64(block.zip_base64, block.file_name);
        }
    };

    const handleDeleteBlock = (blockId, e) => {
        e.stopPropagation();
        setBlockHistory(blockHistory.filter(b => b.id !== blockId));
        if (selectedBlock?.id === blockId) {
            setSelectedBlock(null);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleGenerateBlock();
        }
    };

    return (
        <div className="eds-builder-container">
            {/* Left Panel - Block History */}
            <div className={`history-panel ${leftPanelOpen ? 'open' : 'closed'}`}>
                <div className="panel-header">
                    <div className="header-content">
                        <History size={20} />
                        <h3>Block History</h3>
                    </div>
                    <button
                        className="toggle-btn"
                        onClick={() => setLeftPanelOpen(!leftPanelOpen)}
                    >
                        {leftPanelOpen ? <ChevronLeft size={18} /> : <ChevronRight size={18} />}
                    </button>
                </div>

                {leftPanelOpen && (
                    <div className="history-list">
                        {blockHistory.length === 0 ? (
                            <div className="empty-state">
                                <Sparkles size={32} />
                                <p>No blocks generated yet</p>
                                <span>Create your first block to get started</span>
                            </div>
                        ) : (
                            blockHistory.map((block) => (
                                <div
                                    key={block.id}
                                    className={`history-item ${selectedBlock?.id === block.id ? 'active' : ''}`}
                                    onClick={() => {
                                        setSelectedBlock(block);
                                        setRightPanelOpen(true);
                                    }}
                                >
                                    {block.image && (
                                        <div className="history-item-image">
                                            <img src={block.image} alt={block.name} />
                                        </div>
                                    )}
                                    <div className="history-item-content">
                                        <h4>{block.name}</h4>
                                        <p>{block.description.substring(0, 60)}...</p>
                                        <span className="timestamp">{block.timestamp}</span>
                                    </div>
                                    <button
                                        className="delete-btn"
                                        onClick={(e) => handleDeleteBlock(block.id, e)}
                                    >
                                        <Trash2 size={14} />
                                    </button>
                                </div>
                            ))
                        )}
                    </div>
                )}
            </div>

            {/* Middle Panel - Chat Interface */}
            <div className="chat-panel">
                <div className="chat-header">
                    <div className="header-icon">
                        <Sparkles size={24} />
                    </div>
                    <div>
                        <h1>EDS Block Builder</h1>
                        <p>Describe your block and let AI generate the code</p>
                    </div>
                </div>

                <div className="chat-messages">
                    {/* Figma Import Section */}
                    {isFigmaModalOpen && (
                        <div className="figma-import-box">
                            <div className="figma-header">
                                <div className="figma-logo">
                                    <svg width="24" height="24" viewBox="0 0 38 57" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M19 28.5C19 25.9837 20.0009 23.5706 21.7825 21.7891C23.5641 20.0076 25.9791 19.0067 28.5 19.0067C31.0209 19.0067 33.4359 20.0076 35.2175 21.7891C36.9991 23.5706 38 25.9837 38 28.5V38H28.5C25.9791 38 23.5641 36.9991 21.7825 35.2175C20.0009 33.4359 19 31.0209 19 28.5Z" fill="#1ABCFE" />
                                        <path d="M0 47.5C0 44.9837 1.00089 42.5706 2.78249 40.7891C4.56408 39.0076 6.97908 38.0067 9.5 38.0067H19V47.5C19 50.0209 17.9991 52.4359 16.2175 54.2175C14.4359 55.9991 12.0209 57 9.5 57C6.97908 57 4.56408 55.9991 2.78249 54.2175C1.00089 52.4359 0 50.0209 0 47.5Z" fill="#0ACF83" />
                                        <path d="M0 28.5C0 25.9837 1.00089 23.5706 2.78249 21.7891C4.56408 20.0076 6.97908 19.0067 9.5 19.0067H19V38H9.5C6.97908 38 4.56408 36.9991 2.78249 35.2175C1.00089 33.4359 0 31.0209 0 28.5Z" fill="#A259FF" />
                                        <path d="M0 9.5C0 6.97908 1.00089 4.56408 2.78249 2.78249C4.56408 1.00089 6.97908 0 9.5 0H19V19H9.5C6.97908 19 4.56408 17.9991 2.78249 16.2175C1.00089 14.4359 0 12.0209 0 9.5Z" fill="#F24E1E" />
                                        <path d="M19 0H28.5C31.0209 0 33.4359 1.00089 35.2175 2.78249C36.9991 4.56408 38 6.97908 38 9.5C38 12.0209 36.9991 14.4359 35.2175 16.2175C33.4359 17.9991 31.0209 19 28.5 19H19V0Z" fill="#FF7262" />
                                    </svg>
                                </div>
                                <h2>Import Figma design <span className="beta-badge">Beta</span></h2>
                            </div>

                            <div className="figma-body">
                                <label>Figma frame URL</label>
                                <input
                                    type="text"
                                    placeholder="https://www.figma.com/file/..."
                                    value={figmaUrl}
                                    onChange={(e) => setFigmaUrl(e.target.value)}
                                />
                                <div className="figma-help">
                                    <span className="help-icon">?</span>
                                    <p>
                                        <strong>How to find your frame URL:</strong> In Figma Design, right click on the frame you want to import, then click "Copy/Paste as" and finally "Copy link to selection".
                                    </p>
                                </div>
                            </div>

                            <div className="figma-footer">
                                <button className="figma-cancel" onClick={() => setIsFigmaModalOpen(false)}>Cancel</button>
                                <button
                                    className="figma-attach"
                                    onClick={handleFigmaImport}
                                    disabled={isParsingFigma || !figmaUrl.trim()}
                                >
                                    {isParsingFigma ? 'Parsing...' : 'Attach to prompt'}
                                </button>
                            </div>
                        </div>
                    )}

                    {blockHistory.map((block) => (
                        <div key={block.id} className="message-group">
                            <div className="message user-message">
                                {block.image && (
                                    <div className="message-image">
                                        <img src={block.image} alt="Design" />
                                    </div>
                                )}
                                <div className="message-content">
                                    <strong>Block Name:</strong> {block.name}
                                    <br />
                                    {block.description}
                                </div>
                            </div>
                            <div className="message ai-message">
                                <div className="message-content">
                                    ✅ Block generated successfully! Click to view code →
                                </div>
                            </div>
                        </div>
                    ))}
                    <div ref={messagesEndRef} />
                </div>

                <div className="chat-input-area">
                    {/* Image Upload Preview */}
                    {uploadedImage && (
                        <div className="uploaded-preview">
                            <img src={uploadedImage.url} alt="Uploaded" />
                            <button className="remove-image" onClick={handleClearImage}>
                                <X size={16} />
                            </button>
                            {designAnalysis && (
                                <div className="analysis-badge">
                                    ✓ Analyzed
                                </div>
                            )}
                        </div>
                    )}

                    {/* Error Display */}
                    {error && (
                        <div className="error-banner">
                            <span>⚠️</span> {error}
                            <button onClick={() => setError(null)}><X size={16} /></button>
                        </div>
                    )}

                    {/* Block Name Input */}
                    <input
                        type="text"
                        placeholder="Block name (e.g., hero-banner)"
                        value={blockName}
                        onChange={(e) => setBlockName(e.target.value)}
                        className="block-name-input"
                    />

                    {/* Description Input */}
                    <div className="input-wrapper">
                        <textarea
                            placeholder="Describe your EDS block in detail..."
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            onKeyPress={handleKeyPress}
                            className="description-input"
                            rows={3}
                        />
                        <div className="input-actions">
                            <input
                                ref={fileInputRef}
                                type="file"
                                id="imageUpload"
                                accept="image/png,image/jpeg,image/jpg,image/svg+xml,image/webp"
                                onChange={handleImageSelect}
                                style={{ display: 'none' }}
                            />
                            <label htmlFor="imageUpload" className="upload-btn" title="Upload design image">
                                {isUploading ? '...' : <ImageIcon size={20} />}
                            </label>
                            <button
                                className="figma-btn"
                                title="Import from Figma"
                                onClick={() => setIsFigmaModalOpen(!isFigmaModalOpen)}
                            >
                                <svg width="18" height="18" viewBox="0 0 38 57" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M19 28.5C19 25.9837 20.0009 23.5706 21.7825 21.7891C23.5641 20.0076 25.9791 19.0067 28.5 19.0067C31.0209 19.0067 33.4359 20.0076 35.2175 21.7891C36.9991 23.5706 38 25.9837 38 28.5V38H28.5C25.9791 38 23.5641 36.9991 21.7825 35.2175C20.0009 33.4359 19 31.0209 19 28.5Z" fill="currentColor" />
                                    <path d="M0 47.5C0 44.9837 1.00089 42.5706 2.78249 40.7891C4.56408 39.0076 6.97908 38.0067 9.5 38.0067H19V47.5C19 50.0209 17.9991 52.4359 16.2175 54.2175C14.4359 55.9991 12.0209 57 9.5 57C6.97908 57 4.56408 55.9991 2.78249 54.2175C1.00089 52.4359 0 50.0209 0 47.5Z" fill="currentColor" />
                                    <path d="M0 28.5C0 25.9837 1.00089 23.5706 2.78249 21.7891C4.56408 20.0076 6.97908 19.0067 9.5 19.0067H19V38H9.5C6.97908 38 4.56408 36.9991 2.78249 35.2175C1.00089 33.4359 0 31.0209 0 28.5Z" fill="currentColor" />
                                    <path d="M0 9.5C0 6.97908 1.00089 4.56408 2.78249 2.78249C4.56408 1.00089 6.97908 0 9.5 0H19V19H9.5C6.97908 19 4.56408 17.9991 2.78249 16.2175C1.00089 14.4359 0 12.0209 0 9.5Z" fill="currentColor" />
                                    <path d="M19 0H28.5C31.0209 0 33.4359 1.00089 35.2175 2.78249C36.9991 4.56408 38 6.97908 38 9.5C38 12.0209 36.9991 14.4359 35.2175 16.2175C33.4359 17.9991 31.0209 19 28.5 19H19V0Z" fill="currentColor" />
                                </svg>
                            </button>
                            <button
                                className="send-btn"
                                onClick={handleGenerateBlock}
                                disabled={isGenerating || !description.trim()}
                            >
                                {isGenerating ? (
                                    <div className="spinner-small" />
                                ) : (
                                    <Send size={20} />
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Right Panel - Code Display */}
            <div className={`code-panel ${rightPanelOpen ? 'open' : 'closed'}`}>
                <div className="panel-header">
                    <button
                        className="toggle-btn"
                        onClick={() => setRightPanelOpen(!rightPanelOpen)}
                    >
                        {rightPanelOpen ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
                    </button>
                    <div className="header-content">
                        <Code size={20} />
                        <h3>{selectedBlock ? selectedBlock.name : 'Select a block'}</h3>
                    </div>
                    {selectedBlock && (
                        <button
                            className="download-btn-header"
                            onClick={() => handleDownload(selectedBlock)}
                            title="Download ZIP"
                        >
                            <Download size={18} />
                        </button>
                    )}
                </div>

                {rightPanelOpen && (
                    <>
                        {selectedBlock ? (
                            <>
                                <div className="code-tabs">
                                    <button
                                        className={`tab ${activeTab === 'css' ? 'active' : ''}`}
                                        onClick={() => setActiveTab('css')}
                                    >
                                        CSS
                                    </button>
                                    <button
                                        className={`tab ${activeTab === 'js' ? 'active' : ''}`}
                                        onClick={() => setActiveTab('js')}
                                    >
                                        JavaScript
                                    </button>
                                    <button
                                        className={`tab ${activeTab === 'table' ? 'active' : ''}`}
                                        onClick={() => setActiveTab('table')}
                                    >
                                        Markdown
                                    </button>
                                </div>

                                <div className="code-content">
                                    <pre>
                                        <code>
                                            {activeTab === 'css' && selectedBlock.code.css}
                                            {activeTab === 'js' && selectedBlock.code.js}
                                            {activeTab === 'table' && selectedBlock.code.mkd_table}
                                        </code>
                                    </pre>
                                </div>
                            </>
                        ) : (
                            <div className="empty-code-state">
                                <Code size={48} />
                                <p>No block selected</p>
                                <span>Generate or select a block to view its code</span>
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
};

export default EDSBlockBuilder;
