from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from app.core.dependencies import get_current_user_id
from app.services.stats_service import StatsService
from app.schemas.stats import StatsResponse

router = APIRouter(prefix="/stats", tags=["Statistics"])

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.get(
    "/",
    response_model=StatsResponse,
    summary="Get user statistics",
    description="Get statistics for the authenticated user including total tasks and completion percentage."
)
def get_stats(
    user_id: int = Depends(get_current_user_id),
    token: str = Depends(oauth2_scheme)
) -> StatsResponse:
    """
    Get statistics for the authenticated user.
    
    This endpoint communicates with the task-service to retrieve task data
    and calculate:
    - Total number of tasks
    - Number of completed tasks
    - Completion percentage
    
    Args:
        user_id: Authenticated user ID (from JWT)
        token: JWT authentication token
        
    Returns:
        StatsResponse with aggregated statistics
    """
    stats_service = StatsService(token)
    stats = stats_service.get_user_stats(user_id)
    
    return StatsResponse(**stats)

