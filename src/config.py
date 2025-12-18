import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Qdrant Configuration
    QDRANT_HOST: Optional[str] = os.getenv("QDRANT_HOST", "http://localhost")
    QDRANT_PORT: Optional[str] = os.getenv("QDRANT_PORT", "6333")
    QDRANT_API_KEY: Optional[str] = os.getenv("QDRANT_API_KEY")
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "physical-ai-book")

    # Cohere Configuration
    COHERE_API_KEY: Optional[str] = os.getenv("COHERE_API_KEY")

    # Database Configuration
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL", "sqlite:///./rag_system.db")

    # Application Configuration
    APP_NAME: str = "RAG Question Answering System"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    API_V1_STR: str = "/v1"

    class Config:
        env_file = ".env"


settings = Settings()