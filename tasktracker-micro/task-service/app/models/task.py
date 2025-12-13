from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(TaskStatus, values_callable=lambda obj: [e.value for e in obj]), default=TaskStatus.TODO, nullable=False)
    priority = Column(SQLEnum(TaskPriority, values_callable=lambda obj: [e.value for e in obj]), default=TaskPriority.MEDIUM, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign Key (owner_id) - references user-service user ID
    owner_id = Column(Integer, nullable=False, index=True)

    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, status={self.status})>"

