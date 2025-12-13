# TaskTracker Microservices - Quick Start Guide

## ✅ System Status: OPERATIONAL

All issues have been resolved and the system is fully functional!

## What Was Fixed

1. **Database Enum Issue** - Fixed SQLAlchemy enum handling to use lowercase values matching the database schema
2. **Stats Service Query** - Fixed invalid query parameter (limit too high)

## Quick Test

Run this command to verify everything works:

```bash
# From the tasktracker-micro directory
curl -s http://localhost:8000/health | jq
```

Expected output:
```json
{
  "status": "healthy",
  "service": "api-gateway"
}
```

## API Endpoints

All endpoints are accessible through the API Gateway at `http://localhost:8000/api/v1/`

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user info

### Tasks
- `GET /tasks/` - Get all tasks (with pagination)
- `POST /tasks/` - Create new task
- `GET /tasks/{id}` - Get specific task
- `PUT /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task
- `PATCH /tasks/{id}/complete` - Mark task as complete
- `PATCH /tasks/{id}/incomplete` - Mark task as incomplete

### Statistics
- `GET /stats/` - Get user statistics

## Task Status Values

When creating or updating tasks, use these lowercase values:
- `"todo"` - Task is pending
- `"in_progress"` - Task is being worked on
- `"done"` - Task is completed

## Task Priority Values

- `"low"` - Low priority
- `"medium"` - Medium priority
- `"high"` - High priority

## Example: Create a Task

```bash
# 1. Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@test.com", "username": "user", "password": "pass123"}'

# 2. Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass123"}' | jq -r '.access_token')

# 3. Create Task
curl -X POST http://localhost:8000/api/v1/tasks/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "My Task",
    "description": "Task description",
    "status": "todo",
    "priority": "high"
  }'

# 4. Get Tasks
curl http://localhost:8000/api/v1/tasks/ \
  -H "Authorization: Bearer $TOKEN"

# 5. Get Stats
curl http://localhost:8000/api/v1/stats/ \
  -H "Authorization: Bearer $TOKEN"
```

## Service Ports

- **API Gateway**: http://localhost:8000
- **User Service**: http://localhost:8001 (internal)
- **Task Service**: http://localhost:8002 (internal)
- **Stats Service**: http://localhost:8003 (internal)
- **User Database**: localhost:5433
- **Task Database**: localhost:5434

## Docker Commands

```bash
# Check service status
docker-compose ps

# View logs
docker logs tasktracker_api_gateway --tail 50
docker logs tasktracker_task_service --tail 50
docker logs tasktracker_stats_service --tail 50
docker logs tasktracker_user_service --tail 50

# Restart all services
docker-compose restart

# Rebuild and restart specific service
docker-compose up -d --build task-service

# Stop all services
docker-compose down

# Start all services
docker-compose up -d

# Stop and remove volumes (fresh start)
docker-compose down -v
```

## Testing the Frontend

If you have the frontend application:

1. Make sure the backend is running (services above)
2. Navigate to the frontend directory
3. Update `.env.local` if needed:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
   ```
4. Start the frontend:
   ```bash
   npm run dev
   ```
5. Open http://localhost:3000

## Troubleshooting

### Service won't start
```bash
# Check logs
docker logs tasktracker_<service_name>

# Restart service
docker-compose restart <service_name>
```

### Database issues
```bash
# Reset databases (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d
```

### Port conflicts
If ports 8000-8003, 5433, or 5434 are already in use, modify `docker-compose.yml` to use different ports.

## Architecture

```
┌─────────────────┐
│   Frontend      │
│  (React/Next)   │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  API Gateway    │  :8000
│   (FastAPI)     │
└────────┬────────┘
         │
    ┌────┴────┬────────────┬────────────┐
    │         │            │            │
    v         v            v            v
┌───────┐ ┌───────┐  ┌────────┐  ┌────────┐
│ User  │ │ Task  │  │ Stats  │  │ More   │
│Service│ │Service│  │Service │  │Services│
└───┬───┘ └───┬───┘  └────────┘  └────────┘
    │         │
    v         v
┌───────┐ ┌───────┐
│User DB│ │Task DB│
│(PG)   │ │(PG)   │
└───────┘ └───────┘
```

## Need Help?

Check the following files for more information:
- `FIXES_APPLIED.md` - Detailed fix information
- `ARCHITECTURE_COMPARISON.md` - Architecture details
- `PROJECT_SUMMARY.md` - Project overview
- `README.md` - Full documentation

