#!/bin/bash
# Quick setup script

echo "=========================================="
echo "TASKTRACKER PERFORMANCE TESTS - SETUP"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"
echo ""

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

echo ""

# Activate and install dependencies
echo "Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

echo ""
echo "✓ Dependencies installed"
echo ""

# Make scripts executable
echo "Making scripts executable..."
chmod +x run_*.sh
echo "✓ Scripts are executable"
echo ""

# Create results directory
mkdir -p results
echo "✓ Results directory created"
echo ""

echo "=========================================="
echo "SETUP COMPLETE!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Start both applications:"
echo "     Terminal 1: cd ../tasktracker-mono && docker compose up -d"
echo "     Terminal 2: cd ../tasktracker-micro && docker compose up -d"
echo ""
echo "  2. Activate virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  3. Run tests:"
echo "     ./run_tests.sh (interactive)"
echo "     ./run_both_tests.sh (run both in parallel)"
echo ""

