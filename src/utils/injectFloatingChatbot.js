import ExecutionEnvironment from '@docusaurus/ExecutionEnvironment';
import {FloatingChatbot} from './FloatingChatbotReact';

export function injectFloatingChatbot() {
  if (ExecutionEnvironment.canUseDOM) {
    // Dynamically create a container for the floating chatbot
    let container = document.getElementById('floating-chatbot-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'floating-chatbot-container';
      document.body.appendChild(container);
    }

    // Render the React component
    const React = require('react');
    const ReactDOM = require('react-dom/client');
    
    const root = ReactDOM.createRoot(container);
    root.render(<FloatingChatbot />);
  }
}

// Export the function for use in client modules
export default injectFloatingChatbot;