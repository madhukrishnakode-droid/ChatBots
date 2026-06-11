import React, { useState } from 'react';

const Login = ({ onLogin }) => {
  const [username, setUsername] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    const name = username.trim() || 'guest_user';
    onLogin(name);
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h2>Welcome</h2>
        <p className="login-sub">Sign in to start a supportive chat</p>
        <form className="login-form" onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Your display name (optional)"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <button type="submit">Continue</button>
        </form>
        <p className="login-foot">This is a local demo — no password required.</p>
      </div>
    </div>
  );
};

export default Login;
