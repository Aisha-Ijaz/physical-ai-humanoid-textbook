import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import os

from src.api.main import app

client = TestClient(app)


def test_selected_text_question_answering_journey():
    """
    Integration test for the selected text question answering user journey
    Tests the complete flow from selected text + question submission to answer retrieval
    """
    # Mock all the services that would be involved in the process
    with patch('src.services.rag_service.RAGService') as mock_rag_service:
        # Mock response for a question about selected text
        mock_answer = {
            "id": "answer-123",
            "answer": "Based on the selected text, this concept refers to the implementation of AI systems that can interact with the physical world in ways similar to humans.",
            "confidence_score": 0.89,
            "source_citations": [
                {
                    "section": "Selected text context",
                    "text": "Physical AI systems must integrate perception of the environment, reasoning about actions, and execution of physical tasks."
                }
            ],
            "created_at": "2025-12-13T10:31:00Z"
        }
        
        # Configure the mock to return our answer
        mock_rag_service.return_value.ask.return_value = mock_answer

        # Submit a question with selected text
        response = client.post(
            "/v1/ask-from-selection",
            json={
                "question": "What does this concept refer to?",
                "selected_text": "Physical AI systems must integrate perception of the environment, reasoning about actions, and execution of physical tasks.",
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
        
        # Verify the content is appropriate and focused on the selected text
        assert len(data["answer"]) > 0
        assert 0.0 <= data["confidence_score"] <= 1.0
        assert len(data["source_citations"]) > 0
        
        # Verify source citations include the selected text
        assert "Physical AI systems must integrate" in data["source_citations"][0]["text"]


def test_selected_text_question_no_answer_in_selection():
    """
    Integration test for when the question cannot be answered from the selected text
    """
    # Mock response for when the question isn't answerable from selected text
    with patch('src.services.rag_service.RAGService') as mock_rag_service:
        mock_answer = {
            "id": "answer-456",
            "answer": "The selected text does not contain information to answer this question. The concept you're asking about is discussed elsewhere in the book.",
            "confidence_score": 0.4,
            "source_citations": [
                {
                    "section": "Selected text context",
                    "text": "This is the text that was selected by the user."
                }
            ],
            "created_at": "2025-12-13T10:32:00Z"
        }
        
        mock_rag_service.return_value.ask.return_value = mock_answer

        response = client.post(
            "/v1/ask-from-selection",
            json={
                "question": "How does this relate to neural networks?",
                "selected_text": "This is the text that was selected by the user.",
            },
            headers={
                "Authorization": f"Bearer {os.getenv('API_KEY', 'test-key')}"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that the response indicates the selected text doesn't have the answer
        assert "does not contain information" in data["answer"]
        assert 0.0 <= data["confidence_score"] <= 0.5  # Lower confidence when answer not in selection


def test_selected_text_question_with_context_expansion():
    """
    Integration test for a question that needs context from around the selection
    """
    with patch('src.services.rag_service.RAGService') as mock_rag_service:
        mock_answer = {
            "id": "answer-789",
            "answer": "The text explains that the three principles are perception, reasoning, and action in physical environments. The selected text specifically addresses the perception aspect of these principles.",
            "confidence_score": 0.85,
            "source_citations": [
                {
                    "section": "Selected text context",
                    "text": "Perception is the first of the three core principles, enabling AI systems to understand their environment."
                }
            ],
            "created_at": "2025-12-13T10:33:00Z"
        }
        
        mock_rag_service.return_value.ask.return_value = mock_answer

        response = client.post(
            "/v1/ask-from-selection",
            json={
                "question": "How does the selected text relate to the three principles?",
                "selected_text": "Perception is the first of the three core principles, enabling AI systems to understand their environment.",
            },
            headers={
                "Authorization": f"Bearer {os.getenv('API_KEY', 'test-key')}"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify the answer connects the selected text to the broader context
        assert "three principles" in data["answer"].lower()
        assert "perception" in data["answer"].lower()
        
        # Verify the selected text is referenced in the citations
        assert "Perception is the first" in data["source_citations"][0]["text"]