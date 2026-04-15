import React, { useState } from 'react';
import './Header.css';

const Header = ({ onLoginClick }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <header className="header animate-fade-in">
      <div className="container header-container">
        <div className="logo">Hilary AI</div>
        
        <button 
          className="mobile-menu-toggle" 
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          aria-label="Toggle Navigation"
        >
          <div className={`hamburger ${isMenuOpen ? 'open' : ''}`}></div>
        </button>

        <nav className={`nav-links ${isMenuOpen ? 'active' : ''}`}>
          <a href="#about" onClick={() => setIsMenuOpen(false)}>ABOUT</a>
          <a href="#objectives" onClick={() => setIsMenuOpen(false)}>OBJECTIVES</a>
          <a href="#modalities" onClick={() => setIsMenuOpen(false)}>MODALITIES</a>
          <a href="#system" onClick={() => setIsMenuOpen(false)}>SYSTEM</a>
          <a href="#privacy" onClick={() => setIsMenuOpen(false)}>PRIVACY</a>
          <button className="btn mobile-cta" onClick={() => { onLoginClick(); setIsMenuOpen(false); }}>
            GET STARTED
          </button>
        </nav>

        <button className="btn desktop-cta" onClick={onLoginClick}>GET STARTED</button>
      </div>
    </header>
  );
};

export default Header;
