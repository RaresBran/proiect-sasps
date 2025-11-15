from typing import Optional, List
from sqlalchemy.orm import Session
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut, TaskListResponse, TaskStats
from app.models.task import Task, TaskStatus, TaskPriority


class TaskService:
    """
    Service for task operations.
    Handles business logic for task management.
    All operations are scoped to the authenticated user.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the service with a database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.task_repository = TaskRepository(db)
    
    def create_task(self, task_create: TaskCreate, owner_id: int) -> TaskOut:
        """
        Create a new task for the authenticated user.
        
        Args:
            task_create: Task creation data
            owner_id: The authenticated user's ID
            
        Returns:
            Created task
        """
        db_task = self.task_repository.create(task_create, owner_id)
        return TaskOut.model_validate(db_task)
    
    def get_task(self, task_id: int, owner_id: int) -> Optional[TaskOut]:
        """
        Get a task by ID for the authenticated user.
        
        Args:
            task_id: The task's ID
            owner_id: The authenticated user's ID
            
        Returns:
            Task if found and owned by user, None otherwise
        """
        db_task = self.task_repository.get_by_id(task_id, owner_id)
        if not db_task:
            return None
        return TaskOut.model_validate(db_task)
    
    def get_tasks(
        self,
        owner_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None
    ) -> TaskListResponse:
        """
        Get all tasks for the authenticated user with optional filtering.
        
        Args:
            owner_id: The authenticated user's ID
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return (pagination)
            status: Optional status filter
            priority: Optional priority filter
            
        Returns:
            TaskListResponse with tasks and pagination info
        """
        if status:
            tasks = self.task_repository.get_by_status(owner_id, status, skip, limit)
        elif priority:
            tasks = self.task_repository.get_by_priority(owner_id, priority, skip, limit)
        else:
            tasks = self.task_repository.get_all(owner_id, skip, limit)
        
        total = self.task_repository.count(owner_id)
        
        return TaskListResponse(
            tasks=[TaskOut.model_validate(task) for task in tasks],
            total=total,
            skip=skip,
            limit=limit
        )
    
    def update_task(
        self,
        task_id: int,
        task_update: TaskUpdate,
        owner_id: int
    ) -> Optional[TaskOut]:
        """
        Update a task for the authenticated user.
        
        Args:
            task_id: The task's ID
            task_update: Task update data
            owner_id: The authenticated user's ID
            
        Returns:
            Updated task if successful, None if task not found or not owned by user
        """
        db_task = self.task_repository.update(task_id, task_update, owner_id)
        if not db_task:
            return None
        return TaskOut.model_validate(db_task)
    
    def delete_task(self, task_id: int, owner_id: int) -> bool:
        """
        Delete a task for the authenticated user.
        
        Args:
            task_id: The task's ID
            owner_id: The authenticated user's ID
            
        Returns:
            True if deleted successfully, False if task not found or not owned by user
        """
        return self.task_repository.delete(task_id, owner_id)
    
    def mark_as_completed(self, task_id: int, owner_id: int) -> Optional[TaskOut]:
        """
        Mark a task as completed for the authenticated user.
        
        Args:
            task_id: The task's ID
            owner_id: The authenticated user's ID
            
        Returns:
            Updated task if successful, None if task not found or not owned by user
        """
        db_task = self.task_repository.mark_as_completed(task_id, owner_id)
        if not db_task:
            return None
        return TaskOut.model_validate(db_task)
    
    def mark_as_incomplete(self, task_id: int, owner_id: int) -> Optional[TaskOut]:
        """
        Mark a task as incomplete for the authenticated user.
        
        Args:
            task_id: The task's ID
            owner_id: The authenticated user's ID
            
        Returns:
            Updated task if successful, None if task not found or not owned by user
        """
        db_task = self.task_repository.mark_as_incomplete(task_id, owner_id)
        if not db_task:
            return None
        return TaskOut.model_validate(db_task)
    
    def get_task_stats(self, owner_id: int) -> TaskStats:
        """
        Get task statistics for the authenticated user.
        
        Args:
            owner_id: The authenticated user's ID
            
        Returns:
            TaskStats with counts by status and priority
        """
        total = self.task_repository.count(owner_id)
        todo = self.task_repository.count_by_status(owner_id, TaskStatus.TODO)
        in_progress = self.task_repository.count_by_status(owner_id, TaskStatus.IN_PROGRESS)
        done = self.task_repository.count_by_status(owner_id, TaskStatus.DONE)
        completed = self.task_repository.count_completed(owner_id)
        
        # Count by priority
        all_tasks = self.task_repository.get_all(owner_id, skip=0, limit=1000)
        high_priority = sum(1 for task in all_tasks if task.priority == TaskPriority.HIGH)
        medium_priority = sum(1 for task in all_tasks if task.priority == TaskPriority.MEDIUM)
        low_priority = sum(1 for task in all_tasks if task.priority == TaskPriority.LOW)
        
        return TaskStats(
            total=total,
            todo=todo,
            in_progress=in_progress,
            done=done,
            completed=completed,
            high_priority=high_priority,
            medium_priority=medium_priority,
            low_priority=low_priority
        )

