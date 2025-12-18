import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import os

from src.api.main import app

client = TestClient(app)


def test_full_book_question_answering_journey():
    """
    Integration test for the full book question answering user journey
    Tests the complete flow from question submission to answer retrieval
    """
    # Mock all the services that would be involved in the process
    with patch('src.services.rag_service.RAGService') as mock_rag_service:
        # Mock response for a question about the book content
        mock_answer = {
            "id": "answer-123",
            "answer": "The main theme of the book is the exploration of human-like intelligence in artificial systems, particularly in the context of humanoid robotics.",
            "confidence_score": 0.92,
            "source_citations": [
                {
                    "section": "Chapter 3: Physical AI Fundamentals",
                    "page": 45,
                    "text": "The core principle of physical AI is to create systems that can interact with the physical world in ways similar to humans."
                },
                {
                    "section": "Chapter 7: Humanoid Design",
                    "page": 120,
                    "text": "Humanoid robots are designed to mimic human form and behavior, enabling better human-robot interaction."
                }
            ],
            "created_at": "2025-12-13T10:30:00Z"
        }
        
        # Configure the mock to return our answer
        mock_rag_service.return_value.ask.return_value = mock_answer

        # Submit a question about the book content
        response = client.post(
            "/v1/ask",
            json={
                "question": "What is the main theme of the book?",
                "session_id": "session-456"
            },
            headers={
                "Authorization": f"Bearer {os.getenv('API_KEY', 'test-key')}"
            }
        )
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        
        # Check that the response has the expected structure
        assert "id" in data
        assert "answer" in data
        assert "confidence_score" in data
        assert "source_citations" in data
        assert "created_at" in data
        
        # Verify the content is appropriate
        assert len(data["answer"]) > 0
        assert 0.0 <= data["confidence_score"] <= 1.0
        assert len(data["source_citations"]) > 0
        
        # Verify source citations have expected properties
        for citation in data["source_citations"]:
            assert "section" in citation
            assert "text" in citation


def test_full_book_question_no_answer():
    """
    Integration test for when the question cannot be answered from book content
    """
    # Mock response for a question that isn't in the book
    with patch('src.services.rag_service.RAGService') as mock_rag_service:
        mock_answer = {
            "id": "answer-456",
            "answer": "The requested information is not available in the book content.",
            "confidence_score": 0.1,
            "source_citations": [],
            "created_at": "2025-12-13T10:31:00Z"
        }
        
        mock_rag_service.return_value.ask.return_value = mock_answer

        response = client.post(
            "/v1/ask",
            json={
                "question": "What is the author's favorite color?",
            },
            headers={
                "Authorization": f"Bearer {os.getenv('API_KEY', 'test-key')}"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that the response indicates no answer was found in the book
        assert "not available in the book content" in data["answer"]
        assert data["confidence_score"] < 0.5  # Low confidence since no good answer found
        assert len(data["source_citations"]) == 0


def test_full_book_question_with_context():
    """
    Integration test for a question that requires context from the book
    """
    with patch('src.services.rag_service.RAGService') as mock_rag_service:
        mock_answer = {
            "id": "answer-789",
            "answer": "According to the text, the three principles of physical AI are perception, reasoning, and action in physical environments.",
            "confidence_score": 0.88,
            "source_citations": [
                {
                    "section": "Chapter 2: Core Principles",
                    "page": 25,
                    "text": "Physical AI systems must integrate perception of the environment, reasoning about actions, and execution of physical tasks."
                }
            ],
            "created_at": "2025-12-13T10:32:00Z"
        }
        
        mock_rag_service.return_value.ask.return_value = mock_answer

        response = client.post(
            "/v1/ask",
            json={
                "question": "What are the three principles of physical AI?",
            },
            headers={
                "Authorization": f"Bearer {os.getenv('API_KEY', 'test-key')}"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify the answer contains the specific information from the book
        assert "three principles" in data["answer"].lower()
        assert "perception" in data["answer"].lower()
        assert "reasoning" in data["answer"].lower()
        assert "action" in data["answer"].lower()
        
        # Verify source citations are provided
        assert len(data["source_citations"]) > 0
        assert "chapter 2" in data["source_citations"][0]["section"].lower()