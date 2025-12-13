# Performance Testing Project Summary

## ✅ Project Complete

All performance testing infrastructure has been created and configured.

---

## 📦 What Was Created

### Core Test Files
- ✅ `locustfile_monolithic.py` - Load tests for monolithic architecture
- ✅ `locustfile_microservices.py` - Load tests for microservices architecture
- ✅ `config.py` - Centralized configuration
- ✅ `utils.py` - Helper functions and test data generation

### Analysis Tools
- ✅ `analyze_results.py` - Generate comparison charts and visualizations

### Run Scripts
- ✅ `setup.sh` - First-time setup (install dependencies)
- ✅ `run_mono_test.sh` - Run monolithic test only
- ✅ `run_micro_test.sh` - Run microservices test only
- ✅ `run_both_tests.sh` - Run both tests in parallel (recommended)
- ✅ `run_tests.sh` - Interactive menu
- ✅ `compare_results.sh` - Compare existing test results
- ✅ `cleanup.sh` - Clean old test results

### Documentation
- ✅ `README.md` - Comprehensive documentation
- ✅ `QUICKSTART.md` - Quick reference guide
- ✅ `requirements.txt` - Python dependencies
- ✅ `.gitignore` - Git ignore rules

---

## 🔧 Configuration Changes

### Monolithic App Ports (Updated)
- **Application**: Port 9000 (was 8000)
- **Database**: Port 5435 (was 5432)
- **README.md**: Updated all references to new ports

This allows both architectures to run simultaneously for parallel testing.

---

## 🚀 How to Use

### 1. First Time Setup
```bash
cd tasktracker-performance-tests
./setup.sh
```

### 2. Start Both Applications
```bash
# Terminal 1 - Monolithic (Port 9000)
cd ../tasktracker-mono
docker compose up -d

# Terminal 2 - Microservices (Port 8000)  
cd ../tasktracker-micro
docker compose up -d
```

### 3. Run Tests
```bash
cd tasktracker-performance-tests
source venv/bin/activate

# Interactive menu (easiest)
./run_tests.sh

# Or run both in parallel (recommended)
./run_both_tests.sh

# Or run individually
./run_mono_test.sh
./run_micro_test.sh
```

### 4. View Results
Results are saved in `results/` with timestamps:
- `results/monolithic_*/report.html`
- `results/microservices_*/report.html`
- `results/comparison_*/` (charts and summary)

---

## 📊 What Gets Tested

### Performance Metrics
- ✅ Response times (average, min, max, percentiles)
- ✅ Throughput (requests per second)
- ✅ Failure rates
- ✅ Concurrent user handling
- ✅ Database performance under load

### API Endpoints Tested
1. **Authentication** (User Service)
   - Login
   - Get user info
   - Token validation

2. **Tasks** (Task Service)
   - Create task
   - List all tasks
   - List filtered tasks (by status, priority)
   - Get single task
   - Update task
   - Mark complete/incomplete
   - Delete task

3. **Statistics** (Stats Service)
   - User statistics
   - Cross-service communication

### Test Characteristics
- **Pre-populated data**: 100 users × 20 tasks = 2000 tasks
- **Realistic patterns**: 70% read, 20% write, 7% update, 3% delete
- **Concurrent users**: Configurable (default 50)
- **Duration**: Configurable (default 60s)
- **Wait time**: 1-3 seconds between operations

---

## 📈 Generated Charts

The analysis script creates 5 comparison charts:

1. **Response Time Comparison** - Avg response by endpoint
2. **Throughput Comparison** - Requests/sec by endpoint
3. **Failure Rate Comparison** - Error rates by endpoint
4. **Percentile Comparison** - Response time distribution
5. **Summary Table** - Overall metrics side-by-side

---

## ⚙️ Configuration Options

### Test Parameters
```bash
# Quick test
USERS=30 RUN_TIME=30s ./run_both_tests.sh

# Standard load
USERS=100 RUN_TIME=5m ./run_both_tests.sh

# Stress test
USERS=200 RUN_TIME=10m ./run_both_tests.sh
```

### Edit config.py
- `ARCHITECTURES` - Base URLs
- `TEST_CONFIG` - Default parameters
- `USER_GENERATION` - Pre-test data
- `TASK_WEIGHTS` - Operation distribution

---

## 🎯 Test Scenarios

| Scenario | Command | Purpose |
|----------|---------|---------|
| Quick baseline | `USERS=50 RUN_TIME=60s` | Fast comparison |
| Standard load | `USERS=100 RUN_TIME=5m` | Normal usage |
| Stress test | `USERS=200 RUN_TIME=5m` | High load |
| Endurance | `USERS=100 RUN_TIME=30m` | Stability |

---

## 🔍 Expected Results

### Monolithic Architecture
- **Lower latency** - No network overhead between services
- **Higher throughput** - Direct database access
- **Better for**: Simple operations, transactions

### Microservices Architecture  
- **Higher latency** - Network calls between services
- **Independent scaling** - Each service scales separately
- **Better for**: Complex systems, fault isolation

---

## 📁 Project Structure

```
tasktracker-performance-tests/
├── Core Tests
│   ├── locustfile_monolithic.py
│   ├── locustfile_microservices.py
│   ├── config.py
│   └── utils.py
│
├── Analysis
│   └── analyze_results.py
│
├── Scripts (All executable)
│   ├── setup.sh
│   ├── run_mono_test.sh
│   ├── run_micro_test.sh
│   ├── run_both_tests.sh
│   ├── run_tests.sh
│   ├── compare_results.sh
│   └── cleanup.sh
│
├── Documentation
│   ├── README.md
│   ├── QUICKSTART.md
│   └── PROJECT_SUMMARY.md (this file)
│
└── Configuration
    ├── requirements.txt
    └── .gitignore
```

---

## 🛠️ Technologies Used

- **Locust** - Load testing framework
- **Python 3.11+** - Test scripts
- **Matplotlib** - Chart generation
- **Pandas** - Data analysis
- **Faker** - Realistic test data
- **Requests** - HTTP client

---

## 💡 Tips

1. **Clean state**: Start with fresh databases for accurate results
2. **Warm-up**: Run a short test first
3. **Multiple runs**: Test 3-5 times and average
4. **Monitor resources**: Watch CPU, memory, database connections
5. **Compare fairly**: Same hardware, same conditions

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Apps not running | Start with `docker compose up -d` |
| Port conflicts | Check ports: 8000 (micro), 9000 (mono) |
| Many failures | Reduce concurrent users |
| Slow setup | Reduce `USER_GENERATION` in config.py |
| Permission denied | Run `chmod +x *.sh` |

---

## 📚 Further Reading

- **Locust Docs**: https://docs.locust.io/
- **Mono App**: `../tasktracker-mono/README.md`
- **Micro App**: `../tasktracker-micro/README.md`
- **Architecture Comparison**: `../tasktracker-micro/ARCHITECTURE_COMPARISON.md`

---

## ✨ Key Features

✅ Comprehensive E2E testing  
✅ Parallel test execution  
✅ Automatic data generation  
✅ Visual comparison charts  
✅ HTML interactive reports  
✅ Configurable parameters  
✅ Easy-to-use scripts  
✅ Detailed documentation  

---

## 🎉 Ready to Test!

Everything is set up and ready to go. Just run:

```bash
./setup.sh
./run_both_tests.sh
```

Then open the generated HTML reports and comparison charts!

Happy testing! 🚀

