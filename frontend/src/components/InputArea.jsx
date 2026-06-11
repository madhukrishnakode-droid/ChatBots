import React, { useState } from 'react';

const InputArea = ({ onSendMessage, isLoading }) => {
    const [input, setInput] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (input.trim() && !isLoading) {
            onSendMessage(input);
            setInput('');
        }
    };

    return (
        <div className="input-wrapper">
          <form className="input-area" onSubmit={handleSubmit}>
                <input
                    type="text"
                    className="chat-input"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Type your message here..."
                    disabled={isLoading}
                />
                <button type="submit" className="send-button" disabled={!input.trim() || isLoading}>
                    Send
                </button>
          </form>
        </div>
    );
};

export default InputArea;
