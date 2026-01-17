#!/bin/bash
# ============================================================
# Resilience / Failure Injection Test
# ============================================================
# Runs steady load on microservices, then intentionally stops
# a service mid-run to demonstrate fault isolation and recovery.
#
# Usage:
#   ./run_resilience_test.sh                    # Default (task-service)
#   ./run_resilience_test.sh user-service       # Target user-service
#   ./run_resilience_test.sh api-gateway        # Target api-gateway
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Activate venv if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

echo "=============================================="
echo "   RESILIENCE / FAILURE INJECTION TEST"
echo "=============================================="
echo ""

# Parse target service
TARGET_SERVICE="${1:-task-service}"

echo "Target service: $TARGET_SERVICE"
echo ""

# Validate target
case $TARGET_SERVICE in
    task-service|user-service|stats-service|api-gateway)
        ;;
    *)
        echo "❌ Invalid target service: $TARGET_SERVICE"
        echo ""
        echo "Valid options:"
        echo "  - task-service (default)"
        echo "  - user-service"
        echo "  - stats-service"
        echo "  - api-gateway"
        exit 1
        ;;
esac

# Check microservices
echo "Checking microservices..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "  ✓ Microservices running on port 8000"
else
    echo "  ✗ Microservices NOT running on port 8000"
    echo ""
    echo "❌ Microservices must be running!"
    echo ""
    echo "Start with: cd ../tasktracker-micro && docker compose up -d"
    exit 1
fi

echo ""
echo "Test configuration:"
echo "  - Duration: 120 seconds"
echo "  - Fault injection at: 30 seconds"
echo "  - Fault duration: 30 seconds"
echo "  - Users: 50 concurrent"
echo ""

read -p "Press Enter to start the resilience test..."

echo ""
echo "Starting resilience test..."
echo ""

# Run the Python script
python experiments/resilience_test.py \
    --target-service "$TARGET_SERVICE" \
    --users 50 \
    --spawn-rate 10 \
    --duration 120 \
    --fault-start 30 \
    --fault-duration 30

echo ""
echo "=============================================="
echo "RESILIENCE TEST COMPLETE!"
echo "=============================================="
echo ""
echo "Results are in: results/resilience_*/"
echo "Key plots:"
echo "  - resilience_timeline.png (3-panel view)"
echo "  - resilience_summary.png (combined view)"
echo ""
echo "This demonstrates:"
echo "  1. System handles normal load before fault"
echo "  2. Error rate spikes when $TARGET_SERVICE is stopped"
echo "  3. System recovers after service restarts"
echo ""
