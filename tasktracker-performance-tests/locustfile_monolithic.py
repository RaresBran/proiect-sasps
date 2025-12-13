"""
Locust performance test for Monolithic Architecture
Tests the monolithic TaskTracker application on port 9000
"""
from locust import HttpUser, task, between, events
from locust.runners import MasterRunner
import random
import logging
from utils import (
    generate_user_data, 
    generate_task_data, 
    generate_task_update,
    test_data_store
)
from config import ARCHITECTURES, TASK_WEIGHTS, USER_GENERATION

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Architecture configuration
ARCH_CONFIG = ARCHITECTURES["monolithic"]
BASE_URL = ARCH_CONFIG["base_url"]
API_PREFIX = ARCH_CONFIG["api_prefix"]


class TaskTrackerUser(HttpUser):
    """
    Simulates a user interacting with the TaskTracker monolithic application.
    
    This user performs realistic operations:
    - Logs in with existing credentials
    - Creates, reads, updates, and deletes tasks
    - Checks statistics
    - Performs operations with realistic frequency distribution
    """
    
    host = BASE_URL
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """
        Called when a user starts. 
        Logs in and stores the authentication token.
        """
        # Get a random pre-created user
        user_data = test_data_store.get_random_user()
        self.username = user_data["username"]
        self.password = user_data["password"]
        
        # Check if we already have a token for this user
        token = test_data_store.get_token(self.username)
        
        if not token:
            # Login to get token
            response = self.client.post(
                f"{API_PREFIX}/auth/login",
                json={"username": self.username, "password": self.password},
                name="[Auth] Login"
            )
            
            if response.status_code == 200:
                token = response.json()["access_token"]
                test_data_store.set_token(self.username, token)
                logger.info(f"User {self.username} logged in successfully")
            else:
                logger.error(f"Login failed for {self.username}: {response.status_code}")
                self.environment.runner.quit()
                return
        
        self.token = token
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(TASK_WEIGHTS["read"])
    def get_tasks(self):
        """Get all tasks for the current user (most frequent operation)."""
        self.client.get(
            f"{API_PREFIX}/tasks/",
            headers=self.headers,
            name="[Tasks] List All"
        )
    
    @task(int(TASK_WEIGHTS["read"] * 0.3))
    def get_tasks_with_filters(self):
        """Get tasks with various filters."""
        filters = random.choice([
            "?status=todo",
            "?status=in_progress", 
            "?status=done",
            "?priority=high",
            "?priority=medium",
            "?priority=low",
            "?skip=0&limit=5"
        ])
        
        self.client.get(
            f"{API_PREFIX}/tasks/{filters}",
            headers=self.headers,
            name="[Tasks] List Filtered"
        )
    
    @task(int(TASK_WEIGHTS["read"] * 0.2))
    def get_single_task(self):
        """Get a specific task by ID."""
        task_ids = test_data_store.get_task_ids(self.username)
        
        if task_ids:
            task_id = random.choice(task_ids)
            self.client.get(
                f"{API_PREFIX}/tasks/{task_id}",
                headers=self.headers,
                name="[Tasks] Get Single"
            )
    
    @task(TASK_WEIGHTS["write"])
    def create_task(self):
        """Create a new task."""
        task_data = generate_task_data()
        
        response = self.client.post(
            f"{API_PREFIX}/tasks/",
            json=task_data,
            headers=self.headers,
            name="[Tasks] Create"
        )
        
        if response.status_code == 201:
            task_id = response.json()["id"]
            test_data_store.add_task_id(self.username, task_id)
    
    @task(TASK_WEIGHTS["update"])
    def update_task(self):
        """Update an existing task."""
        task_ids = test_data_store.get_task_ids(self.username)
        
        if task_ids:
            task_id = random.choice(task_ids)
            update_data = generate_task_update()
            
            self.client.put(
                f"{API_PREFIX}/tasks/{task_id}",
                json=update_data,
                headers=self.headers,
                name="[Tasks] Update"
            )
    
    @task(int(TASK_WEIGHTS["update"] * 0.5))
    def complete_task(self):
        """Mark a task as complete."""
        task_ids = test_data_store.get_task_ids(self.username)
        
        if task_ids:
            task_id = random.choice(task_ids)
            
            self.client.patch(
                f"{API_PREFIX}/tasks/{task_id}/complete",
                headers=self.headers,
                name="[Tasks] Mark Complete"
            )
    
    @task(int(TASK_WEIGHTS["update"] * 0.3))
    def incomplete_task(self):
        """Mark a task as incomplete."""
        task_ids = test_data_store.get_task_ids(self.username)
        
        if task_ids:
            task_id = random.choice(task_ids)
            
            self.client.patch(
                f"{API_PREFIX}/tasks/{task_id}/incomplete",
                headers=self.headers,
                name="[Tasks] Mark Incomplete"
            )
    
    @task(TASK_WEIGHTS["delete"])
    def delete_task(self):
        """Delete a task."""
        task_ids = test_data_store.get_task_ids(self.username)
        
        if task_ids and len(task_ids) > 5:  # Keep at least 5 tasks
            task_id = random.choice(task_ids)
            
            response = self.client.delete(
                f"{API_PREFIX}/tasks/{task_id}",
                headers=self.headers,
                name="[Tasks] Delete"
            )
            
            if response.status_code == 204:
                test_data_store.remove_task_id(self.username, task_id)
    
    @task(int(TASK_WEIGHTS["read"] * 0.15))
    def get_stats(self):
        """Get user statistics."""
        self.client.get(
            f"{API_PREFIX}/stats/",
            headers=self.headers,
            name="[Stats] Get User Stats"
        )
    
    @task(int(TASK_WEIGHTS["read"] * 0.1))
    def get_user_info(self):
        """Get current user information."""
        self.client.get(
            f"{API_PREFIX}/auth/me",
            headers=self.headers,
            name="[Auth] Get User Info"
        )


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """
    Setup function that runs once before the test starts.
    Pre-creates users and tasks for testing.
    """
    if not isinstance(environment.runner, MasterRunner):
        logger.info("=" * 80)
        logger.info("SETUP: Pre-creating users and tasks for testing")
        logger.info(f"Architecture: {ARCH_CONFIG['name']}")
        logger.info(f"Base URL: {BASE_URL}")
        logger.info("=" * 80)
        
        import requests
        
        # Create users
        logger.info(f"Creating {USER_GENERATION['total_users']} users...")
        created_users = 0
        
        for i in range(USER_GENERATION['total_users']):
            user_data = generate_user_data()
            
            try:
                response = requests.post(
                    f"{BASE_URL}{API_PREFIX}/auth/register",
                    json=user_data,
                    timeout=10
                )
                
                if response.status_code == 201:
                    test_data_store.add_user(user_data)
                    created_users += 1
                    
                    # Login to get token
                    login_response = requests.post(
                        f"{BASE_URL}{API_PREFIX}/auth/login",
                        json={"username": user_data["username"], "password": user_data["password"]},
                        timeout=10
                    )
                    
                    if login_response.status_code == 200:
                        token = login_response.json()["access_token"]
                        test_data_store.set_token(user_data["username"], token)
                        
                        # Create initial tasks for this user
                        headers = {"Authorization": f"Bearer {token}"}
                        for j in range(USER_GENERATION['tasks_per_user']):
                            task_data = generate_task_data()
                            task_response = requests.post(
                                f"{BASE_URL}{API_PREFIX}/tasks/",
                                json=task_data,
                                headers=headers,
                                timeout=10
                            )
                            
                            if task_response.status_code == 201:
                                task_id = task_response.json()["id"]
                                test_data_store.add_task_id(user_data["username"], task_id)
                    
                    if (i + 1) % 10 == 0:
                        logger.info(f"Created {i + 1}/{USER_GENERATION['total_users']} users...")
                        
            except Exception as e:
                logger.error(f"Error creating user {i}: {e}")
        
        logger.info("=" * 80)
        logger.info(f"SETUP COMPLETE: Created {created_users} users with tasks")
        logger.info(f"Total tasks created: {sum(len(tasks) for tasks in test_data_store.user_tasks.values())}")
        logger.info("=" * 80)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Cleanup function that runs after the test completes."""
    logger.info("=" * 80)
    logger.info("TEST COMPLETED")
    logger.info(f"Architecture: {ARCH_CONFIG['name']}")
    logger.info("=" * 80)

