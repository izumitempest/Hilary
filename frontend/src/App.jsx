import React, { useState, useEffect } from 'react';
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

  useEffect(() => {
    // Check if user is already logged in (has token)
    const token = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');
    if (token) {
      setIsAuthenticated(true);
      if (storedUser) setUser(JSON.parse(storedUser));
    }
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
        @keyframes slideDown {
          from { transform: translateY(-100%); }
          to { transform: translateY(0); }
        }
      `}</style>
    </>
  );
}

export default App;
