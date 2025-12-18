import pytest
from datetime import datetime
from src.models.api_models import AskResponse, AskFromSelectionRequest, AskRequest, ErrorDetail, ErrorResponse


class TestAPIResponseFormat:
    """Test that API responses follow the correct format and structure"""

    def test_ask_response_format(self):
        """Test that AskResponse follows the expected format"""
        response = AskResponse(
            id="test-id-123",
            answer="This is a sample answer",
            confidence_score=0.85,
            source_citations=[
                {
                    "section": "Chapter 1",
                    "page": 10,
                    "text": "Sample citation text from the document"
                }
            ],
            created_at=datetime.now()
        )

        # Check that all required fields are present
        assert hasattr(response, 'id')
        assert hasattr(response, 'answer')
        assert hasattr(response, 'confidence_score')
        assert hasattr(response, 'source_citations')
        assert hasattr(response, 'created_at')

        # Check field values
        assert response.id == "test-id-123"
        assert response.answer == "This is a sample answer"
        assert response.confidence_score == 0.85
        assert len(response.source_citations) == 1
        assert response.source_citations[0]["section"] == "Chapter 1"
        assert response.source_citations[0]["page"] == 10
        assert response.source_citations[0]["text"] == "Sample citation text from the document"
        assert isinstance(response.created_at, datetime)

    def test_ask_request_format(self):
        """Test that AskRequest follows the expected format"""
        request = AskRequest(
            question="What is the main theme?",
            session_id="session-123"
        )

        assert hasattr(request, 'question')
        assert hasattr(request, 'session_id')
        assert request.question == "What is the main theme?"
        assert request.session_id == "session-123"

    def test_ask_from_selection_request_format(self):
        """Test that AskFromSelectionRequest follows the expected format"""
        request = AskFromSelectionRequest(
            question="What does this mean?",
            selected_text="This is the selected text",
            session_id="session-123"
        )

        assert hasattr(request, 'question')
        assert hasattr(request, 'selected_text')
        assert hasattr(request, 'session_id')
        assert request.question == "What does this mean?"
        assert request.selected_text == "This is the selected text"
        assert request.session_id == "session-123"

    def test_error_detail_format(self):
        """Test that ErrorDetail follows the expected format"""
        error_detail = ErrorDetail(
            code="INVALID_REQUEST",
            message="The request was invalid",
            details="Additional error details"
        )

        assert hasattr(error_detail, 'code')
        assert hasattr(error_detail, 'message')
        assert hasattr(error_detail, 'details')
        assert error_detail.code == "INVALID_REQUEST"
        assert error_detail.message == "The request was invalid"
        assert error_detail.details == "Additional error details"

    def test_error_response_format(self):
        """Test that ErrorResponse follows the expected format"""
        error_response = ErrorResponse(
            error=ErrorDetail(
                code="INVALID_REQUEST",
                message="The request was invalid",
                details="Additional error details"
            )
        )

        assert hasattr(error_response, 'error')
        assert hasattr(error_response.error, 'code')
        assert hasattr(error_response.error, 'message')
        assert hasattr(error_response.error, 'details')
        assert error_response.error.code == "INVALID_REQUEST"
        assert error_response.error.message == "The request was invalid"
        assert error_response.error.details == "Additional error details"

    def test_confidence_score_range(self):
        """Test that confidence scores are within the allowed range [0.0, 1.0]"""
        # Test valid confidence scores
        valid_scores = [0.0, 0.25, 0.5, 0.75, 1.0]
        for score in valid_scores:
            response = AskResponse(
                id="test-id",
                answer="Test answer",
                confidence_score=score,
                source_citations=[],
                created_at=datetime.now()
            )
            assert 0.0 <= response.confidence_score <= 1.0

        # Test that values outside the range raise validation errors (would happen during creation)
        with pytest.raises(ValueError):
            AskResponse(
                id="test-id",
                answer="Test answer",
                confidence_score=1.5,  # Invalid: > 1.0
                source_citations=[],
                created_at=datetime.now()
            )

        with pytest.raises(ValueError):
            AskResponse(
                id="test-id",
                answer="Test answer",
                confidence_score=-0.1,  # Invalid: < 0.0
                source_citations=[],
                created_at=datetime.now()
            )

    def test_source_citation_format(self):
        """Test that source citations follow the expected format"""
        citation = {
            "section": "Chapter 1",
            "page": 10,
            "text": "Sample citation text"
        }

        assert "section" in citation
        assert "page" in citation
        assert "text" in citation
        assert citation["section"] == "Chapter 1"
        assert citation["page"] == 10
        assert citation["text"] == "Sample citation text"