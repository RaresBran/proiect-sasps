# TaskTracker Microservices - Quick Reference

## 🚀 Quick Start

```bash
cd tasktracker-micro
docker compose up --build
```

Open http://localhost:8000/docs

---

## 📍 Service URLs

| Service | Base URL | API Docs | Health Check |
|---------|----------|----------|--------------|
| API Gateway | http://localhost:8000 | http://localhost:8000/docs | http://localhost:8000/health |
| User Service | http://localhost:8001 | http://localhost:8001/docs | http://localhost:8001/health |
| Task Service | http://localhost:8002 | http://localhost:8002/docs | http://localhost:8002/health |
| Stats Service | http://localhost:8003 | http://localhost:8003/docs | http://localhost:8003/health |

---

## 🔑 Authentication Flow

1. **Register**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","username":"user","password":"pass123"}'
```

2. **Login**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass123"}'
```

3. **Use Token**:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/v1/tasks/
```

---

## 📝 API Endpoints (via Gateway)

### Authentication (→ User Service)
- `POST /api/v1/auth/register` - Register user
- `POST /api/v1/auth/login` - Login and get JWT
- `GET /api/v1/auth/me` - Get current user

### Tasks (→ Task Service)
- `GET /api/v1/tasks/` - List tasks (with filters)
- `POST /api/v1/tasks/` - Create task
- `GET /api/v1/tasks/{id}` - Get task
- `PUT /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task
- `PATCH /api/v1/tasks/{id}/complete` - Mark complete
- `PATCH /api/v1/tasks/{id}/incomplete` - Mark incomplete

### Statistics (→ Stats Service)
- `GET /api/v1/stats/` - Get user statistics

---

## 🗄️ Database Access

### User Database
```bash
psql -h localhost -p 5433 -U tasktracker -d user_db
# Password: tasktracker
```

### Task Database
```bash
psql -h localhost -p 5434 -U tasktracker -d task_db
# Password: tasktracker
```

---

## 🐳 Docker Commands

```bash
# Start services
docker compose up

# Start in background
docker compose up -d

# Rebuild and start
docker compose up --build

# Stop services
docker compose down

# Stop and remove data
docker compose down -v

# View logs
docker compose logs -f

# View specific service logs
docker compose logs -f task-service

# Check service status
docker compose ps

# Restart a service
docker compose restart user-service

# Scale a service
docker compose up --scale task-service=3
```

---

## 📊 Service Architecture

```
Client
  ↓
API Gateway (:8000)
  ├→ User Service (:8001) → User DB (:5433)
  ├→ Task Service (:8002) → Task DB (:5434)
  └→ Stats Service (:8003) → calls Task Service
```

---

## 🔧 Environment Variables

### All Services
- `SECRET_KEY` - JWT secret (must match across services)
- `DEBUG` - Debug mode (True/False)
- `LOG_LEVEL` - Logging level (INFO/DEBUG/WARNING/ERROR)
- `BACKEND_CORS_ORIGINS` - Allowed CORS origins

### User Service
- `DATABASE_URL` - PostgreSQL connection string
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration (default: 30)

### Task Service
- `DATABASE_URL` - PostgreSQL connection string

### Stats Service
- `TASK_SERVICE_URL` - Task service base URL

### API Gateway
- `USER_SERVICE_URL` - User service base URL
- `TASK_SERVICE_URL` - Task service base URL
- `STATS_SERVICE_URL` - Stats service base URL

---

## 🧪 Testing Workflow

### 1. Health Check All Services
```bash
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
```

### 2. Register and Login
```bash
# Register
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","username":"test","password":"test123"}' \
  | jq -r '.access_token')

# Login (if already registered)
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}' \
  | jq -r '.access_token')

echo $TOKEN
```

### 3. Create and List Tasks
```bash
# Create task
curl -X POST "http://localhost:8000/api/v1/tasks/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Task","status":"todo","priority":"high"}'

# List tasks
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/tasks/" | jq
```

### 4. Get Statistics
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/stats/" | jq
```

---

## 🔍 Troubleshooting

### Check Service Health
```bash
docker compose ps
```

### View Service Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f user-service
docker compose logs -f task-service
docker compose logs -f stats-service
```

### Restart Services
```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart task-service
```

### Clean Start
```bash
docker compose down -v
docker compose up --build
```

### Check Database Connection
```bash
# User DB
docker exec -it tasktracker_user_db psql -U tasktracker -d user_db -c "\dt"

# Task DB
docker exec -it tasktracker_task_db psql -U tasktracker -d task_db -c "\dt"
```

---

## 📁 Project Structure

```
tasktracker-micro/
├── api-gateway/           # API Gateway service
├── user-service/          # User authentication service
├── task-service/          # Task management service
├── stats-service/         # Statistics service
├── docker-compose.yml     # Docker orchestration
├── README.md              # Full documentation
├── SETUP_GUIDE.md         # Detailed setup instructions
└── ARCHITECTURE_COMPARISON.md  # Monolith vs Microservices
```

---

## 🔐 Security Notes

**⚠️ For Production:**
1. Change `SECRET_KEY` in docker-compose.yml
2. Use strong database passwords
3. Enable HTTPS
4. Configure proper CORS origins
5. Use environment variables, not hardcoded values
6. Implement rate limiting
7. Add API authentication/API keys
8. Use secrets management (Docker secrets, Vault, etc.)

---

## 📚 Documentation

- **Full README**: `README.md`
- **Setup Guide**: `SETUP_GUIDE.md`
- **Architecture Comparison**: `ARCHITECTURE_COMPARISON.md`
- **API Docs**: http://localhost:8000/docs (when running)

---

## 💡 Common Use Cases

### Filter Tasks by Status
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/tasks/?status=todo"
```

### Filter Tasks by Priority
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/tasks/?priority=high"
```

### Pagination
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/tasks/?skip=0&limit=10"
```

### Update Task
```bash
curl -X PUT "http://localhost:8000/api/v1/tasks/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status":"done","priority":"low"}'
```

### Mark Task Complete
```bash
curl -X PATCH "http://localhost:8000/api/v1/tasks/1/complete" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🎯 Key Differences from Monolithic

| Aspect | Monolithic | Microservices |
|--------|-----------|---------------|
| Services | 1 | 4 |
| Databases | 1 | 2 |
| Ports | 1 | 5 |
| Containers | 2 | 6 |
| Complexity | Low | High |
| Scalability | Limited | High |

---

## 🚦 Service Dependencies

```
api-gateway
  ├─ depends on: user-service, task-service, stats-service
  └─ starts after: all other services are healthy

user-service
  ├─ depends on: user-db
  └─ starts after: user-db is healthy

task-service
  ├─ depends on: task-db
  └─ starts after: task-db is healthy

stats-service
  ├─ depends on: task-service
  └─ starts after: task-service is healthy
```

---

**Happy coding! 🚀**

For more details, see the full [README.md](README.md) or [SETUP_GUIDE.md](SETUP_GUIDE.md)

