# Quick Start Guide

## 1. Setup (First Time Only)

```bash
# Run setup script
./setup.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
chmod +x run_*.sh
```

## 2. Start Applications

**Terminal 1 - Monolithic (Port 9000):**
```bash
cd ../tasktracker-mono
docker compose up -d
```

**Terminal 2 - Microservices (Port 8000):**
```bash
cd ../tasktracker-micro
docker compose up -d
```

**Verify:**
```bash
curl http://localhost:9000/health
curl http://localhost:8000/health
```

## 3. Run Tests

**Interactive Menu:**
```bash
source venv/bin/activate
./run_tests.sh
```

**Both Architectures (Parallel):**
```bash
source venv/bin/activate
./run_both_tests.sh
```

**Individual Tests:**
```bash
source venv/bin/activate
./run_mono_test.sh
./run_micro_test.sh
```

## 4. View Results

Results are saved in `results/` with timestamp:
- `results/monolithic_*/report.html` - Monolithic HTML report
- `results/microservices_*/report.html` - Microservices HTML report
- `results/comparison_*/` - Comparison charts

**Open Reports:**
```bash
open results/monolithic_*/report.html
open results/microservices_*/report.html
```

**View Comparison Charts:**
```bash
open results/comparison_*/summary_table.png
```

## 5. Cleanup

```bash
./cleanup.sh
```

## Configuration

### Change Test Parameters

```bash
# Quick test (30 users, 30 seconds)
USERS=30 RUN_TIME=30s ./run_both_tests.sh

# Heavy load (200 users, 5 minutes)
USERS=200 RUN_TIME=5m ./run_both_tests.sh
```

### Edit config.py

- Adjust `USER_GENERATION` for pre-test data
- Modify `TASK_WEIGHTS` for operation distribution
- Change base URLs if needed

## Troubleshooting

**Problem:** "Application not running"
- **Solution:** Start the application with `docker compose up -d`

**Problem:** "pip command not found"
- **Solution:** Use `pip3` or install pip

**Problem:** "Permission denied"
- **Solution:** Run `chmod +x *.sh`

**Problem:** Many test failures
- **Solution:** Reduce concurrent users: `USERS=20 ./run_tests.sh`

## Example Results

After running `./run_both_tests.sh`, you'll see:

```
results/
├── monolithic_20231215_143022/
│   ├── report.html              ← Open this!
│   ├── stats_stats.csv
│   └── locust.log
├── microservices_20231215_143022/
│   ├── report.html              ← Open this!
│   ├── stats_stats.csv
│   └── locust.log
└── comparison_20231215_143022/
    ├── response_time_comparison.png    ← Charts!
    ├── throughput_comparison.png
    ├── failure_rate_comparison.png
    ├── percentile_comparison.png
    ├── summary_table.png
    └── summary.txt
```

## Test Scenarios

| Scenario | Command | Purpose |
|----------|---------|---------|
| Quick baseline | `USERS=50 RUN_TIME=60s ./run_both_tests.sh` | Fast comparison |
| Standard load | `USERS=100 RUN_TIME=5m ./run_both_tests.sh` | Normal conditions |
| Stress test | `USERS=200 RUN_TIME=5m ./run_both_tests.sh` | High load |
| Endurance | `USERS=100 RUN_TIME=30m ./run_both_tests.sh` | Long duration |

For detailed documentation, see [README.md](README.md)

