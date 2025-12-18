# API Contract: RAG Question Answering System

## Base URL
`https://api.rag-system.example.com/v1`

## Authentication
All endpoints require an API key in the request header:
`Authorization: Bearer <your-api-key>`

## Endpoints

### POST /ask
Ask a question about the full book content.

#### Request
```json
{
  "question": "What is the main theme of the book?",
  "session_id": "optional-session-id"
}
```

#### Response
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

#### Error Responses
- `400 Bad Request`: Invalid request format or missing required fields
- `401 Unauthorized`: Invalid or missing API key
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Processing error

### POST /ask-from-selection
Ask a question about user-selected text.

#### Request
```json
{
  "question": "What does this paragraph mean?",
  "selected_text": "The paragraph of text that the user has selected...",
  "session_id": "optional-session-id"
}
```

#### Response
```json
{
  "id": "unique-answer-id",
  "answer": "The selected paragraph means...",
  "confidence_score": 0.87,
  "source_citations": [
    {
      "section": "Selected text context",
      "text": "The exact text that was selected..."
    }
  ],
  "created_at": "2025-12-13T10:31:00Z"
}
```

#### Error Responses
- `400 Bad Request`: Invalid request format or missing required fields
- `401 Unauthorized`: Invalid or missing API key
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Processing error

## Common Error Format
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": "Optional additional error details"
  }
}
```

## Rate Limiting
- Standard users: 100 requests per minute
- Premium users: 1000 requests per minute
- Rate limit headers included in responses:
  - `X-RateLimit-Limit`: Request limit per window
  - `X-RateLimit-Remaining`: Remaining requests in current window
  - `X-RateLimit-Reset`: Time when the current window resets