# Advanced Performance Experiments

This folder contains three advanced experiments for deeper performance analysis of Monolithic vs Microservices architectures.

## 📊 Overview

| Experiment | Purpose | Output |
|------------|---------|--------|
| **Crossover Sweep** | Find the exact concurrency level where microservices outperforms monolithic | Crossover curves + dashboard |
| **Resource Monitor** | Measure CPU/memory efficiency (req/s per CPU, req/s per GB) | Resource usage + efficiency plots |
| **Resilience Test** | Demonstrate fault isolation by killing a service mid-test | Recovery timeline plot |

---

## 🚀 Quick Start

### Prerequisites
1. Both applications must be running:
   ```bash
   cd ../tasktracker-mono && docker compose up -d
   cd ../tasktracker-micro && docker compose up -d
   ```

2. Activate the virtual environment:
   ```bash
   cd ..  # back to tasktracker-performance-tests
   source .venv/bin/activate
   ```

3. Make scripts executable:
   ```bash
   chmod +x experiments/*.sh
   ```

---

## 1️⃣ Crossover Curve Parameter Sweep

**Purpose:** Find the exact concurrency level where the performance advantage shifts from monolithic to microservices.

### Run
```bash
# Default (6 levels: 25, 50, 75, 100, 150, 200 users)
./experiments/run_crossover_sweep.sh

# Quick test (3 levels, faster)
./experiments/run_crossover_sweep.sh --quick

# Full comprehensive (8 levels, longer)
./experiments/run_crossover_sweep.sh --full
```

### Or run Python directly
```bash
python experiments/crossover_sweep.py \
    --concurrency-levels "25,50,100,150,200,250" \
    --run-time "90s" \
    --spawn-rate 10
```

### Output (in `results/crossover_TIMESTAMP/`)
- `crossover_throughput.png` - Throughput vs concurrency with crossover marker
- `crossover_response_time.png` - Avg response time comparison
- `crossover_percentiles.png` - P95/P99 latency comparison
- `crossover_error_rate.png` - Error rate comparison
- `crossover_dashboard.png` - **4-panel dashboard (great for slides!)**
- `sweep_results.csv` - Raw data for custom analysis
- `sweep_results.json` - Full results with metadata

### Sample Output
```
[1/12] Testing Monolithic @ 25 users...
    ✓ 45.2 req/s, 5.3ms avg, 0.00% errors
[2/12] Testing Microservices @ 25 users...
    ✓ 38.1 req/s, 12.8ms avg, 0.00% errors
...
Crossover point detected at ~150 users
```

---

## 2️⃣ Resource Efficiency Monitor

**Purpose:** Measure and compare CPU/memory usage and efficiency metrics.

### Run
```bash
# Default (4 levels: 50, 100, 150, 200 users)
./experiments/run_resource_monitor.sh

# Quick test
./experiments/run_resource_monitor.sh --quick
```

### Or run Python directly
```bash
python experiments/resource_monitor.py \
    --concurrency-levels "50,100,150,200" \
    --run-time "60s"
```

### Output (in `results/resource_TIMESTAMP/`)
- `resource_cpu_usage.png` - Total CPU % vs concurrency
- `resource_memory_usage.png` - Total memory MB vs concurrency
- `resource_efficiency.png` - **req/s per CPU and req/s per GB RAM**
- `resource_dashboard.png` - 4-panel dashboard
- `resource_metrics.csv` - All metrics in tabular format
- `resource_metrics.json` - Full results with time series

### Key Metrics Captured
- **Total CPU %** - Sum of all container CPU usage
- **Total Memory MB** - Sum of all container memory
- **req/s per CPU** - Throughput efficiency (higher = better)
- **req/s per GB RAM** - Memory efficiency (higher = better)

### What to Look For
- Monolithic typically shows higher efficiency at low load
- Microservices efficiency improves with scaling
- Memory usage in microservices is higher (more containers)

---

## 3️⃣ Resilience / Failure Injection Test

**Purpose:** Demonstrate microservices fault isolation by killing a service mid-test and observing recovery.

### Run
```bash
# Default (stops task-service)
./experiments/run_resilience_test.sh

# Target different service
./experiments/run_resilience_test.sh user-service
./experiments/run_resilience_test.sh stats-service
./experiments/run_resilience_test.sh api-gateway  # This will break everything!
```

### Or run Python directly
```bash
python experiments/resilience_test.py \
    --target-service task-service \
    --users 50 \
    --duration 120 \
    --fault-start 30 \
    --fault-duration 30
```

### Output (in `results/resilience_TIMESTAMP/`)
- `resilience_timeline.png` - **3-panel timeline showing fault injection**
- `resilience_summary.png` - Combined overlay view
- `resilience_timeseries.csv` - Second-by-second metrics
- `resilience_events.json` - Fault injection timestamps

### What the Plot Shows
```
Time:     0s -------- 30s -------- 60s -------- 90s -------- 120s
Status:   NORMAL      │   FAULT    │   RECOVERY │   NORMAL
                      ▼            ▼
                 Service      Service
                 Stopped      Restarted
```

### Key Observations
1. **Before fault (0-30s):** Normal operation, ~0% errors
2. **During fault (30-60s):** Error spike for affected endpoints
3. **After recovery (60-120s):** System returns to normal

### Why This Matters
- **Monolithic:** One failure = entire app down
- **Microservices:** One service failure = only that functionality affected
- Shows fault isolation benefit of microservices architecture

---

## 📸 Screenshot Guide for Slides

### Best Plots for Presentations

| Purpose | Best Plot | File |
|---------|-----------|------|
| Show crossover point | Crossover Dashboard | `crossover_dashboard.png` |
| Compare throughput | Throughput Curve | `crossover_throughput.png` |
| Show efficiency | Efficiency Comparison | `resource_efficiency.png` |
| Demonstrate resilience | Timeline Plot | `resilience_timeline.png` |
| Show resource usage | Resource Dashboard | `resource_dashboard.png` |

### Slide Suggestions

**Slide: "The Crossover Point"**
- Use `crossover_dashboard.png`
- Caption: "Monolithic wins below ~150 users, Microservices wins above"

**Slide: "Resource Efficiency"**
- Use `resource_efficiency.png`
- Caption: "Monolithic: better efficiency at low load; Microservices: scales better"

**Slide: "Fault Isolation Demo"**
- Use `resilience_timeline.png`
- Caption: "Killing task-service: only task operations fail, rest continues"

---

## 🔧 Advanced Usage

### Custom Concurrency Levels
```bash
python experiments/crossover_sweep.py \
    --concurrency-levels "10,30,60,90,120,180,240,300"
```

### Longer Tests (More Accurate)
```bash
python experiments/crossover_sweep.py \
    --run-time "3m"
```

### Different Fault Duration
```bash
python experiments/resilience_test.py \
    --fault-duration 60  # 60 seconds of downtime
```

### Custom Output Directory
```bash
python experiments/crossover_sweep.py \
    --output "results/my_custom_sweep"
```

---

## 📁 File Structure

```
experiments/
├── README.md                    # This file
├── crossover_sweep.py           # Parameter sweep script
├── resource_monitor.py          # Resource monitoring script
├── resilience_test.py           # Failure injection script
├── run_crossover_sweep.sh       # Wrapper script
├── run_resource_monitor.sh      # Wrapper script
└── run_resilience_test.sh       # Wrapper script

results/
├── crossover_TIMESTAMP/
│   ├── mono_25u/, mono_50u/, ...  # Per-level results
│   ├── micro_25u/, micro_50u/, ...
│   ├── crossover_*.png            # Comparison plots
│   ├── sweep_results.csv
│   └── sweep_results.json
├── resource_TIMESTAMP/
│   ├── mono_50u/, micro_50u/, ...
│   ├── resource_*.png
│   ├── resource_metrics.csv
│   └── resource_metrics.json
└── resilience_TIMESTAMP/
    ├── resilience_*.png
    ├── resilience_timeseries.csv
    └── resilience_events.json
```

---

## 🎯 Expected Results

### Crossover Sweep
- **Monolithic wins** at 25-100 users (lower latency, ~same throughput)
- **Crossover** around 100-200 users
- **Microservices wins** at 200+ users (higher throughput, can scale)

### Resource Efficiency
- **Monolithic:** Higher efficiency (req/s per resource) at low load
- **Microservices:** Uses more resources but handles higher load
- Efficiency gap narrows at high concurrency

### Resilience Test
- **Before fault:** 0% error rate
- **During fault:** ~10-30% error rate (only affected endpoints)
- **After recovery:** Returns to 0% within seconds
- Demonstrates: Other services continue working!

---

## 🐛 Troubleshooting

### "Application not running"
```bash
# Start monolithic
cd ../tasktracker-mono && docker compose up -d

# Start microservices
cd ../tasktracker-micro && docker compose up -d
```

### "Docker stats not working"
- Ensure Docker daemon is running
- Check container names match expected patterns
- Run `docker ps` to verify containers

### "No data points collected"
- Increase test duration (`--run-time "2m"`)
- Reduce concurrency if system is overloaded
- Check locust.log for errors

### "Plots look empty"
- Check that tests completed successfully
- Look at CSV files for raw data
- Run with fewer concurrency levels first

---

## 📚 Further Reading

- [Main Performance Tests README](../README.md)
- [Architecture Comparison](../../tasktracker-micro/ARCHITECTURE_COMPARISON.md)
- [Locust Documentation](https://docs.locust.io/)
- [Docker Stats](https://docs.docker.com/engine/reference/commandline/stats/)

---

**Happy testing! 🚀**
