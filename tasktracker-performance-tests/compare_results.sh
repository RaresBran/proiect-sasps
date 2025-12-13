#!/bin/bash
# Compare results from two test runs

echo "=========================================="
echo "COMPARE TEST RESULTS"
echo "=========================================="
echo ""

if [ ! -d "results" ]; then
    echo "No results directory found."
    exit 1
fi

# List available results
echo "Available test results:"
echo ""
mono_dirs=($(find results -maxdepth 1 -type d -name "monolithic_*" | sort))
micro_dirs=($(find results -maxdepth 1 -type d -name "microservices_*" | sort))

if [ ${#mono_dirs[@]} -eq 0 ] || [ ${#micro_dirs[@]} -eq 0 ]; then
    echo "Not enough test results found."
    echo "You need at least one monolithic and one microservices result."
    exit 1
fi

echo "Monolithic results:"
for i in "${!mono_dirs[@]}"; do
    dir=$(basename "${mono_dirs[$i]}")
    echo "  [$i] $dir"
done

echo ""
echo "Microservices results:"
for i in "${!micro_dirs[@]}"; do
    dir=$(basename "${micro_dirs[$i]}")
    echo "  [$i] $dir"
done

echo ""
read -p "Select monolithic result [0-$((${#mono_dirs[@]}-1))]: " mono_idx
read -p "Select microservices result [0-$((${#micro_dirs[@]}-1))]: " micro_idx

mono_result="${mono_dirs[$mono_idx]}"
micro_result="${micro_dirs[$micro_idx]}"

if [ ! -d "$mono_result" ] || [ ! -d "$micro_result" ]; then
    echo "Invalid selection"
    exit 1
fi

mono_stats="$mono_result/stats_stats.csv"
micro_stats="$micro_result/stats_stats.csv"

if [ ! -f "$mono_stats" ] || [ ! -f "$micro_stats" ]; then
    echo "Statistics files not found"
    exit 1
fi

echo ""
echo "Comparing:"
echo "  Monolithic: $(basename $mono_result)"
echo "  Microservices: $(basename $micro_result)"
echo ""

# Generate comparison
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
output_dir="results/comparison_${TIMESTAMP}"

echo "Generating comparison charts..."
python analyze_results.py "$mono_stats" "$micro_stats" "$output_dir"

echo ""
echo "=========================================="
echo "COMPARISON COMPLETE!"
echo "=========================================="
echo "Results saved to: $output_dir/"
echo ""
echo "View charts:"
echo "  open $output_dir/"
echo ""

