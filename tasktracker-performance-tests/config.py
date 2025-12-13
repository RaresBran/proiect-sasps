"""
Configuration for performance tests
"""
import os
from typing import Dict

# Architecture configurations
ARCHITECTURES: Dict[str, Dict[str, str]] = {
    "monolithic": {
        "name": "Monolithic Architecture",
        "base_url": os.getenv("MONO_BASE_URL", "http://localhost:9000"),
        "api_prefix": "/api/v1",
    },
    "microservices": {
        "name": "Microservices Architecture",
        "base_url": os.getenv("MICRO_BASE_URL", "http://localhost:8000"),
        "api_prefix": "/api/v1",
    }
}

# Test configuration
TEST_CONFIG = {
    "users": int(os.getenv("LOCUST_USERS", "50")),
    "spawn_rate": int(os.getenv("LOCUST_SPAWN_RATE", "10")),
    "run_time": os.getenv("LOCUST_RUN_TIME", "3m"),  # Increased to 3 minutes
}

# User generation settings
USER_GENERATION = {
    "total_users": 20,  # Total users to pre-generate (reduced for faster setup)
    "tasks_per_user": 10,  # Tasks to create per user (reduced for faster setup)
}

# Weights for different operations (used in Locust tasks)
TASK_WEIGHTS = {
    "read": 70,      # 70% read operations
    "write": 20,     # 20% write operations  
    "update": 7,     # 7% update operations
    "delete": 3,     # 3% delete operations
}

# API Endpoints
ENDPOINTS = {
    "register": "/auth/register",
    "login": "/auth/login",
    "me": "/auth/me",
    "tasks": "/tasks/",
    "task_by_id": "/tasks/{id}",
    "task_complete": "/tasks/{id}/complete",
    "task_incomplete": "/tasks/{id}/incomplete",
    "stats": "/stats/",
}

