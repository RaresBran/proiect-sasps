import requests
from typing import Dict, Any
from app.core.config import settings


class StatsService:
    """
    Service for statistics operations.
    Communicates with task-service to get task data and calculate statistics.
    """
    
    def __init__(self, token: str):
        """
        Initialize the service with an authentication token.
        
        Args:
            token: JWT authentication token
        """
        self.token = token
        self.task_service_url = settings.TASK_SERVICE_URL
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Get statistics for a specific user.
        
        Args:
            user_id: The authenticated user's ID
            
        Returns:
            Dictionary with total_tasks, completed_tasks, and completed_percentage
        """
        # Make request to task-service to get all tasks
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            # Get all tasks (use max allowed limit of 1000)
            response = requests.get(
                f"{self.task_service_url}/api/v1/tasks/?limit=1000",
                headers=headers,
                timeout=5
            )
            
            if response.status_code != 200:
                return {
                    "total_tasks": 0,
                    "completed_tasks": 0,
                    "completed_percentage": 0.0
                }
            
            data = response.json()
            tasks = data.get("tasks", [])
            total_tasks = data.get("total", len(tasks))  # Use total count from response
            
            completed_tasks = sum(1 for task in tasks if task.get("is_completed", False))
            
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
            
        except requests.RequestException as e:
            # Log error and return default values
            print(f"Error communicating with task-service: {e}")
            return {
                "total_tasks": 0,
                "completed_tasks": 0,
                "completed_percentage": 0.0
            }

