# Scaled Comparison Guide

**Monolith (1 instance) vs Scaled Microservices (3 replicas per service)**

---

## Overview

This experiment compares:
- **Monolith:** Single application instance + single database
- **Scaled Microservices:** 3 replicas each of user-service, task-service, and stats-service + 2 databases + 1 API gateway

The goal is to demonstrate when horizontal scaling gives microservices an advantage.

---

## Running the Test

### Quick Run (Automated)

```bash
cd experiments
./run_scaled_comparison.sh
```

This will:
1. Stop all existing services
2. Start monolith (single instance)
3. Start microservices with 3 replicas per service
4. Run parameter sweep (10, 25, 50, 100, 200 users)
5. Generate all comparison charts

**Duration:** ~20-30 minutes total

---

### Manual Run

**Step 1: Start Monolith**
```bash
cd tasktracker-mono
docker compose up -d
```

**Step 2: Start Scaled Microservices**
```bash
cd tasktracker-micro
docker compose -f docker-compose.scalable.yml up -d --scale user-service=3 --scale task-service=3 --scale stats-service=3
```

**Step 3: Verify Services**
```bash
# Check monolith
curl http://localhost:9000/health

# Check microservices
curl http://localhost:8000/health

# View running containers
docker ps --format "table {{.Names}}\t{{.Status}}"
```

**Step 4: Run Sweep**
```bash
cd experiments
python run_sweep.py --arch both --concurrency-levels 10,25,50,100,200
```

**Step 5: Generate Plots**
```bash
python plot_results.py experiments/results/scaled_comparison_YYYYMMDD_HHMMSS
```

---

## Expected Results

### Hypothesis

With horizontal scaling (3 replicas), microservices should:
- ✅ **Match or beat monolith throughput** at high loads (200+ users)
- ✅ **Show better resource distribution** (load spread across 9+ containers)
- ✅ **Maintain acceptable latency** (close gap with monolith)
- ⚠️ **Still have network overhead** (gateway remains a bottleneck?)

### Key Metrics to Compare

| Metric | Monolith (1 instance) | Microservices (3 replicas) | Winner? |
|--------|----------------------|----------------------------|---------|
| **P95 Latency @ 200 users** | ? | ? | TBD |
| **Throughput @ 200 users** | ? | ? | TBD |
| **CPU Efficiency** | ? | ? | TBD |
| **Memory Usage** | ? | ? | TBD |
| **Error Rate** | 0% | 0% | Tie |

---

## What to Look For in Results

### 1. Crossover Analysis Chart

**File:** `experiments/plots/*/crossover_analysis.png`

**Look for:**
- Does microservices throughput exceed monolith at high loads?
- At what concurrency level does crossover occur (if any)?
- Does latency gap narrow at high loads?

**Possible Outcomes:**

**Scenario A: Microservices Wins at Scale**
```
Throughput @ 200 users:
  Monolith: 75 req/s
  Microservices: 120 req/s  ← Winner!

Latency P95 @ 200 users:
  Monolith: 17 ms  ← Still better
  Microservices: 35 ms

Conclusion: Microservices throughput advantage offsets latency penalty
```

**Scenario B: No Clear Winner**
```
Throughput @ 200 users:
  Monolith: 75 req/s
  Microservices: 80 req/s  ← Marginal improvement

Latency P95 @ 200 users:
  Monolith: 17 ms  ← Still 2x better
  Microservices: 35 ms

Conclusion: Scaling helps but API Gateway remains bottleneck
```

**Scenario C: Monolith Still Wins**
```
Throughput @ 200 users:
  Monolith: 75 req/s  ← Winner
  Microservices: 73 req/s

Latency P95 @ 200 users:
  Monolith: 17 ms  ← Winner
  Microservices: 40 ms

Conclusion: Single monolith instance sufficient; scaling doesn't help
```

---

### 2. Resource Distribution

**Files:**
- `cpu_vs_concurrency.png`
- `memory_vs_concurrency.png`
- `efficiency_vs_concurrency.png`

**Key Questions:**

1. **Is API Gateway still the bottleneck?**
   - Look at per-container CPU usage in detailed results
   - If API Gateway CPU > 50%, it's limiting scale-out benefits

2. **Are replicas load-balanced evenly?**
   - Check if all 3 replicas show similar CPU usage
   - Uneven distribution indicates load balancing issues

3. **Total resource usage:**
   - Monolith: 1 app + 1 DB = 2 containers
   - Scaled Microservices: 9 services + 2 DBs + 1 gateway = 12 containers
   - Expected: ~4-6x more resources used by microservices

4. **Efficiency metrics:**
   - **RPS per CPU unit** - Which architecture delivers more throughput per vCPU?
   - **RPS per GB memory** - Which is more memory-efficient?

---

### 3. Latency Under Load

**File:** `latency_p95_vs_concurrency.png`

**Key Insight:**

With scaled microservices, we expect:
- Better performance at **high loads** (100-200 users)
- Still worse than monolith due to **network overhead**
- Gap should **narrow** compared to single-replica microservices

**Compare:**
```
Single Replica Microservices (from previous test):
  10 users: 35 ms
  200 users: 64 ms

Scaled Microservices (3 replicas):
  10 users: ? ms (probably similar, ~30-40ms)
  200 users: ? ms (should improve, maybe 40-50ms?)

Monolith:
  10 users: 22 ms
  200 users: 17 ms  ← Benchmark to beat
```

---

### 4. Throughput Scaling

**File:** `throughput_vs_concurrency.png`

**Key Question:** Does microservices throughput scale linearly with replicas?

**Expected Behavior:**
```
Theory:
  1 replica: 40 req/s @ 100 users
  3 replicas: 120 req/s @ 100 users (3x improvement)

Reality:
  3 replicas: 80-100 req/s @ 100 users (2-2.5x improvement)

Why not 3x?
  - API Gateway becomes bottleneck
  - Network overhead increases
  - Database contention (still only 2 DBs)
```

---

## Presentation Talking Points

### If Microservices Wins at High Load:

**Slide Title:** "Horizontal Scaling: When Microservices Shines"

**Key Points:**
- ✅ Microservices throughput **exceeded monolith** at 200 users
- ✅ Load distributed across **3 replicas per service** (9 service instances total)
- ⚠️ Latency still **2x higher** than monolith (network overhead remains)
- 💰 **Cost trade-off:** 6x more containers for 1.5-2x throughput gain

**Quote:**
> "At 200 concurrent users, scaled microservices delivered 1.6x better throughput than single-instance monolith, demonstrating horizontal scaling benefits. However, latency remained 2x higher due to network overhead."

---

### If Monolith Maintains Advantage:

**Slide Title:** "Monolith Resilience: Efficient Even Without Scaling"

**Key Points:**
- ✅ Single monolith instance **matched 3-replica microservices** throughput
- ✅ **2x better latency** maintained across all loads
- ✅ **6x fewer containers** needed (lower operational complexity)
- 🤔 Monolith not yet CPU/memory-bound (vertical scaling headroom remains)

**Quote:**
> "Even with 3 replicas per service, scaled microservices could not outperform a single monolith instance, which handled 200 users with 17ms P95 latency using just 2 containers."

---

### If Results Are Mixed:

**Slide Title:** "Architecture Trade-offs: No Clear Winner"

**Key Points:**
- ⚖️ Microservices **slight throughput edge** at high loads (+10-20%)
- ⚖️ Monolith maintains **2x latency advantage**
- ⚖️ Microservices uses **6x more resources** for marginal gains
- 📊 Decision depends on: latency SLAs, cost constraints, team size

**Quote:**
> "Scaled microservices showed 15% better throughput at peak load but required 6x more containers and maintained 2x higher latency. The choice depends on whether throughput or latency is the critical metric."

---

## Detailed Analysis Checklist

After running the test, analyze these aspects:

### Performance Analysis

- [ ] **Throughput crossover point identified?**
  - At what concurrency level (if any) does microservices exceed monolith?
  
- [ ] **Latency gap quantified?**
  - What is the P95 latency difference at 200 users?
  
- [ ] **Error rates compared?**
  - Both should be 0% under normal conditions

### Resource Analysis

- [ ] **Total CPU usage compared**
  - Monolith: Expected ~10-30% for 2 containers
  - Microservices: Expected ~40-100% across 12 containers
  
- [ ] **API Gateway bottleneck identified?**
  - Check if gateway CPU > 50% (indicates bottleneck)
  
- [ ] **Load balancing verified?**
  - Are all 3 replicas receiving equal load?
  
- [ ] **Efficiency metrics computed**
  - RPS per CPU unit
  - RPS per GB memory

### Cost Analysis

- [ ] **Container count:** Monolith (2) vs Microservices (12) = 6x
- [ ] **Memory footprint:** Total GB used by each architecture
- [ ] **CPU utilization:** Average % across all containers
- [ ] **Cost per request:** Computed based on resource usage

---

## Common Issues and Solutions

### Issue 1: API Gateway Bottleneck

**Symptom:** Gateway CPU at 80-100%, services at 10-20%

**Solution:** Scale API Gateway horizontally too
```bash
docker compose up -d --scale api-gateway=3 --scale user-service=3 ...
```

---

### Issue 2: Database Contention

**Symptom:** DB CPU high, services waiting on queries

**Solution:** 
- Increase DB connection pool size
- Add read replicas
- Implement caching

---

### Issue 3: Uneven Load Distribution

**Symptom:** One replica at 80% CPU, others at 20%

**Solution:**
- Check Docker load balancing (should be round-robin by default)
- Verify healthchecks are passing on all replicas
- Check for session affinity issues

---

### Issue 4: No Performance Gain from Scaling

**Symptom:** 3 replicas perform same as 1 replica

**Possible Causes:**
1. **API Gateway is bottleneck** (most likely)
2. **Database is bottleneck** (check DB CPU)
3. **Load balancer not working** (all requests go to one replica)
4. **Test load too low** (need 500+ users to see benefit)

---

## Next Steps After Results

### If Microservices Wins:

1. **Document the crossover point**
   - "Microservices recommended for > 150 concurrent users"

2. **Calculate cost implications**
   - Cost per request for each architecture
   - Break-even analysis

3. **Test higher loads**
   - Run with 400, 800 users
   - Find the upper scaling limit

### If Monolith Wins:

1. **Test monolith horizontal scaling**
   - Deploy 3 monolith instances with load balancer
   - Compare: 3 monoliths vs 3-replica microservices

2. **Identify monolith scaling limit**
   - At what load does single monolith saturate?
   - Test 400, 800, 1600 users

3. **Explore monolith optimizations**
   - Connection pooling tuning
   - Query optimization
   - Caching strategies

---

## Presentation Slide Suggestions

### Slide 1: Scaled Architecture Comparison

**Title:** "Horizontal Scaling: Monolith vs Microservices"

**Content:**
- Architecture diagrams side-by-side
- Container count: 2 vs 12
- Resource allocation shown visually

---

### Slide 2: Throughput Comparison

**Title:** "Throughput Under Load"

**Screenshot:** `throughput_vs_concurrency.png`

**Table:**
| Users | Monolith (1×) | Microservices (3×) | Winner |
|-------|---------------|-------------------|--------|
| 10    | ? req/s       | ? req/s           | ?      |
| 50    | ? req/s       | ? req/s           | ?      |
| 100   | ? req/s       | ? req/s           | ?      |
| 200   | ? req/s       | ? req/s           | ?      |

---

### Slide 3: Latency Comparison

**Title:** "Latency Performance (P95)"

**Screenshot:** `latency_p95_vs_concurrency.png`

**Highlight:**
- Monolith maintains low latency
- Microservices gap narrows at scale (or doesn't)
- Network overhead quantified

---

### Slide 4: Resource Efficiency

**Title:** "Cost per Request Analysis"

**Screenshot:** `efficiency_vs_concurrency.png`

**Key Metrics:**
- RPS per CPU unit
- RPS per GB memory
- Total containers needed
- Estimated cloud cost

---

### Slide 5: The Verdict

**Title:** "When to Choose Each Architecture"

**If Microservices Wins:**
```
Choose Microservices When:
✅ Concurrent users > 150
✅ Throughput > latency priority
✅ Need independent scaling
✅ Can afford 6x resource cost

Choose Monolith When:
✅ Concurrent users < 150
✅ Latency is critical (< 25ms SLA)
✅ Cost-conscious deployment
✅ Small team
```

**If Monolith Wins:**
```
Choose Monolith When:
✅ Any load tested (< 200 users)
✅ Latency is critical
✅ Resource efficiency matters
✅ Simple deployment preferred

Choose Microservices When:
✅ Fault tolerance > performance
✅ Large team (independent deployments)
✅ Different tech stacks needed
✅ Accept 2x latency penalty
```

---

## Data Files Reference

After running the test, you'll find:

**Results:**
```
experiments/results/scaled_comparison_YYYYMMDD_HHMMSS/
├── config.json                 # Test configuration
├── results.jsonl              # All results (line-delimited)
├── all_results.json           # All results (JSON array)
└── run_NNN_*/                 # Per-run directories
    ├── results.json           # Detailed metrics
    └── stats_stats.csv        # Locust data
```

**Plots:**
```
experiments/plots/YYYYMMDD_HHMMSS/
├── crossover_analysis.png          # Main comparison
├── latency_p95_vs_concurrency.png  # Latency trends
├── throughput_vs_concurrency.png   # Throughput trends
├── efficiency_vs_concurrency.png   # Cost efficiency
├── cpu_vs_concurrency.png          # CPU usage
└── memory_vs_concurrency.png       # Memory usage
```

---

## Quick Data Extraction

```bash
# View throughput results
cd experiments/results/scaled_comparison_*/
cat results.jsonl | jq -r '[.arch, .concurrency, .throughput_rps] | @tsv'

# View latency results
cat results.jsonl | jq -r '[.arch, .concurrency, .latency_p95_ms] | @tsv'

# View resource efficiency
cat results.jsonl | jq -r '[.arch, .concurrency, .resources.rps_per_cpu_unit] | @tsv'

# Find the crossover point (if any)
cat results.jsonl | jq -r 'select(.arch == "microservices") | [.concurrency, .throughput_rps] | @tsv' > micro.txt
cat results.jsonl | jq -r 'select(.arch == "monolith") | [.concurrency, .throughput_rps] | @tsv' > mono.txt
paste mono.txt micro.txt
```

---

**Good luck with your scaled comparison test!** 🚀

The results will provide definitive answers about when horizontal scaling matters.
