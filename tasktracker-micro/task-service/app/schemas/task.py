from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
from typing import Optional
from app.models.task import TaskStatus, TaskPriority


# Base Task schema with common attributes
class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    status: TaskStatus = Field(default=TaskStatus.TODO, description="Task status")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority")
    due_date: Optional[datetime] = Field(None, description="Task due date")
    
    @field_validator('status', mode='before')
    @classmethod
    def validate_status(cls, v):
        """Convert status to lowercase and validate."""
        if isinstance(v, str):
            v = v.lower()
        return v
    
    @field_validator('priority', mode='before')
    @classmethod
    def validate_priority(cls, v):
        """Convert priority to lowercase and validate."""
        if isinstance(v, str):
            v = v.lower()
        return v


# Schema for task creation
class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    pass


# Schema for task update (all fields optional)
class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    status: Optional[TaskStatus] = Field(None, description="Task status")
    priority: Optional[TaskPriority] = Field(None, description="Task priority")
    is_completed: Optional[bool] = Field(None, description="Task completion status")
    due_date: Optional[datetime] = Field(None, description="Task due date")
    
    @field_validator('status', mode='before')
    @classmethod
    def validate_status(cls, v):
        """Convert status to lowercase and validate."""
        if isinstance(v, str):
            v = v.lower()
        return v
    
    @field_validator('priority', mode='before')
    @classmethod
    def validate_priority(cls, v):
        """Convert priority to lowercase and validate."""
        if isinstance(v, str):
            v = v.lower()
        return v


# Schema for task response (output)
class TaskOut(TaskBase):
    """Schema for task output with all fields."""
    id: int
    is_completed: bool
    owner_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Schema for task list response with pagination info
class TaskListResponse(BaseModel):
    """Schema for paginated task list response."""
    tasks: list[TaskOut]
    total: int
    skip: int
    limit: int


# Schema for task statistics
class TaskStats(BaseModel):
    """Schema for task statistics."""
    total: int
    todo: int
    in_progress: int
    done: int
    completed: int
    high_priority: int
    medium_priority: int
    low_priority: int

