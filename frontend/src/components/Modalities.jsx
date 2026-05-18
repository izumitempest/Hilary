import React, { useState } from 'react';
import './Modalities.css';

const MODALITIES = [
  {
    id: 'text',
    label: 'TEXT',
    title: 'Text sentiment analysis',
    body: 'Natural language processing analyzes chat and journal input for sentiment shifts, emotional keywords, and linguistic markers associated with anxiety, depression, or stress.',
    detail: 'Keyword heuristics and Groq Llama 3.3 refine the fused emotional state during each therapy turn.',
    visualLabel: 'Sentiment stream',
    visualValue: 'Active in chat',
    barWidths: ['80%', '60%', '90%', '40%'],
  },
  {
    id: 'speech',
    label: 'SPEECH',
    title: 'Voice tone & transcript',
    body: 'Whisper transcribes voice notes while librosa extracts pitch, energy, and tempo to classify prosody (e.g. withdrawn, agitated, calm).',
    detail: 'Use the microphone in your therapy session to send voice clips for tone-aware responses.',
    visualLabel: 'Voice analysis',
    visualValue: 'Whisper + prosody',
    barWidths: ['50%', '70%', '45%', '85%'],
  },
  {
    id: 'facial',
    label: 'FACIAL',
    title: 'Facial expression analysis',
    body: 'Photos are analyzed with a custom PyTorch mental-health image model, with Groq Vision as fallback when needed.',
    detail: 'Attach an image in chat — vision feeds the multimodal fusion engine alongside your words.',
    visualLabel: 'Vision model',
    visualValue: 'PyTorch + Groq Vision',
    barWidths: ['65%', '75%', '55%', '70%'],
  },
  {
    id: 'screen',
    label: 'SCREEN USAGE',
    title: 'Digital behavior signals',
    body: 'Screen time, unlock frequency, and app-usage patterns contribute behavioral context to the fusion engine.',
    detail: 'Behavior logs via the API enrich session state when mobile or desktop clients report usage.',
    visualLabel: 'Behavior profile',
    visualValue: 'Heuristic fusion',
    barWidths: ['40%', '55%', '80%', '60%'],
  },
];

const Modalities = () => {
  const [active, setActive] = useState('text');
  const mod = MODALITIES.find((m) => m.id === active) || MODALITIES[0];

  return (
    <section className="modalities" id="modalities">
      <div className="container">
        <div className="mod-header">
          <div className="mod-tag">02 — Modalities</div>
          <h2 className="mod-title">
            Four streams,<br />
            <span>one coherent picture</span>
          </h2>
        </div>

        <div className="mod-tabs">
          {MODALITIES.map((m) => (
            <button
              key={m.id}
              type="button"
              className={`tab ${active === m.id ? 'active' : ''}`}
              onClick={() => setActive(m.id)}
            >
              {m.label}
            </button>
          ))}
        </div>

        <div className="mod-content">
          <div className="mod-text">
            <h3>{mod.title}</h3>
            <p>{mod.body}</p>
            <p style={{ marginTop: '1rem', color: 'var(--text-light)', fontSize: '0.9rem' }}>{mod.detail}</p>
          </div>
          <div className="mod-visual">
            <div className="visual-card">
              <div className="visual-card-inner">
                <div className="modality-bars">
                  {mod.barWidths.map((width) => (
                    <div key={width} className="m-line" style={{ width }} />
                  ))}
                </div>
                <div className="modality-visual-footer">
                  {mod.visualLabel}: <strong>{mod.visualValue}</strong>
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
