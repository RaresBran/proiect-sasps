# TaskTracker - Monolithic FastAPI Application

A production-ready task management API built with FastAPI, PostgreSQL, and layered architecture. This project demonstrates modern Python web development practices including authentication, CRUD operations, and comprehensive testing.

---

## 📋 Table of Contents

- [Project Purpose](#-project-purpose)
- [Architecture](#-architecture)
- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Quick Start with Docker](#-quick-start-with-docker)
- [Running Migrations](#-running-migrations)
- [API Examples](#-api-examples)
- [Development](#-development)
- [Testing](#-testing)
- [Project Structure](#-project-structure)

---

## 🎯 Project Purpose

TaskTracker is a monolithic REST API application designed for task management with user authentication. The project serves as a comprehensive example of:

- **Clean Architecture**: Layered design with clear separation of concerns
- **Repository Pattern**: Abstracted data access layer
- **Service Layer**: Business logic separated from controllers
- **Secure Authentication**: JWT-based authentication with bcrypt password hashing
- **Database Migrations**: Version-controlled schema changes with Alembic
- **Containerization**: Production-ready Docker setup
- **Test Coverage**: Comprehensive integration tests

**Use Cases:**
- Personal task management
- Team productivity tracking
- Learning FastAPI and modern Python patterns
- Building RESTful APIs with authentication

---

## 🏗️ Architecture

### Layered Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Client Layer                          │
│              (Web, Mobile, API Clients)                  │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP/JSON
                         ▼
┌─────────────────────────────────────────────────────────┐
│               Presentation Layer (Routers)               │
│  • AuthRouter    • TaskRouter    • StatsRouter          │
│  • Request validation                                    │
│  • Response serialization                                │
│  • Authentication middleware                             │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Business Logic Layer (Services)             │
│  • AuthService   • TaskService   • StatsService          │
│  • Business rules                                        │
│  • Data transformation                                   │
│  • Service orchestration                                 │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│            Data Access Layer (Repositories)              │
│  • UserRepository   • TaskRepository                     │
│  • Database queries                                      │
│  • Transaction management                                │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  Database Layer (PostgreSQL)             │
│  • Users table    • Tasks table                          │
│  • Relationships  • Constraints                          │
└─────────────────────────────────────────────────────────┘
```

### Design Patterns

- **Repository Pattern**: Abstracts database operations
- **Service Layer Pattern**: Encapsulates business logic
- **Dependency Injection**: FastAPI's built-in DI system
- **DTO Pattern**: Pydantic schemas for data transfer

---

## ✨ Features

### Authentication & Authorization
- ✅ User registration with email validation
- ✅ JWT token-based authentication
- ✅ Bcrypt password hashing
- ✅ Protected endpoints with OAuth2 Bearer

### Task Management
- ✅ Full CRUD operations (Create, Read, Update, Delete)
- ✅ Task filtering by status and priority
- ✅ Pagination support
- ✅ User-scoped tasks (complete isolation)
- ✅ Mark tasks as completed/incomplete

### Statistics
- ✅ User statistics (total tasks, completion percentage)
- ✅ Real-time calculation

### Database
- ✅ PostgreSQL with SQLAlchemy ORM
- ✅ Alembic migrations
- ✅ Relationship management
- ✅ Automatic timestamps

---

## 🛠️ Technology Stack

| Category | Technology |
|----------|------------|
| **Framework** | FastAPI 0.109.0 |
| **Language** | Python 3.11+ |
| **Database** | PostgreSQL 15 |
| **ORM** | SQLAlchemy 2.0 |
| **Migrations** | Alembic 1.13 |
| **Authentication** | JWT (python-jose) |
| **Password Hashing** | Passlib with bcrypt |
| **Validation** | Pydantic v2 |
| **Testing** | Pytest |
| **ASGI Server** | Uvicorn |
| **Containerization** | Docker & Docker Compose |

---

## 🚀 Quick Start with Docker

### Prerequisites

- Docker Desktop 20.10+
- Docker Compose 2.0+

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd tasktracker-mono
```

### Step 2: Start the Application

```bash
# Build and start all services (FastAPI + PostgreSQL)
docker compose up --build

# Or run in detached mode (background)
docker compose up -d --build
```

### Step 3: Verify the Application

The application will be available at:

- **API**: http://localhost:8000
- **Interactive API Docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative API Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Step 4: Stop the Application

```bash
# Stop services
docker compose down

# Stop and remove volumes (⚠️ deletes all data)
docker compose down -v
```

### What Happens on Startup?

1. **PostgreSQL** starts with persistent volume
2. **Database health check** verifies PostgreSQL is ready
3. **FastAPI app** waits for database
4. **Migrations** run automatically (`alembic upgrade head`)
5. **Application** starts on port 8000

---

## 🔄 Running Migrations

### Automatic Migrations (Docker)

Migrations run automatically when using Docker Compose:

```bash
docker compose up
```

### Manual Migrations (Docker)

```bash
# Access the app container
docker exec -it tasktracker_app bash

# Run migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View current migration
alembic current

# View migration history
alembic history
```

### Manual Migrations (Local Development)

```bash
# Activate virtual environment
source venv/bin/activate

# Run migrations
alembic upgrade head

# Create a new migration
alembic revision --autogenerate -m "description of changes"

# Rollback
alembic downgrade -1
```

### Migration Structure

```
migrations/
├── versions/
│   └── 001_initial_migration.py  # Creates users and tasks tables
├── env.py                         # Alembic environment config
└── script.py.mako                 # Migration template
```

---

## 📝 API Examples

### Base URL

```
http://localhost:8000/api/v1
```

### 1. Register a New User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "username": "johndoe",
    "password": "securepass123",
    "full_name": "John Doe"
  }'
```

**Response (201 Created):**
```json
{
  "id": 1,
  "email": "john@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-11-15T10:00:00",
  "updated_at": "2024-11-15T10:00:00"
}
```

### 2. Login and Get Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "securepass123"
  }'
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Save the token** - you'll need it for authenticated requests!

### 3. Get Current User Info

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Create a Task

```bash
curl -X POST "http://localhost:8000/api/v1/tasks/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project documentation",
    "description": "Write comprehensive README",
    "status": "todo",
    "priority": "high",
    "due_date": "2024-12-31T23:59:59"
  }'
```

**Response (201 Created):**
```json
{
  "id": 1,
  "title": "Complete project documentation",
  "description": "Write comprehensive README",
  "status": "todo",
  "priority": "high",
  "is_completed": false,
  "due_date": "2024-12-31T23:59:59",
  "owner_id": 1,
  "created_at": "2024-11-15T10:00:00",
  "updated_at": "2024-11-15T10:00:00"
}
```

### 5. Get All Tasks

```bash
# Get all tasks with pagination
curl -X GET "http://localhost:8000/api/v1/tasks/?skip=0&limit=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Filter by status
curl -X GET "http://localhost:8000/api/v1/tasks/?status=todo" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Filter by priority
curl -X GET "http://localhost:8000/api/v1/tasks/?priority=high" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 6. Update a Task

```bash
curl -X PUT "http://localhost:8000/api/v1/tasks/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "priority": "medium"
  }'
```

### 7. Mark Task as Completed

```bash
curl -X PATCH "http://localhost:8000/api/v1/tasks/1/complete" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 8. Get User Statistics

```bash
curl -X GET "http://localhost:8000/api/v1/stats/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "total_tasks": 10,
  "completed_tasks": 3,
  "completed_percentage": 30.0
}
```

### 9. Delete a Task

```bash
curl -X DELETE "http://localhost:8000/api/v1/tasks/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:** 204 No Content

---

## 💻 Development

### Local Setup (Without Docker)

#### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- pip or poetry

#### Steps

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. **Create database**
   ```bash
   createdb tasktracker_db
   ```

5. **Run migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the application**
   ```bash
   # Development mode (with auto-reload)
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   # Production mode
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

### Environment Variables

Create a `.env` file in the project root:

```env
# Application
APP_NAME=TaskTracker Monolithic API
DEBUG=False

# Database
DATABASE_URL=postgresql://tasktracker:tasktracker@localhost:5432/tasktracker_db

# Security
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

---

## 🧪 Testing

### Run Tests with Docker

```bash
# All tests
docker compose run --rm app pytest

# With coverage
docker compose run --rm app pytest --cov=app tests/

# Specific test file
docker compose run --rm app pytest tests/integration/test_auth.py

# Verbose output
docker compose run --rm app pytest -v
```

### Run Tests Locally

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest

# With coverage report
pytest --cov=app tests/

# Generate HTML coverage report
pytest --cov=app --cov-report=html tests/
```

### Test Structure

```
tests/
├── integration/
│   ├── test_auth.py      # Authentication tests (6 tests)
│   ├── test_tasks.py     # Task management tests (18 tests)
│   └── test_stats.py     # Statistics tests (9 tests)
├── unit/                 # Unit tests (future)
└── conftest.py           # Pytest fixtures
```

**Total: 33 integration tests**

---

## 📁 Project Structure

```
tasktracker-mono/
├── app/
│   ├── core/                    # Core configuration
│   │   ├── config.py           # Settings management
│   │   ├── database.py         # Database connection
│   │   ├── dependencies.py     # FastAPI dependencies
│   │   └── security.py         # Authentication utilities
│   │
│   ├── models/                  # SQLAlchemy ORM models
│   │   ├── user.py             # User model
│   │   └── task.py             # Task model
│   │
│   ├── schemas/                 # Pydantic schemas (DTOs)
│   │   ├── user.py             # User schemas
│   │   ├── task.py             # Task schemas
│   │   └── stats.py            # Statistics schemas
│   │
│   ├── repositories/            # Data access layer
│   │   ├── user_repository.py  # User database operations
│   │   └── task_repository.py  # Task database operations
│   │
│   ├── services/                # Business logic layer
│   │   ├── user_service.py     # User/Auth service
│   │   ├── task_service.py     # Task service
│   │   └── stats_service.py    # Statistics service
│   │
│   ├── routers/                 # API endpoints
│   │   ├── users.py            # Auth endpoints
│   │   ├── tasks.py            # Task endpoints
│   │   └── stats.py            # Statistics endpoints
│   │
│   └── main.py                  # Application entry point
│
├── migrations/                  # Alembic migrations
│   ├── versions/
│   │   └── 001_initial_migration.py
│   └── env.py
│
├── tests/                       # Test suite
│   ├── integration/
│   │   ├── test_auth.py
│   │   ├── test_tasks.py
│   │   └── test_stats.py
│   └── conftest.py
│
├── Dockerfile                   # Docker image definition
├── docker-compose.yml           # Docker orchestration
├── .dockerignore                # Docker build exclusions
├── requirements.txt             # Python dependencies
├── alembic.ini                  # Alembic configuration
├── pytest.ini                   # Pytest configuration
├── .env.example                 # Environment template
└── README.md                    # This file
```

---

## 📊 API Endpoints Summary

### Authentication (3 endpoints)
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `GET /api/v1/auth/me` - Get current user info

### Tasks (8 endpoints)
- `POST /api/v1/tasks/` - Create task
- `GET /api/v1/tasks/` - Get all tasks (with filters)
- `GET /api/v1/tasks/{id}` - Get task by ID
- `PUT /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task
- `PATCH /api/v1/tasks/{id}/complete` - Mark as completed
- `PATCH /api/v1/tasks/{id}/incomplete` - Mark as incomplete
- `GET /api/v1/tasks/stats` - Get task statistics

### Statistics (1 endpoint)
- `GET /api/v1/stats/` - Get user statistics

**Total: 12 API endpoints**

---

## 🔒 Security Features

- ✅ JWT token-based authentication
- ✅ Bcrypt password hashing
- ✅ OAuth2 Bearer token scheme
- ✅ User-scoped data access
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ CORS configuration
- ✅ Non-root Docker user
- ✅ Environment-based secrets

---

## 📚 Additional Resources

### Interactive API Documentation
Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Database Schema

**Users Table:**
- id, email (unique), username (unique), hashed_password
- full_name, is_active, is_superuser
- created_at, updated_at

**Tasks Table:**
- id, title, description
- status (todo/in_progress/done), priority (low/medium/high)
- is_completed, due_date
- owner_id (FK to users), created_at, updated_at

---

## 📄 License

This project is for educational purposes.

---

## 👥 Contributing

This is a university project. Contributions are welcome for learning purposes!

---

## 🎉 Summary

TaskTracker is a complete, production-ready FastAPI application demonstrating:
- ✅ Clean layered architecture
- ✅ Repository and Service patterns
- ✅ JWT authentication
- ✅ Full CRUD operations
- ✅ Docker containerization
- ✅ Database migrations
- ✅ Comprehensive testing

**Get started in 2 commands:**
```bash
docker compose up --build
open http://localhost:8000/docs
```

Enjoy building with TaskTracker! 🚀
