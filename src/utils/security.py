from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from typing import Optional
import secrets
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> bool:
    """
    Verify the provided API key against the expected value
    Uses secrets.compare_digest for timing-attack resistant comparison
    """
    expected_api_key = os.getenv("API_KEY")

    if not expected_api_key:
        # In development, allow access without API key
        if os.getenv("DEBUG", "False").lower() == "true":
            logger.warning("DEBUG mode enabled: Skipping API key verification")
            return True
        else:
            logger.error("Server not properly configured: API_KEY not set")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Server not properly configured: API_KEY not set"
            )

    # Use secrets.compare_digest for timing attack resistant comparison
    if not secrets.compare_digest(credentials.credentials, expected_api_key):
        logger.warning(f"Invalid API key attempt from IP: {get_client_ip()}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info("API key verified successfully")
    return True


def get_client_ip():
    """
    Get the client IP address
    Note: This function requires the request object which is not available here.
    For a more complete implementation, we'd need to use FastAPI's Request object.
    For now, this is a placeholder that would be completed with proper dependency injection.
    """
    # In a real implementation, we'd get this from the request object
    # This is a placeholder for the actual implementation
    return "unknown"


def validate_input_security(input_text: str) -> str:
    """
    Apply security validation to user input to prevent injection attacks
    """
    if input_text is None:
        return None

    # Check for potential injection patterns
    dangerous_patterns = [
        "<script", "javascript:", "vbscript:",
        "onload", "onerror", "eval(", "expression("
    ]

    lower_text = input_text.lower()
    for pattern in dangerous_patterns:
        if pattern in lower_text:
            logger.warning(f"Potentially dangerous input blocked: {pattern}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Input contains potentially dangerous content"
            )

    # Limit input length to prevent large payload attacks
    max_length = 10000  # Adjust based on your needs
    if len(input_text) > max_length:
        logger.warning(f"Input too long: {len(input_text)} characters, max allowed: {max_length}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Input too long, max allowed: {max_length} characters"
        )

    return input_text