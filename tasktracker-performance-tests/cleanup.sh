#!/bin/bash
# Cleanup old test results

echo "=========================================="
echo "CLEANUP OLD TEST RESULTS"
echo "=========================================="
echo ""

if [ ! -d "results" ]; then
    echo "No results directory found. Nothing to clean."
    exit 0
fi

# Count results
num_dirs=$(find results -maxdepth 1 -type d | wc -l)
num_dirs=$((num_dirs - 1))  # Subtract the results directory itself

if [ $num_dirs -eq 0 ]; then
    echo "No test results found. Nothing to clean."
    exit 0
fi

echo "Found $num_dirs result directories"
echo ""

# Ask for confirmation
read -p "Delete all test results? [y/N] " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Deleting..."
    rm -rf results/*
    echo "✓ All test results deleted"
else
    echo "Cancelled."
fi

echo ""

