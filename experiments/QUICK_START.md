# 🚀 Quick Reference: Scaled Comparison Test

## Run the Test (One Command)

```bash
cd experiments && ./run_scaled_comparison.sh
```

**Duration:** ~25 minutes  
**What it does:** Compares monolith (1 instance) vs scaled microservices (3 replicas)

---

## What You're Comparing

| Architecture | Instances | Containers | Previous Results @ 200 users |
|--------------|-----------|------------|------------------------------|
| **Monolith** | 1 app + 1 db | 2 | 75 req/s, 17ms P95 |
| **Microservices (scaled)** | 3 replicas each service | 12 | ? req/s, ? ms P95 ← **Testing Now** |

---

## Expected Outcome

✅ **Best Case:** Microservices shows 1.5-2x better throughput at 200 users  
⚠️ **Likely:** Marginal improvement (~10-20% better throughput)  
❌ **Worst Case:** No improvement (API Gateway bottleneck)

---

## Key Files After Test

```
experiments/plots/YYYYMMDD_HHMMSS/
├── crossover_analysis.png          ⭐ Main comparison
├── latency_p95_vs_concurrency.png  ⭐ Latency trends
├── throughput_vs_concurrency.png   ⭐ Throughput trends
└── efficiency_vs_concurrency.png   ⭐ Cost efficiency
```

---

## Quick Data Extraction

```bash
cd experiments/results/scaled_comparison_*/

# Throughput comparison
cat results.jsonl | jq -r '[.arch, .concurrency, .throughput_rps] | @tsv'

# Latency comparison
cat results.jsonl | jq -r '[.arch, .concurrency, .latency_p95_ms] | @tsv'
```

---

## Manual Start (If Needed)

```bash
# Start monolith
cd tasktracker-mono && docker compose up -d

# Start scaled microservices
cd tasktracker-micro
docker compose -f docker-compose.scalable.yml up -d --scale user-service=3 --scale task-service=3 --scale stats-service=3

# Run tests
cd experiments
python run_sweep.py --arch both --concurrency-levels 10,25,50,100,200

# Generate plots
python plot_results.py experiments/results/scaled_comparison_YYYYMMDD_HHMMSS
```

---

## Stop Everything

```bash
cd tasktracker-mono && docker compose down
cd tasktracker-micro && docker compose -f docker-compose.scalable.yml down
```

---

## Documentation

- **Setup guide:** `experiments/SETUP_SUMMARY.md`
- **Interpretation guide:** `experiments/SCALED_COMPARISON_GUIDE.md`
- **Presentation guide:** `experiments/PRESENTATION_README.md`
- **Full docs:** `experiments/README.md`

---

## Troubleshooting

**Services won't start?**
```bash
docker compose down  # in both mono and micro dirs
./run_scaled_comparison.sh  # try again
```

**Need to stop early?**
- Press `Ctrl+C`
- Run `docker compose down` in both directories

**Test results look wrong?**
- Check `docker ps` to see if 12 containers are running
- Verify `curl http://localhost:8000/health` returns 200
- Check `experiments/results/*/run_*/locust.log` for errors

---

**Ready? Just run:** `cd experiments && ./run_scaled_comparison.sh` 🚀
