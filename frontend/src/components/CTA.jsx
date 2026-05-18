import React from 'react';

const CTA = ({ onLoginClick, onViewModalities }) => {
  return (
    <>
      <div style={{ height: '80px', backgroundColor: 'var(--bg-dark-green)', width: '100%' }}></div>
      <section style={{ padding: '8rem 0', textAlign: 'center', backgroundColor: 'var(--bg-cream)' }}>
        <div className="container">
          <div style={{ fontFamily: 'monospace', fontSize: '0.75rem', color: 'var(--text-light)', letterSpacing: '2px', marginBottom: '2rem' }}>
            JOIN THE EARLY ACCESS PROGRAMME
          </div>
          <h2 style={{ fontSize: '4rem', marginBottom: '3rem', lineHeight: '1.1' }}>
            Ready to monitor<br/>
            the mind <span style={{ fontStyle: 'italic', color: 'var(--bg-dark-green)' }}>intelligently?</span>
          </h2>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem' }}>
            <button className="btn" style={{ backgroundColor: 'var(--bg-dark-green)' }} onClick={onLoginClick}>REQUEST EARLY ACCESS</button>
            <button
              type="button"
              className="btn btn-outline"
              style={{ backgroundColor: 'var(--bg-surface)' }}
              onClick={onViewModalities}
            >
              EXPLORE MODALITIES
            </button>
          </div>
        </div>
      </section>
    </>
  );
};

export default CTA;
