import React from 'react';
import './Hero.css';

const Hero = ({ onLoginClick }) => {
  return (
    <section className="hero">
      <div className="container hero-container animate-fade-in" style={{ animationDelay: '0.2s' }}>
        <div className="hero-content">
          <div className="tagline">
            <span className="line"></span>
            MULTIMODAL MENTAL HEALTH INTELLIGENCE
          </div>
          <h1 className="hero-title">
            See the mind<br/>
            <span>before it signals</span><br/>
            for help
          </h1>
          <p className="hero-desc">
            Hilary integrates text, speech, facial expression, and screen behavior into a unified AI system — delivering early detection of mental issues and personalized, real-time therapy.
          </p>
          <div className="hero-actions">
            <button className="btn desktop-hero-btn" onClick={onLoginClick}>EXPLORE THE SYSTEM</button>
            <button className="btn btn-outline desktop-hero-btn" style={{ marginLeft: '15px' }}>VIEW MODALITIES</button>
          </div>
        </div>
        
        <div className="hero-graphic">
          <div className="circle-system">
             <div className="hub">Hilary</div>
             <div className="orbit orbit-1"></div>
             <div className="orbit orbit-2"></div>
             <div className="orbit orbit-3"></div>
             
             {/* Modality nodes */}
             <div className="node text-node">TEXT</div>
             <div className="node voice-node">VOICE</div>
             <div className="node face-node">FACE</div>
             <div className="node screen-node">SCREEN</div>
             <div className="node alert-node">ALERT</div>
             <div className="node ai-node">AI FUSION</div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
