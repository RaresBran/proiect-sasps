#!/bin/bash
# Run performance tests for BOTH architectures in parallel

echo "=========================================="
echo "RUNNING BOTH ARCHITECTURE TESTS IN PARALLEL"
echo "=========================================="
echo ""

# Check if both applications are running
echo "Checking if both applications are running..."

MONO_RUNNING=false
MICRO_RUNNING=false

if curl -s http://localhost:9000/health > /dev/null; then
    echo "✓ Monolithic app is running on port 9000"
    MONO_RUNNING=true
else
    echo "❌ Monolithic app is NOT running on port 9000"
fi

if curl -s http://localhost:8000/health > /dev/null; then
    echo "✓ Microservices app is running on port 8000"
    MICRO_RUNNING=true
else
    echo "❌ Microservices app is NOT running on port 8000"
fi

echo ""

if [ "$MONO_RUNNING" = false ] || [ "$MICRO_RUNNING" = false ]; then
    echo "❌ ERROR: Both applications must be running!"
    echo ""
    echo "Start them with:"
    echo "  Terminal 1: cd ../tasktracker-mono && docker compose up -d"
    echo "  Terminal 2: cd ../tasktracker-micro && docker compose up -d"
    exit 1
fi

# Configuration
USERS=${USERS:-50}
SPAWN_RATE=${SPAWN_RATE:-10}
RUN_TIME=${RUN_TIME:-3m}  # Increased default to 3 minutes

echo "Test Configuration:"
echo "  Users: $USERS"
echo "  Spawn Rate: $SPAWN_RATE users/sec"
echo "  Run Time: $RUN_TIME"
echo ""

# Create results directory with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
MONO_DIR="results/monolithic_${TIMESTAMP}"
MICRO_DIR="results/microservices_${TIMESTAMP}"
mkdir -p "$MONO_DIR" "$MICRO_DIR"

echo "Starting tests in parallel..."
echo "  Monolithic results: $MONO_DIR"
echo "  Microservices results: $MICRO_DIR"
echo ""

# Run both tests in parallel
(
    echo "[MONO] Starting monolithic test..."
    locust -f locustfile_monolithic.py \
        --headless \
        --users $USERS \
        --spawn-rate $SPAWN_RATE \
        --run-time $RUN_TIME \
        --html "$MONO_DIR/report.html" \
        --csv "$MONO_DIR/stats" \
        --logfile "$MONO_DIR/locust.log" \
        --loglevel INFO
    echo "[MONO] Test completed!"
) &

(
    echo "[MICRO] Starting microservices test..."
    locust -f locustfile_microservices.py \
        --headless \
        --users $USERS \
        --spawn-rate $SPAWN_RATE \
        --run-time $RUN_TIME \
        --html "$MICRO_DIR/report.html" \
        --csv "$MICRO_DIR/stats" \
        --logfile "$MICRO_DIR/locust.log" \
        --loglevel INFO
    echo "[MICRO] Test completed!"
) &

# Wait for both tests to complete
wait

echo ""
echo "=========================================="
echo "BOTH TESTS COMPLETED!"
echo "=========================================="
echo ""
echo "Now generating comparison charts..."
echo ""

# Generate comparison charts
python analyze_results.py \
    "$MONO_DIR/stats_stats.csv" \
    "$MICRO_DIR/stats_stats.csv" \
    "results/comparison_${TIMESTAMP}"

echo ""
echo "=========================================="
echo "ALL DONE!"
echo "=========================================="
echo ""
echo "Individual Results:"
echo "  Monolithic: $MONO_DIR/"
echo "  Microservices: $MICRO_DIR/"
echo ""
echo "Comparison Charts:"
echo "  results/comparison_${TIMESTAMP}/"
echo ""
echo "Open the HTML reports in your browser:"
echo "  Monolithic: open $MONO_DIR/report.html"
echo "  Microservices: open $MICRO_DIR/report.html"
echo ""

