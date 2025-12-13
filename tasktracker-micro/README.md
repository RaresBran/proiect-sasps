# TaskTracker - Microservices Architecture

A production-ready task management application built with microservices architecture using FastAPI, PostgreSQL, and Docker. This project demonstrates modern distributed system design with separate services for authentication, task management, and statistics.

---

## 📋 Table of Contents

- [Architecture Overview](#-architecture-overview)
- [Microservices](#-microservices)
- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Quick Start](#-quick-start)
- [API Documentation](#-api-documentation)
- [Service Communication](#-service-communication)
- [Database Architecture](#-database-architecture)
- [Comparison with Monolithic Architecture](#-comparison-with-monolithic-architecture)
- [Development](#-development)
- [Testing](#-testing)

---

## 🏗️ Architecture Overview

The TaskTracker microservices architecture consists of four main services and two databases:

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│              (Web Frontend, Mobile Apps, etc.)                   │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/JSON
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway (Port 8000)                     │
│  • Routes requests to appropriate microservices                  │
│  • Single entry point for all clients                            │
│  • Request forwarding and response aggregation                   │
└─────────┬────────────────┬────────────────┬─────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  User Service   │  │  Task Service   │  │  Stats Service  │
│   (Port 8001)   │  │   (Port 8002)   │  │   (Port 8003)   │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ • Registration  │  │ • Task CRUD     │  │ • Statistics    │
│ • Login/Auth    │  │ • Filtering     │  │ • Aggregation   │
│ • JWT Tokens    │  │ • Completion    │  │ • Task Service  │
│ • User Data     │  │ • Task Data     │  │   Client        │
└────────┬────────┘  └────────┬────────┘  └─────────────────┘
         │                    │
         ▼                    ▼
┌─────────────────┐  ┌─────────────────┐
│   User DB       │  │    Task DB      │
│  PostgreSQL     │  │   PostgreSQL    │
│  (Port 5433)    │  │   (Port 5434)   │
└─────────────────┘  └─────────────────┘
```

### Design Principles

- **Service Isolation**: Each service has its own database and can be deployed independently
- **Single Responsibility**: Each service handles a specific domain (users, tasks, stats)
- **API Gateway Pattern**: Centralized entry point for all client requests
- **Database per Service**: Each service manages its own data store
- **Synchronous Communication**: Services communicate via REST API calls
- **JWT Authentication**: Stateless authentication shared across services

---

## 🔧 Microservices

### 1. API Gateway (Port 8000)

**Purpose**: Single entry point that routes requests to appropriate microservices

**Key Features**:
- Request routing and forwarding
- Centralized CORS handling
- Service health monitoring
- Load balancing ready

**Endpoints**:
- `GET /` - Gateway information
- `GET /health` - Health check
- `/api/v1/auth/*` → User Service
- `/api/v1/tasks/*` → Task Service  
- `/api/v1/stats/*` → Stats Service

### 2. User Service (Port 8001)

**Purpose**: Handles user authentication and management

**Database**: `user_db` (PostgreSQL on port 5433)

**Key Features**:
- User registration with email validation
- Login with JWT token generation
- Password hashing with bcrypt
- User profile management

**Endpoints**:
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `GET /api/v1/auth/me` - Get current user info

**Database Schema**:
```sql
users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  username VARCHAR(100) UNIQUE NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  full_name VARCHAR(255),
  is_active BOOLEAN DEFAULT TRUE,
  is_superuser BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
)
```

### 3. Task Service (Port 8002)

**Purpose**: Manages all task-related operations

**Database**: `task_db` (PostgreSQL on port 5434)

**Key Features**:
- Full CRUD operations for tasks
- Task filtering by status and priority
- Pagination support
- User-scoped tasks (complete isolation)
- Mark tasks as completed/incomplete

**Endpoints**:
- `POST /api/v1/tasks/` - Create task
- `GET /api/v1/tasks/` - Get all tasks (with filters)
- `GET /api/v1/tasks/{id}` - Get task by ID
- `PUT /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task
- `PATCH /api/v1/tasks/{id}/complete` - Mark as completed
- `PATCH /api/v1/tasks/{id}/incomplete` - Mark as incomplete
- `GET /api/v1/tasks/stats` - Get task statistics

**Database Schema**:
```sql
tasks (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  status ENUM('todo', 'in_progress', 'done') DEFAULT 'todo',
  priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
  is_completed BOOLEAN DEFAULT FALSE,
  due_date TIMESTAMP WITH TIME ZONE,
  owner_id INTEGER NOT NULL,  -- References user from User Service
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
)
```

### 4. Stats Service (Port 8003)

**Purpose**: Provides aggregated statistics across tasks

**Database**: None (stateless service)

**Key Features**:
- Calculates task completion statistics
- Communicates with Task Service to get data
- Real-time calculation
- No data persistence

**Endpoints**:
- `GET /api/v1/stats/` - Get user statistics

**Service Dependencies**:
- Depends on Task Service for data

---

## ✨ Features

### Authentication & Authorization
- ✅ User registration with email validation
- ✅ JWT token-based authentication
- ✅ Bcrypt password hashing
- ✅ Protected endpoints with OAuth2 Bearer
- ✅ Stateless authentication across services

### Task Management
- ✅ Full CRUD operations
- ✅ Task filtering by status (todo, in_progress, done)
- ✅ Task filtering by priority (low, medium, high)
- ✅ Pagination support
- ✅ User-scoped tasks (complete isolation)
- ✅ Mark tasks as completed/incomplete
- ✅ Due date tracking

### Statistics
- ✅ Total tasks count
- ✅ Completed tasks count
- ✅ Completion percentage
- ✅ Real-time calculation

### Infrastructure
- ✅ API Gateway for request routing
- ✅ Database per service
- ✅ Service isolation
- ✅ Docker containerization
- ✅ Database migrations with Alembic
- ✅ Health checks for all services

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| **Services Framework** | FastAPI 0.109.0 |
| **Language** | Python 3.11+ |
| **Databases** | PostgreSQL 15 (2 instances) |
| **ORM** | SQLAlchemy 2.0 |
| **Migrations** | Alembic 1.13 |
| **Authentication** | JWT (python-jose) |
| **Password Hashing** | Passlib with bcrypt |
| **API Gateway** | FastAPI + httpx |
| **Service Communication** | REST API (HTTP) |
| **Validation** | Pydantic v2 |
| **ASGI Server** | Uvicorn |
| **Containerization** | Docker & Docker Compose |

---

## 🚀 Quick Start

### Prerequisites

- Docker Desktop 20.10+
- Docker Compose 2.0+

### Step 1: Clone the Repository

```bash
cd tasktracker-micro
```

### Step 2: Start All Services

```bash
# Build and start all services
docker compose up --build

# Or run in detached mode (background)
docker compose up -d --build
```

This will start:
- API Gateway on http://localhost:8000
- User Service on http://localhost:8001
- Task Service on http://localhost:8002
- Stats Service on http://localhost:8003
- User Database on localhost:5433
- Task Database on localhost:5434

### Step 3: Verify Services

Check that all services are running:

```bash
# Check gateway
curl http://localhost:8000/health

# Check user service
curl http://localhost:8001/health

# Check task service
curl http://localhost:8002/health

# Check stats service
curl http://localhost:8003/health
```

### Step 4: Access API Documentation

- **API Gateway Docs**: http://localhost:8000/docs
- **User Service Docs**: http://localhost:8001/docs
- **Task Service Docs**: http://localhost:8002/docs
- **Stats Service Docs**: http://localhost:8003/docs

### Step 5: Stop Services

```bash
# Stop services
docker compose down

# Stop and remove volumes (⚠️ deletes all data)
docker compose down -v
```

---

## 📝 API Documentation

### Base URL

```
http://localhost:8000/api/v1
```

All requests go through the API Gateway which routes them to the appropriate service.

### Authentication Flow

1. **Register a user**:
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

2. **Login to get token**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "securepass123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

3. **Use token for authenticated requests**:
```bash
# Create a task
curl -X POST "http://localhost:8000/api/v1/tasks/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project",
    "description": "Finish microservices implementation",
    "status": "todo",
    "priority": "high"
  }'

# Get all tasks
curl -X GET "http://localhost:8000/api/v1/tasks/" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get statistics
curl -X GET "http://localhost:8000/api/v1/stats/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🔄 Service Communication

### Inter-Service Communication

1. **Client → API Gateway**:
   - All client requests go through the gateway
   - Gateway validates and forwards requests

2. **API Gateway → Services**:
   - Gateway routes requests based on URL path
   - Forwards authentication headers
   - Returns service responses to client

3. **Stats Service → Task Service**:
   - Stats service makes HTTP requests to Task Service
   - Uses JWT token for authentication
   - Retrieves task data for calculations

### Authentication Flow

```
1. User registers/logs in → User Service
2. User Service returns JWT token
3. Client includes token in subsequent requests
4. API Gateway forwards token to services
5. Each service validates token independently
6. Services extract user_id from token
7. Services perform user-scoped operations
```

---

## 💾 Database Architecture

### Database per Service Pattern

Each service has its own database for data isolation:

**User Database** (`user_db` on port 5433):
- Managed by User Service
- Contains user accounts and credentials
- Independent schema and migrations

**Task Database** (`task_db` on port 5434):
- Managed by Task Service
- Contains tasks with owner_id references
- Independent schema and migrations

**Stats Service**:
- No dedicated database
- Stateless service
- Queries Task Service for data

### Advantages

- **Independent Scaling**: Scale databases independently based on load
- **Service Isolation**: Service failures don't affect other databases
- **Technology Freedom**: Each service can use different database technologies
- **Independent Deployment**: Update schemas without coordinating with other services

### Trade-offs

- **No Foreign Keys**: Cannot enforce referential integrity across services
- **Data Consistency**: Must implement eventual consistency patterns
- **Increased Complexity**: More databases to manage and monitor

---

## 🔄 Comparison with Monolithic Architecture

### Monolithic Architecture (`tasktracker-mono`)

```
Single Application (Port 8000)
├── All routers in one app
├── Shared database connection
├── Single deployment unit
└── Single PostgreSQL database
```

**Advantages**:
- Simpler to develop and deploy
- Easier to test
- Better performance (no network calls between services)
- ACID transactions across all tables

**Disadvantages**:
- Tight coupling between components
- Difficult to scale individual components
- Single point of failure
- Larger codebase

### Microservices Architecture (`tasktracker-micro`)

```
API Gateway + 3 Services + 2 Databases
├── Independent services
├── Database per service
├── Separate deployments
└── Service communication via HTTP
```

**Advantages**:
- Independent deployment and scaling
- Technology diversity
- Fault isolation
- Team autonomy
- Easier to understand individual services

**Disadvantages**:
- Increased complexity
- Network latency
- Distributed system challenges
- More infrastructure to manage

---

## 💻 Development

### Running Individual Services

You can run services individually for development:

```bash
# User Service
cd user-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="postgresql://tasktracker:tasktracker@localhost:5433/user_db"
alembic upgrade head
uvicorn app.main:app --reload --port 8001

# Task Service
cd task-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="postgresql://tasktracker:tasktracker@localhost:5434/task_db"
alembic upgrade head
uvicorn app.main:app --reload --port 8002

# Stats Service
cd stats-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export TASK_SERVICE_URL="http://localhost:8002"
uvicorn app.main:app --reload --port 8003

# API Gateway
cd api-gateway
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export USER_SERVICE_URL="http://localhost:8001"
export TASK_SERVICE_URL="http://localhost:8002"
export STATS_SERVICE_URL="http://localhost:8003"
uvicorn app.main:app --reload --port 8000
```

### Service Configuration

Each service can be configured via environment variables:

**User Service**:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time

**Task Service**:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key (must match User Service)

**Stats Service**:
- `TASK_SERVICE_URL`: Task service base URL
- `SECRET_KEY`: JWT secret key (must match other services)

**API Gateway**:
- `USER_SERVICE_URL`: User service base URL
- `TASK_SERVICE_URL`: Task service base URL
- `STATS_SERVICE_URL`: Stats service base URL

---

## 🧪 Testing

### Running Tests

```bash
# Test individual service
docker compose run --rm user-service pytest
docker compose run --rm task-service pytest
docker compose run --rm stats-service pytest

# Test with coverage
docker compose run --rm user-service pytest --cov=app tests/
```

### Manual API Testing

Use the interactive API documentation:
- http://localhost:8000/docs (API Gateway)
- http://localhost:8001/docs (User Service)
- http://localhost:8002/docs (Task Service)
- http://localhost:8003/docs (Stats Service)

---

## 📊 Service Ports

| Service | Port | Database Port |
|---------|------|---------------|
| API Gateway | 8000 | - |
| User Service | 8001 | 5433 |
| Task Service | 8002 | 5434 |
| Stats Service | 8003 | - |

---

## 🔒 Security Features

- ✅ JWT token-based authentication
- ✅ Bcrypt password hashing
- ✅ OAuth2 Bearer token scheme
- ✅ User-scoped data access
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ CORS configuration
- ✅ Non-root Docker users
- ✅ Environment-based secrets
- ✅ Service-to-service authentication

---

## 🎉 Summary

TaskTracker Microservices demonstrates:
- ✅ Microservices architecture with 3 independent services
- ✅ API Gateway pattern for request routing
- ✅ Database per service pattern
- ✅ Service-to-service communication
- ✅ JWT authentication across services
- ✅ Docker containerization and orchestration
- ✅ Independent deployment and scaling
- ✅ Production-ready design patterns

**Get started in 2 commands:**
```bash
cd tasktracker-micro
docker compose up --build
```

Then open http://localhost:8000/docs

**Works with the same frontend as the monolithic version!**

The frontend can connect to either architecture by simply changing the `NEXT_PUBLIC_API_URL` environment variable.

---

## 📚 Additional Resources

- **Monolithic Version**: See `../tasktracker-mono` for comparison
- **Frontend**: See `../tasktracker-frontend` for the Next.js client
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Docker Compose**: https://docs.docker.com/compose/

Enjoy building with TaskTracker Microservices! 🚀

