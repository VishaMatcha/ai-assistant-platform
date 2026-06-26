#!/usr/bin/env python3
"""
Python client for AI Assistant Platform
Example usage of the API
"""

import requests
import json
from typing import Optional

class AIAssistantClient:
    """Simple client for AI Assistant Platform API"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.headers = {"Content-Type": "application/json"}

    def register(self, username: str, email: str, password: str) -> dict:
        """Register a new user"""
        response = requests.post(
            f"{self.base_url}/api/auth/register",
            json={"username": username, "email": email, "password": password},
            headers=self.headers,
        )
        return response.json()

    def login(self, username: str, password: str) -> dict:
        """Login and get access token"""
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            json={"username": username, "password": password},
            headers=self.headers,
        )
        data = response.json()
        if "access_token" in data:
            self.token = data["access_token"]
            self._update_headers()
        return data

    def _update_headers(self):
        """Update headers with authentication"""
        self.headers["Authorization"] = f"Bearer {self.token}"

    def get_me(self) -> dict:
        """Get current user info"""
        response = requests.get(
            f"{self.base_url}/api/auth/me",
            headers=self.headers,
        )
        return response.json()

    def chat(
        self,
        message: str,
        use_documents: bool = False,
        conversation_id: Optional[str] = None,
    ) -> dict:
        """Send a chat message"""
        response = requests.post(
            f"{self.base_url}/api/chat/chat",
            json={
                "message": message,
                "use_documents": use_documents,
                "conversation_id": conversation_id,
            },
            headers=self.headers,
        )
        return response.json()

    def get_conversations(self) -> list:
        """Get all conversations"""
        response = requests.get(
            f"{self.base_url}/api/chat/conversations",
            headers=self.headers,
        )
        return response.json()

    def get_conversation(self, conversation_id: str) -> dict:
        """Get specific conversation"""
        response = requests.get(
            f"{self.base_url}/api/chat/conversations/{conversation_id}",
            headers=self.headers,
        )
        return response.json()

    def upload_document(self, file_path: str) -> dict:
        """Upload a document for RAG"""
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(
                f"{self.base_url}/api/documents/upload",
                files=files,
                headers={"Authorization": f"Bearer {self.token}"},
            )
        return response.json()

    def list_documents(self) -> list:
        """List all documents"""
        response = requests.get(
            f"{self.base_url}/api/documents/",
            headers=self.headers,
        )
        return response.json()

    def create_task(self, title: str, description: str) -> dict:
        """Create and execute a task"""
        response = requests.post(
            f"{self.base_url}/api/tasks/",
            json={"title": title, "description": description},
            headers=self.headers,
        )
        return response.json()

    def list_tasks(self) -> list:
        """List all tasks"""
        response = requests.get(
            f"{self.base_url}/api/tasks/",
            headers=self.headers,
        )
        return response.json()


def main():
    """Example usage"""
    client = AIAssistantClient()

    print("🤖 AI Assistant Platform - Python Client Example\n")

    # 1. Register
    print("1️⃣  Registering user...")
    result = client.register(
        username="demo_user",
        email="demo@example.com",
        password="demo_password_123",
    )
    print(f"✅ Registered: {result.get('username', 'Error')}\n")

    # 2. Login
    print("2️⃣  Logging in...")
    result = client.login(username="demo_user", password="demo_password_123")
    print(f"✅ Token: {client.token[:20]}...\n")

    # 3. Get user info
    print("3️⃣  Getting user info...")
    result = client.get_me()
    print(f"✅ User: {result.get('email')}\n")

    # 4. Chat without documents
    print("4️⃣  Sending chat message...")
    result = client.chat(
        message="What is the capital of France?",
        use_documents=False,
    )
    print(f"🤖 Response: {result.get('assistant_message')}\n")

    # 5. Create a task
    print("5️⃣  Creating a task...")
    result = client.create_task(
        title="Analyze Python Code",
        description="Analyze best practices in Python programming",
    )
    print(f"✅ Task: {result.get('title')} - Status: {result.get('status')}")
    if result.get("result"):
        print(f"📊 Result: {json.dumps(result['result'], indent=2)[:200]}...\n")

    # 6. List conversations
    print("6️⃣  Getting conversations...")
    convs = client.get_conversations()
    print(f"✅ Found {len(convs)} conversation(s)\n")

    # 7. List tasks
    print("7️⃣  Getting tasks...")
    tasks = client.list_tasks()
    print(f"✅ Found {len(tasks)} task(s)\n")

    print("✨ All examples completed successfully!")
    print("\n📚 For more examples, see the API docs at:")
    print("   http://localhost:8000/docs")


if __name__ == "__main__":
    main()
