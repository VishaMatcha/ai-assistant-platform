from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


# Auth schemas
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Document schemas
class DocumentUpload(BaseModel):
    filename: str
    content: str


class DocumentResponse(BaseModel):
    id: str
    filename: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# Message schemas
class MessageCreate(BaseModel):
    content: str
    use_rag: bool = False


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


# Conversation schemas
class ConversationResponse(BaseModel):
    id: str
    title: Optional[str]
    created_at: datetime
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True


# Task schemas
class TaskCreate(BaseModel):
    title: str
    description: str


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    status: str
    result: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


# Chat request/response
class ChatRequest(BaseModel):
    message: str
    use_documents: bool = False
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    conversation_id: str
    user_message: str
    assistant_message: str
    documents_used: int = 0
