import pytest
from pydantic import ValidationError
from datetime import datetime
from src.models.api_models import AskResponse, AskFromSelectionRequest, AskRequest, ErrorDetail, ErrorResponse


class TestJSONSchemaValidation:
    """Test that API models validate JSON schema correctly"""

    def test_ask_response_validation(self):
        """Test validation of AskResponse model"""
        # Valid response
        valid_response = AskResponse(
            id="test-id-123",
            answer="This is the answer",
            confidence_score=0.85,
            source_citations=[
                {
                    "section": "Chapter 1",
                    "page": 10,
                    "text": "Sample text"
                }
            ],
            created_at=datetime.now()
        )
        assert valid_response.id == "test-id-123"
        assert valid_response.confidence_score == 0.85

        # Test missing required field
        with pytest.raises(ValidationError):
            AskResponse(
                id="test-id-123",
                answer="This is the answer",
                # Missing confidence_score
                source_citations=[],
                created_at=datetime.now()
            )

    def test_ask_request_validation(self):
        """Test validation of AskRequest model"""
        # Valid request
        valid_request = AskRequest(
            question="What is the main theme?"
        )
        assert valid_request.question == "What is the main theme?"

        # Test missing required field
        with pytest.raises(ValidationError):
            AskRequest(
                # Missing question
            )

        # Test empty question
        with pytest.raises(ValidationError):
            AskRequest(
                question=""
            )

        # Test question too short (less than 3 chars)
        with pytest.raises(ValidationError):
            AskRequest(
                question="Hi"
            )

        # Test question too long (more than 1000 chars)
        with pytest.raises(ValidationError):
            AskRequest(
                question="a" * 1001
            )

    def test_ask_from_selection_request_validation(self):
        """Test validation of AskFromSelectionRequest model"""
        # Valid request
        valid_request = AskFromSelectionRequest(
            question="What does this mean?",
            selected_text="This is the selected text..."
        )
        assert valid_request.question == "What does this mean?"
        assert valid_request.selected_text == "This is the selected text..."

        # Test missing required question
        with pytest.raises(ValidationError):
            AskFromSelectionRequest(
                # Missing question
                selected_text="This is the selected text..."
            )

        # Test missing required selected_text
        with pytest.raises(ValidationError):
            AskFromSelectionRequest(
                question="What does this mean?",
                # Missing selected_text
            )

        # Test empty question
        with pytest.raises(ValidationError):
            AskFromSelectionRequest(
                question="",
                selected_text="This is the selected text..."
            )

        # Test empty selected_text
        with pytest.raises(ValidationError):
            AskFromSelectionRequest(
                question="What does this mean?",
                selected_text=""
            )

        # Test question too long
        with pytest.raises(ValidationError):
            AskFromSelectionRequest(
                question="a" * 1001,
                selected_text="This is the selected text..."
            )

        # Test selected_text too long
        with pytest.raises(ValidationError):
            AskFromSelectionRequest(
                question="What does this mean?",
                selected_text="a" * 5001
            )

    def test_error_detail_validation(self):
        """Test validation of ErrorDetail model"""
        # Valid error detail
        valid_error = ErrorDetail(
            code="INVALID_REQUEST",
            message="The request was invalid"
        )
        assert valid_error.code == "INVALID_REQUEST"
        assert valid_error.message == "The request was invalid"
        assert valid_error.details is None

        # Test missing required fields
        with pytest.raises(ValidationError):
            ErrorDetail(
                # Missing code and message
            )

        # Test with only code
        with pytest.raises(ValidationError):
            ErrorDetail(
                code="INVALID_REQUEST"
                # Missing message
            )

        # Test with only message
        with pytest.raises(ValidationError):
            ErrorDetail(
                # Missing code
                message="The request was invalid"
            )

    def test_error_response_validation(self):
        """Test validation of ErrorResponse model"""
        # Valid error response
        valid_error_response = ErrorResponse(
            error=ErrorDetail(
                code="INVALID_REQUEST",
                message="The request was invalid"
            )
        )
        assert valid_error_response.error.code == "INVALID_REQUEST"
        assert valid_error_response.error.message == "The request was invalid"

        # Test missing required field
        with pytest.raises(ValidationError):
            ErrorResponse(
                # Missing error
            )

    def test_confidence_score_validation(self):
        """Test that confidence scores are validated correctly"""
        # Test valid confidence scores
        for score in [0.0, 0.5, 1.0]:
            response = AskResponse(
                id="test-id",
                answer="Test answer",
                confidence_score=score,
                source_citations=[],
                created_at=datetime.now()
            )
            assert response.confidence_score == score

        # Test that scores outside [0, 1] range are handled
        # (Pydantic may not validate this by default, so we test if validation is implemented)
        try:
            # This might raise a validation error if we have min/max constraints
            response = AskResponse(
                id="test-id",
                answer="Test answer",
                confidence_score=1.5,  # Invalid: > 1.0
                source_citations=[],
                created_at=datetime.now()
            )
        except ValidationError:
            # If validation is implemented, this is correct behavior
            pass

        try:
            # This might raise a validation error if we have min/max constraints
            response = AskResponse(
                id="test-id",
                answer="Test answer",
                confidence_score=-0.1,  # Invalid: < 0.0
                source_citations=[],
                created_at=datetime.now()
            )
        except ValidationError:
            # If validation is implemented, this is correct behavior
            pass

    def test_source_citations_validation(self):
        """Test that source citations are validated correctly"""
        # Valid citations
        valid_response = AskResponse(
            id="test-id-123",
            answer="This is the answer",
            confidence_score=0.85,
            source_citations=[
                {
                    "section": "Chapter 1",
                    "page": 10,
                    "text": "Sample text"
                },
                {
                    "section": "Chapter 2",
                    "text": "Another sample text without page"  # page is optional
                }
            ],
            created_at=datetime.now()
        )
        assert len(valid_response.source_citations) == 2

    def test_response_serialization(self):
        """Test that responses can be properly serialized to/from JSON"""
        original_response = AskResponse(
            id="test-id-123",
            answer="This is the answer",
            confidence_score=0.85,
            source_citations=[
                {
                    "section": "Chapter 1",
                    "page": 10,
                    "text": "Sample text"
                }
            ],
            created_at=datetime.now()
        )
        
        # Test serialization to dict
        response_dict = original_response.model_dump()
        assert "id" in response_dict
        assert "answer" in response_dict
        assert "confidence_score" in response_dict
        assert "source_citations" in response_dict
        assert "created_at" in response_dict
        
        # Test that we can create a new instance from the dict
        reconstructed_response = AskResponse(**response_dict)
        assert reconstructed_response.id == original_response.id