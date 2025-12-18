#!/usr/bin/env python3
"""
Setup script to initialize Qdrant collection and populate it with textbook content
"""
import os
import sys
from pathlib import Path
import logging

# Add the project root to Python path so we can import modules
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.document_processor import extract_text_from_markdown, chunk_text, ingest_book_files
from src.services.vector_store_service import VectorStoreService
from src.services.embedding_service import EmbeddingService
from src.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_qdrant_collection():
    """Initialize Qdrant collection"""
    logger.info("Initializing Qdrant collection...")
    try:
        vector_store = VectorStoreService()
        logger.info(f"Qdrant collection '{settings.QDRANT_COLLECTION_NAME}' initialized successfully")
        return vector_store
    except Exception as e:
        logger.error(f"Failed to initialize Qdrant collection: {str(e)}")
        raise

def process_documentation_files(docs_dir):
    """Process only core textbook chapter markdown files"""
    logger.info(f"Processing core textbook chapter files in {docs_dir}/chapters")

    # Get only markdown files from the chapters directory (not experiments, safety, etc.)
    chapters_dir = docs_dir / "chapters"
    if not chapters_dir.exists():
        logger.error(f"Chapters directory not found at: {chapters_dir}")
        return [], []

    # Get all markdown files in the chapters directory recursively
    md_files = list(chapters_dir.rglob("*.md"))

    logger.info(f"Found {len(md_files)} chapter markdown files")

    all_chunks = []
    all_metadata = []

    for file_path in md_files:
        logger.info(f"Processing {file_path}")

        try:
            # Extract text from markdown
            text = extract_text_from_markdown(str(file_path))

            # Chunk the text
            chunks = chunk_text(text, chunk_size=1000, overlap=100)

            for i, chunk in enumerate(chunks):
                if len(chunk.strip()) > 0:  # Only add non-empty chunks
                    all_chunks.append(chunk)
                    all_metadata.append({
                        "source_file": str(file_path.relative_to(docs_dir)),
                        "chunk_index": i,
                        "original_title": file_path.stem,
                        "section": file_path.parent.name  # Add section info (intro, fundamentals, etc.)
                    })
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            continue

    logger.info(f"Generated {len(all_chunks)} total text chunks from core textbook chapters")
    return all_chunks, all_metadata

def generate_and_store_embeddings(vector_store, embedding_service, chunks, metadata_list):
    """Generate embeddings and store them in Qdrant"""
    logger.info("Starting embedding generation and storage...")

    total_processed = 0

    # Process chunks one at a time to avoid rate limiting issues
    # Note: Cohere free tier has rate limitations of 100 requests per minute
    for i, (chunk, metadata) in enumerate(zip(chunks, metadata_list)):
        logger.info(f"Processing chunk {i+1}/{len(chunks)}")

        try:
            # Generate embeddings for a single chunk
            embedding = embedding_service.generate_single_embedding(chunk, "search_document")

            # Prepare point for upsert
            import uuid
            from qdrant_client.http import models
            point_id = str(uuid.uuid4())

            point = models.PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "text": chunk,
                    "metadata": metadata
                }
            )

            # Upsert to Qdrant
            vector_store.client.upsert(
                collection_name=vector_store.collection_name,
                points=[point]
            )

            total_processed += 1
            logger.info(f"Stored chunk {i+1}. Total processed: {total_processed}")

            # Add a significant delay to respect rate limits - Cohere limits to 100/min
            import time
            time.sleep(10)  # 10 second delay per request to stay well within rate limits

        except Exception as e:
            logger.error(f"Error processing chunk {i} (text: {chunk[:50]}...): {str(e)}")
            # Add delay before continuing to respect rate limits
            import time
            time.sleep(10)
            # Continue with the next chunk instead of failing completely
            continue

    logger.info(f"Completed storing {total_processed} embeddings in Qdrant")


def main():
    logger.info("Starting RAG system setup...")
    
    # Step 1: Initialize Qdrant collection
    vector_store = setup_qdrant_collection()
    
    # Step 2: Initialize embedding service
    logger.info("Initializing embedding service...")
    embedding_service = EmbeddingService()
    logger.info("Embedding service initialized")
    
    # Step 3: Process documentation files
    docs_dir = project_root / "docs"
    if not docs_dir.exists():
        logger.error(f"Documentation directory not found at: {docs_dir}")
        return 1
    
    chunks, metadata_list = process_documentation_files(docs_dir)
    
    if not chunks:
        logger.warning("No text chunks were generated. Please check if the docs directory contains markdown files.")
        return 1
    
    # Step 4: Generate embeddings and store in Qdrant
    generate_and_store_embeddings(vector_store, embedding_service, chunks, metadata_list)
    
    logger.info("RAG system setup completed successfully!")
    logger.info(f"Stored {len(chunks)} text chunks in Qdrant collection '{settings.QDRANT_COLLECTION_NAME}'")
    
    # Step 5: Verify the setup by checking the collection size
    try:
        collection_info = vector_store.client.get_collection(settings.QDRANT_COLLECTION_NAME)
        logger.info(f"Collection '{settings.QDRANT_COLLECTION_NAME}' contains {collection_info.points_count} points")
    except Exception as e:
        logger.error(f"Could not verify collection size: {str(e)}")
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Setup was interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Setup failed with error: {str(e)}", exc_info=True)
        sys.exit(1)