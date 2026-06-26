from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
from app.database import get_db
from app.models import User, Conversation, Message
from app.schemas import ChatRequest, ChatResponse, ConversationResponse, MessageResponse
from app.auth import get_current_user
from app.rag import RAGEngine, PromptBuilder

router = APIRouter()
rag_engine = RAGEngine()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Chat endpoint following the workflow:
    1. Validate user/auth ✓ (via Depends)
    2. Fetch task/user context
    3. Retrieve relevant documents if RAG
    4. Build prompt
    5. Call LLM
    6. Validate/parse response
    7. Store result
    8. Return response
    """

    # Step 1: Validate user/auth (already done via Depends)

    # Step 2: Fetch or create conversation
    conversation = None
    if request.conversation_id:
        conversation = db.query(Conversation).filter(
            (Conversation.id == request.conversation_id)
            & (Conversation.user_id == current_user.id)
        ).first()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )
    else:
        conversation = Conversation(user_id=current_user.id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Step 3: Retrieve relevant documents if RAG requested
    context = ""
    documents_used = 0
    if request.use_documents:
        docs = rag_engine.retrieve_documents(request.message, limit=3)
        documents_used = len(docs)
        context = "\n".join([doc["content"] for doc in docs])

    # Step 4: Build prompt
    conversation_messages = db.query(Message).filter(
        Message.conversation_id == conversation.id
    ).all()

    msg_history = [
        {"role": msg.role, "content": msg.content}
        for msg in conversation_messages[-5:]
    ]

    if context:
        prompt, _ = PromptBuilder.build_rag_prompt(
            request.message,
            [context],
            system_prompt="You are a helpful AI assistant that answers questions accurately.",
        )
    else:
        prompt = PromptBuilder.build_chat_prompt(
            request.message,
            msg_history,
            system_prompt="You are a helpful AI assistant.",
        )

    # Step 5: Call LLM
    response_text = rag_engine.generate_response(prompt)

    # Step 6: Validate/parse response
    if not response_text or len(response_text.strip()) == 0:
        response_text = "I apologize, but I wasn't able to generate a response. Please try again."

    # Step 7: Store result
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message,
    )
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=response_text,
    )

    db.add(user_message)
    db.add(assistant_message)
    db.commit()

    # Step 8: Return response
    return ChatResponse(
        conversation_id=conversation.id,
        user_message=request.message,
        assistant_message=response_text,
        documents_used=documents_used,
    )


@router.get("/conversations", response_model=list[ConversationResponse])
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all conversations for current user"""
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).all()

    result = []
    for conv in conversations:
        messages = db.query(Message).filter(
            Message.conversation_id == conv.id
        ).all()

        result.append(
            ConversationResponse(
                id=conv.id,
                title=conv.title,
                created_at=conv.created_at,
                messages=[MessageResponse.from_orm(m) for m in messages],
            )
        )

    return result


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get specific conversation"""
    conversation = db.query(Conversation).filter(
        (Conversation.id == conversation_id)
        & (Conversation.user_id == current_user.id)
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    messages = db.query(Message).filter(
        Message.conversation_id == conversation.id
    ).all()

    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        messages=[MessageResponse.from_orm(m) for m in messages],
    )
