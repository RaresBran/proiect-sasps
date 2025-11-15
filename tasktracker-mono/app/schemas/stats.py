from pydantic import BaseModel, Field


class StatsResponse(BaseModel):
    """
    Schema for statistics response.
    """
    total_tasks: int = Field(..., ge=0, description="Total number of tasks")
    completed_tasks: int = Field(..., ge=0, description="Number of completed tasks")
    completed_percentage: float = Field(..., ge=0.0, le=100.0, description="Percentage of completed tasks")

