#!/bin/bash
# ============================================================
# Resource Efficiency Monitor
# ============================================================
# Collects CPU and memory usage during load tests and
# generates efficiency metrics plots.
#
# Usage:
#   ./run_resource_monitor.sh                   # Default settings
#   ./run_resource_monitor.sh --quick           # Quick test
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Activate venv if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

echo "=============================================="
echo "   RESOURCE EFFICIENCY MONITOR"
echo "=============================================="
echo ""

# Parse arguments
MODE="default"
if [ "$1" == "--quick" ]; then
    MODE="quick"
fi

case $MODE in
    quick)
        echo "Mode: QUICK (2 levels, 45s each)"
        LEVELS="50,150"
        RUN_TIME="45s"
        ;;
    *)
        echo "Mode: DEFAULT (4 levels, 60s each)"
        LEVELS="50,100,150,200"
        RUN_TIME="60s"
        ;;
esac

echo "Concurrency levels: $LEVELS"
echo "Run time per test: $RUN_TIME"
echo ""

# Check apps
echo "Checking applications..."
MONO_OK=false
MICRO_OK=false

if curl -s http://localhost:9000/health > /dev/null 2>&1; then
    echo "  ✓ Monolithic running on port 9000"
    MONO_OK=true
else
    echo "  ✗ Monolithic NOT running on port 9000"
fi

if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "  ✓ Microservices running on port 8000"
    MICRO_OK=true
else
    echo "  ✗ Microservices NOT running on port 8000"
fi

if [ "$MONO_OK" = false ] || [ "$MICRO_OK" = false ]; then
    echo ""
    echo "❌ Both applications must be running!"
    echo ""
    echo "Start them with:"
    echo "  cd ../tasktracker-mono && docker compose up -d"
    echo "  cd ../tasktracker-micro && docker compose up -d"
    exit 1
fi

echo ""
echo "Starting resource monitoring sweep..."
echo ""

# Run the Python script
python experiments/resource_monitor.py \
    --concurrency-levels "$LEVELS" \
    --run-time "$RUN_TIME" \
    --spawn-rate 10

echo ""
echo "=============================================="
echo "RESOURCE MONITORING COMPLETE!"
echo "=============================================="
echo ""
echo "Results are in: results/resource_*/"
echo "Key plots:"
echo "  - resource_cpu_usage.png"
echo "  - resource_memory_usage.png"
echo "  - resource_efficiency.png"
echo "  - resource_dashboard.png"
echo ""
