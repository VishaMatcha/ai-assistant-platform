# AI Assistant Platform

A production-ready, open-source AI platform with RAG (Retrieval Augmented Generation), authentication, and task management capabilities.

## 🎯 Features

- **Chat API**: Interactive conversations with LLM (Ollama + Mistral)
- **RAG System**: Document upload and semantic search using Qdrant
- **Authentication**: JWT-based user authentication and authorization
- **Task Management**: Create and execute AI-powered tasks
- **Document Management**: Upload, store, and retrieve documents
- **Conversation History**: Multi-turn conversations with context preservation
- **RESTful API**: Full-featured API with OpenAPI documentation
- **Containerized**: Docker Compose setup for easy deployment

## 🏗️ Architecture

```
API Request
    ↓
Validate user/auth (JWT)
    ↓
Fetch task/user context (PostgreSQL)
    ↓
Retrieve relevant documents (Qdrant + Embeddings)
    ↓
Build prompt (PromptBuilder)
    ↓
Call LLM (Ollama)
    ↓
Validate/parse response
    ↓
Store result (PostgreSQL)
    ↓
Return response (JSON)
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Or: Python 3.11+, PostgreSQL, Ollama, Qdrant

### Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/VishaMatcha/ai-assistant-platform.git
cd ai-assistant-platform

# Copy environment file
cp .env.example .env

# Start services
docker-compose up -d

# Wait for Ollama to download Mistral model
# This takes ~5-10 minutes on first run
docker logs ai_ollama -f

# Once Mistral is pulled, API is ready at http://localhost:8000
```

### Local Development

```bash
# Install Python dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="sqlite:///./ai_assistant.db"
export QDRANT_URL="http://localhost:6333"
export OLLAMA_HOST="http://localhost:11434"
export OLLAMA_MODEL="mistral"
export SECRET_KEY="dev-key-change-in-production"

# Start development server
uvicorn app.main:app --reload

# API available at http://localhost:8000
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user

#### Chat
- `POST /api/chat/chat` - Send message and get response
- `GET /api/chat/conversations` - List all conversations
- `GET /api/chat/conversations/{id}` - Get specific conversation

#### Documents (RAG)
- `POST /api/documents/upload` - Upload document for RAG
- `GET /api/documents/` - List documents
- `DELETE /api/documents/{id}` - Delete document

#### Tasks
- `POST /api/tasks/` - Create and execute task
- `GET /api/tasks/` - List tasks
- `GET /api/tasks/{id}` - Get task result

### Example Usage

```bash
# 1. Register user
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'

# 2. Login
TOKEN=$(curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }' | jq -r '.access_token')

# 3. Send chat message
curl -X POST "http://localhost:8000/api/chat/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the main features of Python?",
    "use_documents": false
  }'

# 4. Upload document for RAG
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@path/to/document.txt"

# 5. Chat with RAG context
curl -X POST "http://localhost:8000/api/chat/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What information is in my uploaded documents?",
    "use_documents": true
  }'
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | sqlite:///./test.db | PostgreSQL connection string |
| `QDRANT_URL` | http://localhost:6333 | Qdrant vector DB URL |
| `OLLAMA_HOST` | http://localhost:11434 | Ollama server URL |
| `OLLAMA_MODEL` | mistral | LLM model to use |
| `SECRET_KEY` | dev-secret | JWT secret key (change in production!) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | Token expiration time |
| `API_HOST` | 0.0.0.0 | API server host |
| `API_PORT` | 8000 | API server port |

### Supported Models (via Ollama)

- `mistral` (7B) - Fast, good for conversations
- `llama2` (7B/13B) - General purpose
- `neural-chat` (7B) - Optimized for chat
- `dolphin-mixtral` (8x7B) - Larger model

To use a different model, update `OLLAMA_MODEL` and pull the model:

```bash
docker exec ai_ollama ollama pull llama2
```

## 📊 Database Schema

### Users Table
- `id` (UUID) - User ID
- `username` (string) - Unique username
- `email` (string) - Unique email
- `hashed_password` (string) - Bcrypt hashed password
- `is_active` (boolean) - Account status
- `created_at`, `updated_at` (datetime)

### Conversations Table
- `id` (UUID) - Conversation ID
- `user_id` (UUID) - Owner
- `title` (string) - Optional title
- `created_at`, `updated_at` (datetime)

### Messages Table
- `id` (UUID) - Message ID
- `conversation_id` (UUID) - Conversation reference
- `role` (string) - "user" or "assistant"
- `content` (text) - Message content
- `tokens_used` (integer) - Token count
- `created_at` (datetime)

### Documents Table
- `id` (UUID) - Document ID
- `user_id` (UUID) - Owner
- `filename` (string) - Original filename
- `content` (text) - Document content (first 5000 chars)
- `vector_id` (string) - Qdrant vector ID
- `status` (string) - "indexed" or "failed"
- `created_at`, `updated_at` (datetime)

### Tasks Table
- `id` (UUID) - Task ID
- `user_id` (UUID) - Owner
- `title` (string) - Task title
- `description` (text) - Task description
- `status` (string) - "pending", "processing", "completed", "failed"
- `result` (JSON) - Task result/output
- `created_at`, `updated_at` (datetime)

## 🔐 Security

- Passwords hashed with bcrypt
- JWT token-based authentication
- CORS configured for production use
- SQL injection protection via SQLAlchemy ORM
- Environment variables for sensitive data

**Important**: Change `SECRET_KEY` in production!

## 🚀 Deployment

### AWS EC2
```bash
# SSH into instance
ssh -i key.pem ubuntu@instance

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Clone and run
git clone https://github.com/VishaMatcha/ai-assistant-platform.git
cd ai-assistant-platform
docker-compose up -d
```

### Railway, Render, or Fly.io

Update `DATABASE_URL` to production PostgreSQL, then deploy.

### Kubernetes

Helm charts available (create if needed).

## 📝 Development

### Project Structure
```
ai-assistant-platform/
├── app/
│   ├── main.py              # FastAPI app
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── database.py          # DB setup
│   ├── auth.py              # JWT auth
│   ├── rag.py               # RAG engine
│   └── routes/
│       ├── auth.py          # Auth endpoints
│       ├── chat.py          # Chat endpoints
│       ├── documents.py     # Document endpoints
│       └── tasks.py         # Task endpoints
├── docker-compose.yml       # Container setup
├── Dockerfile               # App container
├── requirements.txt         # Python deps
├── .env.example            # Environment template
└── README.md               # This file
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Adding New Routes

1. Create file in `app/routes/`
2. Define APIRouter and endpoints
3. Include in `app/main.py`

Example:
```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/example")
async def example():
    return {"message": "Hello"}
```

## 🐛 Troubleshooting

### API won't start
```bash
# Check database connection
docker-compose logs postgres

# Check Ollama
docker-compose logs ollama

# Rebuild
docker-compose down && docker-compose up -d
```

### Documents not being retrieved
```bash
# Check Qdrant
docker-compose logs qdrant

# Verify embedding model
docker exec ai_ollama ollama list
```

### Out of memory
```bash
# Use smaller model
export OLLAMA_MODEL=neural-chat
docker-compose restart ollama
```

## 📄 License

MIT License - See LICENSE file

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push and create PR

## 📧 Support

For issues, questions, or suggestions:
- Open GitHub issue
- Contact: nivasverelli@gmail.com

## 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Ollama Models](https://ollama.ai)
- [Qdrant Vector Search](https://qdrant.tech/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [JWT Authentication](https://pyjwt.readthedocs.io/)

---

**Made with ❤️ using open-source tools**
