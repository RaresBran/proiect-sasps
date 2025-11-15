from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.services.task_service import TaskService
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut, TaskListResponse, TaskStats
from app.models.user import User
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
    current_user: User = Depends(get_current_active_user)
) -> TaskOut:
    """
    Create a new task.
    
    Args:
        task_create: Task creation data
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Created task
    """
    task_service = TaskService(db)
    return task_service.create_task(task_create, current_user.id)


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
    current_user: User = Depends(get_current_active_user)
) -> TaskListResponse:
    """
    Get all tasks for the authenticated user.
    
    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return (pagination)
        status: Optional status filter
        priority: Optional priority filter
        db: Database session
        current_user: Authenticated user
        
    Returns:
        TaskListResponse with tasks and pagination info
    """
    task_service = TaskService(db)
    return task_service.get_tasks(
        owner_id=current_user.id,
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
    current_user: User = Depends(get_current_active_user)
) -> TaskStats:
    """
    Get task statistics for the authenticated user.
    
    Args:
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Task statistics
    """
    task_service = TaskService(db)
    return task_service.get_task_stats(current_user.id)


@router.get(
    "/{task_id}",
    response_model=TaskOut,
    summary="Get task by ID",
    description="Get a specific task by ID for the authenticated user."
)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> TaskOut:
    """
    Get a task by ID.
    
    Args:
        task_id: Task ID
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Task data
        
    Raises:
        HTTPException: If task not found or not owned by user
    """
    task_service = TaskService(db)
    task = task_service.get_task(task_id, current_user.id)
    
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
    current_user: User = Depends(get_current_active_user)
) -> TaskOut:
    """
    Update a task.
    
    Args:
        task_id: Task ID
        task_update: Task update data
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Updated task
        
    Raises:
        HTTPException: If task not found or not owned by user
    """
    task_service = TaskService(db)
    task = task_service.update_task(task_id, task_update, current_user.id)
    
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
    current_user: User = Depends(get_current_active_user)
) -> None:
    """
    Delete a task.
    
    Args:
        task_id: Task ID
        db: Database session
        current_user: Authenticated user
        
    Raises:
        HTTPException: If task not found or not owned by user
    """
    task_service = TaskService(db)
    success = task_service.delete_task(task_id, current_user.id)
    
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
    current_user: User = Depends(get_current_active_user)
) -> TaskOut:
    """
    Mark a task as completed.
    
    Args:
        task_id: Task ID
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Updated task
        
    Raises:
        HTTPException: If task not found or not owned by user
    """
    task_service = TaskService(db)
    task = task_service.mark_as_completed(task_id, current_user.id)
    
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
    current_user: User = Depends(get_current_active_user)
) -> TaskOut:
    """
    Mark a task as incomplete.
    
    Args:
        task_id: Task ID
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Updated task
        
    Raises:
        HTTPException: If task not found or not owned by user
    """
    task_service = TaskService(db)
    task = task_service.mark_as_incomplete(task_id, current_user.id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return task

