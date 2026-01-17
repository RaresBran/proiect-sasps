#!/usr/bin/env python3
"""
Plot results from sweep experiments.

Generates comparison charts for monolith vs microservices performance.

Usage:
    python plot_results.py <results_dir>
    python plot_results.py experiments/results/sweep_20240115_143022
"""
import argparse
import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from experiments.lib.io_utils import read_json, read_jsonl, get_project_root

# Try to import matplotlib
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Install with: pip install matplotlib")


def load_results(results_dir: Path) -> List[Dict[str, Any]]:
    """Load results from a sweep experiment directory."""
    jsonl_path = results_dir / "results.jsonl"
    json_path = results_dir / "all_results.json"
    
    if jsonl_path.exists():
        return read_jsonl(jsonl_path)
    elif json_path.exists():
        return read_json(json_path)
    else:
        raise FileNotFoundError(f"No results found in {results_dir}")


def split_by_arch(results: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Split results by architecture."""
    by_arch = {"monolith": [], "microservices": []}
    for r in results:
        arch = r.get("arch", "unknown")
        if arch in by_arch:
            by_arch[arch].append(r)
    return by_arch


def setup_plot_style():
    """Configure matplotlib style."""
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams['figure.figsize'] = (10, 6)
    plt.rcParams['font.size'] = 11
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['legend.fontsize'] = 10
    plt.rcParams['figure.dpi'] = 150


def plot_latency_vs_concurrency(results: List[Dict[str, Any]], 
                                 output_path: Path,
                                 percentile: str = "p95") -> None:
    """Plot latency percentile vs concurrency for both architectures."""
    by_arch = split_by_arch(results)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = {"monolith": "#2E86AB", "microservices": "#E94F37"}
    markers = {"monolith": "o", "microservices": "s"}
    
    latency_key = f"latency_{percentile}_ms"
    
    for arch, data in by_arch.items():
        if not data:
            continue
        
        # Sort by concurrency
        data = sorted(data, key=lambda x: x.get("concurrency", 0))
        
        concurrency = [d["concurrency"] for d in data]
        latency = [d.get(latency_key, 0) for d in data]
        
        ax.plot(concurrency, latency, 
                marker=markers[arch], 
                color=colors[arch],
                linewidth=2, 
                markersize=8,
                label=arch.capitalize())
    
    ax.set_xlabel("Concurrent Users")
    ax.set_ylabel(f"Latency {percentile.upper()} (ms)")
    ax.set_title(f"Latency ({percentile.upper()}) vs Concurrency")
    ax.legend(loc="upper left")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")


def plot_throughput_vs_concurrency(results: List[Dict[str, Any]], 
                                    output_path: Path) -> None:
    """Plot throughput (req/s) vs concurrency for both architectures."""
    by_arch = split_by_arch(results)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = {"monolith": "#2E86AB", "microservices": "#E94F37"}
    markers = {"monolith": "o", "microservices": "s"}
    
    for arch, data in by_arch.items():
        if not data:
            continue
        
        data = sorted(data, key=lambda x: x.get("concurrency", 0))
        
        concurrency = [d["concurrency"] for d in data]
        throughput = [d.get("throughput_rps", 0) for d in data]
        
        ax.plot(concurrency, throughput,
                marker=markers[arch],
                color=colors[arch],
                linewidth=2,
                markersize=8,
                label=arch.capitalize())
    
    ax.set_xlabel("Concurrent Users")
    ax.set_ylabel("Throughput (req/s)")
    ax.set_title("Throughput vs Concurrency")
    ax.legend(loc="upper left")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")


def plot_error_rate_vs_concurrency(results: List[Dict[str, Any]], 
                                    output_path: Path) -> None:
    """Plot error rate vs concurrency for both architectures."""
    by_arch = split_by_arch(results)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = {"monolith": "#2E86AB", "microservices": "#E94F37"}
    markers = {"monolith": "o", "microservices": "s"}
    
    for arch, data in by_arch.items():
        if not data:
            continue
        
        data = sorted(data, key=lambda x: x.get("concurrency", 0))
        
        concurrency = [d["concurrency"] for d in data]
        error_rate = [d.get("error_rate", 0) for d in data]
        
        ax.plot(concurrency, error_rate,
                marker=markers[arch],
                color=colors[arch],
                linewidth=2,
                markersize=8,
                label=arch.capitalize())
    
    ax.set_xlabel("Concurrent Users")
    ax.set_ylabel("Error Rate (%)")
    ax.set_title("Error Rate vs Concurrency")
    ax.legend(loc="upper left")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")


def plot_cpu_vs_concurrency(results: List[Dict[str, Any]], 
                             output_path: Path) -> None:
    """Plot total CPU usage vs concurrency for both architectures."""
    by_arch = split_by_arch(results)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = {"monolith": "#2E86AB", "microservices": "#E94F37"}
    markers = {"monolith": "o", "microservices": "s"}
    
    for arch, data in by_arch.items():
        if not data:
            continue
        
        data = sorted(data, key=lambda x: x.get("concurrency", 0))
        
        concurrency = [d["concurrency"] for d in data]
        cpu_units = []
        for d in data:
            eff = d.get("efficiency", {})
            cpu_units.append(eff.get("total_cpu_units", 0))
        
        ax.plot(concurrency, cpu_units,
                marker=markers[arch],
                color=colors[arch],
                linewidth=2,
                markersize=8,
                label=arch.capitalize())
    
    ax.set_xlabel("Concurrent Users")
    ax.set_ylabel("CPU Units (100% = 1 vCPU)")
    ax.set_title("CPU Usage vs Concurrency")
    ax.legend(loc="upper left")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")


def plot_efficiency_vs_concurrency(results: List[Dict[str, Any]], 
                                    output_path: Path) -> None:
    """Plot throughput per CPU unit vs concurrency for both architectures."""
    by_arch = split_by_arch(results)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = {"monolith": "#2E86AB", "microservices": "#E94F37"}
    markers = {"monolith": "o", "microservices": "s"}
    
    for arch, data in by_arch.items():
        if not data:
            continue
        
        data = sorted(data, key=lambda x: x.get("concurrency", 0))
        
        concurrency = [d["concurrency"] for d in data]
        rps_per_cpu = []
        for d in data:
            eff = d.get("efficiency", {})
            rps_per_cpu.append(eff.get("rps_per_cpu_unit", 0))
        
        ax.plot(concurrency, rps_per_cpu,
                marker=markers[arch],
                color=colors[arch],
                linewidth=2,
                markersize=8,
                label=arch.capitalize())
    
    ax.set_xlabel("Concurrent Users")
    ax.set_ylabel("Throughput per CPU Unit (req/s per vCPU)")
    ax.set_title("CPU Efficiency vs Concurrency")
    ax.legend(loc="upper right")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")


def plot_crossover_chart(results: List[Dict[str, Any]], 
                          output_path: Path) -> None:
    """Plot combined chart showing crossover point between architectures."""
    by_arch = split_by_arch(results)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    colors = {"monolith": "#2E86AB", "microservices": "#E94F37"}
    markers = {"monolith": "o", "microservices": "s"}
    
    # Plot 1: Latency P95
    for arch, data in by_arch.items():
        if not data:
            continue
        data = sorted(data, key=lambda x: x.get("concurrency", 0))
        concurrency = [d["concurrency"] for d in data]
        latency = [d.get("latency_p95_ms", 0) for d in data]
        ax1.plot(concurrency, latency, marker=markers[arch], color=colors[arch],
                linewidth=2, markersize=8, label=arch.capitalize())
    
    ax1.set_xlabel("Concurrent Users")
    ax1.set_ylabel("Latency P95 (ms)")
    ax1.set_title("Latency P95 vs Concurrency")
    ax1.legend(loc="upper left")
    ax1.set_xlim(left=0)
    ax1.set_ylim(bottom=0)
    
    # Plot 2: Throughput
    for arch, data in by_arch.items():
        if not data:
            continue
        data = sorted(data, key=lambda x: x.get("concurrency", 0))
        concurrency = [d["concurrency"] for d in data]
        throughput = [d.get("throughput_rps", 0) for d in data]
        ax2.plot(concurrency, throughput, marker=markers[arch], color=colors[arch],
                linewidth=2, markersize=8, label=arch.capitalize())
    
    ax2.set_xlabel("Concurrent Users")
    ax2.set_ylabel("Throughput (req/s)")
    ax2.set_title("Throughput vs Concurrency")
    ax2.legend(loc="upper left")
    ax2.set_xlim(left=0)
    ax2.set_ylim(bottom=0)
    
    plt.suptitle("Architecture Performance Crossover Analysis", fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")


def plot_memory_vs_concurrency(results: List[Dict[str, Any]], 
                                output_path: Path) -> None:
    """Plot total memory usage vs concurrency for both architectures."""
    by_arch = split_by_arch(results)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = {"monolith": "#2E86AB", "microservices": "#E94F37"}
    markers = {"monolith": "o", "microservices": "s"}
    
    for arch, data in by_arch.items():
        if not data:
            continue
        
        data = sorted(data, key=lambda x: x.get("concurrency", 0))
        
        concurrency = [d["concurrency"] for d in data]
        mem_gb = []
        for d in data:
            eff = d.get("efficiency", {})
            mem_gb.append(eff.get("total_mem_gb", 0))
        
        ax.plot(concurrency, mem_gb,
                marker=markers[arch],
                color=colors[arch],
                linewidth=2,
                markersize=8,
                label=arch.capitalize())
    
    ax.set_xlabel("Concurrent Users")
    ax.set_ylabel("Memory Usage (GB)")
    ax.set_title("Memory Usage vs Concurrency")
    ax.legend(loc="upper left")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")


def generate_all_plots(results_dir: Path, plots_dir: Optional[Path] = None) -> Path:
    """Generate all plots from experiment results."""
    if not MATPLOTLIB_AVAILABLE:
        print("Error: matplotlib is required for plotting")
        print("Install with: pip install matplotlib")
        sys.exit(1)
    
    setup_plot_style()
    
    # Load results
    results = load_results(results_dir)
    
    if not results:
        print("No results found to plot")
        sys.exit(1)
    
    print(f"Loaded {len(results)} results")
    
    # Create plots directory
    if plots_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plots_dir = get_project_root() / "experiments" / "plots" / timestamp
    
    plots_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating plots in: {plots_dir}")
    
    # Generate all plots
    plot_latency_vs_concurrency(results, plots_dir / "latency_p95_vs_concurrency.png", "p95")
    plot_latency_vs_concurrency(results, plots_dir / "latency_p99_vs_concurrency.png", "p99")
    plot_latency_vs_concurrency(results, plots_dir / "latency_p50_vs_concurrency.png", "p50")
    plot_throughput_vs_concurrency(results, plots_dir / "throughput_vs_concurrency.png")
    plot_error_rate_vs_concurrency(results, plots_dir / "error_rate_vs_concurrency.png")
    plot_cpu_vs_concurrency(results, plots_dir / "cpu_vs_concurrency.png")
    plot_efficiency_vs_concurrency(results, plots_dir / "efficiency_vs_concurrency.png")
    plot_memory_vs_concurrency(results, plots_dir / "memory_vs_concurrency.png")
    plot_crossover_chart(results, plots_dir / "crossover_analysis.png")
    
    print(f"\nAll plots saved to: {plots_dir}")
    return plots_dir


def main():
    parser = argparse.ArgumentParser(
        description="Generate plots from sweep experiment results"
    )
    
    parser.add_argument(
        "results_dir",
        type=str,
        help="Path to results directory (e.g., experiments/results/sweep_20240115)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output directory for plots (default: experiments/plots/<timestamp>)"
    )
    
    args = parser.parse_args()
    
    results_dir = Path(args.results_dir)
    if not results_dir.exists():
        print(f"Error: Results directory not found: {results_dir}")
        sys.exit(1)
    
    plots_dir = Path(args.output) if args.output else None
    generate_all_plots(results_dir, plots_dir)


if __name__ == "__main__":
    main()
