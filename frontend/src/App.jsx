import React, { useState, useEffect } from 'react';
import { apiClient } from './api/client';
import Header from './components/Header';
import Hero from './components/Hero';
import Modalities from './components/Modalities';
import CTA from './components/CTA';
import Footer from './components/Footer';
import Auth from './components/Auth';
import ChatApp from './components/ChatApp';
import LandingSections from './components/LandingSections';

function App() {
  const scrollToModalities = () => {
    document.getElementById('modalities')?.scrollIntoView({ behavior: 'smooth' });
  };
  const [showAuth, setShowAuth] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [verifyStatus, setVerifyStatus] = useState(null);

  useEffect(() => {
    // Check if user is already logged in (has token)
    const token = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');
    if (token) {
      setIsAuthenticated(true);
      if (storedUser) setUser(JSON.parse(storedUser));
    }
  }, []);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get('verify_token');
    if (!token) return;
    (async () => {
      try {
        await apiClient.verifyEmail(token);
        setVerifyStatus({ type: 'success', message: 'Email verified successfully. You can now sign in.' });
      } catch (e) {
        setVerifyStatus({ type: 'error', message: e.message || 'Verification failed.' });
      } finally {
        params.delete('verify_token');
        const clean = `${window.location.pathname}${params.toString() ? `?${params.toString()}` : ''}`;
        window.history.replaceState({}, '', clean);
      }
    })();
  }, []);

  const handleLoginSuccess = (userData) => {
    setShowAuth(false);
    setIsAuthenticated(true);
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const VerificationBanner = () => {
    if (!isAuthenticated || !user || user.is_verified) return null;
    return (
      <div className="verification-banner">
        <span>Please check your inbox ({user.email}) to verify your account.</span>
        <button
          className="resend-link"
          onClick={async () => {
            await apiClient.resendVerification(user.email);
            alert('Verification email resent.');
          }}
        >
          Resend link
        </button>
      </div>
    );
  };

  if (isAuthenticated) {
    return (
      <>
        <VerificationBanner />
        <ChatApp onLogout={() => {
          setIsAuthenticated(false);
          setUser(null);
          localStorage.removeItem('token');
          localStorage.removeItem('user');
        }} />
      </>
    );
  }

  return (
    <>
      <Header onLoginClick={() => setShowAuth(true)} />
      <main>
        {verifyStatus && (
          <div
            style={{
              padding: '12px 20px',
              textAlign: 'center',
              color: verifyStatus.type === 'success' ? '#2D5A4C' : '#B00020',
              background: verifyStatus.type === 'success' ? '#E6F4EE' : '#FDECEC',
              borderBottom: '1px solid rgba(0,0,0,0.08)',
            }}
          >
            {verifyStatus.message}
          </div>
        )}
        <Hero onLoginClick={() => setShowAuth(true)} onViewModalities={scrollToModalities} />
        <Modalities />
        <LandingSections />
        <CTA onLoginClick={() => setShowAuth(true)} onViewModalities={scrollToModalities} />
      </main>
      <Footer />
      
      {showAuth && (
        <Auth 
          onBack={() => setShowAuth(false)} 
          onLoginSuccess={handleLoginSuccess} 
        />
      )}
      <style>{`
        .verification-banner {
          background: #fff9c4;
          color: #856404;
          padding: 10px 20px;
          text-align: center;
          font-size: 0.85rem;
          font-weight: 500;
          display: flex;
          justify-content: center;
          align-items: center;
          gap: 15px;
          border-bottom: 1px solid #ffeeba;
          position: sticky;
          top: 0;
          z-index: 1100;
          animation: slideDown 0.3s ease-out;
        }
        .resend-link {
          background: #856404;
          color: white;
          border: none;
          padding: 4px 12px;
          border-radius: 4px;
          font-size: 0.75rem;
          cursor: pointer;
          font-weight: 700;
        }
        @keyframes slideDown {
          from { transform: translateY(-100%); }
          to { transform: translateY(0); }
        }
      `}</style>
    </>
  );
}

export default App;
