from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.services.task_service import TaskService
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut, TaskListResponse, TaskStats
from app.models.task import TaskStatus, TaskPriority

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post(
    "/",
    response_model=TaskOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Create a new task for the authenticated user."
)
def create_task(
    task_create: TaskCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> TaskOut:
    """Create a new task."""
    task_service = TaskService(db)
    return task_service.create_task(task_create, user_id)


@router.get(
    "/",
    response_model=TaskListResponse,
    summary="Get all tasks",
    description="Get all tasks for the authenticated user with optional filtering and pagination."
)
def get_tasks(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by priority"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> TaskListResponse:
    """Get all tasks for the authenticated user."""
    task_service = TaskService(db)
    return task_service.get_tasks(
        owner_id=user_id,
        skip=skip,
        limit=limit,
        status=status,
        priority=priority
    )


@router.get(
    "/stats",
    response_model=TaskStats,
    summary="Get task statistics",
    description="Get task statistics for the authenticated user."
)
def get_task_stats(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> TaskStats:
    """Get task statistics for the authenticated user."""
    task_service = TaskService(db)
    return task_service.get_task_stats(user_id)


@router.get(
    "/{task_id}",
    response_model=TaskOut,
    summary="Get task by ID",
    description="Get a specific task by ID for the authenticated user."
)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> TaskOut:
    """Get a task by ID."""
    task_service = TaskService(db)
    task = task_service.get_task(task_id, user_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return task


@router.put(
    "/{task_id}",
    response_model=TaskOut,
    summary="Update task",
    description="Update a task for the authenticated user."
)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> TaskOut:
    """Update a task."""
    task_service = TaskService(db)
    task = task_service.update_task(task_id, task_update, user_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return task


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
    description="Delete a task for the authenticated user."
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> None:
    """Delete a task."""
    task_service = TaskService(db)
    success = task_service.delete_task(task_id, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )


@router.patch(
    "/{task_id}/complete",
    response_model=TaskOut,
    summary="Mark task as completed",
    description="Mark a task as completed for the authenticated user."
)
def mark_task_completed(
    task_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> TaskOut:
    """Mark a task as completed."""
    task_service = TaskService(db)
    task = task_service.mark_as_completed(task_id, user_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return task


@router.patch(
    "/{task_id}/incomplete",
    response_model=TaskOut,
    summary="Mark task as incomplete",
    description="Mark a task as incomplete for the authenticated user."
)
def mark_task_incomplete(
    task_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> TaskOut:
    """Mark a task as incomplete."""
    task_service = TaskService(db)
    task = task_service.mark_as_incomplete(task_id, user_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return task

