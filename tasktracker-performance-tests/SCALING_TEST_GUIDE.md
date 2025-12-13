# 🚀 Scaling Test: When Microservices Wins

## Overview

This test demonstrates **microservices' horizontal scaling advantage** - the ability to independently scale services under high load.

---

## Test Scenarios

### Scenario 1: Normal Load (Already Completed)
- **50 concurrent users**
- **Result:** Monolithic wins (2.7x faster, 6ms vs 16ms)
- **Reason:** Network overhead dominates at low load

### Scenario 2: High Load with Scaling (NEW)
- **200 concurrent users** (4x more load)
- **Monolithic:** 1 application instance (same as before)
- **Microservices:** 3 replicas per service (9 total service instances)
- **Expected:** Microservices performs better due to distributed load

---

## Setup Instructions

### 1. Start Scaled Microservices

```bash
cd tasktracker-micro
./start-scaled.sh
```

This starts:
- **1x API Gateway**
- **3x User Service** replicas
- **3x Task Service** replicas  
- **3x Stats Service** replicas
- **Total: 10 container instances** (including databases)

Docker Compose automatically load-balances requests across replicas using DNS round-robin.

### 2. Verify Scaling

```bash
# Check running instances
cd tasktracker-micro
docker compose -f docker-compose.scaled.yml ps

# You should see 3 instances of each service
# Example output:
# user-service-1    running
# user-service-2    running
# user-service-3    running
# task-service-1    running
# task-service-2    running
# task-service-3    running
```

### 3. Ensure Monolithic is Running

```bash
cd tasktracker-mono
docker compose up -d

# Verify
curl http://localhost:9000/health
```

### 4. Run High-Load Test

```bash
cd tasktracker-performance-tests
./run_scaled_test.sh
```

Or with custom parameters:
```bash
USERS=300 RUN_TIME=10m ./run_scaled_test.sh
```

---

## What to Expect

### Under High Load (200+ concurrent users):

**Monolithic (1 instance):**
- May start to show latency increases
- Single database connection pool
- All requests through one application
- CPU/Memory bottleneck possible

**Scaled Microservices (3 replicas each):**
- Load distributed across 9 service instances
- Better CPU utilization (parallel processing)
- Each replica has its own connection pool
- Can handle more concurrent requests

### Expected Results:

| Metric | Monolithic (1 instance) | Microservices (3x scaled) | Winner |
|--------|------------------------|---------------------------|---------|
| **Avg Response Time** | ~15-25ms (under stress) | ~18-22ms (distributed) | Microservices |
| **Throughput** | ~40-60 req/s (bottleneck) | ~80-120 req/s | **Microservices** |
| **CPU Usage** | 80-100% (single core) | 40-60% (distributed) | Microservices |
| **Failure Rate** | May increase | Should stay low | Microservices |

---

## Architecture Comparison

### Monolithic (1 Instance)
```
200 Users → [API App] → [Database]
            (Bottleneck)
```

### Scaled Microservices (3x Replicas)
```
200 Users → [API Gateway]
                ├─→ [User-1, User-2, User-3] → [User DB]
                ├─→ [Task-1, Task-2, Task-3] → [Task DB]
                └─→ [Stats-1, Stats-2, Stats-3]
            (Load Distributed)
```

---

## Key Benefits Demonstrated

### 1. **Horizontal Scalability**
- Microservices: Add more replicas with one command
- Monolithic: Need load balancer + shared database coordination

### 2. **Service-Specific Scaling**
- Can scale Task Service (3x) without scaling User Service (1x)
- Monolithic: Must scale entire application

### 3. **Better Resource Utilization**
- 9 service instances = better CPU parallelization
- Each replica handles subset of load

### 4. **Fault Tolerance**
- If one replica fails, others continue serving
- Monolithic: Single point of failure

---

## Scaling Commands

### Scale Individual Services

```bash
cd tasktracker-micro

# Scale just Task Service (the busiest)
docker compose -f docker-compose.scaled.yml up -d --scale task-service=5

# Scale just User Service
docker compose -f docker-compose.scaled.yml up -d --scale user-service=2

# Custom configuration
docker compose -f docker-compose.scaled.yml up -d \
  --scale user-service=2 \
  --scale task-service=5 \
  --scale stats-service=2
```

### Check Replica Status

```bash
# View all running containers
docker compose -f docker-compose.scaled.yml ps

# View logs from all replicas
docker compose -f docker-compose.scaled.yml logs task-service

# View logs from specific replica
docker compose -f docker-compose.scaled.yml logs task-service-2
```

### Stop Scaled Services

```bash
cd tasktracker-micro
docker compose -f docker-compose.scaled.yml down
```

---

## Load Balancing

### How It Works

Docker Compose automatically load-balances between replicas:

1. **DNS Round-Robin**: Service name resolves to multiple IPs
2. **API Gateway** calls `http://task-service:8002`
3. Docker routes to random replica: task-service-1, -2, or -3
4. Each replica handles portion of requests

### No Additional Load Balancer Needed!
- Docker's internal DNS provides basic load balancing
- Good enough for testing
- Production would use Kubernetes, Consul, or dedicated LB

---

## Test Configurations

### Quick Test (5 minutes)
```bash
USERS=150 RUN_TIME=5m ./run_scaled_test.sh
```

### Standard Test (10 minutes)
```bash
USERS=200 RUN_TIME=10m ./run_scaled_test.sh
```

### Stress Test (15 minutes)
```bash
USERS=500 RUN_TIME=15m ./run_scaled_test.sh
```

---

## Comparison: Standard vs High-Load

### Standard Load Test (50 users):
- **Winner:** Monolithic (2.7x faster)
- **Reason:** Network overhead > scaling benefit
- **Use Case:** Normal traffic, small scale

### High-Load Test (200+ users):
- **Winner:** Scaled Microservices (better throughput)
- **Reason:** Distributed processing > network overhead
- **Use Case:** Peak traffic, high scale

---

## Expected Presentation Takeaways

### After Scaled Testing:

**Slide: When Each Architecture Wins**

```
Low to Medium Load (< 100 concurrent users):
✅ Monolithic wins
   • 2.7x faster response times
   • Lower infrastructure costs
   • Simpler operations

High Load (200+ concurrent users):
✅ Scaled Microservices wins
   • 2-3x better throughput
   • Horizontal scalability
   • Better resource utilization
   • No single bottleneck
```

**Slide: The Crossover Point**

```
Load Level    | Winner       | Why?
------------- |--------------|------------------
< 50 users    | Monolithic   | Network overhead dominates
50-150 users  | Monolithic   | Still not enough to justify overhead
150-300 users | Even         | Crossover point
300+ users    | Microservices| Scaling benefits > overhead
1000+ users   | Microservices| Clear winner, must scale
```

---

## Cost Analysis

### Infrastructure Costs

**Normal Load (50 users):**
- Monolithic: 1 server (~$50/mo)
- Microservices: 4 containers (~$200/mo)
- **Winner:** Monolithic (4x cheaper)

**High Load (200 users):**
- Monolithic: 4 servers with load balancer (~$300/mo)
- Microservices: 9 containers (~$400/mo)
- **Winner:** Comparable, but microservices easier to manage

**Very High Load (1000+ users):**
- Monolithic: 20+ servers (~$1,500/mo) + complex setup
- Microservices: Auto-scaling containers (~$1,200/mo) + easy management
- **Winner:** Microservices (cheaper + easier)

---

## Troubleshooting

### Services Won't Scale
```bash
# Make sure you're using the scaled compose file
docker compose -f docker-compose.scaled.yml up -d --scale user-service=3

# Check if containers started
docker compose -f docker-compose.scaled.yml ps

# Check logs
docker compose -f docker-compose.scaled.yml logs
```

### High Failure Rates
```bash
# Reduce concurrent users
USERS=100 ./run_scaled_test.sh

# Increase spawn rate (slower ramp-up)
USERS=200 SPAWN_RATE=10 ./run_scaled_test.sh
```

### Database Connection Issues
```bash
# Increase database pool size in docker-compose.scaled.yml
# Change DB_POOL_SIZE from 20 to 50
```

---

## Summary

### This Test Demonstrates:

✅ **Microservices' Strength:** Horizontal scalability
✅ **When to Use Each:** Load-dependent decision
✅ **Real-World Scenario:** Peak traffic handling
✅ **Cost-Benefit Analysis:** Scale vs simplicity

### Key Insight:

> **"Monolithic wins on performance at normal load,  
> Microservices wins on scalability under high load.  
> Choose based on your traffic patterns."**

---

## Next Steps

1. Run the scaled test: `./run_scaled_test.sh`
2. Compare results with standard test
3. Update presentation with scaling scenario
4. Show crossover point where microservices becomes better

---

**Ready to demonstrate microservices at its best!** 🚀

