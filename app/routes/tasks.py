from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import json
from app.database import get_db
from app.models import User, Task
from app.schemas import TaskCreate, TaskResponse
from app.auth import get_current_user
from app.rag import RAGEngine, PromptBuilder

router = APIRouter()
rag_engine = RAGEngine()


@router.post("/", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create and execute a task following the workflow:
    1. Validate user/auth ✓
    2. Fetch task/user context ✓
    3. Retrieve relevant documents if needed
    4. Build prompt
    5. Call LLM
    6. Validate/parse response
    7. Store result
    8. Return response
    """

    # Step 1-2: Already validated
    db_task = Task(
        user_id=current_user.id,
        title=task.title,
        description=task.description,
        status="processing",
    )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    try:
        # Step 4: Build prompt for task analysis
        prompt = PromptBuilder.build_task_prompt(task.title, task.description)

        # Step 5: Call LLM
        response = rag_engine.generate_response(
            prompt,
            system_prompt="You are an expert task analyzer. Respond in valid JSON format.",
        )

        # Step 6: Validate/parse response
        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            result = {"analysis": response}

        # Step 7: Store result
        db_task.status = "completed"
        db_task.result = result
        db.commit()
        db.refresh(db_task)

    except Exception as e:
        db_task.status = "failed"
        db_task.result = {"error": str(e)}
        db.commit()
        db.refresh(db_task)

    # Step 8: Return response
    return db_task


@router.get("/", response_model=list[TaskResponse])
async def list_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all tasks for current user"""
    tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get specific task"""
    task = db.query(Task).filter(
        (Task.id == task_id) & (Task.user_id == current_user.id)
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete task"""
    task = db.query(Task).filter(
        (Task.id == task_id) & (Task.user_id == current_user.id)
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    db.delete(task)
    db.commit()

    return {"message": "Task deleted successfully"}
