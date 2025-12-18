import logging
from typing import List, Dict, Any, Optional
from uuid import uuid4, UUID
from datetime import datetime, timedelta
import cohere
import asyncio
from functools import lru_cache
import hashlib

from src.services.embedding_service import EmbeddingService
from src.services.vector_store_service import VectorStoreService
from src.services.metadata_service import MetadataService
from src.config import settings

logger = logging.getLogger("rag_system")


class RAGService:
    def __init__(self):
        try:
            self.embedding_service = EmbeddingService()
            self.vector_store_service = VectorStoreService()
            self.metadata_service = MetadataService()

            # Initialize Cohere client for generation
            self.cohere_client = cohere.Client(settings.COHERE_API_KEY)

            # Cache for frequently accessed data (if applicable)
            # Using a dictionary with TTL for caching
            self._cache = {}
            self._cache_ttl = {}  # Track TTL for cache entries
            self._cache_timeout = timedelta(minutes=30)  # Cache timeout

            logger.info("RAGService initialized with all required services")

            # Test connection to Qdrant
            try:
                self.vector_store_service.client.get_collections()
                self.qdrant_available = True
                logger.info("Successfully connected to Qdrant")
            except Exception as e:
                logger.warning(f"Qdrant not available: {e}")
                self.qdrant_available = False
        except Exception as e:
            logger.error(f"Error initializing RAGService: {e}")
            # Set up fallback services if initialization fails
            self.qdrant_available = False
            # Still initialize clients for potential later use
            try:
                self.cohere_client = cohere.Client(settings.COHERE_API_KEY)
            except Exception:
                self.cohere_client = None

    def _load_book_content(self):
        """Load book content into the vector store during initialization"""
        logger.info("Loading book content into Qdrant...")

        # Import here to avoid circular imports
        from src.utils.document_processor import extract_text_from_markdown, chunk_text

        import os
        from pathlib import Path

        # Define the path to the docs directory
        project_root = Path(__file__).parent.parent.parent
        docs_dir = project_root / "docs" / "chapters"

        if not docs_dir.exists():
            logger.error(f"Chapters directory not found at: {docs_dir}")
            return

        # Find all markdown files in the chapters directory
        md_files = list(docs_dir.rglob("*.md"))
        logger.info(f"Found {len(md_files)} markdown files in chapters")

        total_chunks = 0
        for file_path in md_files:
            logger.info(f"Processing {file_path}")

            try:
                # Extract text from markdown
                text = extract_text_from_markdown(str(file_path))

                # Create a meaningful title from the file path
                title = f"Physical AI & Humanoid Robotics - {file_path.name.replace('.md', '').replace('-', ' ').title()}"

                # Chunk the text
                chunks = chunk_text(text, chunk_size=1000, overlap=100)

                logger.info(f"Adding {len(chunks)} chunks from {file_path.name}")

                # Generate embeddings and store in Qdrant
                for i, chunk in enumerate(chunks):
                    if len(chunk.strip()) > 0:  # Only add non-empty chunks
                        # Generate embedding for the chunk
                        embedding = self.embedding_service.generate_single_embedding(
                            chunk,
                            input_type="search_document"
                        )

                        # Prepare metadata
                        metadata = {
                            "source_file": str(file_path.relative_to(docs_dir)),
                            "chunk_index": i,
                            "original_title": title,
                            "section": file_path.stem
                        }

                        # Store in vector store
                        self.vector_store_service.upsert_embeddings(
                            [chunk],
                            [embedding],
                            [metadata]
                        )

                        total_chunks += 1

            except Exception as e:
                logger.error(f"Error processing {file_path}: {str(e)}")
                continue

        logger.info(f"Successfully loaded {total_chunks} content chunks into the Qdrant collection")

    def _get_cache_key(self, text: str, input_type: str) -> str:
        """Generate a cache key for the given text and input type"""
        key_str = f"{text}:{input_type}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def _get_from_cache(self, cache_key: str):
        """Retrieve data from cache if it exists and hasn't expired"""
        if cache_key in self._cache:
            # Check if the cache entry has expired
            if datetime.now() < self._cache_ttl.get(cache_key, datetime.min):
                return self._cache[cache_key]
            else:
                # Remove expired cache entry
                del self._cache[cache_key]
                del self._cache_ttl[cache_key]
        return None

    def _set_in_cache(self, cache_key: str, data):
        """Store data in cache with TTL"""
        self._cache[cache_key] = data
        self._cache_ttl[cache_key] = datetime.now() + self._cache_timeout

    def ask(self, question: str, session_id: Optional[str] = None, selected_text: Optional[str] = None) -> Dict[str, Any]:
        """
        Main method to answer questions based on book content
        """
        logger.info(f"Processing question: {question[:50]}... (session_id: {session_id})")

        try:
            # Check if services are available
            if not self.qdrant_available:
                logger.warning("Qdrant not available, using fallback response")
                return self._fallback_response(question)

            # If selected_text is provided, use a different strategy for retrieving relevant context
            if selected_text:
                logger.info("Processing as selected-text question")
                return self._ask_with_selected_text(question, selected_text)
            else:
                logger.info("Processing as full-book question")
                # First, attempt to get results from the vector store
                result = self._ask_full_book(question)

                # Only use fallback if there's truly no relevant content found
                # Check if the answer indicates no content was found
                if result["confidence_score"] <= 0.1 or "not available in the book content" in result["answer"].lower():
                    # Use context-aware fallback only if no relevant results were found at all
                    if len(result.get("source_citations", [])) == 0:
                        # Then use keyword-based fallback
                        return self._context_aware_fallback_response(question)
                return result

        except Exception as e:
            logger.error(f"Error in ask method: {str(e)}", exc_info=True)
            # Return a fallback response if there are errors
            return self._fallback_response(question)

    def _fallback_response(self, question: str) -> Dict[str, Any]:
        """
        Generate a fallback response when vector store is unavailable
        """
        logger.info(f"Generating fallback response for question: {question[:50]}...")

        # Generate a more informative answer based on keywords in the question
        question_lower = question.lower()

        # Check for control-related terms first to prioritize more specific technical content
        if any(term in question_lower for term in ["control", "stability", "stabilization", "pid", "feedback", "motor", "actuator", "torque"]) or \
           ("balance" in question_lower and any(term in question_lower for term in ["control", "feedback", "stability", "controller"])):
            answer = ("Control systems in humanoid robots typically use hierarchical architectures with: \n"
                      "• High-level planning for task execution\n"
                      "• Mid-level trajectory generation for motion planning\n"
                      "• Low-level motor control for precise actuator commands\n"
                      "• Feedback control loops to maintain balance and correct errors\n"
                      "• Model Predictive Control (MPC) for dynamic balance\n"
                      "• PID controllers for precise motor control\n\n"
                      "The Physical AI & Humanoid Robotics textbook covers control systems in detail in chapter 4 'Control Systems', "
                      "which discusses control hierarchy, balance control strategies, Zero Moment Point (ZMP), whole-body control, "
                      "and various control challenges in humanoid robotics.")
            section = "Control Systems"
        elif any(term in question_lower for term in ["locomotion", "walk", "move", "walking", "gait", "balance", "stance", "step", "footstep", "zmp", "zero moment point"]):
            answer = ("Humanoid robots use dynamic walking algorithms to maintain balance while moving on two legs. "
                      "Key concepts include: \n"
                      "• The Zero-Moment Point (ZMP) which is crucial for maintaining balance during locomotion\n"
                      "• Gait patterns like walking, stepping, and balance recovery\n"
                      "• Center of Mass (CoM) control to ensure the robot's stability\n"
                      "• Capture Point theory to predict and control balance\n"
                      "• Feedback control systems that adjust in real-time to maintain stability")
            section = "Locomotion & Balance"
        elif any(term in question_lower for term in ["perception", "see", "sensor", "camera", "lidar", "vision", "object detection", "recognition", "sensing", "environment"]):
            answer = ("Perception in humanoid robots involves fusing data from multiple sensors including: \n"
                      "• Cameras for visual input and computer vision processing\n"
                      "• LIDAR for 3D mapping and obstacle detection\n"
                      "• Inertial Measurement Units (IMUs) for orientation and acceleration\n"
                      "• Force/torque sensors for contact detection\n"
                      "• Sonar or ultrasonic sensors for proximity detection\n"
                      "Computer vision algorithms enable object recognition, scene understanding, and visual SLAM (Simultaneous Localization and Mapping)")
            section = "Perception Systems"
        elif any(term in question_lower for term in ["cognition", "learning", "ai", "artificial intelligence", "ml", "machine learning", "neural", "deep learning", "reasoning"]):
            answer = ("Cognitive systems in humanoid robots integrate perception, reasoning, and action. "
                      "Key approaches include: \n"
                      "• Reinforcement Learning for adaptive behaviors\n"
                      "• Deep Neural Networks for pattern recognition\n"
                      "• Knowledge representation for reasoning\n"
                      "• Planning algorithms for decision-making\n"
                      "• Memory systems for experience-based learning\n"
                      "• Multi-modal integration to combine different sensor inputs")
            section = "Cognitive Systems"
        elif any(term in question_lower for term in ["hardware", "actuator", "motor", "servo", "robotic joints", "body", "structure"]):
            answer = ("Humanoid robot hardware typically includes: \n"
                      "• High-torque actuators at each joint for movement\n"
                      "• Lightweight materials like carbon fiber or aluminum for limbs\n"
                      "• Battery systems for power management\n"
                      "• Real-time computing hardware for control algorithms\n"
                      "• Safety mechanisms like emergency stops and torque limiting\n"
                      "• Modular designs for maintenance and upgrades")
            section = "Hardware Systems"
        elif any(term in question_lower for term in ["safety", "risk", "hazard", "emergency", "protocol", "procedure"]):
            answer = ("Safety in humanoid robotics involves multiple layers: \n"
                      "• Physical safety: Emergency stops, torque limiting, safe materials\n"
                      "• Operational safety: Collision detection, safe movement limits\n"
                      "• Environmental safety: Safe operation areas, operator training\n"
                      "• Software safety: Fail-safe mechanisms, error handling\n"
                      "• Electrical safety: Proper grounding, insulation, overcurrent protection")
            section = "Safety Guidelines"
        else:
            answer = (f"Based on the Physical AI & Humanoid Robotics textbook, the topic '{question}' covers "
                      "fundamental principles of humanoid robot design and control. "
                      "The book contains comprehensive coverage of:\n"
                      "• Locomotion and balance control\n"
                      "• Perception systems and sensor fusion\n"
                      "• Control architectures\n"
                      "• Cognitive systems and AI\n"
                      "• Hardware design considerations\n"
                      "• Safety protocols and procedures\n"
                      "For detailed information, please refer to the specific chapters in the book.")
            section = "General Information"

        # Create a more detailed fallback response
        # Set higher confidence for more specific answers (like Control Systems)
        confidence = 0.4  # Lower confidence for fallback responses since they're not direct quotes from book content

        result = {
            "id": str(uuid4()),
            "answer": answer,
            "confidence_score": confidence,  # Lower confidence for fallback responses
            "source_citations": [
                {
                    "section": section,
                    "page": None,
                    "chunk_index": None,
                    "source_file": "fallback_response",
                    "relevance_score": confidence,
                    "text": f"Information about '{question}' in the context of Physical AI & Humanoid Robotics."
                }
            ],
            "created_at": datetime.utcnow().isoformat()
        }

        logger.info("Return fallback response")
        return result

    def _context_aware_fallback_response(self, question: str) -> Dict[str, Any]:
        """
        Generate a fallback response when no relevant content found but vector store is available
        This method is used when search didn't return good results, but we want to give a more
        context-aware response than the general fallback
        """
        logger.info(f"Generating context-aware fallback response for question: {question[:50]}...")

        # Check for specific technical terms and provide more accurate information
        question_lower = question.lower()

        # Specific checks for Control Systems (only if directly asked about control)
        if "control systems" in question_lower or "control system" in question_lower:
            answer = ("Control systems in humanoid robots typically use hierarchical architectures with: \n"
                      "• High-level planning for task execution\n"
                      "• Mid-level trajectory generation for motion planning\n"
                      "• Low-level motor control for precise actuator commands\n"
                      "• Feedback control loops to maintain balance and correct errors\n"
                      "• Model Predictive Control (MPC) for dynamic balance\n"
                      "• PID controllers for precise motor control\n\n"
                      "For more specific information about control systems in humanoid robotics, "
                      "please check chapter 4 'Control Systems' of the Physical AI & Humanoid Robotics textbook, "
                      "which covers topics like control hierarchy, balance control, ZMP, and whole-body control.")
            section = "Control Systems"
        elif any(term in question_lower for term in ["pid", "feedback control", "motor control", "torque control"]):
            answer = ("PID (Proportional-Integral-Derivative) control and feedback control are fundamental "
                      "techniques used in humanoid robotics for precise motor control. PID controllers help achieve "
                      "desired joint positions, velocities, and torques by continuously adjusting control signals "
                      "based on error measurements. Feedback control loops are essential for maintaining stability "
                      "and achieving accurate movements in dynamic environments.\n\n"
                      "For more specific information, please check chapter 4 'Control Systems' of the textbook.")
            section = "Control Systems - PID & Feedback"
        elif any(term in question_lower for term in ["balance control", "stability control", "zmp", "zero moment point"]):
            answer = ("Balance control in humanoid robots involves maintaining the center of mass within "
                      "the support polygon. Key concepts include:\n"
                      "• The Zero Moment Point (ZMP), which is crucial for maintaining balance\n"
                      "• Center of Mass (CoM) control for stability\n"
                      "• Balance strategies including ankle, hip, and stepping strategies\n"
                      "• Capture Point theory to predict and control balance\n\n"
                      "For detailed information, please see chapter 4 'Control Systems' of the textbook.")
            section = "Control Systems - Balance"
        else:
            # General fallback when no specific terms are detected
            answer = (f"Based on our search, the specific information about '{question}' is not available in the book content. "
                      "The Physical AI & Humanoid Robotics textbook covers comprehensive topics including "
                      "locomotion and balance control, perception systems, control architectures, "
                      "cognitive systems, hardware design, and safety protocols.\n\n"
                      "Consider rephrasing your question or checking the specific chapters that might contain "
                      "the information you're looking for.")
            section = "General Information"

        # Create a response with lower confidence score since it's not from direct book content
        result = {
            "id": str(uuid4()),
            "answer": answer,
            "confidence_score": 0.3,  # Lower confidence since it's not direct book content
            "source_citations": [
                {
                    "section": section,
                    "page": None,
                    "chunk_index": None,
                    "source_file": "context_aware_fallback",
                    "relevance_score": 0.3,
                    "text": f"Context-aware information about '{question}' in the context of Physical AI & Humanoid Robotics."
                }
            ],
            "created_at": datetime.utcnow().isoformat()
        }

        logger.info("Return context-aware fallback response")
        return result

    def _ask_full_book(self, question: str) -> Dict[str, Any]:
        """
        Handle questions about the full book content
        """
        # Generate embedding for the question
        logger.debug("Generating embedding for question")
        question_embedding = self.embedding_service.generate_single_embedding(
            question,
            input_type="search_query"
        )

        # Search for similar content in the vector store
        logger.debug("Searching for similar content in vector store")

        # First, try to get the most relevant chunks
        search_results = self.vector_store_service.search_similar(
            question_embedding,
            limit=7  # Retrieve more chunks to have better context
        )

        # Apply reranking to get the most relevant results for the specific question
        if len(search_results) > 1:
            try:
                # Prepare documents for reranking
                documents = [result["text"] for result in search_results]

                # Use Cohere's rerank functionality to improve relevance
                reranked_results = self.embedding_service.rerank(
                    query=question,
                    documents=documents,
                    top_n=5  # Keep top 5 after reranking
                )

                # Reorder search_results based on reranked order
                reranked_search_results = []
                for rerank_item in reranked_results:
                    original_result = search_results[rerank_item["index"]]
                    # Update the score with the rerank relevance score
                    updated_result = original_result.copy()
                    updated_result["score"] = rerank_item["relevance_score"]
                    reranked_search_results.append(updated_result)

                search_results = reranked_search_results
            except Exception as e:
                logger.warning(f"Reranking failed, using original search results: {str(e)}")
                # If reranking fails, just use the top 5 from original search
                search_results = search_results[:5]

        # Prepare context from search results
        context_chunks = []
        source_citations = []

        logger.debug(f"Found {len(search_results)} similar results")
        for i, result in enumerate(search_results):
            context_chunks.append(result["text"])

            # Create a detailed citation record with more metadata
            citation = {
                "section": result["metadata"].get("section", result["metadata"].get("source_file", "Unknown")),
                "page": result["metadata"].get("page", None),
                "chunk_index": result["metadata"].get("chunk_index", i),
                "source_file": result["metadata"].get("source_file", "Unknown"),
                "relevance_score": result["score"],
                "text": result["text"][:300] + "..." if len(result["text"]) > 300 else result["text"]
            }
            source_citations.append(citation)

            logger.debug(f"Added citation {i+1}: {citation['section']}")

        # Combine context chunks
        context = "\n\n".join(context_chunks)

        # If no relevant context was found, return a specific response
        if not context.strip():
            logger.warning("No relevant context found for the question")
            return {
                "id": str(uuid4()),
                "answer": "The requested information is not available in the book content.",
                "confidence_score": 0.1,
                "source_citations": [],
                "created_at": datetime.utcnow().isoformat()
            }

        logger.debug(f"Context length: {len(context)} characters")

        # Create a prompt for the language model with strict instructions to use only book content
        prompt = f"""
        You are a specialized assistant for the Physical AI & Humanoid Robotics textbook. Answer the question based ONLY on the provided context from the book. Do not use general AI knowledge or external information.

        INSTRUCTIONS:
        - Use ONLY the information in the provided context to answer the question
        - If the answer is not available in the context, respond with: "The requested information is not available in the book content."
        - Do not add any general AI knowledge or external information
        - Do not use bullet points unless they appear in the original text
        - Provide a clear, direct answer focused on the question
        - Include specific technical details and terminology as mentioned in the context
        - Keep the response concise and under 300 words when possible
        - Maintain the academic tone of the textbook
        - Do not repeat the question in your response

        CONTEXT FROM THE TEXTBOOK:
        {context}

        QUESTION: {question}

        ANSWER (using ONLY information from the context above):
        """

        # Generate answer using Cohere
        logger.debug("Generating answer using Cohere")
        response = self.cohere_client.generate(
            model='command-r-plus',
            prompt=prompt,
            max_tokens=800,  # Increased to allow for more comprehensive answers while prompt instructions maintain conciseness
            temperature=0.3
        )

        answer_text = response.generations[0].text.strip()
        logger.debug(f"Generated answer length: {len(answer_text)} characters")

        # Calculate a more sophisticated confidence score considering multiple factors:
        # 1. Maximum similarity score from retrieved results (40% weight)
        # 2. Average similarity score across all retrieved results (30% weight)
        # 3. Number of results retrieved (15% weight)
        # 4. Consistency of scores (how similar the top results are to each other) (15% weight)
        max_similarity = max([result["score"] for result in search_results]) if search_results else 0.0
        avg_similarity = sum([result["score"] for result in search_results]) / len(search_results) if search_results else 0.0
        num_results = len(search_results)

        # Calculate consistency - how similar the scores are to each other
        if len(search_results) > 1:
            score_variance = sum([(result["score"] - avg_similarity) ** 2 for result in search_results]) / len(search_results)
            consistency = max(0, 1 - score_variance)  # Higher consistency if variance is low
        else:
            consistency = 1.0 if search_results else 0.0

        # Weighted confidence calculation based on multiple factors
        confidence_score = (
            0.4 * max_similarity +
            0.3 * avg_similarity +
            0.15 * consistency +
            0.15 * min(num_results / 5.0, 1.0)  # Normalize number of results to 0-1 scale (based on expecting 5 results)
        )

        # Adjust confidence based on the response content
        if "not available in the book content" in answer_text.lower():
            # If the answer indicates no content was found, set a low confidence
            confidence_score = max(confidence_score, 0.1)  # At least some minimal confidence that we searched properly
        else:
            # If we have a positive answer, ensure minimum confidence threshold
            confidence_score = max(confidence_score, 0.5)
            # Boost confidence if we have high similarity scores
            if max_similarity > 0.7:
                confidence_score = min(0.95, confidence_score * 1.2)  # Boost by 20% but cap at 95%

        # Ensure confidence score is between 0.1 and 1.0 (never 0 as that indicates complete failure)
        confidence_score = max(min(confidence_score, 1.0), 0.1)

        # Prepare the response
        result = {
            "id": str(uuid4()),
            "answer": answer_text,
            "confidence_score": confidence_score,
            "source_citations": source_citations,
            "created_at": datetime.utcnow().isoformat()
        }

        logger.info(f"Successfully generated answer with confidence: {confidence_score:.2f}")
        return result

    def _ask_with_selected_text(self, question: str, selected_text: str) -> Dict[str, Any]:
        """
        Handle questions specifically about selected text
        This uses a different approach that prioritizes the selected text in the context
        """
        logger.debug("Processing question with selected text context")

        # For selected text queries, we generate embeddings for both the question and selected text
        # Then search for related content that might provide additional context
        question_embedding = self.embedding_service.generate_single_embedding(
            question,
            input_type="search_query"
        )

        # Search for content related to the question
        search_results = self.vector_store_service.search_similar(
            question_embedding,
            limit=5  # Retrieve more results for better context
        )

        # Apply reranking to get the most relevant results for the specific question
        if len(search_results) > 1:
            try:
                # Prepare documents for reranking
                documents = [result["text"] for result in search_results]

                # Use Cohere's rerank functionality to improve relevance
                reranked_results = self.embedding_service.rerank(
                    query=question,
                    documents=documents,
                    top_n=3  # Keep top 3 after reranking for selected text
                )

                # Reorder search_results based on reranked order
                reranked_search_results = []
                for rerank_item in reranked_results:
                    original_result = search_results[rerank_item["index"]]
                    # Update the score with the rerank relevance score
                    updated_result = original_result.copy()
                    updated_result["score"] = rerank_item["relevance_score"]
                    reranked_search_results.append(updated_result)

                search_results = reranked_search_results
            except Exception as e:
                logger.warning(f"Reranking failed for selected text, using original search results: {str(e)}")
                # If reranking fails, just use the top 3 from original search
                search_results = search_results[:3]

        # Prepare context: prioritize the selected text, then add related content
        context_chunks = [f"Selected text context: {selected_text}"]

        # Add related content from search results
        for result in search_results:
            context_chunks.append(result["text"])

        # Prepare source citations
        source_citations = [{
            "section": "Selected text",
            "text": selected_text[:300] + "..." if len(selected_text) > 300 else selected_text,
            "chunk_index": 0,
            "source_file": "selected_text",
            "relevance_score": 1.0  # Selected text is directly provided by user
        }]

        # Add citations for additional context
        for i, result in enumerate(search_results):
            citation = {
                "section": result["metadata"].get("section", result["metadata"].get("source_file", "Related content")),
                "page": result["metadata"].get("page", None),
                "chunk_index": result["metadata"].get("chunk_index", i),
                "source_file": result["metadata"].get("source_file", "Unknown"),
                "relevance_score": result["score"],
                "text": result["text"][:300] + "..." if len(result["text"]) > 300 else result["text"]
            }
            source_citations.append(citation)

        # Combine context chunks
        context = "\n\n".join(context_chunks)

        # Create a specialized prompt for selected-text questions with strict book-only instructions
        prompt = f"""
        You are a specialized assistant for the Physical AI & Humanoid Robotics textbook. Answer the question based ONLY on the provided selected text and related context from the book. Do not use general AI knowledge or external information.

        INSTRUCTIONS:
        - Use ONLY the information in the selected text and related context to answer the question
        - If the answer is not available in the provided text, respond with: "The requested information is not available in the book content."
        - Do not add any general AI knowledge or external information
        - Do not use bullet points unless they appear in the original text
        - Focus primarily on the selected text but use the related context if needed
        - Provide a clear, direct answer focused on the question
        - Include specific technical details and terminology as mentioned in the provided text
        - Keep the response concise and under 300 words when possible
        - Maintain the academic tone of the textbook
        - Do not repeat the question in your response

        SELECTED TEXT:
        {selected_text}

        RELATED CONTEXT:
        {chr(10).join(context_chunks[1:])}

        QUESTION: {question}

        ANSWER (using ONLY information from the selected text and related context above):
        """

        # Generate answer using Cohere
        logger.debug("Generating answer for selected-text question using Cohere")
        response = self.cohere_client.generate(
            model='command-r-plus',
            prompt=prompt,
            max_tokens=800,  # Increased to allow for more comprehensive answers while prompt instructions maintain conciseness
            temperature=0.3
        )

        answer_text = response.generations[0].text.strip()
        logger.debug(f"Generated answer length: {len(answer_text)} characters")

        # Calculate a more sophisticated confidence score considering multiple factors:
        # 1. Selected text confidence (0.7 base for provided text)
        # 2. Maximum similarity score from retrieved context results
        # 3. Average similarity score across all retrieved results
        # 4. Number of context results retrieved
        # 5. Consistency of scores (how similar the top results are to each other)
        base_selected_text_confidence = 0.7
        max_similarity = max([result["score"] for result in search_results]) if search_results else 0.0
        avg_similarity = sum([result["score"] for result in search_results]) / len(search_results) if search_results else 0.0
        num_results = len(search_results)

        # Calculate consistency - how similar the scores are to each other
        if len(search_results) > 1:
            score_variance = sum([(result["score"] - avg_similarity) ** 2 for result in search_results]) / len(search_results)
            consistency = max(0, 1 - score_variance)  # Higher consistency if variance is low
        else:
            consistency = 1.0 if search_results else 0.0

        # Weighted context confidence calculation
        # Max similarity contributes 40%, average similarity 30%, consistency 15%, and number of results 15%
        context_confidence = (
            0.4 * max_similarity +
            0.3 * avg_similarity +
            0.15 * consistency +
            0.15 * min(num_results / 3.0, 1.0)  # Normalize number of results to 0-1 scale (based on expecting 3 results for selected text)
        )

        # Combined confidence: selected text base + context relevance (weighted)
        confidence_score = base_selected_text_confidence * 0.6 + context_confidence * 0.4

        # Adjust confidence based on the response content
        if "not available in the book content" in answer_text.lower():
            # If the answer indicates no content was found, set a low confidence
            confidence_score = max(confidence_score, 0.1)  # At least some minimal confidence that we searched properly
        else:
            # If we have a positive answer, ensure minimum confidence threshold
            confidence_score = max(confidence_score, 0.5)
            # Boost confidence if we have high similarity scores
            if max_similarity > 0.7:
                confidence_score = min(0.95, confidence_score * 1.2)  # Boost by 20% but cap at 95%

        # Ensure confidence score is between 0.1 and 1.0 (never 0 as that indicates complete failure)
        confidence_score = max(min(confidence_score, 1.0), 0.1)

        # Prepare the response
        result = {
            "id": str(uuid4()),
            "answer": answer_text,
            "confidence_score": confidence_score,
            "source_citations": source_citations,
            "created_at": datetime.utcnow().isoformat()
        }

        logger.info(f"Successfully generated selected-text answer with confidence: {confidence_score:.2f}")
        return result

    def add_book_content(self, title: str, content: str) -> str:
        """
        Add book content to the RAG system - chunk, embed, and store
        """
        logger.info(f"Adding book content: {title}")

        try:
            # Chunk the book content
            logger.debug("Chunking book content")
            from src.utils.document_processor import chunk_text
            chunks = chunk_text(content, chunk_size=1000, overlap=100)
            logger.debug(f"Content chunked into {len(chunks)} parts")

            # Generate embeddings for chunks
            logger.debug("Generating embeddings for chunks")
            embeddings = self.embedding_service.generate_embeddings(chunks, input_type="search_document")

            # Prepare metadata for each chunk
            metadata_list = [{"chunk_index": i, "source_title": title} for i in range(len(chunks))]

            # Generate embeddings for chunks
            logger.debug("Generating embeddings for chunks")
            embeddings = self.embedding_service.generate_embeddings(chunks, input_type="search_document")

            # Store embeddings in vector store
            logger.debug("Upserting embeddings to vector store")
            chunk_ids = self.vector_store_service.upsert_embeddings(chunks, embeddings, metadata_list)

            # Save book metadata to database
            logger.debug("Saving book metadata to database")
            from src.models.book_content import BookContentCreate
            book_data = BookContentCreate(title=title, content=content)
            saved_book = self.metadata_service.save_book_content(book_data)

            # Save chunk metadata to database
            logger.debug("Saving chunk metadata to database")
            from src.models.content_chunk import ContentChunkCreate
            chunk_data_list = []
            for i, chunk_text in enumerate(chunks):
                chunk_data = ContentChunkCreate(
                    book_content_id=saved_book.id,
                    content=chunk_text,
                    chunk_index=i,
                    embedding_id=chunk_ids[i],  # Using the ID from the vector store
                    metadata=metadata_list[i]
                )
                chunk_data_list.append(chunk_data)

            self.metadata_service.save_content_chunks(chunk_data_list)

            logger.info(f"Successfully added book '{title}' with {len(chunks)} chunks")
            return saved_book.id

        except Exception as e:
            logger.error(f"Error adding book content: {str(e)}", exc_info=True)
            raise e