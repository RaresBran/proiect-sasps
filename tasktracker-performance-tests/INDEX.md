# 📚 Performance Testing Documentation Index

Welcome! This directory contains comprehensive performance testing for TaskTracker's monolithic and microservices architectures.

---

## 🚀 Quick Start (New Users Start Here!)

1. **[QUICKSTART.md](QUICKSTART.md)** - ⭐ **START HERE** ⭐
   - 5-minute setup guide
   - Commands to run tests
   - How to view results
   - Best for: Getting started quickly

---

## 📖 Main Documentation

2. **[README.md](README.md)** - Complete Documentation
   - Full setup instructions
   - Detailed configuration guide
   - All test scenarios
   - Troubleshooting
   - Best for: Deep understanding

3. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Project Overview
   - What was created
   - Key features
   - File structure
   - Usage examples
   - Best for: Understanding the project

4. **[COMPLETION_SUMMARY.md](COMPLETION_SUMMARY.md)** - Completion Report
   - Complete list of changes
   - Port configurations
   - Expected results
   - Technical details
   - Best for: Comprehensive overview

5. **[ARCHITECTURE_DIAGRAM.txt](ARCHITECTURE_DIAGRAM.txt)** - Visual Diagrams
   - ASCII architecture diagrams
   - Test flow visualization
   - API endpoints map
   - File structure tree
   - Best for: Visual learners

---

## 🔧 Getting Started Checklist

### First Time Setup

```bash
# 1. Read the quick start
cat QUICKSTART.md

# 2. Run setup
./setup.sh

# 3. Verify everything is ready
./verify_setup.sh

# 4. Start both applications
# Terminal 1:
cd ../tasktracker-mono && docker compose up -d

# Terminal 2:
cd ../tasktracker-micro && docker compose up -d

# 5. Run your first test
source venv/bin/activate
./run_both_tests.sh

# 6. View results
open results/comparison_*/summary_table.png
```

---

## 📁 File Guide

### Core Test Files
- `locustfile_monolithic.py` - Tests for monolithic architecture
- `locustfile_microservices.py` - Tests for microservices architecture
- `config.py` - Configuration settings
- `utils.py` - Utility functions

### Analysis
- `analyze_results.py` - Generates comparison charts

### Scripts (All Executable)
- `setup.sh` - First-time setup
- `verify_setup.sh` - Verify everything is configured
- `run_mono_test.sh` - Test monolithic only
- `run_micro_test.sh` - Test microservices only
- `run_both_tests.sh` - ⭐ Test both in parallel (recommended)
- `run_tests.sh` - Interactive menu
- `compare_results.sh` - Compare existing results
- `cleanup.sh` - Delete old results

### Configuration
- `requirements.txt` - Python dependencies
- `.gitignore` - Git ignore rules

---

## 🎯 Common Tasks

### Run a Quick Test
```bash
USERS=30 RUN_TIME=30s ./run_both_tests.sh
```

### Run a Standard Test
```bash
./run_both_tests.sh
```

### Run a Stress Test
```bash
USERS=200 RUN_TIME=10m ./run_both_tests.sh
```

### View Results
```bash
open results/comparison_*/
open results/monolithic_*/report.html
open results/microservices_*/report.html
```

### Clean Old Results
```bash
./cleanup.sh
```

### Compare Two Existing Results
```bash
./compare_results.sh
```

---

## 📊 What You'll Get

After running tests, you'll receive:

### Per Architecture
- Interactive HTML report with charts
- CSV file with raw statistics
- Test execution log

### Comparison
- 5 comparison charts (PNG images)
- Summary table (PNG)
- Text summary report

---

## 🎓 Learning Path

**New to performance testing?**
1. Read [QUICKSTART.md](QUICKSTART.md)
2. Run a quick 30-second test
3. Explore the HTML reports
4. Read [README.md](README.md) for details

**Want to understand the architecture?**
1. Read [ARCHITECTURE_DIAGRAM.txt](ARCHITECTURE_DIAGRAM.txt)
2. Read [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
3. Check the main app READMEs:
   - `../tasktracker-mono/README.md`
   - `../tasktracker-micro/README.md`

**Ready to customize?**
1. Edit `config.py` for test parameters
2. Modify task weights for different load patterns
3. Create custom test scenarios
4. Read advanced sections in [README.md](README.md)

---

## 🎉 Key Features

✅ Tests all 12 API endpoints  
✅ Simulates realistic user behavior  
✅ Generates beautiful comparison charts  
✅ Runs both tests in parallel  
✅ One-command execution  
✅ Comprehensive documentation  
✅ Production-ready code  

---

## 💡 Quick Reference

| Task | Command |
|------|---------|
| Setup | `./setup.sh` |
| Verify | `./verify_setup.sh` |
| Run tests | `./run_both_tests.sh` |
| Interactive | `./run_tests.sh` |
| Quick test | `USERS=30 RUN_TIME=30s ./run_both_tests.sh` |
| Clean up | `./cleanup.sh` |

---

## 📞 Need Help?

1. Check [QUICKSTART.md](QUICKSTART.md) for common issues
2. Read [README.md](README.md) troubleshooting section
3. Run `./verify_setup.sh` to check configuration
4. View [ARCHITECTURE_DIAGRAM.txt](ARCHITECTURE_DIAGRAM.txt) for visual reference

---

## 🔗 Related Documentation

- **Monolithic App**: `../tasktracker-mono/README.md`
- **Microservices App**: `../tasktracker-micro/README.md`
- **Architecture Comparison**: `../tasktracker-micro/ARCHITECTURE_COMPARISON.md`
- **Locust Documentation**: https://docs.locust.io/

---

## ✨ Summary

This directory contains everything you need to:
- ✅ Test both architectures
- ✅ Compare performance
- ✅ Generate visual reports
- ✅ Analyze bottlenecks
- ✅ Make informed decisions

**Ready to start? Open [QUICKSTART.md](QUICKSTART.md)!**

---

*Created: December 13, 2024*  
*Status: Complete and Ready to Use*  
*Documentation: Comprehensive*

🚀 **Happy Testing!** 🚀

