# Quick Start Guide

Get your AI Assistant Platform running in 5 minutes!

## 🚀 Option 1: Docker Compose (Easiest - Recommended)

### Prerequisites
- Docker Desktop installed and running
- ~5GB disk space for models

### Steps

```bash
# 1. Clone repository
cd /Users/saivishalmatcha/Desktop/ai-assistant-platform

# 2. Copy environment file
cp .env.example .env

# 3. Start all services
docker-compose up -d

# 4. Wait for services to be ready (2-5 minutes)
docker-compose logs -f
```

**You'll see**:
```
ai_postgres    | database system is ready to accept connections
ai_qdrant      | HTTP listening on 0.0.0.0:6333
ai_ollama      | listening on 127.0.0.1:11434
ai_api         | Uvicorn running on http://0.0.0.0:8000
```

### Access the API

- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs  ← Click here to test!
- **Health**: http://localhost:8000/health

---

## 🎯 Option 2: Local Development (Manual)

### Prerequisites
- Python 3.11+
- PostgreSQL running
- Ollama installed locally
- Qdrant running

### Steps

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
export DATABASE_URL="sqlite:///./test.db"  # Or PostgreSQL
export QDRANT_URL="http://localhost:6333"
export OLLAMA_HOST="http://localhost:11434"
export OLLAMA_MODEL="mistral"
export SECRET_KEY="dev-secret-change-in-production"

# 3. Start server
uvicorn app.main:app --reload

# 4. Access at http://localhost:8000
```

---

## 📋 First Steps After Starting

### 1️⃣ Test the API

Visit **http://localhost:8000/docs** in your browser:

1. Click "Try it out" on `/api/auth/register`
2. Enter test user:
   ```json
   {
     "username": "testuser",
     "email": "test@example.com",
     "password": "password123"
   }
   ```
3. Click "Execute"

### 2️⃣ Login and Get Token

1. Click `/api/auth/login`
2. Enter credentials:
   ```json
   {
     "username": "testuser",
     "password": "password123"
   }
   ```
3. Copy the `access_token`

### 3️⃣ Chat with the AI

1. Click `/api/chat/chat`
2. Click "Authorize" and paste your token
3. Send a message:
   ```json
   {
     "message": "What is machine learning?",
     "use_documents": false
   }
   ```
4. Get AI response!

### 4️⃣ Upload Documents (RAG)

1. Click `/api/documents/upload`
2. Authorize with your token
3. Upload a `.txt` file
4. Chat with `use_documents: true`

---

## 🔧 Common Commands

```bash
# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Clean up everything
docker-compose down -v

# Pull new Ollama model
docker exec ai_ollama ollama pull llama2

# Access database
docker exec -it ai_postgres psql -U ai_user -d ai_assistant

# Access Qdrant UI
# http://localhost:6333/dashboard
```

---

## 🐛 Troubleshooting

### API won't start
```bash
# Check all services
docker-compose ps

# View API logs
docker-compose logs api

# Restart API
docker-compose restart api
```

### Ollama downloading slowly
```bash
# Check download progress
docker logs ai_ollama -f

# Use a smaller model
docker exec ai_ollama ollama pull neural-chat
```

### Can't connect to database
```bash
# Check PostgreSQL
docker exec ai_postgres pg_isready -U ai_user

# Restart PostgreSQL
docker-compose restart postgres
```

### Port already in use
```bash
# Change ports in docker-compose.yml
# Or kill the process:
lsof -i :8000  # Find PID
kill -9 <PID>
```

---

## 📚 Next Steps

1. **Explore API**: Visit http://localhost:8000/docs
2. **Read**: Check [README.md](README.md) for full documentation
3. **Customize**: Update `OLLAMA_MODEL` to use different LLMs
4. **Deploy**: Push to GitHub and deploy with Docker

---

## 💡 Tips

- **Models**: Mistral (fast), Llama2 (powerful), Neural-Chat (optimized)
- **Documents**: Upload PDFs/TXT for RAG-powered responses
- **Conversations**: Multi-turn chat with context memory
- **Tasks**: AI can analyze and execute complex tasks

---

## 🚀 Ready?

Start with Docker:
```bash
docker-compose up -d && echo "✅ Running at http://localhost:8000"
```

Then visit: **http://localhost:8000/docs**

Happy Building! 🎉
