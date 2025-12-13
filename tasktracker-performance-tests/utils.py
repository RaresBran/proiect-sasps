"""
Utility functions for performance testing
"""
import random
import string
from typing import Dict, List
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()


def generate_random_string(length: int = 10) -> str:
    """Generate a random string of specified length."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


def generate_user_data() -> Dict[str, str]:
    """Generate realistic user data for registration."""
    username = fake.user_name() + generate_random_string(4)
    return {
        "email": fake.email(),
        "username": username,
        "password": "TestPass123!",
        "full_name": fake.name()
    }


def generate_task_data() -> Dict:
    """Generate realistic task data."""
    statuses = ["todo", "in_progress", "done"]
    priorities = ["low", "medium", "high"]
    
    # Some tasks have due dates, some don't
    due_date = None
    if random.random() > 0.3:  # 70% have due dates
        due_date = (datetime.now() + timedelta(days=random.randint(1, 30))).isoformat()
    
    task = {
        "title": fake.sentence(nb_words=6)[:-1],  # Remove trailing period
        "description": fake.paragraph(nb_sentences=3),
        "status": random.choice(statuses),
        "priority": random.choice(priorities),
    }
    
    if due_date:
        task["due_date"] = due_date
    
    return task


def generate_task_update() -> Dict:
    """Generate partial task update data."""
    statuses = ["todo", "in_progress", "done"]
    priorities = ["low", "medium", "high"]
    
    updates = {}
    
    # Randomly update some fields
    if random.random() > 0.5:
        updates["status"] = random.choice(statuses)
    
    if random.random() > 0.5:
        updates["priority"] = random.choice(priorities)
    
    if random.random() > 0.7:
        updates["title"] = fake.sentence(nb_words=6)[:-1]
    
    if random.random() > 0.7:
        updates["description"] = fake.paragraph(nb_sentences=3)
    
    return updates if updates else {"priority": random.choice(priorities)}


class TestDataStore:
    """Store for test data shared across Locust users."""
    
    def __init__(self):
        self.users: List[Dict[str, str]] = []
        self.tokens: Dict[str, str] = {}  # username -> token
        self.user_tasks: Dict[str, List[int]] = {}  # username -> [task_ids]
    
    def add_user(self, user_data: Dict[str, str]):
        """Add a user to the store."""
        self.users.append(user_data)
    
    def get_random_user(self) -> Dict[str, str]:
        """Get a random user from the store."""
        if not self.users:
            raise ValueError("No users in store")
        return random.choice(self.users)
    
    def set_token(self, username: str, token: str):
        """Store a user's authentication token."""
        self.tokens[username] = token
    
    def get_token(self, username: str) -> str:
        """Get a user's authentication token."""
        return self.tokens.get(username, "")
    
    def add_task_id(self, username: str, task_id: int):
        """Add a task ID for a user."""
        if username not in self.user_tasks:
            self.user_tasks[username] = []
        self.user_tasks[username].append(task_id)
    
    def get_task_ids(self, username: str) -> List[int]:
        """Get all task IDs for a user."""
        return self.user_tasks.get(username, [])
    
    def remove_task_id(self, username: str, task_id: int):
        """Remove a task ID from a user's list."""
        if username in self.user_tasks and task_id in self.user_tasks[username]:
            self.user_tasks[username].remove(task_id)


# Global data store instance
test_data_store = TestDataStore()

