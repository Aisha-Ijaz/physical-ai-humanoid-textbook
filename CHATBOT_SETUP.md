# Physical AI & Humanoid Robotics - Chatbot Implementation

This project includes an interactive chatbot integrated into the Docusaurus documentation pages. The chatbot allows users to ask questions about the Physical AI & Humanoid Robotics textbook content and receive answers based on the book's material.

## How to Run the Chatbot

### Prerequisites

1. Python 3.8 or higher
2. Node.js 18 or higher
3. npm package manager

### Setup Instructions

1. **Install Python dependencies**:
   ```bash
   pip install fastapi uvicorn cohere qdrant-client python-dotenv
   ```

2. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

3. **Set up Qdrant** (if not already running):
   - Install Qdrant locally or use the cloud version
   - Make sure Qdrant is running on `http://localhost:6333` (default)
   - Run the setup script to populate the collection:
     ```bash
     python setup_qdrant.py
     ```

4. **Configure environment variables**: 
   - Copy the `.env.example` or create a `.env` file with the following content:
     ```
     # Qdrant Configuration
     QDRANT_HOST=http://localhost
     QDRANT_PORT=6333
     QDRANT_COLLECTION_NAME=physical-ai-book

     # Cohere API key (optional - you can use your own)
     # COHERE_API_KEY=your_api_key_here
     ```

5. **Start the backend server**:
   ```bash
   uvicorn src.api.main:app --host 0.0.0.0 --port 8000
   ```

6. **Start the Docusaurus frontend in a new terminal**:
   ```bash
   npm run start
   ```

7. **Access the chatbot**:
   - The Docusaurus site will be available at `http://localhost:3000`
   - Navigate to the "Chat with the Book" page from the sidebar
   - Ask questions about the Physical AI & Humanoid Robotics content

## How to Use the Chatbot

1. Navigate to the "Chat with the Book" page in the documentation sidebar
2. Type your question in the input field at the bottom of the chat window
3. Press Enter or click the "Send" button to submit your question
4. Wait for the response, which will include:
   - The answer to your question
   - Source citations showing where the information comes from
   - A confidence score indicating the reliability of the answer

## Troubleshooting

- If the backend server doesn't start, ensure all Python dependencies are installed
- If the chatbot doesn't connect to the backend, check that both the backend and Qdrant are running
- If you're getting API errors, verify your Cohere API key in the .env file (if required)
- For Qdrant connection issues, ensure Qdrant is running and the connection settings in .env are correct

## Architecture

The chatbot is built using:

- **Frontend**: React component integrated into Docusaurus
- **Backend**: FastAPI server with endpoints for question answering
- **Database**: Qdrant vector database for storing and retrieving book content
- **Language Model**: Cohere's command-r-plus for answer generation
- **Embeddings**: Cohere embeddings for semantic search