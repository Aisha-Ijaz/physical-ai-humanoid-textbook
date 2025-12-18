// src/clientModules/apiProxy.js
// This module sets up API proxy configuration for Docusaurus
// It's loaded as a client module to make the API endpoint configurable

export function getApiBaseUrl() {
  // Check if we're in the browser environment
  if (typeof window !== 'undefined') {
    // For browser environment, use the backend server directly
    // In Docusaurus, environment variables are available through process.env during build time
    // but at runtime in the browser, we use a default
    return 'http://localhost:8000';
  }

  // For server-side rendering, use environment variable or default
  // Using typeof check to avoid errors in browser
  if (typeof process !== 'undefined' && process.env && process.env.BACKEND_URL) {
    return process.env.BACKEND_URL;
  }

  return 'http://localhost:8000';
}

export default {};