import React, { useEffect, useRef } from 'react';

const ChatWindow = ({ messages, isLoading }) => {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  return (
    <div className="chat-window">
      {messages.length === 0 && (
        <div className="message assistant">
          Hello! I'm here to listen. How are you feeling today?
        </div>
      )}
      
      {messages.map((msg, index) => (
        <div 
          key={index} 
          className={`message ${msg.role === 'user' ? 'user' : 'assistant'} ${msg.sentiment === 'crisis' ? 'crisis' : ''}`}
        >
          {msg.content}
        </div>
      ))}
      
      {isLoading && (
        <div className="message assistant">
          <em>Thinking...</em>
        </div>
      )}
      
      <div ref={messagesEndRef} />
    </div>
  );
};

export default ChatWindow;
