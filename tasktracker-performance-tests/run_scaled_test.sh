#!/bin/bash
# Run high-load performance test comparing single vs scaled microservices

echo "=========================================="
echo "HIGH-LOAD PERFORMANCE TEST"
echo "Monolithic vs Scaled Microservices"
echo "=========================================="
echo ""

# Configuration for high load
USERS=${USERS:-200}        # More concurrent users
SPAWN_RATE=${SPAWN_RATE:-20}  # Faster spawn rate
RUN_TIME=${RUN_TIME:-5m}   # Longer test duration

echo "High-Load Configuration:"
echo "  Users: $USERS concurrent users"
echo "  Spawn Rate: $SPAWN_RATE users/sec"
echo "  Run Time: $RUN_TIME"
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
    echo "✓ Scaled microservices app is running on port 8000"
    MICRO_RUNNING=true
else
    echo "❌ Scaled microservices app is NOT running on port 8000"
fi

echo ""

if [ "$MONO_RUNNING" = false ] || [ "$MICRO_RUNNING" = false ]; then
    echo "❌ ERROR: Both applications must be running!"
    echo ""
    echo "Start them with:"
    echo "  Terminal 1: cd ../tasktracker-mono && docker compose up -d"
    echo "  Terminal 2: cd ../tasktracker-micro && ./start-scaled.sh"
    exit 1
fi

# Create results directory with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
MONO_DIR="results/monolithic_highload_${TIMESTAMP}"
MICRO_DIR="results/microservices_scaled_${TIMESTAMP}"
mkdir -p "$MONO_DIR" "$MICRO_DIR"

echo "Starting HIGH-LOAD tests in parallel..."
echo "  Monolithic results: $MONO_DIR"
echo "  Scaled Microservices results: $MICRO_DIR"
echo ""

# Run both tests in parallel
(
    echo "[MONO] Starting monolithic high-load test..."
    locust -f locustfile_monolithic.py \
        --headless \
        --users $USERS \
        --spawn-rate $SPAWN_RATE \
        --run-time $RUN_TIME \
        --html "$MONO_DIR/report.html" \
        --csv "$MONO_DIR/stats" \
        --logfile "$MONO_DIR/locust.log" \
        --loglevel INFO
    echo "[MONO] High-load test completed!"
) &

(
    echo "[MICRO-SCALED] Starting scaled microservices high-load test..."
    locust -f locustfile_microservices.py \
        --headless \
        --users $USERS \
        --spawn-rate $SPAWN_RATE \
        --run-time $RUN_TIME \
        --html "$MICRO_DIR/report.html" \
        --csv "$MICRO_DIR/stats" \
        --logfile "$MICRO_DIR/locust.log" \
        --loglevel INFO
    echo "[MICRO-SCALED] High-load test completed!"
) &

# Wait for both tests to complete
wait

echo ""
echo "=========================================="
echo "BOTH HIGH-LOAD TESTS COMPLETED!"
echo "=========================================="
echo ""
echo "Now generating comparison charts..."
echo ""

# Generate comparison charts
python analyze_results.py \
    "$MONO_DIR/stats_stats.csv" \
    "$MICRO_DIR/stats_stats.csv" \
    "results/comparison_highload_${TIMESTAMP}"

echo ""
echo "=========================================="
echo "ALL DONE!"
echo "=========================================="
echo ""
echo "Test Configuration:"
echo "  Monolithic: 1 application instance"
echo "  Microservices: 3 replicas per service (9 total instances)"
echo "  Load: $USERS concurrent users"
echo "  Duration: $RUN_TIME"
echo ""
echo "Individual Results:"
echo "  Monolithic: $MONO_DIR/"
echo "  Scaled Microservices: $MICRO_DIR/"
echo ""
echo "Comparison Charts:"
echo "  results/comparison_highload_${TIMESTAMP}/"
echo ""
echo "Open the HTML reports in your browser:"
echo "  Monolithic: open $MONO_DIR/report.html"
echo "  Scaled Microservices: open $MICRO_DIR/report.html"
echo ""
echo "Compare with standard test to see scaling benefits!"
echo ""

