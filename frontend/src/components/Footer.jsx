import React from 'react';

const Footer = () => {
  return (
    <footer style={{ backgroundColor: 'var(--bg-black)', padding: '3rem 0', color: 'var(--text-white)' }}>
      <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ fontFamily: 'Playfair Display', fontSize: '1.25rem' }}>MindScape</div>
        
        <div style={{ display: 'flex', gap: '2rem', fontSize: '0.75rem', color: '#999' }}>
          <a href="#">RESEARCH</a>
          <a href="#">ETHICS</a>
        </div>
        
        <div style={{ fontSize: '0.75rem', color: '#666' }}>
          © 2026 MindScape AI. All rights reserved.
        </div>
      </div>
    </footer>
  );
};

export default Footer;
