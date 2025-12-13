# TaskTracker Microservices - Setup Guide

This guide will help you get the TaskTracker microservices application up and running quickly.

---

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker Desktop** (version 20.10 or higher)
  - Download from: https://www.docker.com/products/docker-desktop
- **Docker Compose** (version 2.0 or higher)
  - Included with Docker Desktop
- **Git** (optional, for cloning the repository)

---

## Quick Start (5 minutes)

### Step 1: Navigate to Project Directory

```bash
cd tasktracker-micro
```

### Step 2: Start All Services

```bash
docker compose up --build
```

This single command will:
- Build Docker images for all 4 services
- Start 2 PostgreSQL databases
- Run database migrations
- Start all microservices
- Set up networking between services

**Expected output:**
```
✅ user-db started
✅ task-db started
✅ user-service started (migrations complete)
✅ task-service started (migrations complete)
✅ stats-service started
✅ api-gateway started
```

### Step 3: Verify Services

Open your browser and visit:

- **API Gateway**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

You should see the interactive API documentation (Swagger UI).

---

## Testing the Application

### 1. Register a User

Using curl:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "password123",
    "full_name": "Test User"
  }'
```

Or use the Swagger UI at http://localhost:8000/docs

### 2. Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

**Save the access_token from the response!**

### 3. Create a Task

Replace `YOUR_TOKEN` with the access_token from step 2:

```bash
curl -X POST "http://localhost:8000/api/v1/tasks/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Task",
    "description": "Testing the microservices",
    "status": "todo",
    "priority": "high"
  }'
```

### 4. Get All Tasks

```bash
curl -X GET "http://localhost:8000/api/v1/tasks/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5. Get Statistics

```bash
curl -X GET "http://localhost:8000/api/v1/stats/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Connecting the Frontend

The microservices work with the same frontend as the monolithic version.

### Option 1: Use Existing Frontend

If you already have the frontend set up:

```bash
cd ../tasktracker-frontend
```

Make sure your `.env.local` file has:
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

Then start the frontend:
```bash
npm run dev
```

Open http://localhost:3000

### Option 2: Start Frontend with Docker

You can also run the frontend in Docker (if you have a Dockerfile in the frontend directory):

```bash
cd ../tasktracker-frontend
docker build -t tasktracker-frontend .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1 tasktracker-frontend
```

---

## Stopping the Services

### Stop All Services

```bash
docker compose down
```

### Stop and Remove All Data

⚠️ **Warning**: This will delete all data from the databases!

```bash
docker compose down -v
```

---

## Service URLs

| Service | URL | API Docs |
|---------|-----|----------|
| API Gateway | http://localhost:8000 | http://localhost:8000/docs |
| User Service | http://localhost:8001 | http://localhost:8001/docs |
| Task Service | http://localhost:8002 | http://localhost:8002/docs |
| Stats Service | http://localhost:8003 | http://localhost:8003/docs |

### Database Connections

| Database | Host | Port | Username | Password | Database Name |
|----------|------|------|----------|----------|---------------|
| User DB | localhost | 5433 | tasktracker | tasktracker | user_db |
| Task DB | localhost | 5434 | tasktracker | tasktracker | task_db |

You can connect to these databases using any PostgreSQL client (e.g., pgAdmin, DBeaver).

---

## Troubleshooting

### Problem: Services won't start

**Solution 1**: Check if ports are already in use
```bash
# Check which ports are in use
lsof -i :8000  # API Gateway
lsof -i :8001  # User Service
lsof -i :8002  # Task Service
lsof -i :8003  # Stats Service
lsof -i :5433  # User DB
lsof -i :5434  # Task DB
```

Stop any services using these ports or modify the ports in `docker-compose.yml`.

**Solution 2**: Clean up Docker
```bash
docker compose down -v
docker system prune -a
docker compose up --build
```

### Problem: Database migrations fail

**Solution**: Remove volumes and restart
```bash
docker compose down -v
docker compose up --build
```

### Problem: "Service unavailable" errors

**Solution**: Wait for all services to be healthy
```bash
docker compose ps
```

All services should show "healthy" status. If not, check logs:
```bash
docker compose logs user-service
docker compose logs task-service
docker compose logs stats-service
docker compose logs api-gateway
```

### Problem: Authentication fails

**Solution**: Make sure all services use the same SECRET_KEY

Check `docker-compose.yml` and ensure the `SECRET_KEY` environment variable is identical across all services that validate JWTs (user-service, task-service, stats-service).

---

## Development Mode

### Running Services Individually

For development, you might want to run services individually:

1. **Start only the databases**:
```bash
docker compose up user-db task-db
```

2. **Run a service locally**:
```bash
cd user-service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
export DATABASE_URL="postgresql://tasktracker:tasktracker@localhost:5433/user_db"
export SECRET_KEY="your-secret-key"
alembic upgrade head
uvicorn app.main:app --reload --port 8001
```

### Viewing Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f user-service
docker compose logs -f task-service
docker compose logs -f stats-service
docker compose logs -f api-gateway
```

### Rebuilding a Single Service

```bash
docker compose up --build user-service
```

---

## Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs to try all endpoints
2. **Connect the Frontend**: Follow the frontend connection steps above
3. **Read the README**: See `README.md` for detailed architecture information
4. **Compare with Monolithic**: Check out `../tasktracker-mono` to see the differences

---

## Common Commands

```bash
# Start all services
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

# Check service status
docker compose ps

# Restart a service
docker compose restart user-service
```

---

## Production Deployment

For production deployment:

1. **Change SECRET_KEY**: Generate a secure key
```bash
openssl rand -hex 32
```

2. **Update environment variables** in `docker-compose.yml`:
   - Set unique SECRET_KEY
   - Set DEBUG=False
   - Configure appropriate CORS origins
   - Use strong database passwords

3. **Use proper orchestration**:
   - Consider Kubernetes for production
   - Use managed databases (AWS RDS, Google Cloud SQL, etc.)
   - Implement proper monitoring and logging
   - Set up CI/CD pipelines

4. **Enable HTTPS**:
   - Use a reverse proxy (nginx, Traefik)
   - Configure SSL certificates

---

## Support

If you encounter any issues:

1. Check the logs: `docker compose logs -f`
2. Verify all services are healthy: `docker compose ps`
3. Review the README.md for architecture details
4. Check the individual service docs: http://localhost:8000/docs

---

Enjoy building with TaskTracker Microservices! 🚀

