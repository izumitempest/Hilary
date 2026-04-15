import React from 'react';
import './Modalities.css';

const Modalities = () => {
  return (
    <section className="modalities" id="modalities">
      <div className="container">
        <div className="mod-header">
          <div className="mod-tag">02 — Modalities</div>
          <h2 className="mod-title">
            Four streams,<br/>
            <span>one coherent picture</span>
          </h2>
        </div>
        
        <div className="mod-tabs">
          <div className="tab active">TEXT</div>
          <div className="tab">SPEECH</div>
          <div className="tab">FACIAL</div>
          <div className="tab">SCREEN USAGE</div>
        </div>
        
        <div className="mod-content">
          <div className="mod-text">
            <h3>Text sentiment<br/>analysis</h3>
            <p> Natural language processing models analyze typed input — journal entries, chat messages, or free-form notes — to detect sentiment shifts, emotional keywords, and linguistic markers associated with anxiety, depression, or stress.</p>
            <p style={{ marginTop: '1rem', color: 'var(--text-light)', fontSize: '0.9rem' }}> Transformer-based architectures fine-tuned on mental health corpora provide nuanced classification.</p>
          </div>
          <div className="mod-visual">
             <div className="visual-card">
                <div style={{ padding: '2rem', background: '#F5F5F0', borderRadius: '8px', height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'flex-end' }}>
                   <div className="mock-lines">
                     <div className="m-line" style={{ width: '80%' }}></div>
                     <div className="m-line" style={{ width: '60%' }}></div>
                     <div className="m-line" style={{ width: '90%' }}></div>
                     <div className="m-line" style={{ width: '40%' }}></div>
                   </div>
                   <div style={{ marginTop: '2rem', fontSize: '0.8rem', fontFamily: 'monospace', color: 'var(--text-main)' }}>
                      Sentiment: Anxious - 74%
                   </div>
                </div>
             </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Modalities;
