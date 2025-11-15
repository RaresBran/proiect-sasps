from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.services.stats_service import StatsService
from app.schemas.stats import StatsResponse
from app.models.user import User

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get(
    "/",
    response_model=StatsResponse,
    summary="Get user statistics",
    description="Get statistics for the authenticated user including total tasks and completion percentage."
)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> StatsResponse:
    """
    Get statistics for the authenticated user.
    
    This endpoint queries the TaskRepository to calculate:
    - Total number of tasks
    - Number of completed tasks
    - Completion percentage
    
    Args:
        db: Database session
        current_user: Authenticated user
        
    Returns:
        StatsResponse with aggregated statistics
    """
    stats_service = StatsService(db)
    stats = stats_service.get_user_stats(current_user.id)
    
    return StatsResponse(**stats)

