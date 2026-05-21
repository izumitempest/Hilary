import React, { useState } from 'react';
import './Modalities.css';

const MODALITIES = [
  {
    id: 'text',
    label: 'TEXT',
    title: 'Text sentiment analysis',
    body: 'Natural language processing analyzes chat and journal input for sentiment shifts, emotional keywords, and linguistic markers associated with anxiety, depression, or stress.',
    detail: 'Each message is scored for tone and emotional cues, then folded into your live session state.',
    visualLabel: 'Sentiment stream',
    visualValue: 'Active in chat',
    barWidths: ['80%', '60%', '90%', '40%'],
  },
  {
    id: 'facial',
    label: 'FACIAL',
    title: 'Facial expression analysis',
    body: 'Photos you share are analyzed by a dedicated vision model trained for mental-health expression cues.',
    detail: 'Attach an image in chat — facial signals feed the fusion engine alongside your words.',
    visualLabel: 'Vision model',
    visualValue: 'Custom classifier',
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
            Three streams,<br />
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
