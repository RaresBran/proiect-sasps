import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db

# Test database URL (use SQLite for testing)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_stats.db"

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
            "email": "statsuser@example.com",
            "username": "statsuser",
            "password": "testpass123"
        }
    )
    
    # Login and get token
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "statsuser",
            "password": "testpass123"
        }
    )
    return response.json()["access_token"]


def test_get_stats_no_tasks(client, auth_token):
    """Test getting statistics when user has no tasks."""
    response = client.get(
        "/api/v1/stats/",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_tasks"] == 0
    assert data["completed_tasks"] == 0
    assert data["completed_percentage"] == 0.0


def test_get_stats_with_tasks_none_completed(client, auth_token):
    """Test getting statistics with tasks but none completed."""
    # Create 5 tasks, all incomplete
    for i in range(5):
        client.post(
            "/api/v1/tasks/",
            json={
                "title": f"Task {i+1}",
                "status": "todo"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    
    # Get stats
    response = client.get(
        "/api/v1/stats/",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_tasks"] == 5
    assert data["completed_tasks"] == 0
    assert data["completed_percentage"] == 0.0


def test_get_stats_with_some_completed(client, auth_token):
    """Test getting statistics with some tasks completed."""
    # Create 10 tasks
    for i in range(10):
        client.post(
            "/api/v1/tasks/",
            json={
                "title": f"Task {i+1}",
                "status": "todo"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    
    # Mark 3 tasks as completed (30%)
    for task_id in [1, 2, 3]:
        client.patch(
            f"/api/v1/tasks/{task_id}/complete",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    
    # Get stats
    response = client.get(
        "/api/v1/stats/",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_tasks"] == 10
    assert data["completed_tasks"] == 3
    assert data["completed_percentage"] == 30.0


def test_get_stats_all_completed(client, auth_token):
    """Test getting statistics when all tasks are completed."""
    # Create 5 tasks, all completed
    for i in range(5):
        response = client.post(
            "/api/v1/tasks/",
            json={
                "title": f"Task {i+1}",
                "status": "done"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    
    # Get stats
    response = client.get(
        "/api/v1/stats/",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_tasks"] == 5
    assert data["completed_tasks"] == 5
    assert data["completed_percentage"] == 100.0


def test_get_stats_fractional_percentage(client, auth_token):
    """Test that completion percentage is calculated correctly with fractions."""
    # Create 3 tasks
    for i in range(3):
        client.post(
            "/api/v1/tasks/",
            json={
                "title": f"Task {i+1}",
                "status": "todo"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    
    # Mark 1 task as completed (33.33%)
    client.patch(
        "/api/v1/tasks/1/complete",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # Get stats
    response = client.get(
        "/api/v1/stats/",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_tasks"] == 3
    assert data["completed_tasks"] == 1
    # Should be rounded to 2 decimal places
    assert data["completed_percentage"] == 33.33


def test_get_stats_unauthorized(client):
    """Test that statistics endpoint requires authentication."""
    response = client.get("/api/v1/stats/")
    assert response.status_code == 401


def test_get_stats_user_isolation(client):
    """Test that each user sees only their own statistics."""
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
    
    # Create 5 tasks for user 1
    for i in range(5):
        client.post(
            "/api/v1/tasks/",
            json={"title": f"User 1 Task {i+1}"},
            headers={"Authorization": f"Bearer {user1_token}"}
        )
    
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
    
    # Create 3 tasks for user 2
    for i in range(3):
        client.post(
            "/api/v1/tasks/",
            json={"title": f"User 2 Task {i+1}"},
            headers={"Authorization": f"Bearer {user2_token}"}
        )
    
    # Check user 1's stats
    user1_stats = client.get(
        "/api/v1/stats/",
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert user1_stats.json()["total_tasks"] == 5
    
    # Check user 2's stats
    user2_stats = client.get(
        "/api/v1/stats/",
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert user2_stats.json()["total_tasks"] == 3


def test_stats_response_schema(client, auth_token):
    """Test that the response matches the expected schema."""
    # Create one task
    client.post(
        "/api/v1/tasks/",
        json={"title": "Test Task", "status": "done"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    response = client.get(
        "/api/v1/stats/",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check all required fields are present
    assert "total_tasks" in data
    assert "completed_tasks" in data
    assert "completed_percentage" in data
    
    # Check types
    assert isinstance(data["total_tasks"], int)
    assert isinstance(data["completed_tasks"], int)
    assert isinstance(data["completed_percentage"], (int, float))
    
    # Check values are valid
    assert data["total_tasks"] >= 0
    assert data["completed_tasks"] >= 0
    assert 0.0 <= data["completed_percentage"] <= 100.0
    assert data["completed_tasks"] <= data["total_tasks"]

