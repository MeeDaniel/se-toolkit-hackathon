import React, { useState } from 'react';
import './TelegramLogin.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function TelegramLogin({ onLogin }) {
  const [telegramAlias, setTelegramAlias] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [step, setStep] = useState('alias'); // 'alias', 'password', 'set-password'
  const [userInfo, setUserInfo] = useState(null);

  const handleAliasSubmit = async (e) => {
    e.preventDefault();
    
    if (!telegramAlias.trim()) {
      setError('Please enter your Telegram username');
      return;
    }
    
    if (telegramAlias.length < 3) {
      setError('Username must be at least 3 characters');
      return;
    }
    
    // Remove @ if present
    const cleanAlias = telegramAlias.replace(/^@/, '');
    
    try {
      // Check if user exists and if password is required
      const response = await fetch(`${API_URL}/api/users/${cleanAlias}`);
      
      if (response.status === 404) {
        // New user - no password needed
        onLogin(cleanAlias);
        return;
      }
      
      if (response.ok) {
        const userData = await response.json();
        setUserInfo(userData);
        
        if (userData.password_protected) {
          // User has password set - ask for it
          setStep('password');
          setError('');
        } else {
          // User exists but no password - allow direct login
          onLogin(cleanAlias);
        }
      }
    } catch (err) {
      console.error('Error checking user:', err);
      setError('Connection error. Please try again.');
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    
    if (!password.trim()) {
      setError('Please enter your password');
      return;
    }
    
    try {
      const cleanAlias = telegramAlias.replace(/^@/, '');
      
      const response = await fetch(`${API_URL}/api/users/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          telegram_alias: cleanAlias, 
          password: password 
        })
      });
      
      if (response.ok) {
        onLogin(cleanAlias);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Invalid password');
      }
    } catch (err) {
      console.error('Login error:', err);
      setError('Connection error. Please try again.');
    }
  };

  const goBack = () => {
    setStep('alias');
    setPassword('');
    setError('');
    setUserInfo(null);
  };

  if (step === 'password') {
    return (
      <div className="telegram-login">
        <div className="login-card">
          <div className="login-header">
            <div className="telegram-icon">
              <svg viewBox="0 0 24 24" width="64" height="64">
                <path fill="#2AABEE" d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.53 8.09l-1.77 8.33c-.13.6-.5.74-.99.46l-2.74-2.02-1.32 1.27c-.15.15-.27.27-.55.27l.2-2.78 5.07-4.58c.22-.2-.05-.3-.34-.12l-6.27 3.95-2.7-.84c-.59-.19-.6-.59.12-.87l10.55-4.07c.49-.18.92.12.74.87z"/>
              </svg>
            </div>
            <h1>TourStats</h1>
            <p className="subtitle">AI-Powered Analytics for Tour Guides</p>
          </div>

          <form onSubmit={handlePasswordSubmit} className="login-form">
            <div className="form-group">
              <label>🔐 Password for @{telegramAlias.replace(/^@/, '')}</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                className="input-field"
                autoFocus
              />
              {error && <div className="error-message">{error}</div>}
            </div>

            <button type="submit" className="login-button">
              🔓 Login
            </button>

            <button type="button" className="back-button" onClick={goBack}>
              ← Back to username
            </button>

            <div className="info-box">
              <p>💡 <strong>Note:</strong> This account requires a password. Set it up in the Telegram bot if you forgot it.</p>
            </div>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="telegram-login">
      <div className="login-card">
        <div className="login-header">
          <div className="telegram-icon">
            <svg viewBox="0 0 24 24" width="64" height="64">
              <path fill="#2AABEE" d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.53 8.09l-1.77 8.33c-.13.6-.5.74-.99.46l-2.74-2.02-1.32 1.27c-.15.15-.27.27-.55.27l.2-2.78 5.07-4.58c.22-.2-.05-.3-.34-.12l-6.27 3.95-2.7-.84c-.59-.19-.6-.59.12-.87l10.55-4.07c.49-.18.92.12.74.87z"/>
            </svg>
          </div>
          <h1>TourStats</h1>
          <p className="subtitle">AI-Powered Analytics for Tour Guides</p>
        </div>

        <form onSubmit={handleAliasSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="telegram">Enter your Telegram username:</label>
            <input
              type="text"
              id="telegram"
              value={telegramAlias}
              onChange={(e) => {
                setTelegramAlias(e.target.value);
                setError('');
              }}
              placeholder="@username or username"
              className="input-field"
              autoFocus
            />
            {error && <div className="error-message">{error}</div>}
          </div>

          <button type="submit" className="login-button">
            Continue to TourStats →
          </button>

          <div className="info-box">
            <p>💡 <strong>Note:</strong> This web app mirrors the Telegram bot experience. Your data will be associated with this username.</p>
          </div>
        </form>
      </div>
    </div>
  );
}

export default TelegramLogin;
