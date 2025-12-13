from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
from app.core.config import settings

# Create FastAPI application
app = FastAPI(
    title="TaskTracker API Gateway",
    version="1.0.0",
    debug=settings.DEBUG,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def proxy_request(
    request: Request,
    service_url: str,
    path: str
):
    """
    Proxy a request to a microservice.
    
    Args:
        request: FastAPI request object
        service_url: Base URL of the target service
        path: Path to append to service URL
        
    Returns:
        Response from the target service
    """
    # Get headers and exclude host
    headers = dict(request.headers)
    headers.pop("host", None)
    
    # Get query parameters
    query_params = dict(request.query_params)
    
    # Build target URL
    target_url = f"{service_url}{path}"
    
    # Get request body if present
    try:
        body = await request.body()
    except:
        body = None
    
    # Make request to microservice
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                params=query_params,
                content=body
            )
            
            # Return response
            try:
                content = response.json() if response.text else None
            except:
                content = {"detail": response.text} if response.text else None
            
            return JSONResponse(
                status_code=response.status_code,
                content=content,
                headers=dict(response.headers)
            )
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=str(e)
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Service unavailable: {str(e)}"
            )


# Root endpoint
@app.get("/", tags=["Root"])
def root():
    """Root endpoint - API Gateway information."""
    return {
        "name": "TaskTracker API Gateway",
        "version": "1.0.0",
        "status": "running",
        "services": {
            "user-service": settings.USER_SERVICE_URL,
            "task-service": settings.TASK_SERVICE_URL,
            "stats-service": settings.STATS_SERVICE_URL
        }
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "api-gateway"}


# Route to user-service (authentication endpoints)
@app.api_route(
    "/api/v1/auth/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    tags=["Authentication"]
)
async def route_to_user_service(request: Request, path: str):
    """Route authentication requests to user-service."""
    return await proxy_request(
        request,
        settings.USER_SERVICE_URL,
        f"/api/v1/auth/{path}"
    )


# Route to task-service
@app.api_route(
    "/api/v1/tasks/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    tags=["Tasks"]
)
async def route_to_task_service(request: Request, path: str):
    """Route task requests to task-service."""
    return await proxy_request(
        request,
        settings.TASK_SERVICE_URL,
        f"/api/v1/tasks/{path}"
    )


# Route to task-service (root tasks endpoint)
@app.api_route(
    "/api/v1/tasks",
    methods=["GET", "POST"],
    tags=["Tasks"]
)
async def route_to_task_service_root(request: Request):
    """Route task requests to task-service (root endpoint)."""
    return await proxy_request(
        request,
        settings.TASK_SERVICE_URL,
        "/api/v1/tasks"
    )


# Route to stats-service
@app.api_route(
    "/api/v1/stats/{path:path}",
    methods=["GET"],
    tags=["Statistics"]
)
async def route_to_stats_service(request: Request, path: str):
    """Route statistics requests to stats-service."""
    return await proxy_request(
        request,
        settings.STATS_SERVICE_URL,
        f"/api/v1/stats/{path}"
    )


# Route to stats-service (root stats endpoint)
@app.api_route(
    "/api/v1/stats",
    methods=["GET"],
    tags=["Statistics"]
)
async def route_to_stats_service_root(request: Request):
    """Route statistics requests to stats-service (root endpoint)."""
    return await proxy_request(
        request,
        settings.STATS_SERVICE_URL,
        "/api/v1/stats/"
    )

