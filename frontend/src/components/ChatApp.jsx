import React, { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import DashboardApp from './DashboardApp';
import './ChatApp.css';

// eslint-disable-next-line react/prop-types
const ChatApp = ({ onLogout }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [currentState, setCurrentState] = useState('Neutral');
  const [view, setView] = useState('chat'); // 'chat' or 'dashboard'
  const [showCrisisModal, setShowCrisisModal] = useState(false);
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const history = await apiClient.get('/chat/history');
      setMessages(history || []);
      if (history?.length > 0) {
        setCurrentState(history[history.length - 1].emotional_state || 'Neutral');
      }
    } catch (e) {
      console.log('History load error:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleNewSession = async () => {
    if (!window.confirm('Are you sure you want to start a new session? Current history will be cleared.')) return;
    try {
      setSending(true);
      await apiClient.delete('/chat/history');
      setMessages([]);
      setCurrentState('Neutral');
    } catch (e) {
      console.error(e);
    } finally {
      setSending(false);
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || sending) return;

    const userContent = input;
    setInput('');
    setSending(true);

    try {
      let image_b64 = null;
      if (imageFile) {
        const reader = new FileReader();
        image_b64 = await new Promise((resolve) => {
          reader.onload = (e) => resolve(e.target.result.split(',')[1]);
          reader.readAsDataURL(imageFile);
        });
      }

      const newMsg = { role: 'user', content: userContent, image_preview: imagePreview };
      setMessages(prev => [...prev, newMsg]);

      // Construct payload with context
      const contextMessages = messages.slice(-10).map(m => ({ role: m.role, content: m.content }));
      contextMessages.push({ role: 'user', content: userContent });

      const payload = { messages: contextMessages, text_sentiment: 0.0, image_b64 };
      
      // Clear image input
      setImageFile(null);
      setImagePreview(null);

      const response = await apiClient.post('/chat/', payload);
      setCurrentState(response.emotional_state);
      await loadHistory();
      if (response.emotional_state === 'Critical Distress') {
          setShowCrisisModal(true);
      }
    } catch (e) {
      console.error(e);
      alert('Failed to send message');
    } finally {
      setSending(false);
    }
  };

  const getOrbColor = (state) => {
    switch(state) {
      case 'Critical Distress': return '#D32F2F';
      case 'Distressed/Anxious': return '#FF9800';
      case 'Positive/Happy': return '#4CAF50';
      case 'Calm/Content': return '#2D5A4C';
      default: return '#A890D3';
    }
  };

  return (
    <div className="chat-layout animate-fade-in">
      {/* Sidebar for Desktop */}
      <div className="chat-sidebar">
        <div className="sidebar-logo">MindScape</div>
        
        <div className="sidebar-nav">
          <button onClick={handleNewSession} className="new-chat-btn">
            <span>+</span> New Session
          </button>
          
          <div className="nav-links">
            <div 
              className={`nav-item ${view === 'chat' ? 'active' : ''}`} 
              onClick={() => setView('chat')}
            >
              Therapy Session
            </div>
            <div 
              className={`nav-item ${view === 'dashboard' ? 'active' : ''}`} 
              onClick={() => setView('dashboard')}
            >
              Mental Health Insights
            </div>
          </div>
        </div>

        <div className="status-section">
          <div className="status-orb" style={{ backgroundColor: getOrbColor(currentState) }}>
            {currentState}
          </div>
          <p className="status-label">CURRENT STATE</p>
        </div>
        
        <div className="sidebar-footer">
          <button onClick={() => { apiClient.logout(); onLogout(); }} className="logout-btn-text">Log Out</button>
        </div>
      </div>

      {/* Header and Bottom Nav for Mobile */}
      <div className="mobile-only mobile-header">
        <div className="logo-small">MindScape</div>
        <button onClick={() => { apiClient.logout(); onLogout(); }} className="mobile-logout">
          Logout
        </button>
      </div>
      
      <div className="mobile-only mobile-tabs">
        <div 
          className={`tab-item ${view === 'chat' ? 'active' : ''}`} 
          onClick={() => setView('chat')}
        >
          Session
        </div>
        <div 
          className={`tab-item ${view === 'dashboard' ? 'active' : ''}`} 
          onClick={() => setView('dashboard')}
        >
          Insights
        </div>
        <div className="tab-item" onClick={handleNewSession} style={{ color: 'var(--bg-dark-green)' }}>
          Reset
        </div>
      </div>
      
      <div className="chat-main">
        {view === 'chat' ? (
          <>
            <div className="chat-history">
              {loading ? (
                <div className="loading-state">Establishing connection...</div>
              ) : (
                messages.map((m, idx) => (
                  <div key={m.id || `msg-${idx}`} className={`chat-bubble ${m.role === 'user' ? 'user' : 'assistant'}`}>
                    {m.image_preview && <img src={m.image_preview} alt="Upload preview" style={{maxWidth: '100%', borderRadius: '12px', marginBottom: '10px', display: 'block'}} />}
                    {m.content}
                  </div>
                ))
              )}
              {sending && <div className="chat-bubble assistant typing">Thinking...</div>}
            </div>
            
            <div className="chat-input-wrapper">
              {imagePreview && (
                <div className="image-preview-container" style={{ position: 'relative', display: 'inline-block', marginBottom: '10px' }}>
                  <img src={imagePreview} alt="Preview" style={{ height: '60px', borderRadius: '8px' }} />
                  <button onClick={() => { setImageFile(null); setImagePreview(null); }} style={{ position: 'absolute', top: '-5px', right: '-5px', background: 'red', color: 'white', borderRadius: '50%', width: '20px', height: '20px', border: 'none', cursor: 'pointer', fontSize: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>&times;</button>
                </div>
              )}
              <form onSubmit={handleSend} className="chat-input-area">
                <label className="image-upload-btn" style={{ cursor: 'pointer', color: 'var(--bg-dark-green)', display: 'flex', alignItems: 'center', padding: '10px' }}>
                  <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
                  <input type="file" accept="image/*" onChange={(e) => {
                    const file = e.target.files[0];
                    if (file) {
                      setImageFile(file);
                      setImagePreview(URL.createObjectURL(file));
                    }
                  }} style={{ display: 'none' }} />
                </label>
                <input 
                  type="text" 
                  value={input} 
                  onChange={(e) => setInput(e.target.value)} 
                  placeholder="Type your thoughts here..." 
                  disabled={sending}
                />
                <button type="submit" className="send-btn" disabled={sending}>
                  <svg viewBox="0 0 24 24" width="24" height="24"><path fill="currentColor" d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"></path></svg>
                </button>
              </form>
            </div>
          </>
        ) : (
          <DashboardApp />
        )}
      </div>

      {showCrisisModal && (
        <div className="crisis-overlay animate-fade-in" style={{
            position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', 
            backgroundColor: 'rgba(0,0,0,0.85)', zIndex: 2000, display: 'flex', 
            alignItems: 'center', justifyContent: 'center', padding: '20px'
        }}>
          <div className="auth-card" style={{ maxWidth: '500px', textAlign: 'center' }}>
            <h2 style={{ fontFamily: 'Playfair Display', color: '#D32F2F', marginBottom: '15px' }}>We're here for you.</h2>
            <p style={{ color: 'var(--text-light)', marginBottom: '25px', lineHeight: '1.6' }}>
              Your safety is our absolute priority. It sounds like you're going through an incredibly difficult time right now. Please consider reaching out to one of these free, confidential resources:
            </p>
            
            <div style={{ textAlign: 'left', marginBottom: '30px' }}>
                <div style={{ marginBottom: '15px', padding: '15px', backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: '12px' }}>
                    <strong style={{color: '#fff'}}>National Suicide and Crisis Lifeline</strong><br/>
                    <small style={{ color: '#ff6b6b' }}>Call or Text 988 (Available 24/7)</small>
                </div>
                <div style={{ padding: '15px', backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: '12px' }}>
                    <strong style={{color: '#fff'}}>Crisis Text Line</strong><br/>
                    <small style={{ color: '#ff6b6b' }}>Text HOME to 741741</small>
                </div>
            </div>

            <button onClick={() => setShowCrisisModal(false)} className="btn auth-btn" style={{ backgroundColor: '#D32F2F', border: 'none' }}>
                I'M SAFE NOW, CONTINUE SESSION
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatApp;
