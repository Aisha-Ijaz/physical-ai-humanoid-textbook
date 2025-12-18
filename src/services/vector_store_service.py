from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Any, Optional
from uuid import uuid4
import logging
import tempfile
import os

from src.config import settings

logger = logging.getLogger("rag_system")


class VectorStoreService:
    def __init__(self):
        # Initialize Qdrant client - try to use local storage if server not available
        try:
            # Try to connect to Qdrant server first
            if settings.QDRANT_HOST.startswith('http://') or settings.QDRANT_HOST.startswith('https://'):
                # For HTTP/HTTPS URLs, we'll use just the URL parameter
                self.client = QdrantClient(
                    url=settings.QDRANT_HOST,
                    port=int(settings.QDRANT_PORT),
                    api_key=settings.QDRANT_API_KEY,
                )
            else:
                # For local instances, use host and port separately
                self.client = QdrantClient(
                    host=settings.QDRANT_HOST,
                    port=int(settings.QDRANT_PORT),
                    api_key=settings.QDRANT_API_KEY,
                )

            # Test connection to Qdrant
            self.client.get_collections()
            self.qdrant_available = True
            logger.info("Successfully connected to Qdrant server")
        except Exception as e:
            logger.warning(f"Qdrant server not available: {e}, using local in-memory storage")
            # Use in-memory Qdrant as fallback
            try:
                self.client = QdrantClient(":memory:")
                self.qdrant_available = True
                logger.info("Using in-memory Qdrant storage")
            except Exception as e:
                logger.error(f"Failed to initialize any Qdrant storage: {e}")
                self.qdrant_available = False
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        """
        Ensure the collection exists in Qdrant with appropriate vector configuration
        """
        try:
            # Check if collection exists
            self.client.get_collection(self.collection_name)
            logger.info(f"Collection '{self.collection_name}' already exists")
        except:
            # Create collection if it doesn't exist
            # Using 1024 as vector size which is standard for Cohere embeddings
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE),
            )
            logger.info(f"Created collection '{self.collection_name}'")

    def upsert_embeddings(self, texts: List[str], embeddings: List[List[float]], metadata_list: List[Dict[str, Any]] = None) -> List[str]:
        """
        Upsert embeddings into Qdrant collection
        """
        if not self.qdrant_available:
            logger.error("Qdrant is not available")
            raise Exception("Qdrant is not available")

        if metadata_list is None:
            metadata_list = [{}] * len(texts)

        if len(texts) != len(embeddings):
            raise ValueError("Number of texts must match number of embeddings")

        # Generate unique IDs for the points
        ids = [str(uuid4()) for _ in texts]

        # Prepare points for upsert
        points = [
            models.PointStruct(
                id=ids[i],
                vector=embeddings[i],
                payload={
                    "text": texts[i],
                    "metadata": metadata_list[i]
                }
            )
            for i in range(len(texts))
        ]

        # Upsert points to collection
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

        logger.info(f"Upserted {len(texts)} embeddings to collection '{self.collection_name}'")
        return ids

    def search_similar(self, query_embedding: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar embeddings in Qdrant collection
        """
        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit,
            with_payload=True
        )

        results = []
        for result in search_results:
            results.append({
                "id": result.id,
                "text": result.payload.get("text", ""),
                "metadata": result.payload.get("metadata", {}),
                "score": result.score
            })

        logger.info(f"Found {len(results)} similar results")
        return results

    def delete_by_ids(self, ids: List[str]):
        """
        Delete points from the collection by their IDs
        """
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.PointIdsList(
                points=ids
            )
        )
        logger.info(f"Deleted {len(ids)} points from collection '{self.collection_name}'")