# 🚀 AI Assistant Platform - Complete Production System

**A fully functional, open-source AI platform demonstrating a complete LLM workflow with RAG, authentication, and task management.**

---

## 📋 Table of Contents

1. [Project Purpose](#project-purpose)
2. [Workflow Explanation](#workflow-explanation)
3. [System Architecture](#system-architecture)
4. [Key Features](#key-features)
5. [Technology Stack](#technology-stack)
6. [Installation & Setup](#installation--setup)
7. [Service Verification](#service-verification)
8. [API Documentation](#api-documentation)
9. [Test Results](#test-results)
10. [Usage Examples](#usage-examples)
11. [Deployment](#deployment)

---

## 🎯 Project Purpose

This project demonstrates a **production-ready AI Assistant platform** that implements a complete large language model (LLM) workflow. It serves as:

- **Educational Example**: Learn how to build LLM applications
- **Portfolio Project**: Showcase full-stack AI development skills
- **Prototype Foundation**: Build custom AI applications on top
- **Proof of Concept**: Demonstrate RAG, authentication, and task management

### Why This Project?

Traditional AI demos often mock the LLM responses or run on expensive cloud infrastructure. This project:
- ✅ Uses **real, local LLMs** (Mistral 7B)
- ✅ Runs entirely **on your machine** (Docker)
- ✅ Implements **production-ready patterns** (JWT auth, ORM, validation)
- ✅ Provides **complete documentation** (architecture, API, examples)
- ✅ Demonstrates **all major features** (chat, RAG, tasks, persistence)

---

## 🔄 Workflow Explanation

### The Complete LLM Pipeline

This system implements the exact workflow you requested:

```
┌─────────────────────────────────────────────────────────────┐
│                   AI ASSISTANT WORKFLOW                     │
└─────────────────────────────────────────────────────────────┘

1️⃣  CLIENT SENDS REQUEST
    └─ Browser/Mobile/API Client
    └─ Example: "What's in my documents?"

2️⃣  API RECEIVES REQUEST
    └─ FastAPI FastAPI endpoint
    └─ Parses JSON, extracts message & options

3️⃣  VALIDATE USER/AUTH (JWT MIDDLEWARE)
    └─ Extract Bearer token from header
    └─ Decode JWT signature
    └─ Verify token hasn't expired
    └─ Fetch user from database
    └─ ✅ User authenticated

4️⃣  FETCH TASK/USER CONTEXT (DATABASE)
    └─ Query PostgreSQL for user info
    └─ Fetch existing conversation (if provided)
    └─ Get last 5 messages for context
    └─ Load user preferences
    └─ ✅ Context retrieved

5️⃣  RETRIEVE RELEVANT DOCUMENTS IF RAG
    └─ IF use_documents == true:
    │   ├─ Get embedding for user query
    │   │  └─ Send query to Ollama embeddings
    │   │  └─ Get 384-dimensional vector
    │   ├─ Search Qdrant vector database
    │   │  └─ Cosine similarity search
    │   │  └─ Return top 3 matching documents
    │   └─ Include document context in prompt
    └─ ✅ Documents retrieved & ranked

6️⃣  BUILD PROMPT (PROMPTBUILDER)
    └─ Start with system prompt
    └─ Add retrieved documents (if any)
    └─ Add conversation history
    └─ Add current user message
    └─ Format for Mistral model
    └─ ✅ Prompt ready

7️⃣  CALL LLM (OLLAMA → MISTRAL 7B)
    └─ Send prompt to Ollama HTTP API
    └─ Model: mistral:latest (4.4 GB)
    └─ Temperature: 0.7 (balanced creativity)
    └─ Wait for response (1-5 seconds)
    └─ Parse streaming response
    └─ ✅ LLM returns completion

8️⃣  VALIDATE/PARSE RESPONSE
    └─ Check response is not empty
    └─ Verify reasonable length
    └─ No malicious content checks
    └─ Extract clean text
    └─ ✅ Response validated

9️⃣  STORE RESULT (POSTGRESQL)
    └─ Insert user message into database
    └─ Insert assistant message
    └─ Update conversation timestamp
    └─ Log tokens used
    └─ ✅ Data persisted

🔟 RETURN RESPONSE (JSON)
    └─ Format response JSON:
    │  ├─ conversation_id
    │  ├─ user_message
    │  ├─ assistant_message
    │  └─ documents_used (count)
    └─ HTTP 200 OK
    └─ ✅ Client receives response

```

### Real Example: "What is the capital of France?"

```
User: "What is the capital of France?"
     │
     ├─ Auth Check: ✅ Valid JWT token
     │
     ├─ Context: Conversation #abc123, User: john_doe
     │
     ├─ Documents: No RAG (use_documents=false)
     │
     ├─ Prompt Built:
     │  "System: You are a helpful assistant.
     │   History: (empty for first message)
     │   User: What is the capital of France?"
     │
     ├─ LLM (Mistral): Processing...
     │
     ├─ Response: "The capital of France is Paris."
     │
     ├─ Stored: ✅ In PostgreSQL
     │
     └─ Returned: ✅ JSON response