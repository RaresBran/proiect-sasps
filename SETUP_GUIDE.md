# TaskTracker - Complete Setup Guide

## Overview

This project consists of two main components:
1. **Backend API** - FastAPI monolithic application (tasktracker-mono)
2. **Frontend** - Next.js application with shadcn/ui (tasktracker-frontend)

## Quick Start

### Prerequisites

- Docker & Docker Compose (for backend)
- Node.js 18+ (for frontend)
- npm or yarn

### Step 1: Start the Backend API

```bash
# Navigate to backend directory
cd tasktracker-mono

# Start PostgreSQL + FastAPI
docker compose up --build

# The API will be available at:
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Health: http://localhost:8000/health
```

Wait until you see:
```
tasktracker_app  | INFO:     Application startup complete.
tasktracker_app  | INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Start the Frontend

Open a **new terminal** window:

```bash
# Navigate to frontend directory
cd tasktracker-frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev

# The frontend will be available at:
# http://localhost:3000
```

### Step 3: Use the Application

1. Open your browser to http://localhost:3000
2. Create an account by clicking "Sign up"
3. Fill in:
   - Email: your@email.com
   - Username: your_username
   - Password: your_password
   - Full Name: Your Name (optional)
4. Click "Sign Up"
5. You'll be automatically logged in and see the dashboard!

## Features

### 🔐 Authentication
- **Register**: Create a new account
- **Login**: Sign in with username and password
- **Auto-login**: Stay logged in with token persistence
- **Logout**: Sign out securely

### ✅ Task Management
- **Create**: Add new tasks with title, description, and priority
- **View**: See all your tasks in a beautiful list
- **Complete**: Mark tasks as done with a single click
- **Delete**: Remove tasks you no longer need
- **Status**: Tasks show current status (todo, in progress, done)

### 📊 Statistics Dashboard
- **Total Tasks**: See how many tasks you have
- **Completed**: Track completed tasks
- **Completion Rate**: View your productivity percentage

## Architecture

```
┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │
│  Frontend       │ ◄─────► │  Backend API    │
│  (Next.js)      │  HTTP   │  (FastAPI)      │
│  Port: 3000     │         │  Port: 8000     │
│                 │         │                 │
└─────────────────┘         └────────┬────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │                 │
                            │  PostgreSQL     │
                            │  Port: 5432     │
                            │                 │
                            └─────────────────┘
```

## Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Stop Docker containers
docker compose down

# Or use different port
# Edit docker-compose.yml: "8001:8000"
```

**Database connection failed:**
```bash
# Check database is healthy
docker compose ps

# View logs
docker compose logs db
```

### Frontend Issues

**Port 3000 already in use:**
```bash
# Use different port
PORT=3001 npm run dev
```

**Cannot connect to API:**
1. Make sure backend is running at http://localhost:8000
2. Check `.env.local` has correct API URL
3. Try accessing http://localhost:8000/docs directly

**CORS errors:**
- Already configured! The backend allows http://localhost:3000

## Development Workflow

### Making Changes

**Backend Changes:**
1. Edit code in `tasktracker-mono/app/`
2. Rebuild: `docker compose up --build`

**Frontend Changes:**
1. Edit code in `tasktracker-frontend/`
2. Changes auto-reload (hot reload enabled)

### Database Migrations

```bash
# Access backend container
docker exec -it tasktracker_app bash

# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

### Testing the API

Use the interactive docs at http://localhost:8000/docs

Or use curl:

```bash
# Register
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"test123"}'

# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}'

# Get tasks (use token from login)
curl -X GET "http://localhost:8000/api/v1/tasks/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Stopping the Application

### Stop Frontend
Press `Ctrl+C` in the terminal running `npm run dev`

### Stop Backend
```bash
# In tasktracker-mono directory
docker compose down

# To also remove database data:
docker compose down -v
```

## Production Build

### Backend
```bash
cd tasktracker-mono
docker compose up -d
```

### Frontend
```bash
cd tasktracker-frontend
npm run build
npm start
```

## Project Structure

```
proiect-sasps/
├── tasktracker-mono/          # Backend API
│   ├── app/                   # Application code
│   ├── migrations/            # Database migrations
│   ├── tests/                 # Test suite
│   ├── docker-compose.yml     # Docker orchestration
│   ├── Dockerfile             # Docker image
│   └── README.md              # Backend docs
│
└── tasktracker-frontend/      # Frontend app
    ├── app/                   # Next.js pages
    ├── components/            # React components
    ├── lib/                   # API client & utilities
    ├── contexts/              # React contexts
    └── README.md              # Frontend docs
```

## Technology Stack

### Backend
- FastAPI 0.109.0
- PostgreSQL 15
- SQLAlchemy 2.0
- Alembic (migrations)
- JWT authentication
- Docker

### Frontend
- Next.js 15
- TypeScript
- Tailwind CSS
- shadcn/ui components
- Lucide icons
- React Context API

## Next Steps

1. ✅ Start backend: `cd tasktracker-mono && docker compose up`
2. ✅ Start frontend: `cd tasktracker-frontend && npm run dev`
3. ✅ Open browser: http://localhost:3000
4. ✅ Create account and start managing tasks!

## Support

- Backend API Docs: http://localhost:8000/docs
- Backend README: `tasktracker-mono/README.md`
- Frontend README: `tasktracker-frontend/README.md`

Enjoy TaskTracker! 🚀

