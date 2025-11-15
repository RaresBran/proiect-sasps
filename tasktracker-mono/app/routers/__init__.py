from app.routers.users import router as auth_router
from app.routers.tasks import router as task_router
from app.routers.stats import router as stats_router

__all__ = ["auth_router", "task_router", "stats_router"]
