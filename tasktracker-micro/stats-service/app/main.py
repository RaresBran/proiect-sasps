from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import stats_router

# Create FastAPI application
app = FastAPI(
    title="Stats Service",
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

# Include routers
app.include_router(stats_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
def root():
    """Root endpoint - Service information."""
    return {
        "service": "Stats Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "stats-service"}

