# Microservices Tracker - Fixes Applied

## Issues Identified and Fixed

### 1. Database Enum Value Mismatch (CRITICAL)

**Problem:**
The task service was failing with the error:
```
psycopg2.errors.InvalidTextRepresentation: invalid input value for enum taskstatus: "TODO"
```

**Root Cause:**
SQLAlchemy's `Enum` type was using the `.name` attribute (uppercase: "TODO", "IN_PROGRESS", "DONE") instead of the `.value` attribute (lowercase: "todo", "in_progress", "done") when inserting data into the PostgreSQL database. The database enum was defined with lowercase values, but SQLAlchemy was trying to insert uppercase names.

**Solution:**
Modified the Task model in `/tasktracker-micro/task-service/app/models/task.py` to explicitly tell SQLAlchemy to use enum values:

```python
# Before:
status = Column(SQLEnum(TaskStatus), default=TaskStatus.TODO, nullable=False)
priority = Column(SQLEnum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)

# After:
status = Column(SQLEnum(TaskStatus, values_callable=lambda obj: [e.value for e in obj]), default=TaskStatus.TODO, nullable=False)
priority = Column(SQLEnum(TaskPriority, values_callable=lambda obj: [e.value for e in obj]), default=TaskPriority.MEDIUM, nullable=False)
```

### 2. Invalid Query Parameter Limit

**Problem:**
The stats service was making requests to the task service with `limit=10000`, but the task service only accepts a maximum limit of 1000:
```
tasktracker_task_service   | INFO:     172.18.0.6:51936 - "GET /api/v1/tasks/?limit=10000 HTTP/1.1" 422 Unprocessable Entity
```

**Root Cause:**
The stats service was hardcoded to request 10,000 tasks, exceeding the validation constraint in the task service router.

**Solution:**
Modified `/tasktracker-micro/stats-service/app/services/stats_service.py`:
- Changed limit from 10000 to 1000
- Updated to use the `total` field from the API response instead of just counting returned tasks

```python
# Before:
response = requests.get(
    f"{self.task_service_url}/api/v1/tasks/?limit=10000",
    headers=headers,
    timeout=5
)
total_tasks = len(tasks)

# After:
response = requests.get(
    f"{self.task_service_url}/api/v1/tasks/?limit=1000",
    headers=headers,
    timeout=5
)
total_tasks = data.get("total", len(tasks))  # Use total count from response
```

## Testing Performed

All tests passed successfully:

1. **User Registration & Authentication** ✅
   - Successfully registered new user
   - Successfully logged in and received JWT token

2. **Task Creation** ✅
   - Created task with status "todo" - SUCCESS
   - Created task with status "in_progress" - SUCCESS
   - Created task with status "done" - SUCCESS
   - All priority levels work correctly

3. **Task Retrieval** ✅
   - Successfully retrieved all tasks for user
   - Pagination working correctly

4. **Task Completion** ✅
   - Successfully marked task as complete
   - Status updated from "todo" to "done"
   - is_completed flag set to true

5. **Statistics** ✅
   - Successfully retrieved user statistics
   - Correct counts: total_tasks, completed_tasks, completed_percentage

## System Status

All services are now running correctly:
- ✅ User Service (port 8001)
- ✅ Task Service (port 8002)
- ✅ Stats Service (port 8003)
- ✅ API Gateway (port 8000)
- ✅ User Database (PostgreSQL)
- ✅ Task Database (PostgreSQL)

## Sample Test Results

```json
{
  "tasks": [
    {
      "title": "Test Task",
      "status": "done",
      "priority": "medium",
      "is_completed": true
    },
    {
      "title": "Another Task",
      "status": "in_progress",
      "priority": "high",
      "is_completed": false
    },
    {
      "title": "Completed Task",
      "status": "done",
      "priority": "low",
      "is_completed": true
    }
  ],
  "total": 3
}

{
  "total_tasks": 3,
  "completed_tasks": 2,
  "completed_percentage": 66.67
}
```

## Next Steps

The microservices tracker is now fully functional. You can:
1. Start the frontend application to interact with the API
2. Use the API directly via the gateway at `http://localhost:8000`
3. Monitor service logs with `docker logs <container_name>`
4. View service health at `http://localhost:8000/health`

## Commands to Manage Services

```bash
# Check status
docker-compose ps

# View logs
docker logs tasktracker_task_service --tail 50
docker logs tasktracker_stats_service --tail 50
docker logs tasktracker_api_gateway --tail 50

# Restart services
docker-compose restart

# Stop all services
docker-compose down

# Start all services
docker-compose up -d
```

