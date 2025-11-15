from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from app.models.task import Task, TaskStatus, TaskPriority
from app.schemas.task import TaskCreate, TaskUpdate


class TaskRepository:
    """
    Repository for Task database operations.
    Implements the Repository Pattern for data access abstraction.
    All operations are scoped to a specific user.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the repository with a database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def get_by_id(self, task_id: int, owner_id: int) -> Optional[Task]:
        """
        Get a task by ID for a specific user.
        
        Args:
            task_id: The task's ID
            owner_id: The owner's user ID
            
        Returns:
            Task object if found and owned by user, None otherwise
        """
        return self.db.query(Task).filter(
            Task.id == task_id,
            Task.owner_id == owner_id
        ).first()
    
    def get_all(self, owner_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
        """
        Get all tasks for a specific user with pagination.
        
        Args:
            owner_id: The owner's user ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of Task objects
        """
        return self.db.query(Task).filter(
            Task.owner_id == owner_id
        ).order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_status(
        self,
        owner_id: int,
        status: TaskStatus,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """
        Get tasks by status for a specific user.
        
        Args:
            owner_id: The owner's user ID
            status: Task status to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of Task objects with the specified status
        """
        return self.db.query(Task).filter(
            Task.owner_id == owner_id,
            Task.status == status
        ).order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_priority(
        self,
        owner_id: int,
        priority: TaskPriority,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """
        Get tasks by priority for a specific user.
        
        Args:
            owner_id: The owner's user ID
            priority: Task priority to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of Task objects with the specified priority
        """
        return self.db.query(Task).filter(
            Task.owner_id == owner_id,
            Task.priority == priority
        ).order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
    
    def count(self, owner_id: int) -> int:
        """
        Count total tasks for a specific user.
        
        Args:
            owner_id: The owner's user ID
            
        Returns:
            Total number of tasks
        """
        return self.db.query(func.count(Task.id)).filter(
            Task.owner_id == owner_id
        ).scalar()
    
    def count_by_status(self, owner_id: int, status: TaskStatus) -> int:
        """
        Count tasks by status for a specific user.
        
        Args:
            owner_id: The owner's user ID
            status: Task status to count
            
        Returns:
            Number of tasks with the specified status
        """
        return self.db.query(func.count(Task.id)).filter(
            Task.owner_id == owner_id,
            Task.status == status
        ).scalar()
    
    def count_completed(self, owner_id: int) -> int:
        """
        Count completed tasks for a specific user.
        
        Args:
            owner_id: The owner's user ID
            
        Returns:
            Number of completed tasks
        """
        return self.db.query(func.count(Task.id)).filter(
            Task.owner_id == owner_id,
            Task.is_completed == True
        ).scalar()
    
    def create(self, task_create: TaskCreate, owner_id: int) -> Task:
        """
        Create a new task for a specific user.
        
        Args:
            task_create: Task creation schema with task data
            owner_id: The owner's user ID
            
        Returns:
            Created Task object
        """
        db_task = Task(
            title=task_create.title,
            description=task_create.description,
            status=task_create.status,
            priority=task_create.priority,
            due_date=task_create.due_date,
            owner_id=owner_id,
            is_completed=(task_create.status == TaskStatus.DONE)
        )
        
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        
        return db_task
    
    def update(self, task_id: int, task_update: TaskUpdate, owner_id: int) -> Optional[Task]:
        """
        Update a task for a specific user.
        
        Args:
            task_id: The task's ID
            task_update: Task update schema with fields to update
            owner_id: The owner's user ID
            
        Returns:
            Updated Task object if successful, None if task not found or not owned by user
        """
        db_task = self.get_by_id(task_id, owner_id)
        if not db_task:
            return None
        
        # Update only provided fields
        update_data = task_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_task, field, value)
        
        # Auto-update is_completed based on status
        if "status" in update_data:
            db_task.is_completed = (update_data["status"] == TaskStatus.DONE)
        
        self.db.commit()
        self.db.refresh(db_task)
        return db_task
    
    def delete(self, task_id: int, owner_id: int) -> bool:
        """
        Delete a task for a specific user.
        
        Args:
            task_id: The task's ID
            owner_id: The owner's user ID
            
        Returns:
            True if deleted successfully, False if task not found or not owned by user
        """
        db_task = self.get_by_id(task_id, owner_id)
        if not db_task:
            return False
        
        self.db.delete(db_task)
        self.db.commit()
        return True
    
    def mark_as_completed(self, task_id: int, owner_id: int) -> Optional[Task]:
        """
        Mark a task as completed for a specific user.
        
        Args:
            task_id: The task's ID
            owner_id: The owner's user ID
            
        Returns:
            Updated Task object if successful, None if task not found or not owned by user
        """
        db_task = self.get_by_id(task_id, owner_id)
        if not db_task:
            return None
        
        db_task.is_completed = True
        db_task.status = TaskStatus.DONE
        self.db.commit()
        self.db.refresh(db_task)
        return db_task
    
    def mark_as_incomplete(self, task_id: int, owner_id: int) -> Optional[Task]:
        """
        Mark a task as incomplete for a specific user.
        
        Args:
            task_id: The task's ID
            owner_id: The owner's user ID
            
        Returns:
            Updated Task object if successful, None if task not found or not owned by user
        """
        db_task = self.get_by_id(task_id, owner_id)
        if not db_task:
            return None
        
        db_task.is_completed = False
        if db_task.status == TaskStatus.DONE:
            db_task.status = TaskStatus.TODO
        self.db.commit()
        self.db.refresh(db_task)
        return db_task

