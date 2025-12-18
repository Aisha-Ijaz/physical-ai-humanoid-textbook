import cohere
from typing import List
import os
import hashlib
import time
from datetime import datetime, timedelta
from src.config import settings

class EmbeddingService:
    def __init__(self):
        # Initialize Cohere client
        self.client = cohere.Client(settings.COHERE_API_KEY)
        self.model = "embed-multilingual-v3.0"  # Using Cohere's latest embedding model

        # Cache for embeddings with TTL
        self._cache = {}
        self._cache_ttl = {}
        self._cache_timeout = timedelta(minutes=30)  # 30 minutes cache timeout
    
    def _get_cache_key(self, text: str, input_type: str) -> str:
        """Generate a cache key for a single text and input type"""
        key_str = f"{text}:{input_type}:{self.model}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def _get_from_cache(self, text: str, input_type: str):
        """Retrieve embedding from cache if it exists and hasn't expired"""
        cache_key = self._get_cache_key(text, input_type)
        if cache_key in self._cache:
            # Check if the cache entry has expired
            if datetime.now() < self._cache_ttl.get(cache_key, datetime.min):
                return self._cache[cache_key]
            else:
                # Remove expired cache entry
                del self._cache[cache_key]
                del self._cache_ttl[cache_key]
        return None

    def _set_in_cache(self, text: str, input_type: str, embedding: List[float]):
        """Store embedding in cache with TTL"""
        cache_key = self._get_cache_key(text, input_type)
        self._cache[cache_key] = embedding
        self._cache_ttl[cache_key] = datetime.now() + self._cache_timeout

    def generate_embeddings(self, texts: List[str], input_type: str = "search_document") -> List[List[float]]:
        """
        Generate embeddings for a list of texts using Cohere
        With caching to avoid regenerating embeddings for the same text
        """
        embeddings = []

        # Process each text individually, checking cache first
        for text in texts:
            # Check if embedding is in cache
            cached_embedding = self._get_from_cache(text, input_type)
            if cached_embedding is not None:
                # Use cached embedding
                embeddings.append(cached_embedding)
            else:
                # Generate new embedding for texts not in cache
                # For efficiency, we'll need to make separate API calls for uncached texts
                response = self.client.embed(
                    texts=[text],
                    model=self.model,
                    input_type=input_type
                )

                # Extract the embedding from the response
                embedding = response.embeddings[0]

                # Store in cache
                self._set_in_cache(text, input_type, embedding)

                # Add to results
                embeddings.append(embedding)

        return embeddings
    
    def generate_single_embedding(self, text: str, input_type: str = "search_document") -> List[float]:
        """
        Generate embedding for a single text
        """
        return self.generate_embeddings([text], input_type)[0]
    
    def rerank(self, query: str, documents: List[str], top_n: int = 5) -> List[dict]:
        """
        Rerank documents based on relevance to the query using Cohere's rerank functionality
        """
        response = self.client.rerank(
            model="rerank-multilingual-v2.0",
            query=query,
            documents=documents,
            top_n=top_n
        )
        
        return [
            {
                "index": item.index,
                "document": item.document,
                "relevance_score": item.relevance_score
            }
            for item in response.results
        ]