import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';

// Use environment variable or default to localhost
const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

const AIChatInterface = ({ userId = 1, onBack }) => {
    const [messages, setMessages] = useState([
        { id: 1, text: "Hello! I'm your AI assistant. How can I help you today?", isBot: true }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const messagesEndRef = useRef(null);
    const messageIdRef = useRef(1);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isLoading]);

    const sendMessage = async (text) => {
        if (!text.trim()) return;
        messageIdRef.current += 1;
        const userMessage = { id: messageIdRef.current, text, isBot: false };
        setMessages((prev) => [...prev, userMessage]);
        setIsLoading(true);
        setError(null);

        try {
            const res = await axios.post(`${API_BASE_URL}/chat`, { user_id: userId, message: text });
            const botText = res?.data?.response || "Sorry, I couldn't process that.";
            messageIdRef.current += 1;
            setMessages((prev) => [...prev, { id: messageIdRef.current, text: botText, isBot: true }]);
        } catch (err) {
            console.error(err);
            messageIdRef.current += 1;
            setMessages((prev) => [...prev, { id: messageIdRef.current, text: "Sorry, I encountered an error.", isBot: true, isError: true }]);
            setError('Failed to get response');
        } finally {
            setIsLoading(false);
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;
        sendMessage(input);
        setInput('');
    };

    return (
        <div className="app-container">
          <div className="main-card">
            <div className="chat-container">
              <div className="chat-window">
                {messages.map((msg) => (
                    <div key={msg.id} className={`flex ${msg.isBot ? 'justify-start' : 'justify-end'}`}>
                        <div className={`max-w-[80%] rounded-2xl px-4 py-2 shadow-sm ${msg.isBot ? (msg.isError ? 'bg-red-100 text-red-800' : 'bg-white text-gray-800 border border-gray-200') : 'bg-blue-600 text-white'}`}>
                            <p className="whitespace-pre-wrap leading-relaxed">{msg.text}</p>
                        </div>
                    </div>
                ))}
                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-white rounded-2xl px-4 py-2 border border-gray-200 shadow-sm flex items-center space-x-2">
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            </div>
            <div className="input-wrapper">
              <form onSubmit={handleSubmit} className="input-area" style={{width:'100%', maxWidth:920, margin:'0 auto', display:'flex', gap:12}}>
                  <input
                      type="text"
                      className="chat-input"
                      value={input}
                      onChange={(e) => setInput(e.target.value.slice(0, 1000))}
                      placeholder="Type your message..."
                      disabled={isLoading}
                      maxLength="1000"
                      autoFocus
                      aria-label="Message input"
                  />
                  <button type="submit" className="send-button" disabled={!input.trim() || isLoading} aria-label="Send message">
                      Send
                  </button>
              </form>
            </div>

            <div className="disclaimer">AI may produce inaccurate information.</div>
          </div>
        </div>
    );
};

export default AIChatInterface;
