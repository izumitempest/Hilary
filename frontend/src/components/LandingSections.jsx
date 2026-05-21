import React from 'react';

const sectionStyle = {
  padding: '5rem 0',
  borderTop: '1px solid rgba(0,0,0,0.05)',
};

const tagStyle = {
  fontFamily: 'monospace',
  fontSize: '0.75rem',
  color: 'var(--text-light)',
  marginBottom: '1rem',
  letterSpacing: '1px',
};

const LandingSections = () => (
  <>
    <section id="about" style={{ ...sectionStyle, backgroundColor: 'var(--bg-cream)' }}>
      <div className="container">
        <div style={tagStyle}>ABOUT</div>
        <h2 style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>Clinical empathy, powered by AI</h2>
        <p style={{ maxWidth: '640px', lineHeight: 1.7, color: 'var(--text-light)' }}>
          MindScape fuses conversational therapy with behavioral signals and facial expression analysis
          so support adapts to how you feel — not only what you type.
        </p>
      </div>
    </section>

    <section id="objectives" style={{ ...sectionStyle, backgroundColor: 'var(--bg-surface)' }}>
      <div className="container">
        <div style={tagStyle}>OBJECTIVES</div>
        <ul style={{ maxWidth: '640px', lineHeight: 1.9, color: 'var(--text-main)', paddingLeft: '1.2rem' }}>
          <li>Early detection of emotional distress across multiple input streams</li>
          <li>Personalized, evidence-informed therapeutic dialogue (CBT / DBT aligned)</li>
          <li>Proactive safety monitoring with crisis-resource escalation</li>
        </ul>
      </div>
    </section>

    <section id="system" style={{ ...sectionStyle, backgroundColor: 'var(--bg-cream)' }}>
      <div className="container">
        <div style={tagStyle}>SYSTEM</div>
        <p style={{ maxWidth: '640px', lineHeight: 1.7, color: 'var(--text-light)' }}>
          A secure API handles authentication, therapy chat, and multimodal fusion. Vision runs on dedicated inference
          infrastructure; the web app connects through encrypted, authenticated endpoints.
        </p>
      </div>
    </section>

    <section id="privacy" style={{ ...sectionStyle, backgroundColor: 'var(--bg-surface)' }}>
      <div className="container">
        <div style={tagStyle}>PRIVACY</div>
        <p style={{ maxWidth: '640px', lineHeight: 1.7, color: 'var(--text-light)' }}>
          Sessions are tied to your account via JWT. Images are analyzed in memory for inference and are not stored
          as separate media files on the server. Conversation text is persisted to support continuity of care.
        </p>
      </div>
    </section>
  </>
);

export default LandingSections;
