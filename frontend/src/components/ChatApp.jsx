import React, { useState, useEffect, useRef } from 'react';
import { apiClient } from '../api/client';
import DashboardApp from './DashboardApp';
import { logMobileBehaviorSnapshot, openUsageSettings } from '../mobile/usageStats';
import './ChatApp.css';

const IMAGE_PREVIEW_KEY = 'hilary_image_previews';

const stripPhotoMarkers = (content) =>
  (content || '')
    .replace(/\n?\[Photo attached\]/g, '')
    .replace(/\[Photo shared for emotional analysis\]/g, '')
    .trim();

const attachImagePreviews = (history) => {
  let previews = {};
  try {
    previews = JSON.parse(sessionStorage.getItem(IMAGE_PREVIEW_KEY) || '{}');
  } catch {
    previews = {};
  }
  return (history || []).map((m) => {
    const hasPhoto = m.content?.includes('[Photo');
    return {
      ...m,
      image_preview: hasPhoto && m.id ? previews[String(m.id)] : null,
      displayContent: stripPhotoMarkers(m.content) || (hasPhoto ? '' : m.content),
    };
  });
};

// eslint-disable-next-line react/prop-types
const ChatApp = ({ onLogout }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [currentState, setCurrentState] = useState('Neutral');
  const [view, setView] = useState('chat');
  const [showCrisisModal, setShowCrisisModal] = useState(false);
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [lastVision, setLastVision] = useState(null);
  const pendingImagePreviewRef = useRef(null);

  useEffect(() => {
    loadHistory();
  }, []);

  useEffect(() => {
    logMobileBehaviorSnapshot(apiClient);
  }, []);

  const loadHistory = async () => {
    try {
      const history = await apiClient.get('/chat/history');
      setMessages(attachImagePreviews(history));
      if (history?.length > 0) {
        setCurrentState(history[history.length - 1].emotional_state || 'Neutral');
      }
    } catch (e) {
      console.log('History load error:', e);
    } finally {
      setLoading(false);
    }
  };

  const saveImagePreviewForMessage = (messageId, previewUrl) => {
    if (!messageId || !previewUrl) return;
    try {
      const previews = JSON.parse(sessionStorage.getItem(IMAGE_PREVIEW_KEY) || '{}');
      previews[String(messageId)] = previewUrl;
      sessionStorage.setItem(IMAGE_PREVIEW_KEY, JSON.stringify(previews));
    } catch {
      /* ignore quota errors */
    }
  };

  const handleNewSession = async () => {
    if (!window.confirm('Are you sure you want to start a new session? Current history will be cleared.')) return;
    try {
      setSending(true);
      await apiClient.delete('/chat/history');
      setMessages([]);
      setCurrentState('Neutral');
      setLastVision(null);
      sessionStorage.removeItem(IMAGE_PREVIEW_KEY);
    } catch (e) {
      console.error(e);
    } finally {
      setSending(false);
    }
  };

  const readImageAsBase64 = (file) =>
    new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = (ev) => resolve(ev.target.result.split(',')[1]);
      reader.readAsDataURL(file);
    });

  const handleSend = async (e) => {
    e.preventDefault();
    const text = input.trim();
    if ((!text && !imageFile) || sending) return;

    const userContent = text || (imageFile ? 'Shared a photo for emotional analysis' : '');
    const previewForMessage = imagePreview;
    pendingImagePreviewRef.current = previewForMessage;

    setInput('');
    setSending(true);

    try {
      let image_b64 = null;
      if (imageFile) {
        image_b64 = await readImageAsBase64(imageFile);
      }

      const newMsg = {
        role: 'user',
        content: userContent,
        displayContent: userContent,
        image_preview: previewForMessage,
      };
      setMessages((prev) => [...prev, newMsg]);

      const contextMessages = messages.slice(-10).map((m) => ({
        role: m.role,
        content: stripPhotoMarkers(m.content) || m.displayContent || m.content,
      }));
      contextMessages.push({ role: 'user', content: userContent });

      const payload = {
        messages: contextMessages,
        text_sentiment: 0.0,
        image_b64,
      };

      setImageFile(null);
      setImagePreview(null);

      const response = await apiClient.post('/chat/', payload);
      setCurrentState(response.emotional_state);
      if (response.face_emotion) {
        setLastVision({ emotion: response.face_emotion });
      }

      const history = await apiClient.get('/chat/history');
      const withPreviews = attachImagePreviews(history);
      if (pendingImagePreviewRef.current) {
        const lastUser = [...withPreviews].reverse().find((m) => m.role === 'user');
        if (lastUser?.id) {
          saveImagePreviewForMessage(lastUser.id, pendingImagePreviewRef.current);
          lastUser.image_preview = pendingImagePreviewRef.current;
        }
      }
      setMessages(withPreviews);
      pendingImagePreviewRef.current = null;

      if (response.emotional_state === 'Critical Distress') {
        setShowCrisisModal(true);
      }
    } catch (err) {
      console.error(err);
      alert('Failed to send message');
    } finally {
      setSending(false);
    }
  };

  const getOrbColor = (state) => {
    switch (state) {
      case 'Critical Distress':
        return '#D32F2F';
      case 'Distressed/Anxious':
        return '#FF9800';
      case 'Positive/Happy':
        return '#4CAF50';
      case 'Calm/Content':
        return '#2D5A4C';
      default:
        return '#A890D3';
    }
  };

  const canSend = (input.trim() || imageFile) && !sending;

  return (
    <div className="chat-layout animate-fade-in">
      <div className="chat-sidebar">
        <div className="sidebar-logo">MindScape</div>

        <div className="sidebar-nav">
          <button onClick={handleNewSession} className="new-chat-btn" type="button">
            <span>+</span> New Session
          </button>

          <div className="nav-links">
            <div
              className={`nav-item ${view === 'chat' ? 'active' : ''}`}
              onClick={() => setView('chat')}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && setView('chat')}
            >
              Therapy Session
            </div>
            <div
              className={`nav-item ${view === 'dashboard' ? 'active' : ''}`}
              onClick={() => setView('dashboard')}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && setView('dashboard')}
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
          <button type="button" className="usage-access-link" onClick={openUsageSettings}>
            Enable app usage access
          </button>
          {lastVision && (
            <p className="vision-hint">From photo: {lastVision.emotion}</p>
          )}
        </div>

        <div className="sidebar-footer">
          <button
            type="button"
            onClick={() => {
              apiClient.logout();
              onLogout();
            }}
            className="logout-btn-text"
          >
            Log Out
          </button>
        </div>
      </div>

      <div className="mobile-only mobile-header">
        <div className="logo-small">MindScape</div>
        <button
          type="button"
          onClick={() => {
            apiClient.logout();
            onLogout();
          }}
          className="mobile-logout"
        >
          Logout
        </button>
      </div>

      <div className="mobile-only mobile-tabs">
        <div
          className={`tab-item ${view === 'chat' ? 'active' : ''}`}
          onClick={() => setView('chat')}
          role="button"
          tabIndex={0}
        >
          Session
        </div>
        <div
          className={`tab-item ${view === 'dashboard' ? 'active' : ''}`}
          onClick={() => setView('dashboard')}
          role="button"
          tabIndex={0}
        >
          Insights
        </div>
        <div
          className="tab-item"
          onClick={handleNewSession}
          style={{ color: 'var(--bg-dark-green)' }}
          role="button"
          tabIndex={0}
        >
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
                    {m.image_preview && (
                      <img
                        src={m.image_preview}
                        alt="Shared"
                        className="chat-image-preview"
                      />
                    )}
                    {!m.image_preview && m.content?.includes('[Photo') && (
                      <div className="chat-photo-placeholder">Photo analyzed</div>
                    )}
                    {(m.displayContent ?? stripPhotoMarkers(m.content)) && (
                      <span>{m.displayContent ?? stripPhotoMarkers(m.content)}</span>
                    )}
                  </div>
                ))
              )}
              {sending && <div className="chat-bubble assistant typing">Analyzing & thinking...</div>}
            </div>

            <div className="chat-input-wrapper">
              {imagePreview && (
                <div className="image-preview-container">
                  <img src={imagePreview} alt="Preview" className="image-preview-thumb" />
                  <button
                    type="button"
                    aria-label="Remove image"
                    onClick={() => {
                      setImageFile(null);
                      setImagePreview(null);
                    }}
                    className="image-preview-remove"
                  >
                    &times;
                  </button>
                </div>
              )}
              <form onSubmit={handleSend} className="chat-input-area">
                <label className="image-upload-btn" title="Attach photo for facial analysis">
                  <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                    <circle cx="8.5" cy="8.5" r="1.5" />
                    <polyline points="21 15 16 10 5 21" />
                  </svg>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) {
                        setImageFile(file);
                        setImagePreview(URL.createObjectURL(file));
                      }
                      e.target.value = '';
                    }}
                    style={{ display: 'none' }}
                  />
                </label>
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder={imageFile ? 'Add a caption (optional)...' : 'Type your thoughts here...'}
                  disabled={sending}
                />
                <button type="submit" className="send-btn" disabled={!canSend}>
                  <svg viewBox="0 0 24 24" width="24" height="24">
                    <path fill="currentColor" d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
                  </svg>
                </button>
              </form>
            </div>
          </>
        ) : (
          <DashboardApp />
        )}
      </div>

      {showCrisisModal && (
        <div className="crisis-overlay animate-fade-in">
          <div className="auth-card crisis-card">
            <h2>We&apos;re here for you.</h2>
            <p>
              Your safety is our absolute priority. It sounds like you&apos;re going through an incredibly difficult
              time right now. Please consider reaching out to one of these free, confidential resources:
            </p>

            <div className="crisis-resources">
              <div className="crisis-resource-item">
                <strong>National Suicide and Crisis Lifeline</strong>
                <br />
                <small>Call or Text 988 (Available 24/7)</small>
              </div>
              <div className="crisis-resource-item">
                <strong>Crisis Text Line</strong>
                <br />
                <small>Text HOME to 741741</small>
              </div>
            </div>

            <button type="button" onClick={() => setShowCrisisModal(false)} className="btn auth-btn crisis-continue-btn">
              I&apos;M SAFE NOW, CONTINUE SESSION
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatApp;
