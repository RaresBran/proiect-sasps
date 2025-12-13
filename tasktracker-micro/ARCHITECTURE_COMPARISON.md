# Architecture Comparison: Monolithic vs Microservices

This document provides a detailed comparison between the monolithic and microservices implementations of TaskTracker.

---

## Overview

| Aspect | Monolithic (`tasktracker-mono`) | Microservices (`tasktracker-micro`) |
|--------|--------------------------------|-------------------------------------|
| **Services** | 1 application | 4 services (Gateway + 3 microservices) |
| **Databases** | 1 PostgreSQL instance | 2 PostgreSQL instances |
| **Ports** | 1 (8000) | 5 (8000-8003 + 2 DB ports) |
| **Deployment** | Single container | 6 containers |
| **Code Organization** | Layered monolith | Service-oriented |

---

## Architecture Diagrams

### Monolithic Architecture

```
Client → FastAPI Application (Port 8000)
         ├── Routers (users, tasks, stats)
         ├── Services (AuthService, TaskService, StatsService)
         ├── Repositories (UserRepository, TaskRepository)
         └── PostgreSQL Database (Port 5432)
             ├── users table
             └── tasks table
```

### Microservices Architecture

```
Client → API Gateway (Port 8000)
         ├── User Service (Port 8001)
         │   └── User DB (Port 5433)
         │       └── users table
         ├── Task Service (Port 8002)
         │   └── Task DB (Port 5434)
         │       └── tasks table
         └── Stats Service (Port 8003)
             └── Calls Task Service
```

---

## Detailed Comparison

### 1. Code Structure

#### Monolithic
```
tasktracker-mono/
├── app/
│   ├── main.py                 # Single entry point
│   ├── core/                   # Shared configuration
│   ├── models/                 # All models together
│   │   ├── user.py
│   │   └── task.py
│   ├── services/               # All services together
│   │   ├── user_service.py
│   │   ├── task_service.py
│   │   └── stats_service.py
│   ├── repositories/           # All repositories together
│   ├── routers/                # All routers together
│   └── schemas/                # All schemas together
├── migrations/                 # Single migration folder
├── Dockerfile                  # Single Dockerfile
└── docker-compose.yml          # Single app + single DB
```

#### Microservices
```
tasktracker-micro/
├── api-gateway/                # Separate service
│   ├── app/
│   │   ├── main.py
│   │   └── core/
│   ├── Dockerfile
│   └── requirements.txt
├── user-service/               # Separate service
│   ├── app/
│   │   ├── main.py
│   │   ├── models/user.py
│   │   ├── services/user_service.py
│   │   └── ...
│   ├── migrations/
│   ├── Dockerfile
│   └── requirements.txt
├── task-service/               # Separate service
│   ├── app/
│   │   ├── main.py
│   │   ├── models/task.py
│   │   └── ...
│   ├── migrations/
│   ├── Dockerfile
│   └── requirements.txt
├── stats-service/              # Separate service
│   ├── app/
│   │   ├── main.py
│   │   └── ...
│   ├── Dockerfile
│   └── requirements.txt
└── docker-compose.yml          # All services + all DBs
```

---

### 2. Database Design

#### Monolithic

**Single Database**: `tasktracker_db`

```sql
-- Foreign key relationship
CREATE TABLE users (...);
CREATE TABLE tasks (
    ...
    owner_id INTEGER REFERENCES users(id) ON DELETE CASCADE
);
```

**Advantages**:
- ACID transactions across all tables
- Foreign key constraints enforced
- Joins are efficient
- Simple backup/restore

**Disadvantages**:
- Tight coupling
- Cannot scale independently
- Single point of failure
- Difficult to use different DB technologies

#### Microservices

**Database per Service**: `user_db` and `task_db`

```sql
-- User DB
CREATE TABLE users (...);

-- Task DB (separate database)
CREATE TABLE tasks (
    ...
    owner_id INTEGER  -- No foreign key, reference only
);
```

**Advantages**:
- Services are decoupled
- Can scale independently
- Technology freedom per service
- Fault isolation

**Disadvantages**:
- No foreign key constraints
- Distributed transactions needed
- Eventual consistency
- More complex queries

---

### 3. Service Communication

#### Monolithic

**In-Process Communication**:
```python
# In routers/stats.py
stats_service = StatsService(db)  # Direct instantiation
stats = stats_service.get_user_stats(user_id)
```

**Characteristics**:
- Function calls within the same process
- Fast (no network overhead)
- Shared database session
- Synchronous and reliable

#### Microservices

**HTTP-Based Communication**:
```python
# Stats Service calling Task Service
response = requests.get(
    f"{TASK_SERVICE_URL}/api/v1/tasks/",
    headers={"Authorization": f"Bearer {token}"}
)
```

**Characteristics**:
- Network calls between services
- Slower (network latency)
- Must handle failures
- Can be asynchronous

---

### 4. Authentication & Authorization

#### Monolithic

**Shared Security Context**:
```python
# All routers use the same dependency
def get_current_user(db: Session, token: str) -> User:
    # Decode token and query database
    return user
```

**Flow**:
1. User logs in → receives JWT
2. Subsequent requests include JWT
3. Dependencies decode JWT and query DB
4. User object passed to handlers

#### Microservices

**Distributed Authentication**:
```python
# Each service validates JWT independently
def get_current_user_id(token: str) -> int:
    # Decode token (no DB query)
    payload = decode_token(token)
    return int(payload["sub"])
```

**Flow**:
1. User logs in via User Service → receives JWT
2. Client sends JWT to API Gateway
3. Gateway forwards JWT to services
4. Each service validates JWT independently
5. User ID extracted from token

---

### 5. Deployment

#### Monolithic

**Single Deployment Unit**:
```yaml
docker-compose.yml:
  app:              # Single service
    ports: ["8000:8000"]
  db:               # Single database
    ports: ["5432:5432"]
```

**Deployment Steps**:
1. Build one Docker image
2. Run migrations
3. Start one container
4. Application ready

**Advantages**:
- Simple deployment
- Easy to test
- Single version to manage

**Disadvantages**:
- Must redeploy everything for any change
- Downtime during deployment
- Cannot scale components independently

#### Microservices

**Multiple Deployment Units**:
```yaml
docker-compose.yml:
  api-gateway:      # Service 1
    ports: ["8000:8000"]
  user-service:     # Service 2
    ports: ["8001:8001"]
  task-service:     # Service 3
    ports: ["8002:8002"]
  stats-service:    # Service 4
    ports: ["8003:8003"]
  user-db:          # Database 1
    ports: ["5433:5432"]
  task-db:          # Database 2
    ports: ["5434:5432"]
```

**Deployment Steps**:
1. Build 4 Docker images
2. Run migrations for 2 databases
3. Start services in order (databases → services → gateway)
4. Wait for health checks

**Advantages**:
- Deploy services independently
- Zero-downtime deployments possible
- Scale services independently
- Different teams can own services

**Disadvantages**:
- Complex orchestration
- Service versioning challenges
- Distributed system complexity

---

### 6. Scaling

#### Monolithic

**Vertical and Horizontal Scaling**:
```bash
# Scale entire application
docker compose up --scale app=3
```

**Characteristics**:
- Must scale the entire application
- All routes get more resources
- Database is still a bottleneck
- Simple load balancing

#### Microservices

**Independent Service Scaling**:
```bash
# Scale only the task service
docker compose up --scale task-service=5

# Scale only the stats service
docker compose up --scale stats-service=3
```

**Characteristics**:
- Scale services based on demand
- Task Service might need 10 instances
- Stats Service might need 2 instances
- Database scaling is independent
- More complex load balancing

---

### 7. Development Experience

#### Monolithic

**Advantages**:
- Single codebase to understand
- Easy to navigate and debug
- Shared utilities and models
- Simple local development setup
- IDE works well (go to definition, etc.)

**Disadvantages**:
- Large codebase over time
- Slow builds as app grows
- Git conflicts in shared files
- Tight coupling between features

#### Microservices

**Advantages**:
- Smaller, focused codebases
- Clear service boundaries
- Teams can work independently
- Technology freedom per service

**Disadvantages**:
- Must run multiple services locally
- Debugging across services is harder
- More complex local setup
- Testing interactions is complex
- Code duplication (auth logic, etc.)

---

### 8. Testing

#### Monolithic

**Test Structure**:
```python
# tests/integration/test_stats.py
def test_get_stats(client):
    # Test entire flow in one process
    user = create_user(client)
    token = login(client)
    create_task(client, token)
    stats = get_stats(client, token)
    assert stats["total_tasks"] == 1
```

**Advantages**:
- End-to-end tests are straightforward
- Fast test execution (no network)
- Easy to set up test database
- Can test transactions

#### Microservices

**Test Structure**:
```python
# Must test services individually or use contract testing
def test_stats_service(mock_task_service):
    # Mock task service responses
    with requests_mock.Mocker() as m:
        m.get('http://task-service/tasks/', json=mock_data)
        stats = get_stats()
```

**Advantages**:
- Services can be tested independently
- Unit tests are more focused
- Can mock service dependencies

**Disadvantages**:
- Integration testing is complex
- Need contract testing
- Must run multiple services for E2E tests
- Network issues in tests

---

### 9. Performance

#### Monolithic

**Latency**:
- Request → Processing → Response
- No network calls between components
- Single database connection

**Example**: Get statistics
1. Receive request (< 1ms)
2. Query database (10ms)
3. Calculate stats (< 1ms)
4. Return response (< 1ms)
**Total: ~12ms**

#### Microservices

**Latency**:
- Request → Gateway → Service → Other Services → Response
- Multiple network hops
- Multiple service processing

**Example**: Get statistics
1. Client → Gateway (1ms)
2. Gateway → Stats Service (1ms)
3. Stats → Task Service (1ms)
4. Task Service query DB (10ms)
5. Task Service → Stats (1ms)
6. Stats calculate (< 1ms)
7. Stats → Gateway (1ms)
8. Gateway → Client (1ms)
**Total: ~17ms** (42% slower)

---

### 10. Failure Handling

#### Monolithic

**Single Point of Failure**:
- If app crashes, everything is down
- Database failure affects everything
- Errors are easier to track (single log)

**Example**:
```
App crashes → All endpoints return 503
```

#### Microservices

**Fault Isolation**:
- If Task Service crashes, User Service still works
- Stats Service might degrade gracefully
- Requires circuit breakers and fallbacks

**Example**:
```
Task Service crashes:
  - User registration: ✅ Still works
  - Get tasks: ❌ Fails
  - Get stats: ⚠️ Returns cached/default data
```

---

## When to Use Which Architecture?

### Use Monolithic When:

✅ Small to medium-sized application  
✅ Team size < 10 developers  
✅ Rapid prototyping needed  
✅ Simple deployment requirements  
✅ All components scale together  
✅ Strong consistency is critical  
✅ Low latency is important  

### Use Microservices When:

✅ Large, complex application  
✅ Multiple teams working independently  
✅ Different components have different scaling needs  
✅ Need to use different technologies  
✅ Want independent deployments  
✅ Can handle eventual consistency  
✅ Have DevOps expertise  

---

## Migration Path

### Monolith → Microservices

1. **Identify Bounded Contexts**: User management, Task management, Statistics
2. **Extract Services**: Start with the least coupled service (Stats)
3. **Implement API Gateway**: Route requests to old and new services
4. **Migrate Data**: Create separate databases
5. **Update Clients**: Point to gateway instead of monolith
6. **Decommission Monolith**: Once all services are extracted

### Our Implementation

This project demonstrates both architectures so you can:
- Compare implementations side-by-side
- Understand trade-offs
- Choose the right approach for your needs
- See a realistic migration path

---

## Conclusion

**Neither architecture is inherently better**. The choice depends on:

- Team size and structure
- Application complexity
- Scaling requirements
- Deployment needs
- Consistency requirements
- Performance requirements
- DevOps maturity

The monolithic architecture (`tasktracker-mono`) is excellent for getting started and iterating quickly. The microservices architecture (`tasktracker-micro`) provides flexibility and scalability but comes with increased complexity.

Both implementations work with the same frontend, demonstrating that you can migrate between architectures as your needs evolve.

---

## Further Reading

- **Monolithic README**: `../tasktracker-mono/README.md`
- **Microservices README**: `../tasktracker-micro/README.md`
- **Setup Guide**: `../tasktracker-micro/SETUP_GUIDE.md`

Happy architecting! 🏗️

