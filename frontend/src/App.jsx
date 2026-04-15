import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import Modalities from './components/Modalities';
import CTA from './components/CTA';
import Footer from './components/Footer';
import Auth from './components/Auth';
import ChatApp from './components/ChatApp';

function App() {
  const [showAuth, setShowAuth] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check if user is already logged in (has token)
    const token = localStorage.getItem('token');
    if (token) {
      setIsAuthenticated(true);
    }
  }, []);

  if (isAuthenticated) {
    return <ChatApp onLogout={() => setIsAuthenticated(false)} />;
  }

  return (
    <>
      <Header onLoginClick={() => setShowAuth(true)} />
      <main>
        <Hero onLoginClick={() => setShowAuth(true)} />
        <Modalities />
        <CTA onLoginClick={() => setShowAuth(true)} />
      </main>
      <Footer />
      
      {showAuth && (
        <Auth 
          onBack={() => setShowAuth(false)} 
          onLoginSuccess={() => {
            setShowAuth(false);
            setIsAuthenticated(true);
          }} 
        />
      )}
    </>
  );
}

export default App;
