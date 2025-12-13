#!/bin/bash
# Run performance tests for Microservices Architecture

echo "============================================="
echo "MICROSERVICES ARCHITECTURE PERFORMANCE TEST"
echo "============================================="
echo ""

# Check if applications are running
echo "Checking if Microservices app is running on port 8000..."
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ ERROR: Microservices app is not running on port 8000"
    echo "Please start it first with:"
    echo "  cd ../tasktracker-micro && docker compose up -d"
    exit 1
fi

echo "✓ Microservices app is running"
echo ""

# Configuration
USERS=${USERS:-50}
SPAWN_RATE=${SPAWN_RATE:-10}
RUN_TIME=${RUN_TIME:-3m}  # Increased default to 3 minutes

echo "Test Configuration:"
echo "  Users: $USERS"
echo "  Spawn Rate: $SPAWN_RATE users/sec"
echo "  Run Time: $RUN_TIME"
echo ""

# Create results directory
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULTS_DIR="results/microservices_${TIMESTAMP}"
mkdir -p "$RESULTS_DIR"

echo "Running Locust test..."
echo "Results will be saved to: $RESULTS_DIR"
echo ""

# Run Locust in headless mode
locust -f locustfile_microservices.py \
    --headless \
    --users $USERS \
    --spawn-rate $SPAWN_RATE \
    --run-time $RUN_TIME \
    --html "$RESULTS_DIR/report.html" \
    --csv "$RESULTS_DIR/stats" \
    --logfile "$RESULTS_DIR/locust.log" \
    --loglevel INFO

echo ""
echo "=========================================="
echo "TEST COMPLETED!"
echo "=========================================="
echo "Results saved to: $RESULTS_DIR"
echo "  - HTML Report: $RESULTS_DIR/report.html"
echo "  - CSV Stats: $RESULTS_DIR/stats_stats.csv"
echo "  - Log File: $RESULTS_DIR/locust.log"
echo ""

