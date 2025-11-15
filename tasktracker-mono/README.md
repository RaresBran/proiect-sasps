# TaskTracker Monolithic API

A monolithic FastAPI application for task management with authentication, built using layered architecture.

## 🏗️ Architecture

This project follows a **layered architecture** pattern:

```
Presentation Layer (Routers) 
    ↓
Business Logic Layer (Services)
    ↓
Data Access Layer (Repositories)
    ↓
Database (PostgreSQL)
```

## 📁 Project Structure

```
tasktracker-mono/
├── app/
│   ├── routers/         # API endpoints (Presentation layer)
│   ├── services/        # Business logic
│   ├── repositories/    # Data access layer
│   ├── models/          # SQLAlchemy ORM models
│   ├── schemas/         # Pydantic schemas (DTOs)
│   ├── core/           # Configuration, security, database
│   └── utils/          # Utility functions
├── migrations/         # Alembic database migrations
├── tests/             # Test suite
├── .env.example       # Environment variables template
└── requirements.txt   # Python dependencies
```

## 🚀 Features

### ✅ Implemented

- **Authentication System**
  - User registration with email and username validation
  - Password hashing using bcrypt
  - JWT token-based authentication
  - Login and token generation
  - Get current user endpoint
  
- **Task Management System**
  - Full CRUD operations for tasks
  - User-scoped tasks (users only see their own tasks)
  - Task filtering by status and priority
  - Pagination support
  - Task statistics (counts by status/priority)
  - Mark tasks as completed/incomplete
  
- **Statistics Module**
  - User statistics (total tasks, completion percentage)
  - Reuses TaskRepository for efficient queries
  - Real-time calculation based on current data
  
- **Database**
  - PostgreSQL with SQLAlchemy ORM
  - Alembic migrations
  - User and Task models with relationships
  
- **Security**
  - Password hashing with Passlib
  - JWT tokens with configurable expiration
  - OAuth2 Bearer authentication
  - Protected endpoints with dependencies
  - User isolation (tasks scoped to owner)

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 14+
- pip or poetry for dependency management

## 🔧 Installation

1. **Clone the repository**
   ```bash
   cd tasktracker-mono
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up the database**
   ```bash
   # Create PostgreSQL database
   createdb tasktracker_db
   
   # Run migrations
   alembic upgrade head
   ```

## 🏃 Running the Application

### Option 1: Docker (Recommended) 🐳

**Prerequisites:** Docker Desktop 20.10+ and Docker Compose 2.0+

```bash
# Build and start all services (FastAPI + PostgreSQL)
docker compose up --build

# Or run in detached mode
docker compose up -d --build

# View logs
docker compose logs -f

# Stop services
docker compose down
```

**Access the application:**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

**Note:** Database migrations run automatically on container startup.

📖 **See [DOCKER.md](DOCKER.md) for detailed Docker documentation.**

### Option 2: Local Development

**Prerequisites:** Python 3.11+, PostgreSQL 14+

#### Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📝 API Documentation

Once the application is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔐 Authentication Endpoints

### 1. Register User

**POST** `/api/v1/auth/register`

```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-01-15T10:00:00",
  "updated_at": "2024-01-15T10:00:00"
}
```

### 2. Login

**POST** `/api/v1/auth/login`

```json
{
  "username": "johndoe",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Get Current User

**GET** `/api/v1/auth/me`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-01-15T10:00:00",
  "updated_at": "2024-01-15T10:00:00"
}
```

## 📋 Task Management Endpoints

### 1. Create Task

**POST** `/api/v1/tasks/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "title": "Complete project",
  "description": "Finish the FastAPI project",
  "status": "todo",
  "priority": "high",
  "due_date": "2024-12-31T23:59:59"
}
```

**Response:** (201 Created)
```json
{
  "id": 1,
  "title": "Complete project",
  "description": "Finish the FastAPI project",
  "status": "todo",
  "priority": "high",
  "is_completed": false,
  "due_date": "2024-12-31T23:59:59",
  "owner_id": 1,
  "created_at": "2024-01-15T10:00:00",
  "updated_at": "2024-01-15T10:00:00"
}
```

### 2. Get All Tasks

**GET** `/api/v1/tasks/?skip=0&limit=100&status=todo&priority=high`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 100, max: 1000)
- `status`: Filter by status (optional: todo, in_progress, done)
- `priority`: Filter by priority (optional: low, medium, high)

**Response:**
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Complete project",
      "status": "todo",
      "priority": "high",
      ...
    }
  ],
  "total": 10,
  "skip": 0,
  "limit": 100
}
```

### 3. Get Task by ID

**GET** `/api/v1/tasks/{task_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** Task object or 404 if not found

### 4. Update Task

**PUT** `/api/v1/tasks/{task_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "title": "Updated title",
  "status": "in_progress",
  "priority": "medium"
}
```

**Response:** Updated task object or 404 if not found

### 5. Delete Task

**DELETE** `/api/v1/tasks/{task_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** 204 No Content or 404 if not found

### 6. Mark Task as Completed

**PATCH** `/api/v1/tasks/{task_id}/complete`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** Updated task with `is_completed: true` and `status: done`

### 7. Get Task Statistics

**GET** `/api/v1/tasks/stats`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "total": 25,
  "todo": 10,
  "in_progress": 8,
  "done": 7,
  "completed": 7,
  "high_priority": 5,
  "medium_priority": 12,
  "low_priority": 8
}
```

## 📊 Statistics Endpoint

### Get User Statistics

**GET** `/api/v1/stats/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Description:**
Get aggregated statistics for the authenticated user including total tasks and completion percentage.

**Response:**
```json
{
  "total_tasks": 10,
  "completed_tasks": 3,
  "completed_percentage": 30.0
}
```

**Response Fields:**
- `total_tasks`: Total number of tasks for the user
- `completed_tasks`: Number of completed tasks (status = DONE or is_completed = true)
- `completed_percentage`: Percentage of completed tasks (0.0 to 100.0, rounded to 2 decimals)

**Examples:**

No tasks:
```json
{
  "total_tasks": 0,
  "completed_tasks": 0,
  "completed_percentage": 0.0
}
```

Partial completion:
```json
{
  "total_tasks": 3,
  "completed_tasks": 1,
  "completed_percentage": 33.33
}
```

All completed:
```json
{
  "total_tasks": 5,
  "completed_tasks": 5,
  "completed_percentage": 100.0
}
```

## 🗄️ Database Models

### User Model
- `id`: Primary key
- `email`: Unique email address
- `username`: Unique username
- `hashed_password`: Bcrypt hashed password
- `full_name`: Optional full name
- `is_active`: Account active status
- `is_superuser`: Admin privileges flag
- `created_at`: Timestamp
- `updated_at`: Timestamp

### Task Model
- `id`: Primary key
- `title`: Task title
- `description`: Task description
- `status`: Enum (TODO, IN_PROGRESS, DONE)
- `priority`: Enum (LOW, MEDIUM, HIGH)
- `is_completed`: Boolean flag
- `due_date`: Optional due date
- `owner_id`: Foreign key to User
- `created_at`: Timestamp
- `updated_at`: Timestamp

## 🧪 Testing

Run tests with pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/integration/test_auth.py
```

## 🔄 Database Migrations

### Create a new migration

```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations

```bash
alembic upgrade head
```

### Rollback migration

```bash
alembic downgrade -1
```

## 🐳 Docker Support

Complete Docker setup with PostgreSQL included!

```bash
# Quick start with Docker
docker compose up --build
```

See [DOCKER.md](DOCKER.md) for:
- Complete Docker configuration
- Production deployment guide
- Health checks and monitoring
- Database backup/restore
- Troubleshooting tips

## 📚 Technology Stack

- **Framework**: FastAPI 0.109.0
- **Database**: PostgreSQL with SQLAlchemy 2.0
- **Migrations**: Alembic
- **Authentication**: JWT with python-jose
- **Password Hashing**: Passlib with bcrypt
- **Validation**: Pydantic v2
- **Testing**: Pytest
- **ASGI Server**: Uvicorn

## 🏛️ Architecture Patterns

### Repository Pattern
Abstracts data access logic into repository classes, making the code more maintainable and testable.

```python
class UserRepository:
    def get_by_id(self, user_id: int) -> Optional[User]
    def create(self, user_create: UserCreate) -> Optional[User]
    def update(self, user_id: int, user_update: UserUpdate) -> Optional[User]
    def delete(self, user_id: int) -> bool
```

### Service Layer
Contains business logic and orchestrates operations between repositories.

```python
class AuthService:
    def register(self, user_create: UserCreate) -> Optional[UserResponse]
    def login(self, user_login: UserLogin) -> Optional[Token]
    def authenticate_user(self, username: str, password: str) -> Optional[User]
```

### Dependency Injection
Uses FastAPI's dependency injection system for database sessions and authentication.

```python
def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    ...
```

## 🔒 Security

- Passwords are hashed using bcrypt
- JWT tokens with configurable expiration
- OAuth2 Bearer token authentication
- Protected endpoints with role-based access control
- SQL injection prevention through SQLAlchemy ORM

## 📄 License

This project is for educational purposes.

## 👥 Contributing

This is a university project. Contributions are welcome for learning purposes!

