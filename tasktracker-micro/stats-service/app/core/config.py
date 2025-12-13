from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    
    # Application
    APP_NAME: str = Field(default="Stats Service", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    DEBUG: bool = Field(default=False, description="Debug mode")
    
    # Security (for JWT validation - should match user-service)
    SECRET_KEY: str = Field(
        default="your-secret-key-change-this-in-production",
        description="Secret key for JWT validation"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    
    # Service URLs
    TASK_SERVICE_URL: str = Field(
        default="http://task-service:8002",
        description="Task service URL"
    )
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000", "http://localhost:8080"],
        description="Allowed CORS origins"
    )
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    This function is cached to avoid reading .env file multiple times.
    """
    return Settings()


# Export settings instance
settings = get_settings()

