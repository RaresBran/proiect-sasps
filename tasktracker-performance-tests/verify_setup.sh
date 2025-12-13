#!/bin/bash
# Verify setup and check if everything is ready

echo "=========================================="
echo "PERFORMANCE TEST SETUP VERIFICATION"
echo "=========================================="
echo ""

# Check Python
echo "1. Checking Python..."
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version)
    echo "   ✓ $python_version"
else
    echo "   ❌ Python 3 not found"
    exit 1
fi

# Check pip
echo "2. Checking pip..."
if command -v pip3 &> /dev/null; then
    pip_version=$(pip3 --version | awk '{print $2}')
    echo "   ✓ pip $pip_version"
else
    echo "   ❌ pip not found"
    exit 1
fi

# Check virtual environment
echo "3. Checking virtual environment..."
if [ -d "venv" ]; then
    echo "   ✓ Virtual environment exists"
else
    echo "   ⚠ Virtual environment not found (run ./setup.sh)"
fi

# Check dependencies
echo "4. Checking dependencies..."
if [ -f "requirements.txt" ]; then
    echo "   ✓ requirements.txt found"
else
    echo "   ❌ requirements.txt missing"
    exit 1
fi

# Check scripts
echo "5. Checking scripts..."
scripts=(
    "setup.sh"
    "run_mono_test.sh"
    "run_micro_test.sh"
    "run_both_tests.sh"
    "run_tests.sh"
    "compare_results.sh"
    "cleanup.sh"
)

all_executable=true
for script in "${scripts[@]}"; do
    if [ -x "$script" ]; then
        echo "   ✓ $script is executable"
    else
        echo "   ⚠ $script is NOT executable (run chmod +x *.sh)"
        all_executable=false
    fi
done

# Check applications
echo ""
echo "6. Checking applications..."
mono_running=false
micro_running=false

if curl -s http://localhost:9000/health > /dev/null 2>&1; then
    echo "   ✓ Monolithic app is running (port 9000)"
    mono_running=true
else
    echo "   ⚠ Monolithic app is NOT running (port 9000)"
    echo "     Start: cd ../tasktracker-mono && docker compose up -d"
fi

if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✓ Microservices app is running (port 8000)"
    micro_running=true
else
    echo "   ⚠ Microservices app is NOT running (port 8000)"
    echo "     Start: cd ../tasktracker-micro && docker compose up -d"
fi

echo ""
echo "=========================================="
echo "VERIFICATION SUMMARY"
echo "=========================================="

ready=true

if [ "$all_executable" = false ]; then
    echo "⚠ Some scripts are not executable"
    echo "   Fix: chmod +x *.sh"
    ready=false
fi

if [ ! -d "venv" ]; then
    echo "⚠ Virtual environment not set up"
    echo "   Fix: ./setup.sh"
    ready=false
fi

if [ "$mono_running" = false ] || [ "$micro_running" = false ]; then
    echo "⚠ One or both applications are not running"
    echo "   Fix: Start the applications with docker compose"
    ready=false
fi

echo ""

if [ "$ready" = true ]; then
    echo "✅ EVERYTHING IS READY!"
    echo ""
    echo "You can now run tests:"
    echo "  ./run_tests.sh (interactive)"
    echo "  ./run_both_tests.sh (run both)"
else
    echo "⚠ SETUP INCOMPLETE"
    echo ""
    echo "Please fix the issues above before running tests."
fi

echo ""

