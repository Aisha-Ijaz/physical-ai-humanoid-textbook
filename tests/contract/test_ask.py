import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from src.api.main import app

client = TestClient(app)


def test_ask_endpoint_contract():
    """
    Contract test for /ask endpoint
    Tests that the endpoint accepts the expected input and returns the expected output structure
    """
    # Mock the RAG service response
    mock_response = {
        "id": "test-answer-id",
        "answer": "This is a test answer based on the book content.",
        "confidence_score": 0.95,
        "source_citations": [
            {
                "section": "Chapter 3",
                "page": 45,
                "text": "Excerpt from the source..."
            }
        ],
        "created_at": "2025-12-13T10:30:00Z"
    }
    
    with patch('src.services.rag_service.RAGService') as mock_rag_service:
        # Mock the ask method to return our test response
        mock_rag_service.return_value.ask.return_value = mock_response

        # Test the endpoint with valid input
        response = client.post(
            "/v1/ask",
            json={
                "question": "What is the main theme of the book?"
            },
            headers={
                "Authorization": "Bearer test-api-key"
            }
        )
        
        # Check that the response has the correct status code
        assert response.status_code == 200
        
        # Check that the response has the expected structure
        data = response.json()
        assert "id" in data
        assert "answer" in data
        assert "confidence_score" in data
        assert "source_citations" in data
        assert "created_at" in data
        
        # Check that confidence score is within valid range
        assert 0.0 <= data["confidence_score"] <= 1.0
        
        # Check that source citations is a list
        assert isinstance(data["source_citations"], list)
        
        # Validate source citation structure
        for citation in data["source_citations"]:
            assert "section" in citation
            assert "text" in citation


def test_ask_endpoint_contract_with_session():
    """
    Contract test for /ask endpoint with session ID
    """
    mock_response = {
        "id": "test-answer-id",
        "answer": "This is a test answer based on the book content.",
        "confidence_score": 0.95,
        "source_citations": [
            {
                "section": "Chapter 3",
                "page": 45,
                "text": "Excerpt from the source..."
            }
        ],
        "created_at": "2025-12-13T10:30:00Z"
    }
    
    with patch('src.services.rag_service.RAGService') as mock_rag_service:
        mock_rag_service.return_value.ask.return_value = mock_response

        # Test the endpoint with session ID
        response = client.post(
            "/v1/ask",
            json={
                "question": "What is the main theme of the book?",
                "session_id": "test-session-id"
            },
            headers={
                "Authorization": "Bearer test-api-key"
            }
        )
        
        assert response.status_code == 200


def test_ask_endpoint_invalid_input():
    """
    Test /ask endpoint with invalid input
    """
    response = client.post(
        "/v1/ask",
        json={
            "invalid_param": "This should cause a validation error"
        },
        headers={
            "Authorization": "Bearer test-api-key"
        }
    )
    
    # Should return 422 for validation error
    assert response.status_code == 422


def test_ask_endpoint_missing_auth():
    """
    Test /ask endpoint without authentication
    """
    response = client.post(
        "/v1/ask",
        json={
            "question": "What is the main theme of the book?"
        }
    )
    
    # Should return 401 for unauthorized
    assert response.status_code == 401