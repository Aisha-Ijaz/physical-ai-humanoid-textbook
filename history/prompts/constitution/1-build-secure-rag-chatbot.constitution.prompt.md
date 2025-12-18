---
id: 1
title: "Build Secure RAG Chatbot Constitution"
stage: constitution
date_iso: "2025-12-13"
surface: "agent"
model: "gpt-4o"
feature: "none"
branch: "main"
user: "user"
command: "/sp.constitution Build a secure, simple RAG chatbot for a Docusaurus book. Use FastAPI, Qdrant Cloud, Neon Postgres, Cohere embeddings. Answer ONLY from book content. Support normal questions and selected-text questions. Return short, clear answers."
labels: ["constitution", "rag", "chatbot", "security"]
spec: null
ticket: null
adr: null
pr: null
files_yaml:
  - ".specify/memory/constitution.md"
tests_yaml: []
prompt_text: |
  /sp.constitution Build a secure, simple RAG chatbot for a Docusaurus book.
  Use FastAPI, Qdrant Cloud, Neon Postgres, Cohere embeddings.
  Answer ONLY from book content.
  Support normal questions and selected-text questions.
  Return short, clear answers.
response_text: |
  Created a new constitution for the RAG Chatbot project with 6 core principles: 
  1. Security-First Architecture
  2. Accuracy Through Book Content Only
  3. Simplicity and Clarity
  4. Selective Text Question Support
  5. Robust Data Pipeline
  6. Resilient Infrastructure
  
  Also added sections for Technology Stack Requirements and Development Workflow,
  along with governance information and version tracking.
outcome: |
  Successfully created the constitution file with all requested principles and requirements.
evaluation: |
  The constitution correctly captures all the requirements from the user input: 
  security-first approach, accuracy from book content only, simplicity, support 
  for selected-text questions, and the specified tech stack (FastAPI, Qdrant 
  Cloud, Neon Postgres, Cohere embeddings).
---

# RAG Chatbot for Docusaurus Book Constitution

## Core Principles

### Security-First Architecture
All components must prioritize security by design; Implement proper authentication, authorization, and data protection; Encrypt data in transit and at rest; Secure APIs with rate limiting and input validation

### Accuracy Through Book Content Only
The chatbot MUST ONLY answer from the book content provided; No hallucinations allowed; Response must cite source documents with confidence scores; Fail gracefully when questions fall outside book scope

### Simplicity and Clarity
Answers must be short, clear, and directly address user questions; Complex topics should be broken down into simple points; User interface must be intuitive with minimal cognitive load

### Selective Text Question Support
System must handle both normal queries and selected-text questions; Selected text functionality must allow users to highlight content and ask questions about it; Context from selected text must be properly integrated into responses

### Robust Data Pipeline
Implement reliable document ingestion, chunking, and indexing pipeline; Ensure high-quality embeddings using Cohere; Maintain vector store (Qdrant Cloud) and metadata store (Neon Postgres) synchronization

### Resilient Infrastructure
Leverage FastAPI for high-performance API layer with proper error handling and monitoring; Design for scalability and reliability with cloud services (Qdrant Cloud, Neon Postgres); Implement circuit breakers and retry mechanisms

## Technology Stack Requirements

Use FastAPI for the backend API; Integrate with Qdrant Cloud for vector storage; Use Neon Postgres for metadata and user session data; Implement Cohere embeddings for document vectorization; Deploy on a secure cloud platform with HTTPS

## Development Workflow

Follow test-driven development practices; Ensure all API endpoints have security tests; Conduct regular security audits; Verify accuracy of responses against source documents; Perform load testing to validate performance

## Governance
Constitution applies to all project decisions; Amendments require team approval and documented migration plans; All PRs must verify compliance with principles

**Version**: 1.0.0 | **Ratified**: 2025-06-13 | **Last Amended**: 2025-12-13