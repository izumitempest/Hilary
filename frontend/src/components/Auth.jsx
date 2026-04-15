import React, { useState } from 'react';
import { apiClient } from '../api/client';
import './Auth.css';

const Auth = ({ onLoginSuccess, onBack }) => {
  const [isLogin, setIsLogin] = useState(true);
  
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [regSuccess, setRegSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) return;
    
    setLoading(true);
    setError(null);
    try {
      if (isLogin) {
        const userData = await apiClient.login(email, password);
        onLoginSuccess(userData);
      } else {
        if (!username) {
          setError('Username is required for registration.');
          setLoading(false);
          return;
        }
        await apiClient.register(username, email, password);
        setRegSuccess(true);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-overlay animate-fade-in">
      <div className="auth-card">
        {regSuccess ? (
          <div className="verification-state animate-fade-in">
            <div className="verify-icon">✉️</div>
            <h2 style={{ fontFamily: 'Playfair Display', marginBottom: '15px' }}>Verify your identity</h2>
            <p style={{ color: 'var(--text-light)', marginBottom: '30px', lineHeight: '1.6' }}>
              We've sent a secure confirmation link to <strong style={{color: '#fff'}}>{email}</strong>.<br/><br/>
              Please click the link in your inbox to complete your registration and unlock your dashboard.
            </p>
            <button onClick={() => { setRegSuccess(false); setIsLogin(true); }} className="btn auth-btn">
              BACK TO LOGIN
            </button>
          </div>
        ) : (
          <>
            <button onClick={onBack} className="close-btn">&times;</button>
            <h2 style={{ fontFamily: 'Playfair Display', marginBottom: '10px' }}>
              {isLogin ? 'Welcome back' : 'Join Hilary'}
            </h2>
            <p style={{ color: 'var(--text-light)', marginBottom: '30px', fontSize: '0.9rem' }}>
              {isLogin 
                ? 'Securely log in to access your intelligence dashboard.' 
                : 'Register for early access to the mental health platform.'}
            </p>
            
            <form onSubmit={handleSubmit} className="auth-form">
              {!isLogin && (
                <div className="input-group">
                  <label>Full Name / Username</label>
                  <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Izumi" />
                </div>
              )}
              <div className="input-group">
                <label>Email Address</label>
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="izumi@example.com" />
              </div>
              <div className="input-group">
                <label>Password</label>
                <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" />
              </div>
              
              {error && <div className="error-msg">{error}</div>}
              
              <button type="submit" className="btn auth-btn" disabled={loading}>
                {loading ? 'AUTHENTICATING...' : (isLogin ? 'SECURE LOGIN' : 'CREATE ACCOUNT')}
              </button>
            </form>
            
            <div style={{ textAlign: 'center', marginTop: '20px', fontSize: '0.85rem', color: 'var(--text-light)' }}>
              {isLogin ? "Don't have an account? " : "Already have an account? "}
              <span 
                onClick={() => { setIsLogin(!isLogin); setError(null); }} 
                style={{ color: 'var(--bg-dark-green)', fontWeight: 'bold', cursor: 'pointer' }}
              >
                {isLogin ? 'Request Access' : 'Sign In'}
              </span>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Auth;
