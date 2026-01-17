# ✅ READY TO RUN: Scaled Comparison Test

## Summary

I've set up everything you need to compare **Monolith (1 instance)** vs **Scaled Microservices (3 replicas per service)**.

---

## What's Been Created

### 1. Automated Test Script ✅
**File:** `experiments/run_scaled_comparison.sh` (executable)

This script will:
- Stop any existing services
- Start monolith (1 app + 1 db = 2 containers)
- Start scaled microservices (3 replicas × 3 services + gateway + 2 dbs = 12 containers)
- Run parameter sweep across 5 load levels (10, 25, 50, 100, 200 users)
- Generate all comparison charts automatically

### 2. Documentation Created ✅

| File | Purpose |
|------|---------|
| `experiments/SETUP_SUMMARY.md` | Complete setup overview and expected outcomes |
| `experiments/SCALED_COMPARISON_GUIDE.md` | Detailed guide for interpreting results |
| `experiments/QUICK_START.md` | Quick reference card (1 page) |
| `experiments/README.md` | Updated with scaled comparison instructions |

### 3. Existing Infrastructure (Already Works) ✅

- `experiments/run_sweep.py` - Parameter sweep runner
- `experiments/plot_results.py` - Chart generator
- `experiments/lib/` - Docker metrics, load test runner, I/O utils

---

## How to Run (One Command)

```bash
cd /Users/nicolacatalin/Desktop/facultate/proiect-sasps/experiments
./run_scaled_comparison.sh
```

**That's it!** The script handles everything.

---

## What You'll Get

After ~25 minutes, you'll have:

### Data Files
```
experiments/results/scaled_comparison_YYYYMMDD_HHMMSS/
├── config.json          # Test configuration
├── results.jsonl       # All results (easily parseable)
├── all_results.json    # All results (JSON array)
└── run_*/              # Per-run detailed data
```

### Charts (Ready for Presentation)
```
experiments/plots/YYYYMMDD_HHMMSS/
├── crossover_analysis.png          ⭐ Main comparison slide
├── latency_p95_vs_concurrency.png  ⭐ Shows latency advantage
├── throughput_vs_concurrency.png   ⭐ Shows if scaling helped
├── efficiency_vs_concurrency.png   ⭐ Cost analysis
├── cpu_vs_concurrency.png
├── memory_vs_concurrency.png
└── error_rate_vs_concurrency.png
```

---

## What This Test Will Answer

### Key Questions

1. **Does horizontal scaling help microservices beat monolith?**
   - Previous test: Monolith won (1 replica microservices = 73 req/s @ 200 users)
   - This test: Will 3 replicas improve to 120+ req/s?

2. **At what load does microservices win (if any)?**
   - Looking for crossover point in throughput

3. **Does scaling reduce the latency gap?**
   - Previous: Monolith 17ms vs Microservices 64ms (3.8x worse)
   - This test: Will scaling improve microservices latency?

4. **What's the resource cost?**
   - Monolith: 2 containers
   - Scaled Microservices: 12 containers
   - Is 6x resource cost justified by performance?

---

## Previous Results (Baseline)

From your earlier test (`experiments/results/sweep_20260117_210725/`):

| Users | Mono Throughput | Micro Throughput | Mono P95 | Micro P95 | Winner |
|-------|----------------|------------------|----------|-----------|--------|
| 10 | 4.53 req/s | 4.26 req/s | 22 ms | 35 ms | Mono |
| 50 | 21.45 req/s | 20.96 req/s | 21 ms | 41 ms | Mono |
| 100 | 40.39 req/s | 39.83 req/s | 20 ms | 44 ms | Mono |
| 200 | 75.14 req/s | 73.03 req/s | 17 ms | 64 ms | **Mono** |

**Conclusion:** Monolith dominated in latency (2-4x better), throughput was tied

---

## Expected Results (Hypothesis)

With 3 replicas, microservices should:

**Optimistic Scenario:**
- Throughput @ 200 users: **120-150 req/s** (2x improvement) ✅ Beats monolith!
- Latency @ 200 users: **35-40 ms** (P95) - Still worse than monolith's 17ms

**Realistic Scenario:**
- Throughput @ 200 users: **90-100 req/s** (1.3x improvement) - Marginal win
- Latency @ 200 users: **45-50 ms** (P95) - Still 2-3x worse

**Pessimistic Scenario (API Gateway Bottleneck):**
- Throughput @ 200 users: **75-80 req/s** (no improvement) ❌
- Latency @ 200 users: **50-60 ms** (P95) - Worse than before!
- Root cause: API Gateway at 100% CPU, services underutilized

---

## Presentation Value

### If Microservices Wins:

**Key Message:**
> "With horizontal scaling, microservices achieved 1.6x better throughput than monolith at peak load, demonstrating the value of distributed architecture at scale."

**Charts to Show:**
- `throughput_vs_concurrency.png` - Shows microservices crossing over
- `crossover_analysis.png` - Shows the crossover point clearly

### If Monolith Still Wins:

**Key Message:**
> "Even with 3 replicas (12 containers vs 2), microservices could not outperform a single monolith instance, highlighting the efficiency of simpler architectures."

**Charts to Show:**
- `crossover_analysis.png` - Shows monolith maintaining advantage
- `efficiency_vs_concurrency.png` - Shows monolith is more resource-efficient

### Either Way, You Have a Story! 📊

---

## After the Test

1. **Review the charts**
   ```bash
   open experiments/plots/$(ls -t experiments/plots/ | head -1)
   ```

2. **Extract key numbers**
   ```bash
   cd experiments/results/scaled_comparison_*/
   cat results.jsonl | jq -r '[.arch, .concurrency, .throughput_rps, .latency_p95_ms] | @tsv'
   ```

3. **Update presentation**
   - Add scaled comparison section to `experiments/PRESENTATION_README.md`
   - Create conclusion slides
   - Prepare for Q&A

4. **(Optional) Compare with previous results**
   ```bash
   # Previous (single replica)
   cat experiments/results/sweep_20260117_210725/results.jsonl | \
     jq -r 'select(.arch=="microservices") | [.concurrency, .throughput_rps] | @tsv'
   
   # New (scaled 3 replicas)
   cat experiments/results/scaled_comparison_*/results.jsonl | \
     jq -r 'select(.arch=="microservices") | [.concurrency, .throughput_rps] | @tsv'
   ```

---

## Troubleshooting

### Services Won't Start
```bash
# Stop everything
cd tasktracker-mono && docker compose down
cd tasktracker-micro && docker compose down

# Check if ports are free
lsof -i :8000,9000

# Try again
cd experiments && ./run_scaled_comparison.sh
```

### Test Fails Mid-Run
```bash
# Check container status
docker ps

# Check logs
docker logs tasktracker_api_gateway
docker logs tasktracker_task_service
```

### Need to Stop Early
```bash
# Press Ctrl+C, then:
cd tasktracker-mono && docker compose down
cd tasktracker-micro && docker compose down
```

---

## Files Overview

```
experiments/
├── run_scaled_comparison.sh      ⭐ RUN THIS
├── SETUP_SUMMARY.md              📚 What's been set up
├── SCALED_COMPARISON_GUIDE.md    📚 How to interpret results
├── QUICK_START.md                📚 Quick reference
├── PRESENTATION_README.md        📚 Presentation guide (existing)
├── README.md                     📚 Main documentation
│
├── run_sweep.py                  🔧 Parameter sweep runner
├── plot_results.py               🔧 Chart generator
├── run_failure_injection.py      🔧 Failure test (already done)
├── plot_failure_results.py       🔧 Failure charts (already done)
│
├── lib/                          📦 Shared utilities
│   ├── docker_metrics.py
│   ├── loadtest_runner.py
│   └── io_utils.py
│
├── results/                      📊 Test outputs (gitignored)
│   ├── sweep_20260117_210725/    ← Previous test (baseline)
│   ├── failure_20260117_212704/  ← Failure test (done)
│   └── scaled_comparison_*/      ← New test (will be created)
│
└── plots/                        📈 Generated charts (gitignored)
    ├── 20260117_212028/          ← Previous charts (baseline)
    ├── failure_20260117_212856/  ← Failure charts (done)
    └── YYYYMMDD_HHMMSS/          ← New charts (will be created)
```

---

## Ready to Go! 🎯

Everything is set up and ready. Just run:

```bash
cd /Users/nicolacatalin/Desktop/facultate/proiect-sasps/experiments
./run_scaled_comparison.sh
```

The script will:
1. ✅ Ask for confirmation
2. ✅ Stop existing services
3. ✅ Start monolith (1 instance)
4. ✅ Start scaled microservices (3 replicas each)
5. ✅ Run 10 tests (5 loads × 2 architectures)
6. ✅ Generate all charts
7. ✅ Show you where results are saved

**Estimated time:** 25-30 minutes

---

## Questions?

- **What am I testing?** → Read `SETUP_SUMMARY.md`
- **How do I interpret results?** → Read `SCALED_COMPARISON_GUIDE.md`
- **Quick reference?** → Read `QUICK_START.md`
- **Something broke?** → Check "Troubleshooting" section above

---

**You're all set! Good luck with your test!** 🚀
