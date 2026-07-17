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
        <p>Three Streams, One Coherent Picture.</p>
      </div>

      <div className="dash-grid">
        <div className="dash-card">
          <h4>Wellbeing Score</h4>
          <div className="big-stat score-stat">{data.wellbeing_score || 0}</div>
          <p>0-100 Holistic Index</p>
        </div>
        <div className="dash-card">
          <h4>Active Modality</h4>
          <div className="big-stat">{data.last_detected_state || 'Neutral'}</div>
          <p>Fused multimodal state</p>
        </div>
      </div>

      <div className="dash-section">
        <h3>App Usage Breakdown (Last 30 Days)</h3>
        <div className="distribution-list">
          {data.app_breakdown && Object.entries(data.app_breakdown).map(([category, time]) => {
            const totalTime = Object.values(data.app_breakdown).reduce((a, b) => a + b, 0);
            const percentage = totalTime > 0 ? (time / totalTime) * 100 : 0;
            const hours = (time / 3600).toFixed(1);
            
            return (
              <div key={category} className="dist-row">
                <div className="dist-info">
                  <span className="dist-label">{category}</span>
                  <span className="dist-count">{hours} hrs</span>
                </div>
                <div className="dist-bar-bg">
                  <div 
                    className="dist-bar-fill" 
                    style={{ 
                      width: `${percentage}%`,
                      backgroundColor: 'var(--color-blue)'
                    }}
                  ></div>
                </div>
              </div>
            );
          })}
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
