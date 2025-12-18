import ExecutionEnvironment from '@docusaurus/ExecutionEnvironment';

if (ExecutionEnvironment.canUseDOM) {
  // Dynamically load React and ReactDOM
  const React = require('react');
  const ReactDOM = require('react-dom/client');
  const { FloatingChatbot } = require('../utils/FloatingChatbotReact');

  // Create a container for the floating chatbot
  let container = document.getElementById('floating-chatbot-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'floating-chatbot-container';
    document.body.appendChild(container);
  }

  // Render the React component
  const root = ReactDOM.createRoot(container);
  root.render(React.createElement(FloatingChatbot));
}

export default {};