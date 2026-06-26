# Architecture & Design

## System Design

### Request Flow (Workflow Implementation)

```
Client Request
    ↓
1. API receives request
    ↓
2. Validate user/auth (JWT middleware)
    ↓
3. Fetch task/user context (database.py)
    ↓
4. Retrieve relevant documents if RAG (rag.py → Qdrant)
    ↓
5. Build prompt (PromptBuilder in rag.py)
    ↓
6. Call LLM (RAGEngine → Ollama)
    ↓
7. Validate/parse response
    ↓
8. Store result (PostgreSQL)
    ↓
9. Return response (JSON)
```

## Component Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Application                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   auth.py    │  │ database.py  │  │  schemas.py  │ │
│  │              │  │              │  │              │ │
│  │ • JWT tokens │  │ • DB setup   │  │ • Validation │ │
│  │ • Passwords  │  │ • Sessions   │  │ • Types      │ │
│  │ • Users      │  │ • ORM        │  │              │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │              rag.py (RAG Engine)                 │  │
│  │                                                   │  │
│  │ ┌──────────────────────────────────────────────┐ │  │
│  │ │ RAGEngine                                    │ │  │
│  │ │ • get_embedding() → Ollama embeddings       │ │  │
│  │ │ • add_document() → Store in Qdrant          │ │  │
│  │ │ • retrieve_documents() → Semantic search    │ │  │
│  │ │ • generate_response() → Call LLM            │ │  │
│  │ └──────────────────────────────────────────────┘ │  │
│  │                                                   │  │
│  │ ┌──────────────────────────────────────────────┐ │  │
│  │ │ PromptBuilder                                │ │  │
│  │ │ • build_chat_prompt()                       │ │  │
│  │ │ • build_rag_prompt()                        │ │  │
│  │ │ • build_task_prompt()                       │ │  │
│  │ └──────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ routes/auth  │  │ routes/chat  │  │ routes/tasks │ │
│  │              │  │              │  │              │ │
│  │ • register   │  │ • chat       │  │ • create     │ │
│  │ • login      │  │ • get conv   │  │ • list       │ │
│  │ • me         │  │ • get msgs   │  │ • delete     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                         │
│  ┌──────────────┐                                      │
│  │ routes/docs  │                                      │
│  │              │                                      │
│  │ • upload     │                                      │
│  │ • list       │                                      │
│  │ • delete     │                                      │
│  └──────────────┘                                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
        ↓              ↓              ↓              ↓
   PostgreSQL      Qdrant      Ollama LLM      Embeddings
```

## Data Models

### User
```
id: UUID
username: string (unique)
email: string (unique)
hashed_password: string
is_active: boolean
created_at: datetime
updated_at: datetime
```

### Conversation
```
id: UUID
user_id: UUID → User
title: optional string
created_at: datetime
updated_at: datetime
messages: [Message]  ← One-to-many
```

### Message
```
id: UUID
conversation_id: UUID → Conversation
role: "user" | "assistant"
content: text
tokens_used: integer
created_at: datetime
```

### Document
```
id: UUID
user_id: UUID → User
filename: string
content: text (first 5000 chars)
vector_id: string → Qdrant
status: "indexed" | "processing" | "failed"
created_at: datetime
updated_at: datetime
```

### Task
```
id: UUID
user_id: UUID → User
title: string
description: text
status: "pending" | "processing" | "completed" | "failed"
result: JSON
created_at: datetime
updated_at: datetime
```

## Authentication Flow

```
┌─────────────────┐
│  Client         │
└────────┬────────┘
         │
         │ 1. POST /register
         │    (username, email, password)
         ↓
┌─────────────────────────────┐
│  Auth Handler (auth.py)     │
│  • hash_password()          │
│  • Create User              │
└────────┬────────────────────┘
         │
         │ 2. POST /login
         │    (username, password)
         ↓
┌─────────────────────────────┐
│  authenticate_user()        │
│  • Verify password          │
│  • Return user              │
└────────┬────────────────────┘
         │
         │ 3. create_access_token()
         │
         ↓
┌─────────────────────────────┐
│  JWT Token                  │
│  {exp, sub: user_id}        │
└────────┬────────────────────┘
         │
         │ 4. Bearer token in header
         │    Authorization: Bearer <token>
         ↓
┌─────────────────────────────┐
│  get_current_user()         │
│  • Decode JWT               │
│  • Fetch user from DB       │
│  • Return user              │
└─────────────────────────────┘
```

## Chat Workflow

```
Client: "What is in my documents?"
         │
         ↓
    1. Validate user/auth
         ↓
    2. Create/get conversation
         ↓
    3. If use_documents=true:
         ├→ Query: "What is in my documents?"
         ├→ Get embeddings for query
         ├→ Search Qdrant (similarity search)
         └→ Get top 3 matching documents
         │
         ↓
    4. Build prompt with context:
         ├→ System prompt
         ├→ Retrieved documents
         ├→ Conversation history
         └→ User message
         │
         ↓
    5. Call Ollama LLM
         │
         ├→ POST /api/generate
         ├→ model: "mistral"
         ├→ prompt: <built prompt>
         ├→ temperature: 0.7
         └→ Return: response text
         │
         ↓
    6. Validate response
         ├→ Check not empty
         ├→ Check reasonable length
         └→ Return text
         │
         ↓
    7. Store in database
         ├→ Insert user message
         ├→ Insert assistant message
         └→ Update conversation
         │
         ↓
    8. Return to client
         └→ JSON response
```

## RAG System

```
Document Upload → Embeddings → Vector Store → Retrieval
         ↓            ↓             ↓             ↓
    text.txt    Ollama      Qdrant      Semantic
    content  embeddings   vectors      search
              384-dim

Example:
1. Upload: "Python is a programming language"
   ↓
2. Get embedding: [0.45, 0.23, ..., 0.89]  (384 dimensions)
   ↓
3. Store in Qdrant with metadata
   ↓
4. User asks: "What languages do you know?"
   ↓
5. Get query embedding: [0.41, 0.28, ..., 0.85]
   ↓
6. Search Qdrant (cosine similarity)
   ↓
7. Return: "Python is a programming language" (0.92 similarity)
   ↓
8. Include in prompt context for LLM
```

## Task Execution

```
Create Task
    ↓
Title: "Analyze Python Code"
Description: "Best practices in Python"
    ↓
Build task prompt
    ↓
Call LLM with structured output request
    ↓
LLM analyzes task
Returns: {
  "breakdown": [...steps...],
  "considerations": [...points...],
  "challenges": [...risks...],
  "approach": "recommended approach"
}
    ↓
Store result in task.result JSON
    ↓
Status: completed
```

## Deployment Architecture

### Local Development
```
Client ↔ FastAPI (localhost:8000)
             ↓
    SQLite database
    Qdrant (localhost:6333)
    Ollama (localhost:11434)
```

### Docker Compose
```
Container Network
├── api (FastAPI, port 8000)
│   └── depends_on: postgres, qdrant, ollama
├── postgres (port 5432)
│   └── volume: postgres_data
├── qdrant (port 6333)
│   └── volume: qdrant_data
└── ollama (port 11434)
    └── volume: ollama_data
```

### Production Deployment
```
Load Balancer
    ↓
┌───────────────────┐
│  API Container(s) │
│  (Kubernetes)     │
└───────┬───────────┘
        ↓
┌───────────────────────────────────────┐
│  PostgreSQL (RDS/Cloud SQL)           │
│  Qdrant (Cloud deployment or self)    │
│  Ollama (self-hosted or external LLM) │
└───────────────────────────────────────┘
```

## Performance Considerations

### Optimizations
1. **Connection Pooling**: SQLAlchemy with pool_pre_ping
2. **Vector Search**: Qdrant with HNSW indexing (O(log n))
3. **Caching**: Conversation context (last 5 messages)
4. **Async**: FastAPI async routes
5. **Embedding Model**: Lightweight (nomic-embed-text)

### Bottlenecks
1. **LLM Inference**: Ollama response time (varies by model)
2. **Vector Search**: Qdrant latency (usually <100ms)
3. **Database**: PostgreSQL query optimization
4. **Network**: API-to-service communication

### Scaling Strategy
- **Horizontal**: Multiple API instances with load balancer
- **Vertical**: Larger machines for Ollama/Qdrant
- **Caching**: Redis for conversation cache
- **Batching**: Batch multiple requests to Ollama

## Security Architecture

```
Request → CORS Check → Auth Middleware → Route Handler → DB
              ↓             ↓
         Whitelist      JWT Validation
         origins        get_current_user

Database:
- ORM (SQLAlchemy) prevents SQL injection
- Password hashing (bcrypt)
- Environment variables for secrets
```

## Error Handling

```
Try Block (Route Handler)
    ↓
    └→ Database error → 400/500 with details
    └→ LLM error → Default response
    └→ Auth error → 401 Unauthorized
    └→ Validation error → 422 Unprocessable Entity
    └→ Not found → 404 Not Found
```

---

## Technology Choices

| Component | Choice | Why |
|-----------|--------|-----|
| Framework | FastAPI | Modern, fast, async-ready |
| Database | PostgreSQL | Production-ready, ACID |
| Vectors | Qdrant | Lightweight, semantic search |
| LLM | Ollama | Local control, multiple models |
| Auth | JWT | Stateless, scalable |
| ORM | SQLAlchemy | Flexible, powerful queries |
| Embedding | nomic-embed-text | Fast, 384-dim vectors |

---

## Next Steps

1. **Scale horizontally**: Add load balancer
2. **Optimize inference**: Try smaller models or inference servers
3. **Add caching**: Redis for conversations
4. **Monitor**: Add observability (Prometheus, ELK)
5. **Secure**: Add HTTPS, rate limiting, CORS restrictions
