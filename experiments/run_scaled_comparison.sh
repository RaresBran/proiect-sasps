#!/bin/bash
# Run comparison test: Monolith (1 instance) vs Scaled Microservices (3 replicas per service)

set -e

echo "=================================================================="
echo "MONOLITH vs SCALED MICROSERVICES COMPARISON TEST"
echo "=================================================================="
echo ""
echo "This will:"
echo "  1. Stop any existing services"
echo "  2. Start Monolith (1 instance)"
echo "  3. Start Scaled Microservices (3 replicas per service)"
echo "  4. Run parameter sweep for both"
echo "  5. Generate comparison charts"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

PROJECT_ROOT="/Users/nicolacatalin/Desktop/facultate/proiect-sasps"
cd "$PROJECT_ROOT"

# Step 1: Stop any existing services
echo ""
echo "=================================================================="
echo "Step 1: Stopping existing services..."
echo "=================================================================="

echo "Stopping monolith..."
cd "$PROJECT_ROOT/tasktracker-mono"
docker compose down 2>/dev/null || true

echo "Stopping microservices..."
cd "$PROJECT_ROOT/tasktracker-micro"
docker compose down 2>/dev/null || true
docker compose -f docker-compose.scalable.yml down 2>/dev/null || true

echo "✓ All services stopped"

# Step 2: Start Monolith
echo ""
echo "=================================================================="
echo "Step 2: Starting Monolith (single instance)..."
echo "=================================================================="

cd "$PROJECT_ROOT/tasktracker-mono"
docker compose up -d

echo "Waiting for monolith to be healthy..."
for i in {1..30}; do
    if curl -s http://localhost:9000/health > /dev/null 2>&1; then
        echo "✓ Monolith is healthy!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "✗ Monolith failed to start within 30 seconds"
        exit 1
    fi
    echo "  Waiting... ($i/30)"
    sleep 1
done

# Step 3: Start Scaled Microservices
echo ""
echo "=================================================================="
echo "Step 3: Starting Scaled Microservices (3 replicas per service)..."
echo "=================================================================="

cd "$PROJECT_ROOT/tasktracker-micro"

# Start using scalable compose file
echo "Starting databases..."
docker compose -f docker-compose.scalable.yml up -d user-db task-db

echo "Waiting for databases to be ready..."
sleep 10

echo "Starting services with 3 replicas each..."
docker compose -f docker-compose.scalable.yml up -d --scale user-service=3 --scale task-service=3 --scale stats-service=3

echo "Starting API Gateway..."
docker compose -f docker-compose.scalable.yml up -d api-gateway

echo "Waiting for scaled microservices to be healthy..."
for i in {1..60}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✓ Scaled Microservices are healthy!"
        break
    fi
    if [ $i -eq 60 ]; then
        echo "✗ Scaled Microservices failed to start within 60 seconds"
        exit 1
    fi
    echo "  Waiting... ($i/60)"
    sleep 1
done

# Show running services
echo ""
echo "Running services:"
docker compose -f docker-compose.scalable.yml ps --format "table {{.Name}}\t{{.Status}}"

# Step 4: Run Parameter Sweep
echo ""
echo "=================================================================="
echo "Step 4: Running Parameter Sweep Tests..."
echo "=================================================================="

cd "$PROJECT_ROOT"

# Run sweep with focus on the comparison
python experiments/run_sweep.py \
    --arch both \
    --concurrency-levels 10,25,50,100,200 \
    --duration-seconds 60 \
    --warmup-seconds 10 \
    --spawn-rate 10 \
    --outdir experiments/results/scaled_comparison_$(date +%Y%m%d_%H%M%S)

# The script will save results to the specified directory
RESULTS_DIR=$(ls -td experiments/results/scaled_comparison_* | head -1)

echo ""
echo "=================================================================="
echo "Step 5: Generating Comparison Charts..."
echo "=================================================================="

python experiments/plot_results.py "$RESULTS_DIR"

PLOTS_DIR=$(ls -td experiments/plots/* | head -1)

echo ""
echo "=================================================================="
echo "TEST COMPLETE!"
echo "=================================================================="
echo ""
echo "Results saved to:"
echo "  Data: $RESULTS_DIR"
echo "  Plots: $PLOTS_DIR"
echo ""
echo "Key files to review:"
echo "  - $RESULTS_DIR/config.json"
echo "  - $RESULTS_DIR/results.jsonl"
echo "  - $PLOTS_DIR/crossover_analysis.png"
echo "  - $PLOTS_DIR/latency_p95_vs_concurrency.png"
echo "  - $PLOTS_DIR/efficiency_vs_concurrency.png"
echo ""
echo "To view results:"
echo "  open $PLOTS_DIR"
echo ""
echo "Services are still running. To stop them:"
echo "  cd tasktracker-mono && docker compose down"
echo "  cd tasktracker-micro && docker compose -f docker-compose.scalable.yml down"
echo ""
