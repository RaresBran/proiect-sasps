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
  
- **Database**
  - PostgreSQL with SQLAlchemy ORM
  - Alembic migrations
  - User and Task models
  
- **Security**
  - Password hashing with Passlib
  - JWT tokens with configurable expiration
  - OAuth2 Bearer authentication
  - Protected endpoints with dependencies

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

### Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

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

Coming soon! Docker and docker-compose configurations will be added.

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

