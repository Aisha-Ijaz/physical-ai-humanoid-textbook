from typing import List, Optional
import logging
from datetime import datetime
import uuid

logger = logging.getLogger("rag_system")


class MetadataService:
    def __init__(self):
        # Initialize a simple in-memory store for fallback
        self.storage = {
            'books': {},
            'chunks': {},
            'questions': {}
        }

        # For production, we would connect to a proper database
        # Check if database is available
        try:
            from src.db import SessionLocal
            from src.models.question import Question, QuestionCreate
            from src.models.book_content import BookContent, BookContentCreate
            from src.models.content_chunk import ContentChunk, ContentChunkCreate

            self.db_available = True
            self.SessionLocal = SessionLocal
            self.models_loaded = True
        except Exception as e:
            logger.warning(f"Database not available, using in-memory storage: {str(e)}")
            self.db_available = False
            self.models_loaded = False

    def _get_db_session(self):
        """Get a database session if available, otherwise return None"""
        if self.db_available:
            return self.SessionLocal()
        return None

    def save_question(self, question_data: 'QuestionCreate') -> 'Question':
        """
        Save a question to the database or in-memory storage
        """
        if self.db_available and self.models_loaded:
            # Use the database
            try:
                from src.models.question import Question as QuestionModel
                db = self._get_db_session()
                # Create a Question instance
                db_question = QuestionModel(
                    id=question_data.id if hasattr(question_data, 'id') else None,
                    content=question_data.content,
                    selected_text=question_data.selected_text,
                    created_at=datetime.utcnow()
                )

                db.add(db_question)
                db.commit()
                db.refresh(db_question)

                logger.info(f"Saved question with ID: {db_question.id}")
                return db_question
            except Exception as e:
                if 'db' in locals():
                    db.rollback()
                logger.error(f"Error saving question: {str(e)}")
                raise e
            finally:
                if 'db' in locals():
                    db.close()
        else:
            # Use in-memory storage as fallback
            question_id = str(uuid.uuid4())
            question_obj = {
                'id': question_id,
                'content': question_data.content,
                'selected_text': question_data.selected_text,
                'created_at': datetime.utcnow()
            }

            self.storage['questions'][question_id] = question_obj
            logger.info(f"Saved question with ID: {question_id} to in-memory storage")
            return question_obj

    def save_book_content(self, book_data: 'BookContentCreate') -> 'BookContent':
        """
        Save book content to the database or in-memory storage
        """
        if self.db_available and self.models_loaded:
            # Use the database
            try:
                from src.models.book_content import BookContent as BookContentModel
                db = self._get_db_session()

                # Create a BookContent instance
                db_book = BookContentModel(
                    id=book_data.id if hasattr(book_data, 'id') else None,
                    title=book_data.title,
                    content=book_data.content,
                    metadata=book_data.metadata,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )

                db.add(db_book)
                db.commit()
                db.refresh(db_book)

                logger.info(f"Saved book content with ID: {db_book.id}")
                return db_book
            except Exception as e:
                if 'db' in locals():
                    db.rollback()
                logger.error(f"Error saving book content: {str(e)}")
                raise e
            finally:
                if 'db' in locals():
                    db.close()
        else:
            # Use in-memory storage as fallback
            book_id = str(uuid.uuid4())
            book_obj = {
                'id': book_id,
                'title': book_data.title,
                'content': book_data.content,
                'metadata': book_data.metadata,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }

            self.storage['books'][book_id] = book_obj
            logger.info(f"Saved book content with ID: {book_id} to in-memory storage")
            return book_obj

    def save_content_chunks(self, chunks_data: List['ContentChunkCreate']) -> List['ContentChunk']:
        """
        Save multiple content chunks to the database or in-memory storage
        """
        if self.db_available and self.models_loaded:
            # Use the database
            try:
                from src.models.content_chunk import ContentChunk as ContentChunkModel
                db = self._get_db_session()

                db_chunks = []
                for chunk_data in chunks_data:
                    # Create a ContentChunk instance
                    db_chunk = ContentChunkModel(
                        id=chunk_data.id if hasattr(chunk_data, 'id') else None,
                        book_content_id=chunk_data.book_content_id,
                        content=chunk_data.content,
                        chunk_index=chunk_data.chunk_index,
                        embedding_id=chunk_data.embedding_id,
                        metadata=chunk_data.metadata,
                        created_at=datetime.utcnow()
                    )
                    db.add(db_chunk)
                    db_chunks.append(db_chunk)

                db.commit()
                for db_chunk in db_chunks:
                    db.refresh(db_chunk)

                logger.info(f"Saved {len(db_chunks)} content chunks")
                return db_chunks
            except Exception as e:
                if 'db' in locals():
                    db.rollback()
                logger.error(f"Error saving content chunks: {str(e)}")
                raise e
            finally:
                if 'db' in locals():
                    db.close()
        else:
            # Use in-memory storage as fallback
            saved_chunks = []
            for chunk_data in chunks_data:
                chunk_id = str(uuid.uuid4())
                chunk_obj = {
                    'id': chunk_id,
                    'book_content_id': chunk_data.book_content_id,
                    'content': chunk_data.content,
                    'chunk_index': chunk_data.chunk_index,
                    'embedding_id': chunk_data.embedding_id,
                    'metadata': chunk_data.metadata,
                    'created_at': datetime.utcnow()
                }

                self.storage['chunks'][chunk_id] = chunk_obj
                saved_chunks.append(chunk_obj)

            logger.info(f"Saved {len(saved_chunks)} content chunks to in-memory storage")
            return saved_chunks

    def get_book_content_by_id(self, book_id: str) -> Optional['BookContent']:
        """
        Retrieve book content by ID from database or in-memory storage
        """
        if self.db_available and self.models_loaded:
            # Use the database
            try:
                from src.models.book_content import BookContent as BookContentModel
                db = self._get_db_session()

                book = db.query(BookContentModel).filter(BookContentModel.id == book_id).first()
                return book
            except Exception as e:
                logger.error(f"Error retrieving book content: {str(e)}")
                return None
            finally:
                if 'db' in locals():
                    db.close()
        else:
            # Use in-memory storage as fallback
            return self.storage['books'].get(book_id)

    def get_content_chunks_by_book(self, book_id: str) -> List['ContentChunk']:
        """
        Retrieve content chunks for a specific book from database or in-memory storage
        """
        if self.db_available and self.models_loaded:
            # Use the database
            try:
                from src.models.content_chunk import ContentChunk as ContentChunkModel
                db = self._get_db_session()

                chunks = db.query(ContentChunkModel)\
                           .filter(ContentChunkModel.book_content_id == book_id)\
                           .order_by(ContentChunkModel.chunk_index)\
                           .all()
                return chunks
            except Exception as e:
                logger.error(f"Error retrieving content chunks: {str(e)}")
                return []
            finally:
                if 'db' in locals():
                    db.close()
        else:
            # Use in-memory storage as fallback - filter chunks by book ID
            book_chunks = []
            for chunk in self.storage['chunks'].values():
                if chunk['book_content_id'] == book_id:
                    book_chunks.append(chunk)
            # Sort by chunk_index to maintain order
            book_chunks.sort(key=lambda x: x['chunk_index'])
            return book_chunks

    def update_book_content(self, book_id: str, content: str) -> Optional['BookContent']:
        """
        Update book content in database or in-memory storage
        """
        if self.db_available and self.models_loaded:
            # Use the database
            try:
                from src.models.book_content import BookContent as BookContentModel
                db = self._get_db_session()

                book = db.query(BookContentModel).filter(BookContentModel.id == book_id).first()
                if book:
                    book.content = content
                    book.updated_at = datetime.utcnow()
                    db.commit()
                    db.refresh(book)
                    logger.info(f"Updated book content with ID: {book_id}")
                    return book
                return None
            except Exception as e:
                if 'db' in locals():
                    db.rollback()
                logger.error(f"Error updating book content: {str(e)}")
                raise e
            finally:
                if 'db' in locals():
                    db.close()
        else:
            # Use in-memory storage as fallback
            if book_id in self.storage['books']:
                self.storage['books'][book_id]['content'] = content
                self.storage['books'][book_id]['updated_at'] = datetime.utcnow()
                logger.info(f"Updated book content with ID: {book_id} in in-memory storage")
                return self.storage['books'][book_id]
            return None