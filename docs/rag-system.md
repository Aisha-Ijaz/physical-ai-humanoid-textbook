# RAG Question Answering System Documentation

## Overview

The RAG (Retrieval Augmented Generation) Question Answering System allows users to ask questions about book content and receive accurate answers based only on the provided book information. The system supports both full-book and selected-text question answering modes.

## Features

- **Full-book Question Answering**: Ask questions about the entire book content
- **Selected-text Question Answering**: Ask questions about specific selected text within the book
- **Source Citations**: All answers include references to the source sections
- **Confidence Scoring**: Each answer includes a confidence score between 0.0 and 1.0
- **Rate Limiting**: API includes rate limiting to prevent abuse
- **Structured JSON Responses**: All responses follow a consistent JSON format

## API Endpoints

### Full-book Questions
- `POST /v1/ask` - Ask a question about the full book content
- `POST /v1/ask/ask` - Alternative path for the same functionality

### Selected-text Questions
- `POST /v1/ask-from-selection` - Ask a question about selected text
- `POST /v1/ask-from-selection/ask-from-selection` - Alternative path for the same functionality

## Rate Limiting

The API implements rate limiting:
- Standard accounts: 100 requests per minute
- Premium accounts: 1000 requests per minute
- The rate limiting header information is included in response headers:
  - `X-RateLimit-Limit`: Your request limit per window
  - `X-RateLimit-Remaining`: Remaining requests in current window
  - `X-RateLimit-Reset`: Time when the current window resets

## Request Format

### Full-book Questions
```json
{
  "question": "What is the main theme of the book?",
  "session_id": "optional-session-id"
}
```

### Selected-text Questions
```json
{
  "question": "What does this paragraph mean?",
  "selected_text": "The paragraph of text that the user has selected...",
  "session_id": "optional-session-id"
}
```

## Response Format

All successful responses follow this format:
- `id`: Unique identifier for the answer
- `answer`: The text response to your question
- `confidence_score`: A value between 0.0 and 1.0 indicating confidence
- `source_citations`: Array of sources used to generate the answer
- `created_at`: ISO 8601 timestamp of when the answer was generated

```json
{
  "id": "unique-answer-id",
  "answer": "The main theme of the book is...",
  "confidence_score": 0.92,
  "source_citations": [
    {
      "section": "Chapter 3",
      "page": 45,
      "text": "Excerpt from the source..."
    }
  ],
  "created_at": "2025-12-13T10:30:00Z"
}
```

## Error Handling

If your request encounters an issue, you'll receive an error response:
- `400 Bad Request`: Invalid request format or missing required fields
- `401 Unauthorized`: Invalid or missing API key
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Processing error

## Error Response Format

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": "Optional additional error details"
  }
}
```

## Getting Started

1. Get your API key from the administrator
2. Make POST requests to the appropriate endpoint with proper authentication
3. Include your question in the request body
4. For selected-text questions, also include the selected text in the request body

## Authentication

All endpoints require an API key in the request header:
`Authorization: Bearer <your-api-key>`