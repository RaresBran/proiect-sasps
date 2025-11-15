from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/", summary="Health check")
def health_check():
    """
    Check if the API is running.
    
    Returns:
        Health status
    """
    return {"status": "healthy"}


@router.get("/ready", summary="Readiness check")
def readiness_check():
    """
    Check if the API is ready to accept requests.
    
    Returns:
        Readiness status
    """
    return {"status": "ready"}


@router.get("/live", summary="Liveness check")
def liveness_check():
    """
    Check if the API is alive.
    
    Returns:
        Liveness status
    """
    return {"status": "alive"}

