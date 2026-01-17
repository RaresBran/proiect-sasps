# Experiments Quick Reference

**Three new experiments for your presentation - ready to run and screenshot!**

---

## 🚀 Before Running

Make sure both apps are running:
```bash
cd ../tasktracker-mono && docker compose up -d
cd ../tasktracker-micro && docker compose up -d
```

Activate virtual environment:
```bash
source .venv/bin/activate
```

---

## 1️⃣ Crossover Curve Sweep

**What it does:** Runs tests at multiple concurrency levels to find where microservices beats monolithic.

**Quick run (~15 min):**
```bash
./experiments/run_crossover_sweep.sh --quick
```

**Full run (~45 min):**
```bash
./experiments/run_crossover_sweep.sh
```

**Best screenshot:** `results/crossover_*/crossover_dashboard.png`

---

## 2️⃣ Resource Efficiency

**What it does:** Measures CPU/memory and calculates efficiency (req/s per CPU, req/s per GB).

**Quick run (~10 min):**
```bash
./experiments/run_resource_monitor.sh --quick
```

**Full run (~20 min):**
```bash
./experiments/run_resource_monitor.sh
```

**Best screenshot:** `results/resource_*/resource_efficiency.png`

---

## 3️⃣ Resilience / Failure Injection

**What it does:** Kills task-service mid-test to show fault isolation.

**Run (~2 min):**
```bash
./experiments/run_resilience_test.sh
```

**Best screenshot:** `results/resilience_*/resilience_timeline.png`

---

## 📸 Screenshot Checklist for Slides

| Slide Topic | Screenshot File | What It Shows |
|-------------|----------------|---------------|
| Crossover Point | `crossover_dashboard.png` | Where micro beats mono |
| Throughput Curve | `crossover_throughput.png` | Performance vs load |
| Resource Usage | `resource_dashboard.png` | CPU/memory comparison |
| Efficiency | `resource_efficiency.png` | req/s per resource |
| Fault Tolerance | `resilience_timeline.png` | Recovery after failure |

---

## 📊 Expected Results Summary

### Crossover Sweep
- **Monolithic wins:** 0-100 users (2-3x faster)
- **Crossover:** ~100-200 users
- **Microservices wins:** 200+ users (higher throughput)

### Resource Efficiency
- **Monolithic:** Higher efficiency (req/s per CPU) at low load
- **Microservices:** Uses more resources but scales better

### Resilience Test
- **Before fault:** ~0% errors
- **During fault:** ~20-40% errors (only task operations)
- **After recovery:** Back to ~0% errors

---

## 🎯 One-Liner for Each Experiment

```bash
# Crossover (find the crossover point)
./experiments/run_crossover_sweep.sh --quick

# Resources (measure efficiency)
./experiments/run_resource_monitor.sh --quick

# Resilience (show fault isolation)
./experiments/run_resilience_test.sh
```

---

**All results go to `results/` folder with timestamps. Just screenshot and add to slides!** 📸
