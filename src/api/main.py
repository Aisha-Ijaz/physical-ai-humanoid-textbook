from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging
import sys

from src.config import settings
from src.api.endpoints import ask, ask_from_selection
from src.utils.rate_limiting import add_rate_limiting


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup events
    print("Starting up RAG Question Answering System...")
    # Any initialization logic can go here
    yield
    # Shutdown events
    print("Shutting down RAG Question Answering System...")
    # Any cleanup logic can go here


# Create FastAPI app instance
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="RAG Question Answering System API for book content",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Add rate limiting middleware
add_rate_limiting(app)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Trusted Host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # In production, replace with specific domains
)

# Include API endpoints
app.include_router(ask.router, prefix=settings.API_V1_STR, tags=["ask"])
app.include_router(ask_from_selection.router, prefix=settings.API_V1_STR, tags=["ask-from-selection"])

# Add a basic health check endpoint
@app.get("/")
def read_root():
    return {"message": "RAG Question Answering System API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}