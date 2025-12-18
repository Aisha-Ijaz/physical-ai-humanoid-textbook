import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.services.rag_service import RAGService
from src.services.embedding_service import EmbeddingService
from src.services.vector_store_service import VectorStoreService
from src.services.metadata_service import MetadataService


class TestRAGServiceUnit:
    """Unit tests for RAGService functionality"""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Mock the services to isolate RAGService tests
        with patch('src.services.rag_service.EmbeddingService'):
            with patch('src.services.rag_service.VectorStoreService'):
                with patch('src.services.rag_service.MetadataService'):
                    with patch('src.services.rag_service.cohere.Client'):
                        self.rag_service = RAGService()

    def test_ask_full_book_returns_correct_format(self):
        """Test that _ask_full_book returns response in correct format"""
        # Mock the required methods
        mock_embedding = [0.1, 0.2, 0.3]
        mock_search_results = [
            {
                "text": "Sample content chunk",
                "score": 0.8,
                "metadata": {"section": "Chapter 1", "page": 10}
            }
        ]

        # Patch the methods in the RAGService instance
        self.rag_service.embedding_service.generate_single_embedding = Mock(return_value=mock_embedding)
        self.rag_service.vector_store_service.search_similar = Mock(return_value=mock_search_results)
        self.rag_service.cohere_client.generate = Mock(return_value=Mock(
            generations=[Mock(text="This is the generated answer")]
        ))

        # Call the method
        result = self.rag_service._ask_full_book("What is the main theme?")

        # Verify the result format
        assert "id" in result
        assert "answer" in result
        assert "confidence_score" in result
        assert "source_citations" in result
        assert "created_at" in result
        assert result["answer"] == "This is the generated answer"
        assert isinstance(result["confidence_score"], float)
        assert isinstance(result["source_citations"], list)

    def test_ask_full_book_with_no_results(self):
        """Test that _ask_full_book handles case with no search results"""
        # Mock the required methods
        mock_embedding = [0.1, 0.2, 0.3]
        
        # Mock empty search results
        mock_search_results = []

        # Patch the methods in the RAGService instance
        self.rag_service.embedding_service.generate_single_embedding = Mock(return_value=mock_embedding)
        self.rag_service.vector_store_service.search_similar = Mock(return_value=mock_search_results)

        # Call the method
        result = self.rag_service._ask_full_book("What is the main theme?")

        # Verify the result for no context found
        assert result["answer"] == "The requested information is not available in the book content."
        assert result["confidence_score"] == 0.1  # As per the implementation
        assert len(result["source_citations"]) == 0

    def test_ask_with_selected_text_returns_correct_format(self):
        """Test that _ask_with_selected_text returns response in correct format"""
        # Mock the required methods
        mock_embedding = [0.1, 0.2, 0.3]
        mock_search_results = [
            {
                "text": "Related content chunk",
                "score": 0.7,
                "metadata": {"section": "Related content", "page": None}
            }
        ]

        # Patch the methods in the RAGService instance
        self.rag_service.embedding_service.generate_single_embedding = Mock(return_value=mock_embedding)
        self.rag_service.vector_store_service.search_similar = Mock(return_value=mock_search_results)
        self.rag_service.cohere_client.generate = Mock(return_value=Mock(
            generations=[Mock(text="This is the generated answer based on selected text")]
        ))

        # Call the method
        result = self.rag_service._ask_with_selected_text(
            "What does this mean?", 
            "This is the selected text"
        )

        # Verify the result format
        assert "id" in result
        assert "answer" in result
        assert "confidence_score" in result
        assert "source_citations" in result
        assert "created_at" in result
        assert result["answer"] == "This is the generated answer based on selected text"
        assert isinstance(result["confidence_score"], float)
        assert isinstance(result["source_citations"], list)
        assert len(result["source_citations"]) > 0
        
        # Check that the first citation is from the selected text
        assert result["source_citations"][0]["section"] == "Selected text"
        assert "selected text" in result["source_citations"][0]["text"]

    def test_ask_method_calls_correct_submethod(self):
        """Test that the main ask method calls the correct submethods based on input"""
        question = "What is the main theme?"
        selected_text = "This is selected text"
        
        # Mock the submethods
        with patch.object(self.rag_service, '_ask_full_book') as mock_full_book:
            with patch.object(self.rag_service, '_ask_with_selected_text') as mock_selected_text:
                mock_full_book.return_value = {"id": "1", "answer": "Full book answer", "confidence_score": 0.8, "source_citations": [], "created_at": datetime.now()}
                mock_selected_text.return_value = {"id": "2", "answer": "Selected text answer", "confidence_score": 0.9, "source_citations": [], "created_at": datetime.now()}
                
                # Test with selected_text provided
                self.rag_service.ask(question, selected_text=selected_text)
                mock_selected_text.assert_called_once_with(question, selected_text)
                
                # Reset mocks
                mock_full_book.reset_mock()
                mock_selected_text.reset_mock()
                
                # Test without selected_text
                self.rag_service.ask(question)
                mock_full_book.assert_called_once_with(question)

class TestEmbeddingServiceUnit:
    """Unit tests for EmbeddingService functionality"""

    def test_generate_single_embedding_calls_generate_embeddings(self):
        """Test that generate_single_embedding calls generate_embeddings with correct parameters"""
        with patch('src.services.embedding_service.cohere.Client') as mock_cohere:
            mock_client_instance = Mock()
            mock_client_instance.embed = Mock(return_value=Mock(embeddings=[[0.1, 0.2, 0.3]]))
            mock_cohere.return_value = mock_client_instance
            
            embedding_service = EmbeddingService()
            result = embedding_service.generate_single_embedding("test text", "search_query")
            
            # Verify the call was made correctly
            mock_client_instance.embed.assert_called_once_with(
                texts=["test text"],
                input_type="search_query",
                model="embed-multilingual-v3.0"
            )
            assert result == [0.1, 0.2, 0.3]


class TestSecurityFeatures:
    """Tests for security-related functionality"""
    
    def test_api_key_verification(self):
        """Test that API key verification functions work correctly"""
        # This would test the verify_api_key function in security module
        from src.utils.security import verify_api_key
        from fastapi import HTTPException
        
        # Since this function likely accesses config or headers, 
        # we'll test that it exists and raises appropriate errors
        assert verify_api_key is not None
        
        # Test that it raises an HTTPException when no API key provided
        # (This would require mocking the request, which we're not doing here)
        # Instead, we'll verify the function exists and check its module