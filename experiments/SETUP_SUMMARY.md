# Scaled Comparison Test - Setup Summary

## What We've Prepared

You now have a complete setup to compare **Monolith (1 instance)** vs **Scaled Microservices (3 replicas per service)**.

---

## Files Created

### 1. Automated Test Script
**File:** `experiments/run_scaled_comparison.sh` ✅ (executable)

**What it does:**
- Stops all existing Docker services
- Starts monolith (single instance)
- Starts microservices with 3 replicas per service
- Runs parameter sweep for both architectures
- Generates all comparison charts automatically

### 2. Comprehensive Guide
**File:** `experiments/SCALED_COMPARISON_GUIDE.md` ✅

**Contains:**
- How to run the test (automated & manual)
- What to expect in results
- How to interpret charts
- Presentation slide suggestions
- Troubleshooting tips

### 3. Updated Experiments README
**File:** `experiments/README.md` ✅ (updated)

**Added:**
- Quick start option for scaled comparison
- Instructions for scaling microservices manually
- Reference to new files

---

## How to Run

### Quick Start (Recommended)

```bash
cd /Users/nicolacatalin/Desktop/facultate/proiect-sasps/experiments
./run_scaled_comparison.sh
```

The script will:
1. Ask for confirmation
2. Stop existing services
3. Start both architectures
4. Run tests (5 concurrency levels × 2 architectures = ~20 minutes)
5. Generate plots automatically

**Results will be in:**
- `experiments/results/scaled_comparison_YYYYMMDD_HHMMSS/`
- `experiments/plots/YYYYMMDD_HHMMSS/`

---

## What You're Testing

### Before (Previous Test Results)

**Monolith (1 instance):**
- P95 Latency @ 200 users: **17 ms** ⭐
- Throughput @ 200 users: **75 req/s**
- Containers: **2** (app + db)

**Microservices (1 replica per service):**
- P95 Latency @ 200 users: **64 ms**
- Throughput @ 200 users: **73 req/s**
- Containers: **6** (gateway + 3 services + 2 dbs)

**Winner:** Monolith (better latency, similar throughput, fewer resources)

---

### After This Test

**Monolith (1 instance):**
- Same as before (baseline)

**Scaled Microservices (3 replicas per service):**
- P95 Latency @ 200 users: **? ms** (testing now)
- Throughput @ 200 users: **? req/s** (testing now)
- Containers: **12** (gateway + 9 services + 2 dbs)

**Expected:** Microservices should show better throughput at high loads

---

## Possible Outcomes

### Scenario A: Microservices Wins 🎉

```
Throughput @ 200 users:
  Monolith: 75 req/s
  Scaled Microservices: 120+ req/s ← 1.6x better!

Latency P95 @ 200 users:
  Monolith: 17 ms ← Still better
  Scaled Microservices: 40-50 ms

Presentation Takeaway:
"Microservices with horizontal scaling delivers 1.6x better 
throughput at peak load, making it ideal for high-traffic 
applications where throughput matters more than latency."
```

---

### Scenario B: Monolith Still Wins 🤔

```
Throughput @ 200 users:
  Monolith: 75 req/s ← Better
  Scaled Microservices: 80 req/s ← Marginal improvement

Latency P95 @ 200 users:
  Monolith: 17 ms ← 2x better
  Scaled Microservices: 35 ms

Presentation Takeaway:
"Even with 3 replicas per service (12 containers vs 2), 
microservices could not significantly outperform a single 
monolith instance. API Gateway remains a bottleneck."
```

---

### Scenario C: API Gateway Bottleneck 🔍

```
Throughput @ 200 users:
  Monolith: 75 req/s
  Scaled Microservices: 75 req/s ← No improvement

API Gateway CPU: 80-100% ← Bottleneck!
Service Replicas CPU: 10-30% each ← Underutilized

Presentation Takeaway:
"Scaling services didn't help because API Gateway became 
the bottleneck. This demonstrates the importance of 
identifying and scaling all components in the request path."
```

---

## Key Charts You'll Get

After the test completes, you'll have these charts in `experiments/plots/*/`:

1. **crossover_analysis.png** ⭐⭐⭐
   - Shows latency and throughput side-by-side
   - Reveals if/when microservices wins

2. **latency_p95_vs_concurrency.png** ⭐⭐⭐
   - Shows latency comparison across all loads
   - Key for "monolith is 2x faster" claim

3. **throughput_vs_concurrency.png** ⭐⭐⭐
   - Shows if scaling improved throughput
   - Key for "microservices wins at scale" claim

4. **efficiency_vs_concurrency.png** ⭐⭐
   - Shows RPS per CPU unit
   - Key for cost analysis

5. **cpu_vs_concurrency.png** ⭐
   - Shows total CPU usage
   - Helps identify bottlenecks

6. **memory_vs_concurrency.png** ⭐
   - Shows total memory usage
   - Helps with cost estimation

---

## Expected Test Duration

**Total time:** ~25-30 minutes

Breakdown:
- Service startup: 2-3 minutes
- Monolith tests (5 levels): 8-10 minutes
- Microservices tests (5 levels): 8-10 minutes
- Plot generation: 1-2 minutes

**Concurrency levels tested:** 10, 25, 50, 100, 200 users
**Duration per level:** 60 seconds + 10s warmup

---

## After the Test

### Step 1: Review the Charts

```bash
# Open plots folder
open experiments/plots/$(ls -t experiments/plots/ | head -1)
```

Look at:
- `crossover_analysis.png` - Main comparison
- `latency_p95_vs_concurrency.png` - Latency trends
- `throughput_vs_concurrency.png` - Throughput trends

### Step 2: Extract Key Numbers

```bash
cd experiments/results/scaled_comparison_*/

# View throughput results
cat results.jsonl | jq -r '[.arch, .concurrency, .throughput_rps] | @tsv'

# View latency results
cat results.jsonl | jq -r '[.arch, .concurrency, .latency_p95_ms] | @tsv'

# View efficiency
cat results.jsonl | jq -r '[.arch, .concurrency, .resources.rps_per_cpu_unit] | @tsv'
```

### Step 3: Update Presentation README

Add the scaled comparison results to `experiments/PRESENTATION_README.md`:
- Update the executive summary
- Add new data tables
- Add interpretation of scaling results

### Step 4: Create Summary Slide

**Slide Title:** "Scaling Analysis: When Does It Matter?"

**Content:**
```
Single-Instance Comparison:
  Latency: Monolith wins (2x better)
  Throughput: Tie (within 3%)

Scaled Comparison (3 replicas):
  Latency: Monolith still wins (? vs ?)
  Throughput: ? (Does scaling help?)
  
Conclusion: [Based on your results]
```

---

## Troubleshooting

### If services won't start:

```bash
# Check if ports are in use
lsof -i :8000,9000

# Kill existing containers
docker compose -f tasktracker-mono/docker-compose.yml down
docker compose -f tasktracker-micro/docker-compose.yml down

# Try again
./run_scaled_comparison.sh
```

### If tests fail:

```bash
# Check service health
curl http://localhost:9000/health  # Monolith
curl http://localhost:8000/health  # Microservices

# View container status
docker ps
```

### If you need to stop early:

```bash
# Press Ctrl+C to stop the test

# Clean up services
cd tasktracker-mono && docker compose down
cd tasktracker-micro && docker compose down
```

---

## Next Steps

1. **Run the test:**
   ```bash
   cd experiments
   ./run_scaled_comparison.sh
   ```

2. **Review results:**
   - Check plots in `experiments/plots/*/`
   - Read `SCALED_COMPARISON_GUIDE.md` for interpretation

3. **Update presentation:**
   - Add scaled comparison data
   - Create conclusion slides
   - Prepare Q&A responses

4. **(Optional) Test higher loads:**
   ```bash
   python experiments/run_sweep.py \
       --arch both \
       --concurrency-levels 200,400,800 \
       --duration-seconds 90
   ```

---

## Files Reference

```
experiments/
├── run_scaled_comparison.sh      ← Run this to start test
├── SCALED_COMPARISON_GUIDE.md    ← Read this for interpretation
├── PRESENTATION_README.md        ← Update this with new results
├── README.md                     ← Main experiments documentation
│
├── results/
│   └── scaled_comparison_*/      ← Results will be here
│       ├── config.json
│       ├── results.jsonl
│       └── run_*/
│
└── plots/
    └── YYYYMMDD_HHMMSS/          ← Plots will be here
        ├── crossover_analysis.png
        ├── latency_p95_vs_concurrency.png
        ├── throughput_vs_concurrency.png
        └── ...
```

---

## Ready to Run?

Everything is set up! Just execute:

```bash
cd /Users/nicolacatalin/Desktop/facultate/proiect-sasps/experiments
./run_scaled_comparison.sh
```

The script will guide you through the entire process and generate all the charts you need for your presentation.

**Good luck!** 🚀
