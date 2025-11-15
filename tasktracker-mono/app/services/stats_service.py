from sqlalchemy.orm import Session
from app.repositories.task_repository import TaskRepository


class StatsService:
    """
    Service for statistics operations.
    Provides aggregated statistics by querying the TaskRepository.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the service with a database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.task_repository = TaskRepository(db)
    
    def get_user_stats(self, owner_id: int) -> dict:
        """
        Get statistics for a specific user.
        
        Args:
            owner_id: The authenticated user's ID
            
        Returns:
            Dictionary with total_tasks and completed_percentage
        """
        # Get total tasks count
        total_tasks = self.task_repository.count(owner_id)
        
        # Get completed tasks count
        completed_tasks = self.task_repository.count_completed(owner_id)
        
        # Calculate completion percentage
        if total_tasks > 0:
            completed_percentage = round((completed_tasks / total_tasks) * 100, 2)
        else:
            completed_percentage = 0.0
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completed_percentage": completed_percentage
        }

