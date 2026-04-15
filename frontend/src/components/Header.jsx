import React from 'react';
import './Header.css';

const Header = ({ onLoginClick }) => {
  return (
    <header className="header animate-fade-in">
      <div className="container header-container">
        <div className="logo">MindScape</div>
        <nav className="nav-links">
          <a href="#about">ABOUT</a>
          <a href="#objectives">OBJECTIVES</a>
          <a href="#modalities">MODALITIES</a>
          <a href="#system">SYSTEM</a>
          <a href="#privacy">PRIVACY</a>
        </nav>
        <button className="btn" onClick={onLoginClick}>GET STARTED</button>
      </div>
    </header>
  );
};


export default Header;
