import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.models.task import TaskStatus, TaskPriority

# Test database URL (use SQLite for testing)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_tasks.db"

# Create test engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def auth_token(client):
    """Register a user and return authentication token."""
    # Register user
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "taskuser@example.com",
            "username": "taskuser",
            "password": "testpass123"
        }
    )
    
    # Login and get token
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "taskuser",
            "password": "testpass123"
        }
    )
    return response.json()["access_token"]


def test_create_task(client, auth_token):
    """Test creating a task."""
    response = client.post(
        "/api/v1/tasks/",
        json={
            "title": "Test Task",
            "description": "This is a test task",
            "status": "todo",
            "priority": "high"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "This is a test task"
    assert data["status"] == "todo"
    assert data["priority"] == "high"
    assert "id" in data
    assert "owner_id" in data


def test_create_task_unauthorized(client):
    """Test creating a task without authentication."""
    response = client.post(
        "/api/v1/tasks/",
        json={
            "title": "Test Task",
            "description": "This is a test task"
        }
    )
    assert response.status_code == 401


def test_get_all_tasks(client, auth_token):
    """Test getting all tasks."""
    # Create multiple tasks
    for i in range(3):
        client.post(
            "/api/v1/tasks/",
            json={
                "title": f"Task {i+1}",
                "description": f"Description {i+1}",
                "priority": "medium"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    
    # Get all tasks
    response = client.get(
        "/api/v1/tasks/",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["tasks"]) == 3


def test_get_tasks_with_pagination(client, auth_token):
    """Test getting tasks with pagination."""
    # Create 5 tasks
    for i in range(5):
        client.post(
            "/api/v1/tasks/",
            json={
                "title": f"Task {i+1}",
                "priority": "low"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    
    # Get first 2 tasks
    response = client.get(
        "/api/v1/tasks/?skip=0&limit=2",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["tasks"]) == 2
    assert data["total"] == 5
    assert data["skip"] == 0
    assert data["limit"] == 2


def test_get_tasks_by_status(client, auth_token):
    """Test filtering tasks by status."""
    # Create tasks with different statuses
    client.post(
        "/api/v1/tasks/",
        json={"title": "Todo Task", "status": "todo"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    client.post(
        "/api/v1/tasks/",
        json={"title": "In Progress Task", "status": "in_progress"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    client.post(
        "/api/v1/tasks/",
        json={"title": "Done Task", "status": "done"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # Filter by status
    response = client.get(
        "/api/v1/tasks/?status=todo",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["tasks"]) == 1
    assert data["tasks"][0]["status"] == "todo"


def test_get_task_by_id(client, auth_token):
    """Test getting a specific task by ID."""
    # Create a task
    create_response = client.post(
        "/api/v1/tasks/",
        json={
            "title": "Specific Task",
            "description": "Get this task by ID"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    task_id = create_response.json()["id"]
    
    # Get the task
    response = client.get(
        f"/api/v1/tasks/{task_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Specific Task"


def test_get_nonexistent_task(client, auth_token):
    """Test getting a task that doesn't exist."""
    response = client.get(
        "/api/v1/tasks/99999",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 404


def test_update_task(client, auth_token):
    """Test updating a task."""
    # Create a task
    create_response = client.post(
        "/api/v1/tasks/",
        json={
            "title": "Original Title",
            "description": "Original Description",
            "priority": "low"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    task_id = create_response.json()["id"]
    
    # Update the task
    response = client.put(
        f"/api/v1/tasks/{task_id}",
        json={
            "title": "Updated Title",
            "priority": "high"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["priority"] == "high"


def test_update_nonexistent_task(client, auth_token):
    """Test updating a task that doesn't exist."""
    response = client.put(
        "/api/v1/tasks/99999",
        json={"title": "Updated Title"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 404


def test_delete_task(client, auth_token):
    """Test deleting a task."""
    # Create a task
    create_response = client.post(
        "/api/v1/tasks/",
        json={"title": "Task to Delete"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    task_id = create_response.json()["id"]
    
    # Delete the task
    response = client.delete(
        f"/api/v1/tasks/{task_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 204
    
    # Verify task is deleted
    get_response = client.get(
        f"/api/v1/tasks/{task_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert get_response.status_code == 404


def test_delete_nonexistent_task(client, auth_token):
    """Test deleting a task that doesn't exist."""
    response = client.delete(
        "/api/v1/tasks/99999",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 404


def test_mark_task_completed(client, auth_token):
    """Test marking a task as completed."""
    # Create a task
    create_response = client.post(
        "/api/v1/tasks/",
        json={"title": "Task to Complete", "status": "todo"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    task_id = create_response.json()["id"]
    
    # Mark as completed
    response = client.patch(
        f"/api/v1/tasks/{task_id}/complete",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_completed"] == True
    assert data["status"] == "done"


def test_mark_task_incomplete(client, auth_token):
    """Test marking a task as incomplete."""
    # Create a completed task
    create_response = client.post(
        "/api/v1/tasks/",
        json={"title": "Completed Task", "status": "done"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    task_id = create_response.json()["id"]
    
    # Mark as incomplete
    response = client.patch(
        f"/api/v1/tasks/{task_id}/incomplete",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_completed"] == False
    assert data["status"] == "todo"


def test_get_task_stats(client, auth_token):
    """Test getting task statistics."""
    # Create tasks with different statuses and priorities
    client.post(
        "/api/v1/tasks/",
        json={"title": "Todo Task 1", "status": "todo", "priority": "high"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    client.post(
        "/api/v1/tasks/",
        json={"title": "Todo Task 2", "status": "todo", "priority": "medium"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    client.post(
        "/api/v1/tasks/",
        json={"title": "In Progress Task", "status": "in_progress", "priority": "low"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    client.post(
        "/api/v1/tasks/",
        json={"title": "Done Task", "status": "done", "priority": "high"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # Get stats
    response = client.get(
        "/api/v1/tasks/stats",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 4
    assert data["todo"] == 2
    assert data["in_progress"] == 1
    assert data["done"] == 1
    assert data["high_priority"] == 2
    assert data["medium_priority"] == 1
    assert data["low_priority"] == 1


def test_user_can_only_access_own_tasks(client):
    """Test that users can only access their own tasks."""
    # Register and login user 1
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "user1@example.com",
            "username": "user1",
            "password": "pass123"
        }
    )
    user1_response = client.post(
        "/api/v1/auth/login",
        json={"username": "user1", "password": "pass123"}
    )
    user1_token = user1_response.json()["access_token"]
    
    # Create task for user 1
    task_response = client.post(
        "/api/v1/tasks/",
        json={"title": "User 1 Task"},
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    task_id = task_response.json()["id"]
    
    # Register and login user 2
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "user2@example.com",
            "username": "user2",
            "password": "pass123"
        }
    )
    user2_response = client.post(
        "/api/v1/auth/login",
        json={"username": "user2", "password": "pass123"}
    )
    user2_token = user2_response.json()["access_token"]
    
    # Try to access user 1's task with user 2's token
    response = client.get(
        f"/api/v1/tasks/{task_id}",
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert response.status_code == 404  # Should not find the task

