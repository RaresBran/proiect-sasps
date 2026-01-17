#!/bin/bash
# ============================================================
# Crossover Curve Parameter Sweep
# ============================================================
# Runs load tests at multiple concurrency levels and generates
# plots showing the crossover point where microservices 
# outperforms monolithic.
#
# Usage:
#   ./run_crossover_sweep.sh                    # Default settings
#   ./run_crossover_sweep.sh --quick            # Quick test (fewer levels)
#   ./run_crossover_sweep.sh --full             # Full comprehensive test
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Activate venv if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

echo "=============================================="
echo "   CROSSOVER CURVE PARAMETER SWEEP"
echo "=============================================="
echo ""

# Parse arguments
MODE="default"
if [ "$1" == "--quick" ]; then
    MODE="quick"
elif [ "$1" == "--full" ]; then
    MODE="full"
fi

case $MODE in
    quick)
        echo "Mode: QUICK (3 levels, 60s each)"
        LEVELS="25,75,150"
        RUN_TIME="60s"
        ;;
    full)
        echo "Mode: FULL (8 levels, 2m each)"
        LEVELS="25,50,75,100,125,150,175,200"
        RUN_TIME="2m"
        ;;
    *)
        echo "Mode: DEFAULT (6 levels, 90s each)"
        LEVELS="25,50,75,100,150,200"
        RUN_TIME="90s"
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
echo "Starting sweep..."
echo ""

# Run the Python script
python experiments/crossover_sweep.py \
    --concurrency-levels "$LEVELS" \
    --run-time "$RUN_TIME" \
    --spawn-rate 10

echo ""
echo "=============================================="
echo "SWEEP COMPLETE!"
echo "=============================================="
echo ""
echo "Results are in: results/crossover_*/"
echo "Key plots:"
echo "  - crossover_throughput.png"
echo "  - crossover_response_time.png"
echo "  - crossover_dashboard.png"
echo ""
