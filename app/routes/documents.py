from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
import uuid
from app.database import get_db
from app.models import User, Document
from app.schemas import DocumentResponse
from app.auth import get_current_user
from app.rag import RAGEngine

router = APIRouter()
rag_engine = RAGEngine()


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload and index a document for RAG"""
    try:
        content = await file.read()
        content_str = content.decode("utf-8")

        # Add to vector store
        vector_id = rag_engine.add_document(
            content_str,
            metadata={
                "filename": file.filename,
                "user_id": current_user.id,
            },
        )

        # Store in database
        db_document = Document(
            user_id=current_user.id,
            filename=file.filename,
            content=content_str[:5000],  # Store first 5000 chars
            vector_id=vector_id,
            status="indexed",
        )

        db.add(db_document)
        db.commit()
        db.refresh(db_document)

        return db_document

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing document: {str(e)}",
        )


@router.get("/", response_model=list[DocumentResponse])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all documents for current user"""
    documents = db.query(Document).filter(
        Document.user_id == current_user.id
    ).all()
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get specific document"""
    document = db.query(Document).filter(
        (Document.id == document_id) & (Document.user_id == current_user.id)
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return document


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete document"""
    document = db.query(Document).filter(
        (Document.id == document_id) & (Document.user_id == current_user.id)
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    db.delete(document)
    db.commit()

    return {"message": "Document deleted successfully"}
