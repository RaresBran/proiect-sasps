# TaskTracker Performance Tests

Comprehensive end-to-end performance testing suite for comparing **Monolithic** vs **Microservices** architectures using **Locust**.

---

## 📋 Overview

This test suite provides automated performance testing and comparison for both TaskTracker architectures:

- **Monolithic Architecture** (Port 9000)
- **Microservices Architecture** (Port 8000)

### What Gets Tested

✅ **Authentication Operations**
- User login
- Token validation
- User info retrieval

✅ **Task Management (CRUD)**
- Create tasks
- List all tasks
- List filtered tasks (by status, priority)
- Get single task
- Update tasks
- Mark complete/incomplete
- Delete tasks

✅ **Statistics**
- User statistics aggregation
- Cross-service communication (microservices)

### Test Characteristics

- **Realistic User Behavior**: Simulates actual user patterns with weighted operations
- **Pre-populated Data**: Creates 100 users with 20 tasks each before testing
- **Concurrent Load**: Tests with configurable concurrent users
- **Comprehensive Metrics**: Response times, throughput, failure rates, percentiles
- **Visual Reports**: Generates comparison charts and HTML reports

---

## 🛠️ Prerequisites

### Required Software

1. **Python 3.11+**
2. **pip** (Python package manager)
3. **Both applications running**:
   - Monolithic on port 9000
   - Microservices on port 8000

### Start Applications

**Terminal 1 - Monolithic:**
```bash
cd ../tasktracker-mono
docker compose up -d
```

**Terminal 2 - Microservices:**
```bash
cd ../tasktracker-micro
docker compose up -d
```

Verify both are running:
```bash
curl http://localhost:9000/health  # Should return {"status":"healthy"}
curl http://localhost:8000/health  # Should return {"status":"healthy"}
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Make Scripts Executable

```bash
chmod +x run_*.sh
```

### 3. Run Tests

**Option A: Interactive Menu**
```bash
./run_tests.sh
```

**Option B: Test Both Architectures in Parallel (Recommended)**
```bash
./run_both_tests.sh
```

**Option C: Test Individual Architectures**
```bash
# Monolithic only
./run_mono_test.sh

# Microservices only
./run_micro_test.sh
```

### 4. View Results

Results are saved in `results/` directory with timestamp:
```
results/
├── monolithic_20231215_143022/
│   ├── report.html          # Interactive HTML report
│   ├── stats_stats.csv      # Raw statistics
│   └── locust.log          # Test logs
├── microservices_20231215_143022/
│   ├── report.html
│   ├── stats_stats.csv
│   └── locust.log
└── comparison_20231215_143022/
    ├── response_time_comparison.png
    ├── throughput_comparison.png
    ├── failure_rate_comparison.png
    ├── percentile_comparison.png
    ├── summary_table.png
    └── summary.txt
```

---

## ⚙️ Configuration

### Test Parameters

Configure via environment variables or script prompts:

```bash
# Number of concurrent users (default: 50)
export USERS=100

# Users spawned per second (default: 10)
export SPAWN_RATE=20

# Test duration (default: 60s)
export RUN_TIME=5m

# Run test
./run_both_tests.sh
```

### Architecture URLs

Edit `config.py` to change base URLs:

```python
ARCHITECTURES = {
    "monolithic": {
        "base_url": "http://localhost:9000",
    },
    "microservices": {
        "base_url": "http://localhost:8000",
    }
}
```

### Task Weights

Control operation frequency in `config.py`:

```python
TASK_WEIGHTS = {
    "read": 70,      # 70% read operations
    "write": 20,     # 20% write operations  
    "update": 7,     # 7% update operations
    "delete": 3,     # 3% delete operations
}
```

### User Generation

Configure test data in `config.py`:

```python
USER_GENERATION = {
    "total_users": 100,        # Users to create
    "tasks_per_user": 20,      # Tasks per user
}
```

---

## 📊 Understanding Results

### HTML Reports

Open `report.html` in your browser for interactive charts:
- Request statistics by endpoint
- Response time graphs
- Request count over time
- Failure rate trends
- Charts tab with visual analytics

### Comparison Charts

The analysis script generates 5 comparison charts:

1. **Response Time Comparison** (`response_time_comparison.png`)
   - Average response time by endpoint
   - Lower is better

2. **Throughput Comparison** (`throughput_comparison.png`)
   - Requests per second by endpoint
   - Higher is better

3. **Failure Rate Comparison** (`failure_rate_comparison.png`)
   - Percentage of failed requests
   - Lower is better (0% ideal)

4. **Percentile Comparison** (`percentile_comparison.png`)
   - Response time distribution
   - Shows tail latencies (99th, 99.9th percentiles)

5. **Summary Table** (`summary_table.png`)
   - Overall metrics comparison
   - Total requests, failure rates, response times

### Key Metrics to Analyze

| Metric | Description | Goal |
|--------|-------------|------|
| **Average Response Time** | Mean time to complete request | Lower is better |
| **95th Percentile** | 95% of requests complete within this time | Lower is better |
| **99th Percentile** | 99% of requests complete within this time | Lower is better |
| **Requests/sec** | Throughput capacity | Higher is better |
| **Failure Rate** | Percentage of failed requests | 0% is ideal |
| **Max Response Time** | Worst-case latency | Lower is better |

---

## 🎯 Test Scenarios

### Standard Load Test (Default)
```bash
USERS=50 SPAWN_RATE=10 RUN_TIME=60s ./run_both_tests.sh
```
- 50 concurrent users
- 10 users spawned per second
- 60-second duration
- Good for baseline comparison

### Stress Test
```bash
USERS=200 SPAWN_RATE=20 RUN_TIME=5m ./run_both_tests.sh
```
- 200 concurrent users
- High load scenario
- 5-minute duration
- Tests system limits

### Endurance Test
```bash
USERS=100 SPAWN_RATE=10 RUN_TIME=30m ./run_both_tests.sh
```
- Moderate load
- Extended duration
- Tests stability over time

### Spike Test
```bash
USERS=500 SPAWN_RATE=100 RUN_TIME=2m ./run_both_tests.sh
```
- Rapid user increase
- Tests handling of traffic spikes

---

## 📁 Project Structure

```
tasktracker-performance-tests/
├── locustfile_monolithic.py      # Locust test for monolithic
├── locustfile_microservices.py   # Locust test for microservices
├── config.py                     # Test configuration
├── utils.py                      # Utility functions
├── analyze_results.py            # Results analysis & visualization
├── run_mono_test.sh             # Run monolithic test
├── run_micro_test.sh            # Run microservices test
├── run_both_tests.sh            # Run both in parallel
├── run_tests.sh                 # Interactive menu
├── requirements.txt             # Python dependencies
├── README.md                    # This file
└── results/                     # Test results (generated)
    ├── monolithic_*/
    ├── microservices_*/
    └── comparison_*/
```

---

## 🔬 How It Works

### 1. Pre-Test Setup (Automatic)

When a test starts, it automatically:
1. Creates 100 test users
2. Logs in each user to get JWT token
3. Creates 20 tasks per user (2000 total tasks)
4. Stores tokens and task IDs for test execution

This ensures realistic data exists before load testing begins.

### 2. Test Execution

Each simulated user:
1. Logs in (or uses cached token)
2. Performs weighted operations:
   - 70% reads (list tasks, get task, get stats)
   - 20% writes (create tasks)
   - 7% updates (update task, mark complete/incomplete)
   - 3% deletes (delete tasks)
3. Waits 1-3 seconds between operations (realistic behavior)

### 3. Results Collection

Locust collects:
- Request count per endpoint
- Response times (min, max, avg, percentiles)
- Failure rates
- Requests per second
- Time-series data

### 4. Analysis & Visualization

The `analyze_results.py` script:
1. Loads CSV statistics from both tests
2. Compares metrics side-by-side
3. Generates comparison charts
4. Creates summary report

---

## 💡 Tips & Best Practices

### For Accurate Results

1. **Clean State**: Start with fresh databases
   ```bash
   cd ../tasktracker-mono && docker compose down -v && docker compose up -d
   cd ../tasktracker-micro && docker compose down -v && docker compose up -d
   ```

2. **Warm-Up**: Run a short test first to warm up caches

3. **System Resources**: Close unnecessary applications

4. **Multiple Runs**: Run tests 3-5 times and average results

5. **Consistent Environment**: Use same hardware, network conditions

### Interpreting Results

- **Monolithic typically has**:
  - Lower latency (no network overhead between services)
  - Higher throughput for simple operations
  - Better performance for operations requiring multiple data sources

- **Microservices typically has**:
  - Higher latency (network calls between services)
  - Better fault isolation
  - Independent scaling capabilities
  - Overhead from API gateway

### Common Issues

**Issue**: Tests fail immediately
- **Solution**: Verify both apps are running and healthy

**Issue**: Many failures during test
- **Solution**: Reduce concurrent users or increase spawn rate time

**Issue**: Database errors
- **Solution**: Check database connection limits in docker-compose.yml

**Issue**: Slow setup phase
- **Solution**: Reduce `USER_GENERATION` values in config.py

---

## 📈 Example Results Interpretation

### Sample Output
```
Monolithic Architecture:
  Total Requests: 15,234
  Requests/sec: 253.9
  Avg Response Time: 45ms
  95th Percentile: 120ms
  Failure Rate: 0.02%

Microservices Architecture:
  Total Requests: 14,876
  Requests/sec: 247.9
  Avg Response Time: 78ms
  95th Percentile: 210ms
  Failure Rate: 0.15%
```

### Analysis
- Monolithic processes ~2.4% more requests
- Monolithic has ~42% lower latency
- Microservices has higher tail latencies (95th percentile)
- Both have acceptable failure rates (<1%)

---

## 🧪 Advanced Usage

### Custom Test Scenarios

Create your own locustfile:

```python
from locust import HttpUser, task, between

class CustomUser(HttpUser):
    host = "http://localhost:9000"
    wait_time = between(1, 2)
    
    def on_start(self):
        # Login logic
        pass
    
    @task
    def custom_scenario(self):
        # Your custom test
        pass
```

Run with:
```bash
locust -f custom_locustfile.py --headless -u 100 -r 10 -t 60s
```

### Web UI Mode

Run with interactive web UI:
```bash
locust -f locustfile_monolithic.py
```
Then open http://localhost:8089

### Distributed Testing

Run tests across multiple machines:

**Master:**
```bash
locust -f locustfile.py --master
```

**Workers:**
```bash
locust -f locustfile.py --worker --master-host=<master-ip>
```

---

## 📚 Resources

- **Locust Documentation**: https://docs.locust.io/
- **Monolithic App**: `../tasktracker-mono/README.md`
- **Microservices App**: `../tasktracker-micro/README.md`
- **Architecture Comparison**: `../tasktracker-micro/ARCHITECTURE_COMPARISON.md`

---

## 🤝 Contributing

Improvements welcome! Consider adding:
- Additional test scenarios
- More visualizations
- Performance profiling
- Database query analysis
- Network monitoring integration

---

## 📄 License

Educational project - same license as parent TaskTracker project.

---

## 🎉 Summary

This performance testing suite provides:

✅ Comprehensive API testing for both architectures  
✅ Realistic user behavior simulation  
✅ Automated result collection and analysis  
✅ Visual comparison charts  
✅ Easy-to-use scripts  
✅ Configurable test parameters  

**Quick Start:**
```bash
pip install -r requirements.txt
chmod +x run_*.sh
./run_both_tests.sh
```

**View Results:**
```bash
open results/comparison_*/summary_table.png
open results/monolithic_*/report.html
open results/microservices_*/report.html
```

Happy testing! 🚀

