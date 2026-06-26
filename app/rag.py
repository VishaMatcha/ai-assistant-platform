import requests
import json
from typing import List, Dict, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import hashlib
from datetime import datetime
import os


class RAGEngine:
    """RAG (Retrieval Augmented Generation) Engine using Qdrant and Ollama"""

    def __init__(self):
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "mistral")
        self.client = QdrantClient(url=self.qdrant_url)
        self.collection_name = "documents"
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        """Ensure Qdrant collection exists"""
        try:
            self.client.get_collection(self.collection_name)
        except:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )

    def get_embedding(self, text: str) -> List[float]:
        """Get text embedding from Ollama"""
        try:
            response = requests.post(
                f"{self.ollama_host}/api/embeddings",
                json={"model": "nomic-embed-text", "prompt": text},
                timeout=30,
            )
            if response.status_code == 200:
                return response.json()["embedding"]
        except Exception as e:
            print(f"Embedding error: {e}")
        return [0.0] * 384  # Fallback embedding

    def add_document(self, content: str, metadata: Dict = None) -> str:
        """Add document to vector store"""
        try:
            embedding = self.get_embedding(content[:1000])
            doc_id = hashlib.md5(content.encode()).hexdigest()[:8]

            point = PointStruct(
                id=int(doc_id, 16) % 10**9,
                vector=embedding,
                payload={
                    "content": content,
                    "metadata": metadata or {},
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

            self.client.upsert(self.collection_name, points=[point])
            return doc_id
        except Exception as e:
            print(f"Error adding document: {e}")
            return None

    def retrieve_documents(self, query: str, limit: int = 3) -> List[Dict]:
        """Retrieve relevant documents using semantic search"""
        try:
            query_embedding = self.get_embedding(query)
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=0.5,
            )

            documents = []
            for result in results:
                documents.append(
                    {
                        "content": result.payload.get("content", ""),
                        "score": result.score,
                        "metadata": result.payload.get("metadata", {}),
                    }
                )
            return documents
        except Exception as e:
            print(f"Error retrieving documents: {e}")
            return []

    def generate_response(
        self,
        prompt: str,
        context: str = "",
        system_prompt: str = "",
    ) -> str:
        """Generate response using Ollama"""
        try:
            full_prompt = f"{system_prompt}\n\n{context}\n\nQuestion: {prompt}"

            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "temperature": 0.7,
                },
                timeout=60,
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
        except Exception as e:
            print(f"Error generating response: {e}")

        return "I'm unable to process your request at the moment. Please try again."


class PromptBuilder:
    """Build optimized prompts for LLM"""

    @staticmethod
    def build_chat_prompt(
        user_message: str,
        conversation_history: List[Dict] = None,
        system_prompt: str = "",
    ) -> str:
        """Build chat prompt with history"""
        prompt = system_prompt or "You are a helpful AI assistant."

        if conversation_history:
            prompt += "\n\n## Conversation History\n"
            for msg in conversation_history[-5:]:  # Last 5 messages
                role = "User" if msg["role"] == "user" else "Assistant"
                prompt += f"\n{role}: {msg['content']}"

        prompt += f"\n\nUser: {user_message}\nAssistant:"
        return prompt

    @staticmethod
    def build_rag_prompt(
        user_question: str,
        documents: List[str],
        system_prompt: str = "",
    ) -> tuple:
        """Build RAG prompt with context"""
        context = ""
        if documents:
            context = "## Relevant Documents:\n"
            for i, doc in enumerate(documents, 1):
                context += f"\n[Document {i}]:\n{doc[:500]}...\n"

        system = system_prompt or "You are a helpful AI assistant that answers questions based on provided documents."
        prompt = f"{system}\n\n{context}\n\nQuestion: {user_question}\nAnswer:"

        return prompt, context

    @staticmethod
    def build_task_prompt(
        task_title: str,
        task_description: str,
    ) -> str:
        """Build task execution prompt"""
        prompt = f"""
Task: {task_title}
Description: {task_description}

Please analyze this task and provide:
1. A breakdown of steps needed
2. Key considerations
3. Potential challenges
4. Recommended approach

Format your response as structured JSON.
"""
        return prompt
