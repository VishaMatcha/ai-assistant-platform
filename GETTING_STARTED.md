# Getting Started with AI Assistant Platform

Your AI Assistant Platform is now running locally! Here's how to use it.

## 🎯 Access the Platform

### API Documentation (Swagger UI)
**Open in your browser:** http://localhost:8000/docs

This interactive documentation lets you:
1. Test all API endpoints directly
2. View request/response schemas
3. See live examples

### API Health
Check if everything is running: http://localhost:8000/health

---

## 🚀 Quick Start (5 minutes)

### 1. Register a User
Visit http://localhost:8000/docs and:
1. Click `POST /api/auth/register`
2. Click "Try it out"
3. Enter:
   ```json
   {
     "username": "myuser",
     "email": "myuser@example.com",
     "password": "password123"
   }
   ```
4. Click "Execute"
5. You'll get your User ID back

### 2. Login
1. Click `POST /api/auth/login`
2. Enter your username and password
3. Copy the `access_token` from the response

### 3. Authorize Swagger
1. Click the green "Authorize" button (top right)
2. Paste: `Bearer <your_access_token>`
3. Click "Authorize" and close

### 4. Chat with AI
1. Click `POST /api/chat/chat`
2. Click "Try it out"
3. Send a message:
   ```json
   {
     "message": "What is machine learning?",
     "use_documents": false
   }
   ```
4. Click "Execute"
5. Get AI response!

---

## 📚 Complete Workflow

### Upload Documents (RAG)
1. Click `POST /api/documents/upload`
2. Upload a `.txt` or `.md` file
3. Get the document ID

### Chat with Documents
1. Click `POST /api/chat/chat`
2. Use the document context:
   ```json
   {
     "message": "What's in my documents?",
     "use_documents": true
   }
   ```

### Create Tasks
1. Click `POST /api/tasks/`
2. Ask AI to analyze something:
   ```json
   {
     "title": "Analyze Python",
     "description": "Best practices in Python programming"
   }
   ```
3. Get structured analysis back

### View Conversations
1. Click `GET /api/chat/conversations`
2. See all your chat histories
3. Click `GET /api/chat/conversations/{id}`
4. See full conversation with all messages

---

## 🐍 Using Python Client

Use the included client SDK:

```python
from client import AIAssistantClient

client = AIAssistantClient("http://localhost:8000")

# Register
client.register("username", "email@example.com", "password")

# Login
client.login("username", "password")

# Chat
response = client.chat("Hello AI!")
print(response['assistant_message'])

# Upload document
client.upload_document("/path/to/file.txt")

# Create task
task = client.create_task("Analyze Code", "Review Python code")
print(task['result'])
```

Run the example:
```bash
python client.py
```

---

## 📊 Architecture Overview

```
You (Browser/Client)
    ↓
FastAPI (8000)
    ├→ PostgreSQL (Database)
    ├→ Qdrant (Vector Search)
    ├→ Ollama (LLM - Mistral)
    └→ Embeddings (nomic-embed-text)
```

---

## 🔧 Managing Services

### View Logs
```bash
docker-compose logs -f api
docker-compose logs -f ollama
docker-compose logs -f postgres
```

### Restart Services
```bash
docker-compose restart api
docker-compose restart ollama
```

### Stop Everything
```bash
docker-compose down
```

### Restart Everything
```bash
docker-compose up -d
```

---

## ⚙️ Configuration

Environment variables in `docker-compose.yml`:

- `DATABASE_URL` - PostgreSQL connection
- `QDRANT_URL` - Vector database endpoint
- `OLLAMA_HOST` - LLM server
- `OLLAMA_MODEL` - Default: mistral (can change to llama2, neural-chat, etc.)
- `SECRET_KEY` - JWT signing key (change in production!)

---

## 🎓 What You Can Do

### Chat Features
- ✅ Multi-turn conversations with history
- ✅ RAG (Retrieval Augmented Generation) with your documents
- ✅ Semantic search across uploaded files
- ✅ Context-aware responses

### Document Management
- ✅ Upload PDF/TXT files
- ✅ Automatic indexing for vector search
- ✅ Query documents with natural language
- ✅ Organize by user

### Task Execution
- ✅ Ask AI to analyze tasks
- ✅ Get structured JSON responses
- ✅ Track task status (pending/processing/completed)
- ✅ Store results for later retrieval

### Authentication
- ✅ JWT tokens for stateless auth
- ✅ Password hashing (bcrypt)
- ✅ User-scoped data (documents, conversations)

---

## 🚨 Troubleshooting

### API won't start
```bash
docker-compose logs api
docker-compose restart api
```

### Chat returns error
This likely means:
1. Ollama is still downloading Mistral (first time)
2. Check: `docker-compose logs ollama`
3. Wait for model to finish (~5-10 minutes for Mistral)

### Can't upload files
- Check file is `.txt` or `.md`
- Ensure you're authenticated (Bearer token)
- File should be under 100MB

### Connection refused
- Make sure Docker is running
- Check port 8000 is free
- Try: `docker-compose down && docker-compose up -d`

---

## 📖 Next Steps

1. **Explore API**: Visit http://localhost:8000/docs
2. **Upload docs**: Test RAG with your own documents
3. **Read ARCHITECTURE.md**: Understand the system design
4. **Customize**: Change OLLAMA_MODEL to try different LLMs

---

## 💡 Tips

- **Models**: Mistral (fast), Llama2 (powerful), Neural-Chat (optimized)
- **Token limit**: Keep conversations under ~2000 tokens
- **RAG**: Upload PDFs about a topic, then ask questions
- **Performance**: First request takes longer (model loading)

---

## 🎉 You're Ready!

Start exploring:
```
http://localhost:8000/docs
```

Happy building! 🚀
