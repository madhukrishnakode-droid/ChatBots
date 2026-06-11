import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './App.css';

// Set base URL for FastAPI - use environment variable or default to localhost
const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

function App() {
  const [selectedApp, setSelectedApp] = useState('none');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [userId] = useState(1);
  const [username, setUsername] = useState('hackathon_user');

  // Helper to create a user on first load
  useEffect(() => {
    const initUser = async () => {
      try {
        await axios.post(`${API_BASE_URL}/users`, { username: "hackathon_user" });
      } catch (error) {
        console.error("User init error:", error);
      }
    };
    initUser();
  }, []);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    const input = e.target.elements.message;
    const text = input.value.trim();
    if (!text || isLoading) return;

    const userMsg = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);
    input.value = '';

    let url = `${API_BASE_URL}/chat`;
    if (selectedApp === 'general') {
      url = `${API_BASE_URL}/chat-general`;
    }

    try {
      const response = await axios.post(url, {
        user_id: userId,
        message: text
      });

      const botMsg = {
        role: 'assistant',
        content: response.data.response || response.data.bot_reply || response.data.reply,
        sentiment: response.data.sentiment
      };

      setMessages(prev => [...prev, botMsg]);
    } catch (error) {
      console.error("Chat error:", error);
      const fallback = "I encountered an error connecting to the AI. Please ensure the backend is running.";
      const errorContent = error?.response?.data?.message || fallback;
      const errorMsg = { role: 'assistant', content: errorContent, isError: true };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  if (selectedApp === 'none') {
    return (
      <div className="app-container">
        <div className="choice-screen">
          <h1>Unified AI Platform</h1>
          <p>Select a specialized assistant to begin</p>
          
          <div className="choice-grid">
            <div className="choice-card" onClick={() => setSelectedApp('general')}>
              <h3>General AI Chat</h3>
              <p>Standard conversation with Gemini</p>
            </div>
            
            <div className="choice-card" onClick={() => setSelectedApp('mh')}>
              <h3>Mental Health</h3>
              <p>CBT-based supportive check-ins</p>
            </div>
            
            <div className="choice-card" onClick={() => setSelectedApp('resume')}>
              <h3>Resume Analyzer</h3>
              <p>Career advice and skill matching</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container">
      <div className="main-chat-container">
        <header className="chat-header">
          <div>
            <h3>{selectedApp === 'mh' ? 'Mental Health Companion' : selectedApp === 'general' ? 'General AI Chat' : 'Resume Analyzer'}</h3>
            <p style={{fontSize: '0.8rem', color: '#64748b', margin: 0}}>Powered by Gemini AI</p>
          </div>
          <button className="back-button" onClick={() => {
            setSelectedApp('none');
            setMessages([]);
          }}>
            Back to Platform
          </button>
        </header>

        {selectedApp === 'resume' ? (
          <iframe
            src="/resume/index.html"
            title="resume-app"
            style={{width: '100%', height: '100%', border: 0}}
          />
        ) : (
          <>
            <div className="chat-window">
              {messages.length === 0 && (
                <div className="message assistant">
                  {selectedApp === 'mh' 
                    ? "Hello. I'm here to listen. How are you feeling today?" 
                    : "Hello! How can I help you today?"}
                </div>
              )}
              {messages.map((msg, i) => (
                <div key={i} className={`message ${msg.role} ${msg.sentiment === 'crisis' ? 'crisis' : ''} ${msg.isError ? 'error' : ''}`}>
                  {msg.role === 'assistant' ? (
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                  ) : (
                    msg.content
                  )}
                </div>
              ))}
              {isLoading && (
                <div className="message assistant">
                  <span className="dot-pulse">AI is thinking...</span>
                </div>
              )}
            </div>

            <div className="input-area">
              <form className="input-form" onSubmit={handleSendMessage}>
                <input
                  name="message"
                  type="text"
                  className="chat-input"
                  placeholder="Type your message..."
                  autoComplete="off"
                  disabled={isLoading}
                />
                <button type="submit" className="send-button" disabled={isLoading}>
                  Send
                </button>
              </form>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default App;
