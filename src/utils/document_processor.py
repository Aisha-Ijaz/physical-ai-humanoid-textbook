import os
import re
from typing import List, Dict, Any
from pathlib import Path
import markdown
from bs4 import BeautifulSoup

from src.models.book_content import BookContentCreate
from src.models.content_chunk import ContentChunkCreate


def extract_text_from_markdown(file_path: str) -> str:
    """
    Extract text content from a markdown file
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        markdown_content = file.read()
    
    # Convert markdown to HTML
    html_content = markdown.markdown(markdown_content)
    
    # Extract text from HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text()
    
    return text


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """
    Split text into overlapping chunks
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # If this isn't the last chunk, try to break at sentence boundary
        if end < len(text):
            # Find the last sentence ending within the chunk
            chunk_text = text[start:end]
            last_period = chunk_text.rfind('. ')
            
            if last_period != -1 and last_period > chunk_size // 2:  # Only if it's reasonably far in
                end = start + last_period + 2  # +2 to include the '. '
        
        chunks.append(text[start:end])
        start = end - overlap if end - overlap > start else end
        
        # Prevent infinite loop in case of overlapping issues
        if start >= len(text):
            break
            
        # Ensure we don't have an empty chunk at the end
        if len(text) - start < 50 and len(chunks) > 0:
            # Append short ending to the last chunk
            chunks[-1] += text[start:]
            break
    
    return chunks


def process_book_markdown(book_path: str, title: str = None) -> BookContentCreate:
    """
    Process a book markdown file and convert it into a BookContentCreate object
    """
    if not title:
        title = Path(book_path).stem
    
    # Extract text from markdown
    full_text = extract_text_from_markdown(book_path)
    
    # Create BookContentCreate object
    book_content = BookContentCreate(
        title=title,
        content=full_text,
        metadata={"source_file": book_path, "processed_at": str(Path(book_path).stat().st_mtime)}
    )
    
    return book_content


def chunk_book_content(book_content: BookContentCreate, chunk_size: int = 1000, overlap: int = 100) -> List[ContentChunkCreate]:
    """
    Chunk the book content into smaller pieces for embedding
    """
    text_chunks = chunk_text(book_content.content, chunk_size, overlap)
    
    chunks = []
    for idx, chunk_text in enumerate(text_chunks):
        chunk = ContentChunkCreate(
            book_content_id="temp_id",  # This would be set after the book content is saved
            content=chunk_text,
            chunk_index=idx,
            embedding_id="",  # This would be set after embedding
            metadata={"chunk_index": idx, "source_title": book_content.title}
        )
        chunks.append(chunk)
    
    return chunks


def ingest_book_files(directory_path: str, pattern: str = "*.md") -> List[BookContentCreate]:
    """
    Ingest all book markdown files from a directory
    """
    book_contents = []
    
    for file_path in Path(directory_path).glob(pattern):
        try:
            book_content = process_book_markdown(str(file_path))
            book_contents.append(book_content)
            print(f"Successfully processed: {file_path.name}")
        except Exception as e:
            print(f"Error processing {file_path.name}: {str(e)}")
    
    return book_contents


if __name__ == "__main__":
    # Example usage
    # This script can be run directly to ingest books from a directory
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python document_processor.py <directory_path> [pattern]")
        sys.exit(1)
    
    directory_path = sys.argv[1]
    pattern = sys.argv[2] if len(sys.argv) > 2 else "*.md"
    
    print(f"Processing markdown files in {directory_path} with pattern {pattern}")
    books = ingest_book_files(directory_path, pattern)
    
    print(f"Processed {len(books)} books")