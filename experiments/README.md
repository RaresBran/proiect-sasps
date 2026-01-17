# TaskTracker Experiments

Advanced performance experiments for comparing Monolithic vs Microservices architectures.

This directory contains three experiment types:
1. **Parameter Sweep**: Tests both architectures across multiple concurrency levels
2. **Resource Efficiency**: Measures CPU/memory usage and computes efficiency metrics
3. **Failure Injection**: Tests microservices resilience by killing/restarting a service

---

## Prerequisites

1. **Python 3.11+** with required packages
2. **Docker** and **Docker Compose** installed
3. **Both applications running** (or just the one you're testing)

### Install Dependencies

```bash
# From project root
cd experiments
pip install -r requirements.txt

# Or use the existing performance tests venv
cd ../tasktracker-performance-tests
source .venv/bin/activate
pip install matplotlib
```

---

## Quick Start

### Option A: Automated Scaled Comparison Test (Recommended)

Run the full comparison: **Monolith (1 instance) vs Scaled Microservices (3 replicas per service)**

```bash
cd experiments
./run_scaled_comparison.sh
```

This script will:
1. Stop any existing services
2. Start Monolith (single instance)
3. Start Microservices with 3 replicas per service
4. Run parameter sweep for both
5. Generate comparison charts automatically

**Results** will be saved to `experiments/results/scaled_comparison_*/` and `experiments/plots/*/`

---

### Option B: Manual Setup

**For Monolith:**
```bash
cd tasktracker-mono
docker compose up -d
# Wait for healthy: curl http://localhost:9000/health
```

**For Microservices (Single Instance):**
```bash
cd tasktracker-micro
docker compose up -d
# Wait for healthy: curl http://localhost:8000/health
```

**For Microservices (Scaled - 3 Replicas):**
```bash
cd tasktracker-micro
docker compose -f docker-compose.scalable.yml up -d --scale user-service=3 --scale task-service=3 --scale stats-service=3
# Wait for healthy: curl http://localhost:8000/health
```

> **Note:** The `docker-compose.scalable.yml` file is identical to `docker-compose.yml` except it removes `container_name` declarations from services that need to scale (user-service, task-service, stats-service). Docker requires each container to have a unique name.

### Run Parameter Sweep (Manual)

```bash
# From project root
python experiments/run_sweep.py --arch both --concurrency-levels 10,25,50,100,200

# Or test just one architecture
python experiments/run_sweep.py --arch monolith --concurrency-levels 25,50,100
python experiments/run_sweep.py --arch microservices --concurrency-levels 25,50,100
```

### Generate Plots (Manual)

```bash
# After sweep completes, it will print the results directory
python experiments/plot_results.py experiments/results/sweep_YYYYMMDD_HHMMSS
```

### Run Failure Injection (Microservices Only - Manual)

```bash
# Make sure microservices are running
python experiments/run_failure_injection.py --target-service tasktracker_task_service

# Then generate failure plots
python experiments/plot_failure_results.py experiments/results/failure_YYYYMMDD_HHMMSS
```

---

## Detailed Usage

### Parameter Sweep (`run_sweep.py`)

Runs load tests across multiple concurrency levels for both architectures.

**Arguments:**
| Argument | Default | Description |
|----------|---------|-------------|
| `--arch` | `both` | Architecture to test: `monolith`, `microservices`, or `both` |
| `--concurrency-levels` | `10,25,50,100,200` | Comma-separated list of user counts |
| `--duration-seconds` | `60` | Test duration per run (excluding warmup) |
| `--warmup-seconds` | `10` | Warmup time (user ramp-up) |
| `--spawn-rate` | `10` | Users spawned per second |
| `--base-url-monolith` | `http://localhost:9000` | Monolith URL |
| `--base-url-micro` | `http://localhost:8000` | Microservices URL |
| `--outdir` | Auto-generated | Output directory for results |
| `--sample-interval` | `1.0` | Docker stats sample interval (seconds) |
| `--skip-health-check` | False | Skip service health verification |

**Example - Full Sweep:**
```bash
python experiments/run_sweep.py \
    --arch both \
    --concurrency-levels 10,25,50,100,200,400 \
    --duration-seconds 90 \
    --warmup-seconds 15
```

**Example - Quick Test:**
```bash
python experiments/run_sweep.py \
    --arch both \
    --concurrency-levels 25,50 \
    --duration-seconds 30
```

### Failure Injection (`run_failure_injection.py`)

Tests microservices resilience by injecting failures during steady load.

**Arguments:**
| Argument | Default | Description |
|----------|---------|-------------|
| `--concurrency` | `100` | Number of concurrent users |
| `--duration-seconds` | `90` | Total test duration |
| `--inject-at` | `30` | Seconds after start to inject failure |
| `--downtime` | `10` | Seconds to keep service down (stop-start mode) |
| `--target-service` | `tasktracker_task_service` | Container to fail |
| `--failure-mode` | `restart` | Mode: `restart` or `stop-start` |
| `--spawn-rate` | `20` | User spawn rate |
| `--base-url` | `http://localhost:8000` | Microservices URL |

**Example - Quick Restart Test:**
```bash
python experiments/run_failure_injection.py \
    --concurrency 50 \
    --duration-seconds 60 \
    --inject-at 20 \
    --failure-mode restart
```

**Example - Extended Outage Test:**
```bash
python experiments/run_failure_injection.py \
    --concurrency 100 \
    --duration-seconds 120 \
    --inject-at 40 \
    --downtime 15 \
    --failure-mode stop-start \
    --target-service tasktracker_task_service
```

### Plotting Results

**Sweep Results:**
```bash
python experiments/plot_results.py <results_directory>
```

**Failure Injection Results:**
```bash
python experiments/plot_failure_results.py <results_directory>
```

---

## Output Structure

### Sweep Results

```
experiments/results/sweep_YYYYMMDD_HHMMSS/
├── config.json                    # Experiment configuration
├── results.jsonl                  # All results (one JSON per line)
├── all_results.json              # All results as JSON array
├── run_000_monolith_c10/         # Per-run directory
│   ├── results.json              # Run results with resource metrics
│   ├── stats_stats.csv           # Locust stats
│   ├── stats_stats_history.csv   # Time series data
│   ├── report.html               # Locust HTML report
│   └── locust.log                # Test log
├── run_001_microservices_c10/
│   └── ...
└── ...
```

### Failure Injection Results

```
experiments/results/failure_YYYYMMDD_HHMMSS/
├── config.json                   # Experiment configuration
├── failure_results.json          # Complete results with time series
├── stats_stats.csv               # Locust stats
├── stats_stats_history.csv       # Time series data
├── report.html                   # Locust HTML report
└── locust.log                    # Test log
```

### Generated Plots

```
experiments/plots/YYYYMMDD_HHMMSS/
├── latency_p95_vs_concurrency.png     # P95 latency comparison
├── latency_p99_vs_concurrency.png     # P99 latency comparison
├── latency_p50_vs_concurrency.png     # P50 latency comparison
├── throughput_vs_concurrency.png      # Throughput comparison
├── error_rate_vs_concurrency.png      # Error rate comparison
├── cpu_vs_concurrency.png             # CPU usage comparison
├── efficiency_vs_concurrency.png      # RPS per CPU comparison
├── memory_vs_concurrency.png          # Memory usage comparison
└── crossover_analysis.png             # Combined crossover chart
```

**Failure Plots:**
```
experiments/plots/failure_YYYYMMDD_HHMMSS/
├── error_rate_over_time.png           # Error rate with failure markers
├── latency_over_time.png              # Latency with failure markers
├── throughput_over_time.png           # Throughput with failure markers
├── combined_failure_analysis.png      # All metrics combined
└── recovery_analysis.png              # Focus on recovery period
```

---

## What to Screenshot for Slides

### From Parameter Sweep:

1. **`crossover_analysis.png`** - Shows both latency and throughput, revealing the crossover point where architectures compare
2. **`latency_p95_vs_concurrency.png`** - Key latency comparison (P95 is most relevant for SLAs)
3. **`throughput_vs_concurrency.png`** - Shows scaling behavior of both architectures
4. **`efficiency_vs_concurrency.png`** - RPS per CPU unit (cost efficiency metric)

### From Failure Injection:

5. **`combined_failure_analysis.png`** - Shows throughput, latency, and error rate with failure markers
6. **`recovery_analysis.png`** - Shows how quickly the system recovers after failure

### Key Insights to Highlight:

| Chart | What to Look For |
|-------|------------------|
| `crossover_analysis.png` | Concurrency level where microservices starts winning |
| `latency_p95_vs_concurrency.png` | Latency degradation under load |
| `efficiency_vs_concurrency.png` | Which architecture is more resource-efficient |
| `combined_failure_analysis.png` | Impact duration and recovery time |

---

## Metrics Collected

### Performance Metrics (from Locust)

| Metric | Description |
|--------|-------------|
| `throughput_rps` | Requests per second |
| `latency_p50_ms` | Median response time |
| `latency_p95_ms` | 95th percentile response time |
| `latency_p99_ms` | 99th percentile response time |
| `latency_avg_ms` | Average response time |
| `error_rate` | Percentage of failed requests |
| `total_requests` | Total requests made |
| `total_failures` | Total failed requests |

### Resource Metrics (from Docker stats)

| Metric | Description |
|--------|-------------|
| `cpu_percent` | CPU usage percentage per container |
| `mem_usage_bytes` | Memory usage per container |
| `total_cpu_units` | Sum of CPU% / 100 (vCPU equivalents) |
| `total_mem_gb` | Total memory in GB |

### Efficiency Metrics (computed)

| Metric | Description |
|--------|-------------|
| `rps_per_cpu_unit` | Throughput per vCPU equivalent |
| `rps_per_gb_mem` | Throughput per GB of memory |

---

## Troubleshooting

### "Service not healthy" Error

```bash
# Check if containers are running
docker ps

# Check container logs
docker logs tasktracker_app       # Monolith
docker logs tasktracker_api_gateway  # Microservices

# Start services if needed
cd tasktracker-mono && docker compose up -d
cd tasktracker-micro && docker compose up -d
```

### Docker Stats Not Working

```bash
# Test docker stats manually
docker stats --no-stream --format "{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

### Empty Results

- Increase `--duration-seconds` to allow more requests
- Check that Locust test setup creates test data (users, tasks)
- Verify endpoints are responding: `curl http://localhost:9000/health`

### Matplotlib Import Error

```bash
pip install matplotlib
# Or if using system Python on macOS:
pip3 install matplotlib
```

---

## Architecture Reference

### Monolith Containers
- `tasktracker_app` - FastAPI application (port 9000)
- `tasktracker_db` - PostgreSQL database (port 5435)

### Microservices Containers
- `tasktracker_api_gateway` - API Gateway (port 8000)
- `tasktracker_user_service` - User service (port 8001)
- `tasktracker_task_service` - Task service (port 8002)
- `tasktracker_stats_service` - Stats service (port 8003)
- `tasktracker_user_db` - User database (port 5433)
- `tasktracker_task_db` - Task database (port 5434)

---

## Example Workflow

### Complete Comparison Study

```bash
# 1. Start both stacks
cd tasktracker-mono && docker compose up -d
cd ../tasktracker-micro && docker compose up -d
cd ..

# 2. Wait for services to be healthy
sleep 30

# 3. Run parameter sweep
python experiments/run_sweep.py \
    --arch both \
    --concurrency-levels 10,25,50,100,200 \
    --duration-seconds 60

# 4. Note the results directory from output
# e.g., experiments/results/sweep_20240115_143022

# 5. Generate plots
python experiments/plot_results.py experiments/results/sweep_20240115_143022

# 6. Run failure injection (optional)
python experiments/run_failure_injection.py \
    --duration-seconds 90 \
    --inject-at 30 \
    --target-service tasktracker_task_service

# 7. Generate failure plots
python experiments/plot_failure_results.py experiments/results/failure_20240115_150000

# 8. Find all plots in experiments/plots/
ls experiments/plots/
```

---

## Files Overview

```
experiments/
├── __init__.py
├── config.py                    # Configuration constants
├── requirements.txt             # Python dependencies
├── README.md                    # This file
│
├── run_sweep.py                 # Parameter sweep experiment
├── plot_results.py              # Plot sweep results
├── run_failure_injection.py     # Failure injection experiment
├── plot_failure_results.py      # Plot failure results
│
├── lib/                         # Shared library modules
│   ├── __init__.py
│   ├── io_utils.py              # File I/O utilities
│   ├── loadtest_runner.py       # Locust test runner wrapper
│   └── docker_metrics.py        # Docker stats collector
│
├── results/                     # Generated results (gitignored)
│   ├── sweep_YYYYMMDD_HHMMSS/
│   └── failure_YYYYMMDD_HHMMSS/
│
└── plots/                       # Generated plots (gitignored)
    ├── YYYYMMDD_HHMMSS/
    └── failure_YYYYMMDD_HHMMSS/
```

---

## Tips for Presentations

1. **Run sweep with sufficient duration** (60-90s per concurrency level) for stable results
2. **Include at least 5 concurrency levels** to show trends clearly
3. **Use crossover_analysis.png** as your key slide
4. **Highlight efficiency metrics** for cloud cost discussions
5. **Show failure injection** to demonstrate microservices resilience
6. **Include raw numbers** in a table alongside charts

---

Happy experimenting! 🔬
