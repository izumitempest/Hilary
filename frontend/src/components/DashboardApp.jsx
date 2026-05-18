import React, { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import './DashboardApp.css';

const DashboardApp = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSummary();
  }, []);

  const fetchSummary = async () => {
    try {
      const summary = await apiClient.get('/dashboard/summary');
      setData(summary);
    } catch (e) {
      console.log('Dashboard error:', e);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !data) {
    return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading intelligence metrics...</div>;
  }

  return (
    <div className="dashboard-content animate-fade-in">
      <div className="dash-header">
        <h2>Intelligence Dashboard</h2>
        <p>Four Streams, One Coherent Picture.</p>
      </div>

      <div className="dash-grid">
        <div className="dash-card">
          <h4>Active Modality</h4>
          <div className="big-stat">{data.last_detected_state || 'Neutral'}</div>
          <p>Fused multimodal state</p>
        </div>
        <div className="dash-card">
          <h4>Behavior Profile</h4>
          <div className="big-stat">{data.behavior_history.length > 0 ? "Active" : "None"}</div>
          <p>Last 30 Days</p>
        </div>
      </div>

      <div className="dash-section">
        <h3>Emotional Distribution</h3>
        <div className="distribution-list">
          {Object.entries(data.emotion_distribution).map(([label, count]) => {
            const total = Object.values(data.emotion_distribution).reduce((a, b) => a + b, 0);
            const percentage = total > 0 ? (count / total) * 100 : 0;
            return (
              <div key={label} className="dist-row">
                <div className="dist-info">
                  <span className="dist-label">{label}</span>
                  <span className="dist-count">{count} {count === 1 ? 'session' : 'sessions'}</span>
                </div>
                <div className="dist-bar-bg">
                  <div 
                    className="dist-bar-fill" 
                    style={{ 
                      width: `${percentage}%`,
                      backgroundColor: label === data.last_detected_state ? 'var(--bg-dark-green)' : '#E0E0E0'
                    }}
                  ></div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default DashboardApp;
