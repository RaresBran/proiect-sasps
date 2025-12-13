#!/bin/bash
# Interactive test runner with options

echo "=========================================="
echo "TASKTRACKER PERFORMANCE TEST RUNNER"
echo "=========================================="
echo ""

# Function to check if app is running
check_app() {
    local url=$1
    local name=$2
    if curl -s "$url/health" > /dev/null; then
        echo "✓ $name is running"
        return 0
    else
        echo "❌ $name is NOT running"
        return 1
    fi
}

# Check applications
echo "Checking applications..."
MONO_RUNNING=false
MICRO_RUNNING=false

if check_app "http://localhost:9000" "Monolithic (port 9000)"; then
    MONO_RUNNING=true
fi

if check_app "http://localhost:8000" "Microservices (port 8000)"; then
    MICRO_RUNNING=true
fi

echo ""

# Menu
echo "What would you like to test?"
echo "  1) Monolithic only"
echo "  2) Microservices only"
echo "  3) Both (in parallel)"
echo "  4) Exit"
echo ""
read -p "Select option [1-4]: " option

case $option in
    1)
        if [ "$MONO_RUNNING" = false ]; then
            echo "❌ Monolithic app is not running!"
            echo "Start it: cd ../tasktracker-mono && docker compose up -d"
            exit 1
        fi
        ;;
    2)
        if [ "$MICRO_RUNNING" = false ]; then
            echo "❌ Microservices app is not running!"
            echo "Start it: cd ../tasktracker-micro && docker compose up -d"
            exit 1
        fi
        ;;
    3)
        if [ "$MONO_RUNNING" = false ] || [ "$MICRO_RUNNING" = false ]; then
            echo "❌ Both apps must be running!"
            echo "Start them:"
            echo "  cd ../tasktracker-mono && docker compose up -d"
            echo "  cd ../tasktracker-micro && docker compose up -d"
            exit 1
        fi
        ;;
    4)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac

echo ""
echo "Test Configuration:"
read -p "Number of users (default 50): " users
users=${users:-50}

read -p "Spawn rate (users/sec, default 10): " spawn_rate
spawn_rate=${spawn_rate:-10}

read -p "Run time (e.g., 60s, 5m, default 60s): " run_time
run_time=${run_time:-60s}

export USERS=$users
export SPAWN_RATE=$spawn_rate
export RUN_TIME=$run_time

echo ""
echo "Configuration:"
echo "  Users: $USERS"
echo "  Spawn Rate: $SPAWN_RATE"
echo "  Run Time: $RUN_TIME"
echo ""
read -p "Press Enter to start..."

case $option in
    1)
        ./run_mono_test.sh
        ;;
    2)
        ./run_micro_test.sh
        ;;
    3)
        ./run_both_tests.sh
        ;;
esac

