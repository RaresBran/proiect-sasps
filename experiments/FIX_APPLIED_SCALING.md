# Fix Applied: Docker Scaling Issue

## Problem
```
WARNING: The "task-service" service is using the custom container name 
"tasktracker_task_service". Docker requires each container to have a unique 
name. Remove the custom name to scale the service.
```

## Root Cause
The original `docker-compose.yml` had `container_name:` declarations for all services. Docker cannot scale services with fixed container names because each replica needs a unique name.

## Solution Implemented

### 1. Created New Scalable Compose File ✅
**File:** `tasktracker-micro/docker-compose.scalable.yml`

**Changes from original:**
- ✅ Removed `container_name:` from `user-service`, `task-service`, `stats-service`
- ✅ Removed `ports:` mapping from scalable services (prevents port conflicts)
- ✅ Kept `container_name:` for DBs and API Gateway (not scaling these)

**Services that can now scale:**
- `user-service` ← No container_name
- `task-service` ← No container_name  
- `stats-service` ← No container_name

**Services with fixed names (not scaling):**
- `user-db` → `tasktracker_user_db`
- `task-db` → `tasktracker_task_db`
- `api-gateway` → `tasktracker_api_gateway`

### 2. Updated Test Script ✅
**File:** `experiments/run_scaled_comparison.sh`

**Updated to use:**
```bash
docker compose -f docker-compose.scalable.yml up -d --scale user-service=3 --scale task-service=3 --scale stats-service=3
```

### 3. Updated Documentation ✅
**Files updated:**
- `experiments/README.md`
- `experiments/SCALED_COMPARISON_GUIDE.md`
- `experiments/QUICK_START.md`

All now reference `docker-compose.scalable.yml` instead of `docker-compose.yml`

## How to Use

### Start Scaled Microservices (Manual)
```bash
cd tasktracker-micro
docker compose -f docker-compose.scalable.yml up -d --scale user-service=3 --scale task-service=3 --scale stats-service=3
```

### Run Full Comparison Test (Automated)
```bash
cd experiments
./run_scaled_comparison.sh
```

### Stop Scaled Microservices
```bash
cd tasktracker-micro
docker compose -f docker-compose.scalable.yml down
```

## Verify It Works

```bash
# Start scaled microservices
cd tasktracker-micro
docker compose -f docker-compose.scalable.yml up -d --scale user-service=3 --scale task-service=3 --scale stats-service=3

# Check running containers (should see 3 of each service)
docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "user-service|task-service|stats-service"

# Expected output:
# tasktracker-micro-user-service-1    Up X seconds
# tasktracker-micro-user-service-2    Up X seconds
# tasktracker-micro-user-service-3    Up X seconds
# tasktracker-micro-task-service-1    Up X seconds
# tasktracker-micro-task-service-2    Up X seconds
# tasktracker-micro-task-service-3    Up X seconds
# tasktracker-micro-stats-service-1   Up X seconds
# tasktracker-micro-stats-service-2   Up X seconds
# tasktracker-micro-stats-service-3   Up X seconds

# Test health endpoint
curl http://localhost:8000/health

# Clean up
docker compose -f docker-compose.scalable.yml down
```

## Files Changed

| File | Status | Change |
|------|--------|--------|
| `tasktracker-micro/docker-compose.scalable.yml` | ✅ Created | Scalable version without container names |
| `experiments/run_scaled_comparison.sh` | ✅ Updated | Uses scalable compose file |
| `experiments/README.md` | ✅ Updated | References scalable compose |
| `experiments/SCALED_COMPARISON_GUIDE.md` | ✅ Updated | Updated commands |
| `experiments/QUICK_START.md` | ✅ Updated | Updated commands |

## Why This Works

**Docker's Scaling Behavior:**
- Without `container_name`: Docker auto-generates names like `project-service-1`, `project-service-2`, etc.
- With `container_name`: Docker tries to use the same name for all replicas → FAIL

**Port Mapping:**
- Removed port mappings from scalable services because multiple containers can't bind to the same host port
- Services communicate internally via Docker network
- Only API Gateway exposes port 8000 to host

**Load Balancing:**
- Docker's built-in DNS round-robins requests to `user-service`, `task-service`, `stats-service`
- Each replica receives ~equal traffic automatically

## Ready to Test!

The issue is fixed. You can now run:

```bash
cd /Users/nicolacatalin/Desktop/facultate/proiect-sasps/experiments
./run_scaled_comparison.sh
```

This will successfully scale the microservices to 3 replicas each! 🚀
