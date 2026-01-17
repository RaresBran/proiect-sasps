"""
Configuration for experiments.
"""
import os
from typing import Dict, List

# Default URLs
MONOLITH_BASE_URL = os.getenv("MONO_BASE_URL", "http://localhost:9000")
MICROSERVICES_BASE_URL = os.getenv("MICRO_BASE_URL", "http://localhost:8000")

# Container names for resource monitoring
MONOLITH_CONTAINERS = [
    "tasktracker_app",
    "tasktracker_db"
]

MICROSERVICES_CONTAINERS = [
    "tasktracker_api_gateway",
    "tasktracker_user_service",
    "tasktracker_task_service", 
    "tasktracker_stats_service",
    "tasktracker_user_db",
    "tasktracker_task_db"
]

# Docker compose paths (relative to project root)
MONOLITH_COMPOSE_PATH = "tasktracker-mono/docker-compose.yml"
MICROSERVICES_COMPOSE_PATH = "tasktracker-micro/docker-compose.yml"

# Locust file paths (relative to project root)
LOCUSTFILE_MONOLITH = "tasktracker-performance-tests/locustfile_monolithic.py"
LOCUSTFILE_MICROSERVICES = "tasktracker-performance-tests/locustfile_microservices.py"

# Default sweep configuration
DEFAULT_CONCURRENCY_LEVELS = [10, 25, 50, 100, 200]
DEFAULT_DURATION_SECONDS = 60
DEFAULT_WARMUP_SECONDS = 10
DEFAULT_SPAWN_RATE = 10

# Default failure injection configuration
DEFAULT_FAILURE_CONCURRENCY = 100
DEFAULT_FAILURE_DURATION = 90
DEFAULT_INJECT_AT_SECONDS = 30
DEFAULT_DOWNTIME_SECONDS = 10
DEFAULT_TARGET_SERVICE = "tasktracker_task_service"

# Resource monitoring
DEFAULT_SAMPLE_INTERVAL = 1.0  # seconds
