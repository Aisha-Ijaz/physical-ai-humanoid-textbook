# Quickstart Guide: RAG Question Answering System

## Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher
- npm package manager
- A Cohere API key
- Qdrant vector database (local or cloud)

## Setup Instructions

### 1. Clone and Navigate to Project

```bash
cd physical-ai-humanoid-main
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Node.js Dependencies

```bash
npm install
```

### 4. Set up Qdrant Vector Database

You have two options for Qdrant:

**Option A: Local Qdrant**
```bash
# Install Qdrant using pip
pip install qdrant-client

# Run Qdrant locally (in a separate terminal)
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

**Option B: Qdrant Cloud**
- Sign up at [qdrant.tech](https://qdrant.tech)
- Create a collection and note your API key and URL

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Qdrant Configuration
QDRANT_HOST=http://localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=physical-ai-book
# For cloud: QDRANT_URL=your_qdrant_cloud_url
# For cloud: QDRANT_API_KEY=your_qdrant_api_key

# Cohere API key (required)
COHERE_API_KEY=your_cohere_api_key_here

# Optional: Database Configuration
DATABASE_URL=sqlite:///./rag_system.db
```

### 6. Initialize Qdrant Collection

```bash
python setup_qdrant.py
```

### 7. Start the Backend Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 8. Start the Docusaurus Frontend (in a new terminal)

```bash
npm run start
```

### 9. Access the Chatbot

- The Docusaurus site will be available at `http://localhost:3000`
- Navigate to the "Chat with the Book" page from the sidebar
- Ask questions about the Physical AI & Humanoid Robotics content

## API Endpoints

The backend exposes the following endpoints:

- `POST /ask` - Ask questions about the full book
- `POST /ask-from-selection` - Ask questions about selected text
- `POST /v1/ask` - v1 API for asking questions about the full book
- `POST /v1/ask-from-selection` - v1 API for asking questions about selected text
- `GET /health` - Health check endpoint
- `GET /` - Root endpoint

## Troubleshooting

- If the backend server doesn't start, ensure all Python dependencies are installed
- If the chatbot doesn't connect to the backend, check that both the backend and Qdrant are running
- If you're getting API errors, verify your Cohere API key in the .env file
- For Qdrant connection issues, ensure Qdrant is running and the connection settings in .env are correct
- If you get 404 errors, ensure the backend server is running on port 8000

## Testing the API Directly

You can test the API endpoints using curl:

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the Zero-Moment Point in humanoid robotics?"
  }'
```