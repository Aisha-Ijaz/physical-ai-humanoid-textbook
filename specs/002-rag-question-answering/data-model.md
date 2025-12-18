# Data Model: RAG Question Answering System

## Core Entities

### Question
- **Description**: A query submitted by the user to the RAG system
- **Fields**:
  - `question` (string, required): The text of the question (min 3, max 1000 characters)
  - `session_id` (string, optional): Identifier for the conversation session
  - `selected_text` (string, optional): Specific text selected by the user for focused questioning (1-5000 characters)

### Answer
- **Description**: A response from the system containing the answer and metadata
- **Fields**:
  - `id` (string): Unique identifier for the response
  - `answer` (string): The text response to the user's question
  - `confidence_score` (float): Confidence level in the answer (0.0 to 1.0)
  - `source_citations` (array[SourceCitation]): List of sources used to generate the answer
  - `created_at` (string): ISO timestamp of when the answer was generated

### SourceCitation
- **Description**: Information about the source of information in the answer
- **Fields**:
  - `section` (string): Name or identifier of the source section
  - `text` (string): Excerpt of the source text
  - `page` (integer, optional): Page number in the source material

### ErrorDetail
- **Description**: Structure for error responses
- **Fields**:
  - `code` (string): Machine-readable error code
  - `message` (string): Human-readable error message
  - `details` (string, optional): Additional error details

### BookContent
- **Description**: Represents a book or document in the knowledge base
- **Fields**:
  - `id` (string): Unique identifier for the book
  - `title` (string): Title of the book
  - `content` (string): Full text content of the book
  - `created_at` (string): Timestamp of when book was added to the system

### ContentChunk
- **Description**: A processed chunk of book content for vector storage
- **Fields**:
  - `id` (string): Unique identifier for the chunk
  - `book_content_id` (string): Reference to the parent book
  - `content` (string): Text content of the chunk
  - `chunk_index` (integer): Position of this chunk in the original book
  - `embedding_id` (string): Reference to the vector embedding of this chunk
  - `metadata` (object): Additional metadata about the chunk

## API Request/Response Models

### AskRequest
- **Description**: Request body for asking questions about the full book
- **Fields**:
  - `question` (string): The question to ask
  - `session_id` (string, optional): Session identifier

### AskFromSelectionRequest
- **Description**: Request body for asking questions about selected text
- **Fields**:
  - `question` (string): The question to ask
  - `selected_text` (string): The specific text to focus on
  - `session_id` (string, optional): Session identifier

### AskResponse
- **Description**: Response from the RAG system
- **Fields**:
  - `id` (string): Response identifier
  - `answer` (string): The answer to the question
  - `confidence_score` (float): Confidence in the answer (0.0 to 1.0)
  - `source_citations` (array[SourceCitation]): Sources supporting the answer
  - `created_at` (string): Response timestamp

### ErrorResponse
- **Description**: Error response structure
- **Fields**:
  - `error` (ErrorDetail): Details about the error