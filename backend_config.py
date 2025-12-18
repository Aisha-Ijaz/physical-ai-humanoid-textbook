from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Qdrant Configuration
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "http://localhost")
    QDRANT_PORT: str = os.getenv("QDRANT_PORT", "6333")
    QDRANT_API_KEY: Optional[str] = os.getenv("QDRANT_API_KEY")
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "physical-ai-book")

    # Cohere Configuration
    COHERE_API_KEY: Optional[str] = os.getenv("COHERE_API_KEY")

    # Application Configuration
    APP_NAME: str = "Book Chatbot API"
    API_V1_STR: str = os.getenv("API_V1_STR", "/v1")  # API version prefix
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    class Config:
        env_file = ".env"

settings = Settings()