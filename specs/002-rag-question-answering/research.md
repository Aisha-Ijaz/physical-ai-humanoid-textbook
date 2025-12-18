# Research Summary: Fixing Chatbot 404 Error

## Phase 0 Research Findings

This document consolidates findings related to fixing the chatbot 404 error and ensuring all backend services are properly running.

### Decision: Backend Server Configuration
**Rationale**: The primary cause of the 404 error is that the backend FastAPI server is not running on port 8000 as expected by the Docusaurus proxy configuration. The frontend component `FloatingChatbotReact.jsx` sends requests to `/api/ask`, which proxies to `http://localhost:8000`.

**Implementation**: The backend server should be started using:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Decision: API Endpoint Accessibility
**Rationale**: The Docusaurus frontend uses a proxy to forward `/api/*` requests to the backend at `http://localhost:8000`. The backend has both legacy endpoints (`/ask`, `/ask-from-selection`) and v1 endpoints (`/v1/ask`, `/v1/ask-from-selection`) available.

**Implementation**: Ensure the proxy configuration in `docusaurus.config.js` correctly forwards requests:
```javascript
customFields: {
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        pathRewrite: { '^/api': '' },
      },
    },
  },
},
```

### Decision: Qdrant Collection Setup
**Rationale**: The RAG system requires a Qdrant collection to be available for vector storage and retrieval. If Qdrant is not running or the collection doesn't exist, the system will fall back to a basic response mode without proper RAG functionality.

**Implementation**: Use the provided setup script to initialize Qdrant:
```bash
python setup_qdrant.py
```

Ensure Qdrant is running on the default port (6333) or configured port, and check that the collection specified in the environment variables exists.

### Decision: Cohere API Configuration
**Rationale**: The system requires a Cohere API key to generate embeddings and answers. Without this key, the Cohere client initialization will fail, causing the RAG service to fail.

**Implementation**: Set the COHERE_API_KEY in the environment variables (`.env` file):
```
COHERE_API_KEY=your_cohere_api_key_here
```

### Decision: Environment Configuration
**Rationale**: Multiple services need to be properly configured and connected to ensure the RAG system works correctly.

**Implementation**: Create a `.env` file with the following configuration:
```
# Qdrant Configuration
QDRANT_HOST=http://localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=physical-ai-book

# Cohere API key (required)
COHERE_API_KEY=your_cohere_api_key_here

# Optional: Database Configuration
DATABASE_URL=sqlite:///./rag_system.db
```

### Decision: Testing and Verification
**Rationale**: To ensure all components are working properly, we need to verify each service is accessible.

**Implementation**: Create test endpoints and procedures:
1. Test the `/health` endpoint to verify the backend is running
2. Test direct API calls to `/ask` and `/ask-from-selection`
3. Verify Qdrant connection through the RAG service
4. Test the complete flow from frontend to backend

### Alternatives Considered:

1. **Alternative 1**: Change frontend to call backend directly without proxy
   - Rejected because it would require CORS configuration and could cause security issues
   
2. **Alternative 2**: Use different proxy approach
   - Rejected because the current proxy approach is standard for Docusaurus applications

3. **Alternative 3**: Implement a fallback mechanism in the frontend
   - Implemented as part of the existing RAG service, which already has fallback responses