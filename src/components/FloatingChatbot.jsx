import React, { useState, useRef, useEffect } from 'react';
import { useColorMode } from '@docusaurus/theme-common';

// Floating Chatbot component
const FloatingChatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const { colorMode } = useColorMode();

  // Effect to handle external toggle events
  useEffect(() => {
    const handleToggle = () => {
      setIsOpen(prev => !prev);
    };

    const toggleButton = document.getElementById('chatbot-toggle');
    if (toggleButton) {
      toggleButton.addEventListener('click', handleToggle);
    }

    // Also listen for a custom event to toggle the chat
    window.addEventListener('toggleChatbot', handleToggle);

    return () => {
      if (toggleButton) {
        toggleButton.removeEventListener('click', handleToggle);
      }
      window.removeEventListener('toggleChatbot', handleToggle);
    };
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    // Add user message
    const userMessage = { type: 'user', content: inputValue, id: Date.now() };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Using proxy endpoint configured in docusaurus.config.js
      const apiUrl = '/api/ask';

      // Call the backend API
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: inputValue,
          session_id: 'docusaurus-chat-session'
        })
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();

      // Add bot response
      const botMessage = {
        type: 'bot',
        content: data.answer,
        sources: data.source_citations,
        confidence: data.confidence_score,
        id: Date.now() + 1
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage = {
        type: 'bot',
        content: `Sorry, I encountered an error: ${error.message}. Please make sure the backend server is running.`,
        id: Date.now() + 1
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className={`floating-chatbot ${isOpen ? 'open' : ''}`}>
      {/* Chatbot Toggle Button */}
      <button 
        className={`chatbot-toggle-button ${colorMode}`}
        onClick={() => setIsOpen(!isOpen)}
        aria-label={isOpen ? 'Close chatbot' : 'Open chatbot'}
      >
        {isOpen ? '✕' : '🤖'}
      </button>

      {/* Chatbot Container */}
      {isOpen && (
        <div className={`chatbot-window ${colorMode}`}>
          <div className="chatbot-header">
            <h3>Book Assistant</h3>
          </div>
          <div className="chatbot-messages">
            {messages.length === 0 ? (
              <div className="welcome-message">
                <p>Hello! I'm your Physical AI & Humanoid Robotics textbook assistant.</p>
                <p>Ask me anything about the book content, and I'll provide answers based on the material.</p>
              </div>
            ) : (
              messages.map((message) => (
                <div key={message.id} className={`message ${message.type}-message`}>
                  <div className="message-content">
                    {message.content}
                  </div>
                  {message.sources && message.sources.length > 0 && (
                    <details className="sources-details">
                      <summary>Sources ({message.sources.length})</summary>
                      <ul className="sources-list">
                        {message.sources.map((source, idx) => (
                          <li key={idx} className="source-item">
                            <strong>{source.section}</strong>
                            {source.page && <span>, Page: {source.page}</span>}
                            <p>{source.text}</p>
                          </li>
                        ))}
                      </ul>
                    </details>
                  )}
                  {message.confidence !== undefined && (
                    <div className="confidence-score">
                      Confidence: {(message.confidence * 100).toFixed(1)}%
                    </div>
                  )}
                </div>
              ))
            )}
            {isLoading && (
              <div className="message bot-message">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
          <form onSubmit={handleSubmit} className="chatbot-input-form">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a question about the book..."
              rows={2}
              disabled={isLoading}
              className="chatbot-input"
            />
            <button type="submit" disabled={!inputValue.trim() || isLoading} className="chatbot-send-button">
              Send
            </button>
          </form>
        </div>
      )}
    </div>
  );
};

export default FloatingChatbot;