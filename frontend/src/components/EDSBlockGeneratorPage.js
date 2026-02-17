import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import {
  Send,
  Upload,
  Search,
  Plus,
  Trash2,
  MessageSquare,
  X,
  Copy,
  Check,
  Download
} from 'lucide-react';
import { apiConfig } from '../config/apiConfig.js';
import { downloadZipFromBase64 } from '../utils/zipdownload.js';
import MkdTable from './MarkdownTable';
import ImageUploadPanel from './ImageUploadPanel';

const API_BASE_URL = apiConfig.baseUrl;

export default function EDSBlockGeneratorPage() {
  // Chat session state
  const [chatSessions, setChatSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [showNewSessionModal, setShowNewSessionModal] = useState(false);
  const [sessionTitle, setSessionTitle] = useState('');

  // Message and component state
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [generatedBlocks, setGeneratedBlocks] = useState([]);
  const [selectedBlock, setSelectedBlock] = useState(null);

  // Image upload state
  const [uploadedImageData, setUploadedImageData] = useState(null);
  const [designAnalysis, setDesignAnalysis] = useState(null);

  // UI state
  const [leftPanelOpen, setLeftPanelOpen] = useState(true);
  const [rightPanelOpen, setRightPanelOpen] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [activeCodeTab, setActiveCodeTab] = useState('css');
  const [copiedSection, setCopiedSection] = useState(null);

  const messagesEndRef = useRef(null);

  // Load chat sessions on mount
  useEffect(() => {
    loadChatSessions();
  }, []);

  // Load current session when currentSessionId changes
  useEffect(() => {
    if (currentSessionId) {
      loadCurrentSession();
    }
  }, [currentSessionId]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Auto-select latest block when generatedBlocks updates
  useEffect(() => {
    console.log('🔄 generatedBlocks changed:', generatedBlocks.length, generatedBlocks);
    if (generatedBlocks.length > 0) {
      const latestBlock = generatedBlocks[generatedBlocks.length - 1];
      console.log('✅ Setting selectedBlock to:', latestBlock.name);
      setSelectedBlock(latestBlock);
      setRightPanelOpen(true);
    } else {
      // Clear selected block when there are no blocks
      console.log('🚫 No blocks, clearing selectedBlock and closing right panel');
      setSelectedBlock(null);
      setRightPanelOpen(false);
    }
  }, [generatedBlocks]);

  const loadChatSessions = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}${apiConfig.endpoints.edsGetSessions}`);
      if (response.data.success) {
        setChatSessions(response.data.sessions);
      }
    } catch (error) {
      console.error('Failed to load EDS chat sessions:', error);
    }
  };

  const loadCurrentSession = async () => {
    if (!currentSessionId) return;

    try {
      const endpoint = typeof apiConfig.endpoints.edsGetSession === 'function'
        ? apiConfig.endpoints.edsGetSession(currentSessionId)
        : apiConfig.endpoints.edsGetSession.replace('{session_id}', currentSessionId);

      const response = await axios.get(`${API_BASE_URL}${endpoint}`);

      if (response.data.success) {
        const session = response.data.session;

        // Convert messages to UI format
        const formattedMessages = session.messages.map(msg => ({
          id: msg.id,
          text: msg.content,
          sender: msg.message_type === 'user' ? 'user' : 'ai',
          timestamp: new Date(msg.timestamp).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          }),
        }));

        // Convert components to UI format
        const formattedBlocks = session.generated_components.map(comp => ({
          id: comp.component_id,
          name: comp.component_name,
          timestamp: new Date(comp.generation_timestamp).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          }),
          code: {
            css: comp.client_lib?.css || '',
            js: comp.client_lib?.js || '',
            mkd_table: comp.client_lib?.mkd_table || '',
            zip_base64: comp.client_lib?.zip_base64 || '',
            file_name: comp.client_lib?.file_name || ''
          }
        }));

        setMessages(formattedMessages);
        setGeneratedBlocks(formattedBlocks);
      }
    } catch (error) {
      console.error('Failed to load current session:', error);
      if (error.response?.status === 404) {
        setCurrentSessionId(null);
        setMessages([]);
        setGeneratedBlocks([]);
        setSelectedBlock(null);
      }
    }
  };

  const createNewSession = async () => {
    try {
      const response = await axios.post(`${API_BASE_URL}${apiConfig.endpoints.edsCreateSession}`, {
        session_title: sessionTitle || `New EDS Chat - ${new Date().toLocaleDateString()}`,
        user_id: 'default_user',
        model_provider: 'openai'
      });

      if (response.data.success) {
        const newSessionId = response.data.session_id;
        setCurrentSessionId(newSessionId);
        setMessages([]);
        setGeneratedBlocks([]);
        setSelectedBlock(null);
        setShowNewSessionModal(false);
        setSessionTitle('');

        setTimeout(() => {
          loadChatSessions();
        }, 100);
      }
    } catch (error) {
      console.error('Failed to create new session:', error);
    }
  };

  const deleteSession = async (sessionId, event) => {
    event.stopPropagation();
    try {
      const endpoint = typeof apiConfig.endpoints.edsDeleteSession === 'function'
        ? apiConfig.endpoints.edsDeleteSession(sessionId)
        : apiConfig.endpoints.edsDeleteSession.replace('{session_id}', sessionId);

      const response = await axios.delete(`${API_BASE_URL}${endpoint}`);
      if (response.data.success) {
        if (currentSessionId === sessionId) {
          setCurrentSessionId(null);
          setMessages([]);
          setGeneratedBlocks([]);
          setSelectedBlock(null);
        }
        loadChatSessions();
      }
    } catch (error) {
      console.error('Failed to delete session:', error);
    }
  };

  const searchSessions = async () => {
    if (!searchTerm.trim()) {
      loadChatSessions();
      return;
    }

    try {
      const response = await axios.get(
        `${API_BASE_URL}${apiConfig.endpoints.edsSearchSessions}?q=${encodeURIComponent(searchTerm)}`
      );
      if (response.data.success) {
        setChatSessions(response.data.sessions);
      }
    } catch (error) {
      console.error('Failed to search sessions:', error);
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    // Create new session if none exists
    if (!currentSessionId) {
      setIsLoading(true);
      try {
        const tempTitle = inputMessage.substring(0, 50) + (inputMessage.length > 50 ? '...' : '');
        const response = await axios.post(`${API_BASE_URL}${apiConfig.endpoints.edsCreateSession}`, {
          session_title: tempTitle,
          user_id: 'default_user',
          model_provider: 'openai'
        });

        if (response.data.success) {
          const newSessionId = response.data.session_id;
          setCurrentSessionId(newSessionId);
          await sendMessageToSession(newSessionId);
          loadChatSessions();
        }
      } catch (error) {
        console.error('Failed to create new session:', error);
        setIsLoading(false);
      }
      return;
    }

    // Send message to existing session
    await sendMessageToSession(currentSessionId);
  };

  const sendMessageToSession = async (sessionId) => {
    setIsLoading(true);

    try {
      // Build request payload
      const payload = {
        description: inputMessage,
        sessionId: sessionId,
        userId: 'default_user'
      };

      // Add image data if available
      if (uploadedImageData) {
        payload.imageUrl = uploadedImageData.imageUrl;
      }

      // Add design analysis if available
      if (designAnalysis) {
        payload.designAnalysis = designAnalysis;
      }

      const response = await axios.post(
        apiConfig.getFullUrl(apiConfig.endpoints.generateEdsBlock),
        payload
      );

      if (response.data) {
        // Reload session to get updated messages and blocks
        await loadCurrentSession();
        loadChatSessions();

        // Clear image data after successful generation
        setUploadedImageData(null);
        setDesignAnalysis(null);
      }

      setInputMessage('');
    } catch (error) {
      console.error('Error generating EDS block:', error);
      alert('Error generating block');
    } finally {
      setIsLoading(false);
    }
  };

  const handleImageUpload = (imageData) => {
    console.log('Image uploaded:', imageData);
    setUploadedImageData(imageData);
  };

  const handleAnalysisComplete = (analysis) => {
    console.log('Design analysis complete:', analysis);
    setDesignAnalysis(analysis);

    // Auto-fill input with detected block type if available
    if (analysis.blockType && !inputMessage) {
      setInputMessage(`Create a ${analysis.blockType} block`);
    }
  };

  const handleCopyCode = (section) => {
    if (selectedBlock) {
      const code = selectedBlock.code[section] || '';
      navigator.clipboard.writeText(code);
      setCopiedSection(section);
      setTimeout(() => setCopiedSection(null), 2000);
    }
  };

  const handleDownload = () => {
    if (selectedBlock?.code?.zip_base64) {
      downloadZipFromBase64(selectedBlock.code.zip_base64, selectedBlock.code.file_name);
    }
  };

  const filteredSessions = searchTerm
    ? chatSessions.filter(session =>
      session.session_title.toLowerCase().includes(searchTerm.toLowerCase())
    )
    : chatSessions;

  return (
    <div style={{ display: 'flex', height: '100vh', backgroundColor: '#0f172a', color: '#e2e8f0' }}>
      {/* Left Panel - Chat History */}
      {leftPanelOpen && (
        <div style={{
          width: '300px',
          borderRight: '1px solid #1e293b',
          display: 'flex',
          flexDirection: 'column',
          backgroundColor: '#1e293b'
        }}>
          <div style={{ padding: '1rem', borderBottom: '1px solid #334155' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
              <MessageSquare size={20} />
              <h2 style={{ margin: 0, fontSize: '1.1rem' }}>EDS Chat History</h2>
            </div>

            {/* Search */}
            <div style={{ position: 'relative', marginBottom: '0.5rem' }}>
              <Search size={16} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: '#64748b' }} />
              <input
                type="text"
                placeholder="Search sessions..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyUp={searchSessions}
                style={{
                  width: '100%',
                  padding: '0.5rem 0.5rem 0.5rem 2.5rem',
                  backgroundColor: '#0f172a',
                  border: '1px solid #334155',
                  borderRadius: '6px',
                  color: '#e2e8f0',
                  fontSize: '0.875rem'
                }}
              />
            </div>

            {/* New Chat Button */}
            <button
              onClick={() => setShowNewSessionModal(true)}
              style={{
                width: '100%',
                padding: '0.5rem',
                backgroundColor: '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem',
                fontSize: '0.875rem',
                fontWeight: '500'
              }}
            >
              <Plus size={16} />
              New Chat
            </button>
          </div>

          {/* Sessions List */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '0.5rem' }}>
            {filteredSessions.map(session => (
              <div
                key={session.session_id}
                onClick={() => setCurrentSessionId(session.session_id)}
                style={{
                  padding: '0.75rem',
                  marginBottom: '0.5rem',
                  backgroundColor: currentSessionId === session.session_id ? '#334155' : '#0f172a',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  border: '1px solid #334155',
                  position: 'relative'
                }}
              >
                <div style={{ fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.25rem' }}>
                  {session.session_title}
                </div>
                <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
                  {session.component_count} blocks • {new Date(session.updated_at).toLocaleDateString()}
                </div>
                <button
                  onClick={(e) => deleteSession(session.session_id, e)}
                  style={{
                    position: 'absolute',
                    top: '0.5rem',
                    right: '0.5rem',
                    background: 'none',
                    border: 'none',
                    color: '#64748b',
                    cursor: 'pointer',
                    padding: '0.25rem'
                  }}
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Center Panel - Chat Interface */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <div style={{
          padding: '1rem',
          borderBottom: '1px solid #1e293b',
          backgroundColor: '#1e293b'
        }}>
          <h1 style={{ margin: 0, fontSize: '1.5rem' }}>EDS Block Generator</h1>
          <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.875rem', color: '#64748b' }}>
            AI-Powered Edge Delivery Services Block Creation
          </p>
        </div>

        {/* Messages Area */}
        <div style={{
          flex: 1,
          overflowY: 'auto',
          padding: '1rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '1rem'
        }}>
          {!currentSessionId ? (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
              color: '#64748b',
              textAlign: 'center'
            }}>
              <div>
                <MessageSquare size={48} style={{ margin: '0 auto 1rem' }} />
                <p>Create a new chat session to start generating EDS blocks</p>
              </div>
            </div>
          ) : (
            <>
              {messages.map(msg => (
                <div
                  key={msg.id}
                  style={{
                    alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                    maxWidth: '70%',
                    padding: '0.75rem 1rem',
                    backgroundColor: msg.sender === 'user' ? '#3b82f6' : '#1e293b',
                    borderRadius: '12px',
                    fontSize: '0.875rem'
                  }}
                >
                  <div>{msg.text}</div>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
                    {msg.timestamp}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div style={{
                  alignSelf: 'flex-start',
                  padding: '0.75rem 1rem',
                  backgroundColor: '#1e293b',
                  borderRadius: '12px',
                  fontSize: '0.875rem'
                }}>
                  Generating EDS block...
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input Area */}
        <div style={{
          padding: '1rem',
          borderTop: '1px solid #1e293b',
          backgroundColor: '#1e293b'
        }}>
          {/* Image Upload Panel */}
          {currentSessionId && (
            <div style={{ marginBottom: '1rem' }}>
              <ImageUploadPanel
                onImageUpload={handleImageUpload}
                onAnalysisComplete={handleAnalysisComplete}
              />
            </div>
          )}

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <input
              type="text"
              placeholder={uploadedImageData ? "Describe what you want (design image uploaded)" : "Describe the EDS block you want to generate..."}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              disabled={isLoading}
              style={{
                flex: 1,
                padding: '0.75rem',
                backgroundColor: '#0f172a',
                border: uploadedImageData ? '2px solid #4CAF50' : '1px solid #334155',
                borderRadius: '8px',
                color: '#e2e8f0',
                fontSize: '0.875rem'
              }}
            />
            <button
              onClick={handleSendMessage}
              disabled={isLoading || !inputMessage.trim()}
              style={{
                padding: '0.75rem 1.5rem',
                backgroundColor: isLoading || !inputMessage.trim() ? '#334155' : '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: isLoading || !inputMessage.trim() ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}
            >
              <Send size={16} />
              Send
            </button>
          </div>
        </div>
      </div>

      {/* Right Panel - Code Preview */}
      {rightPanelOpen && selectedBlock && (
        <div style={{
          width: '400px',
          borderLeft: '1px solid #1e293b',
          display: 'flex',
          flexDirection: 'column',
          backgroundColor: '#1e293b'
        }}>
          <div style={{ padding: '1rem', borderBottom: '1px solid #334155' }}>
            <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '1.1rem' }}>Generated Block</h3>
            <p style={{ margin: 0, fontSize: '0.875rem', color: '#64748b' }}>
              {selectedBlock.name}
            </p>
          </div>

          {/* Code Tabs */}
          <div style={{ display: 'flex', borderBottom: '1px solid #334155', padding: '0 1rem' }}>
            {['css', 'js', 'mkd_table'].map(tab => (
              <button
                key={tab}
                onClick={() => setActiveCodeTab(tab)}
                style={{
                  padding: '0.75rem 1rem',
                  backgroundColor: 'transparent',
                  color: activeCodeTab === tab ? '#3b82f6' : '#64748b',
                  border: 'none',
                  borderBottom: activeCodeTab === tab ? '2px solid #3b82f6' : 'none',
                  cursor: 'pointer',
                  fontSize: '0.875rem',
                  fontWeight: '500'
                }}
              >
                {tab === 'mkd_table' ? 'Table' : tab.toUpperCase()}
              </button>
            ))}
          </div>

          {/* Code Content */}
          <div style={{ flex: 1, overflow: 'auto', padding: '1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ fontSize: '0.875rem', color: '#64748b' }}>
                {activeCodeTab === 'mkd_table' ? 'Markdown Table' : activeCodeTab.toUpperCase()}
              </span>
              <button
                onClick={() => handleCopyCode(activeCodeTab)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#64748b',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.25rem',
                  fontSize: '0.875rem'
                }}
              >
                {copiedSection === activeCodeTab ? <Check size={14} /> : <Copy size={14} />}
                {copiedSection === activeCodeTab ? 'Copied!' : 'Copy'}
              </button>
            </div>

            {activeCodeTab === 'mkd_table' ? (
              <MkdTable tableData={selectedBlock.code.mkd_table || ''} />
            ) : (
              <pre style={{
                backgroundColor: '#0f172a',
                padding: '1rem',
                borderRadius: '6px',
                fontSize: '0.75rem',
                overflow: 'auto',
                margin: 0,
                border: '1px solid #334155'
              }}>
                <code>{selectedBlock.code[activeCodeTab] || ''}</code>
              </pre>
            )}
          </div>

          {/* Download Button */}
          <div style={{ padding: '1rem', borderTop: '1px solid #334155' }}>
            <button
              onClick={handleDownload}
              style={{
                width: '100%',
                padding: '0.75rem',
                backgroundColor: '#10b981',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem',
                fontSize: '0.875rem',
                fontWeight: '500'
              }}
            >
              <Download size={16} />
              Download ZIP
            </button>
          </div>
        </div>
      )}

      {/* New Session Modal */}
      {showNewSessionModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: '#1e293b',
            padding: '2rem',
            borderRadius: '12px',
            width: '400px',
            border: '1px solid #334155'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
              <h3 style={{ margin: 0 }}>New EDS Chat Session</h3>
              <button
                onClick={() => setShowNewSessionModal(false)}
                style={{ background: 'none', border: 'none', color: '#64748b', cursor: 'pointer' }}
              >
                <X size={20} />
              </button>
            </div>
            <input
              type="text"
              placeholder="Session title (optional)"
              value={sessionTitle}
              onChange={(e) => setSessionTitle(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && createNewSession()}
              style={{
                width: '100%',
                padding: '0.75rem',
                backgroundColor: '#0f172a',
                border: '1px solid #334155',
                borderRadius: '8px',
                color: '#e2e8f0',
                marginBottom: '1rem'
              }}
            />
            <button
              onClick={createNewSession}
              style={{
                width: '100%',
                padding: '0.75rem',
                backgroundColor: '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontWeight: '500'
              }}
            >
              Create Session
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
