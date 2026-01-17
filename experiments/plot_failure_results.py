#!/usr/bin/env python3
"""
Plot failure injection experiment results.

Generates charts showing the impact of failure injection on microservices.

Usage:
    python plot_failure_results.py <results_dir>
    python plot_failure_results.py experiments/results/failure_20240115_143022
"""
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from experiments.lib.io_utils import read_json, get_project_root

# Try to import matplotlib
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available")


def load_failure_results(results_dir: Path) -> Dict[str, Any]:
    """Load failure injection results."""
    results_path = results_dir / "failure_results.json"
    if not results_path.exists():
        raise FileNotFoundError(f"Results not found: {results_path}")
    return read_json(results_path)


def setup_plot_style():
    """Configure matplotlib style."""
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams['figure.figsize'] = (12, 6)
    plt.rcParams['font.size'] = 11
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['legend.fontsize'] = 10
    plt.rcParams['figure.dpi'] = 150


def normalize_timestamps(timestamps: List[float]) -> List[float]:
    """Normalize timestamps to start at 0."""
    if not timestamps:
        return []
    start = min(timestamps)
    return [t - start for t in timestamps]


def plot_error_rate_over_time(results: Dict[str, Any], output_path: Path) -> None:
    """Plot error rate over time with failure injection markers."""
    ts_data = results.get("time_series", {})
    injection = results.get("injection", {})
    test_start = results.get("test_start_epoch", 0)
    
    timestamps = ts_data.get("timestamps", [])
    failures_per_second = ts_data.get("failures_per_second", [])
    requests_per_second = ts_data.get("requests_per_second", [])
    
    if not timestamps or not failures_per_second:
        print("Warning: No time series data for error rate plot")
        return
    
    # Normalize to test start
    time_offset = [t - test_start for t in timestamps]
    
    # Calculate error rate per second
    error_rates = []
    for fail, req in zip(failures_per_second, requests_per_second):
        if req > 0:
            error_rates.append((fail / req) * 100)
        else:
            error_rates.append(0)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(time_offset, error_rates, color='#E94F37', linewidth=1.5, label='Error Rate')
    ax.fill_between(time_offset, error_rates, alpha=0.3, color='#E94F37')
    
    # Add injection markers
    if injection:
        inject_start = injection.get("inject_start_epoch", 0) - test_start
        inject_end = injection.get("inject_end_epoch", 0) - test_start
        
        ax.axvline(x=inject_start, color='red', linestyle='--', linewidth=2, label='Failure Start')
        ax.axvline(x=inject_end, color='green', linestyle='--', linewidth=2, label='Failure End')
        
        # Shade the failure period
        ax.axvspan(inject_start, inject_end, alpha=0.2, color='red')
    
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Error Rate (%)")
    ax.set_title("Error Rate Over Time During Failure Injection")
    ax.legend(loc="upper right")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")


def plot_latency_over_time(results: Dict[str, Any], output_path: Path) -> None:
    """Plot latency P95 over time with failure injection markers."""
    ts_data = results.get("time_series", {})
    injection = results.get("injection", {})
    test_start = results.get("test_start_epoch", 0)
    
    timestamps = ts_data.get("timestamps", [])
    latency_p95 = ts_data.get("latency_p95", [])
    latency_p50 = ts_data.get("latency_p50", [])
    
    if not timestamps or not latency_p95:
        print("Warning: No time series data for latency plot")
        return
    
    time_offset = [t - test_start for t in timestamps]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(time_offset, latency_p50, color='#2E86AB', linewidth=1.5, label='P50')
    ax.plot(time_offset, latency_p95, color='#E94F37', linewidth=1.5, label='P95')
    
    # Add injection markers
    if injection:
        inject_start = injection.get("inject_start_epoch", 0) - test_start
        inject_end = injection.get("inject_end_epoch", 0) - test_start
        
        ax.axvline(x=inject_start, color='red', linestyle='--', linewidth=2, label='Failure Start')
        ax.axvline(x=inject_end, color='green', linestyle='--', linewidth=2, label='Failure End')
        ax.axvspan(inject_start, inject_end, alpha=0.2, color='red')
    
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Latency (ms)")
    ax.set_title("Latency Over Time During Failure Injection")
    ax.legend(loc="upper right")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")


def plot_throughput_over_time(results: Dict[str, Any], output_path: Path) -> None:
    """Plot throughput over time with failure injection markers."""
    ts_data = results.get("time_series", {})
    injection = results.get("injection", {})
    test_start = results.get("test_start_epoch", 0)
    
    timestamps = ts_data.get("timestamps", [])
    requests_per_second = ts_data.get("requests_per_second", [])
    
    if not timestamps or not requests_per_second:
        print("Warning: No time series data for throughput plot")
        return
    
    time_offset = [t - test_start for t in timestamps]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(time_offset, requests_per_second, color='#2E86AB', linewidth=1.5, label='Throughput')
    ax.fill_between(time_offset, requests_per_second, alpha=0.3, color='#2E86AB')
    
    # Add injection markers
    if injection:
        inject_start = injection.get("inject_start_epoch", 0) - test_start
        inject_end = injection.get("inject_end_epoch", 0) - test_start
        
        ax.axvline(x=inject_start, color='red', linestyle='--', linewidth=2, label='Failure Start')
        ax.axvline(x=inject_end, color='green', linestyle='--', linewidth=2, label='Failure End')
        ax.axvspan(inject_start, inject_end, alpha=0.2, color='red')
    
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Requests per Second")
    ax.set_title("Throughput Over Time During Failure Injection")
    ax.legend(loc="upper right")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")


def plot_combined_failure_analysis(results: Dict[str, Any], output_path: Path) -> None:
    """Plot combined view of failure injection impact."""
    ts_data = results.get("time_series", {})
    injection = results.get("injection", {})
    test_start = results.get("test_start_epoch", 0)
    
    timestamps = ts_data.get("timestamps", [])
    requests_per_second = ts_data.get("requests_per_second", [])
    failures_per_second = ts_data.get("failures_per_second", [])
    latency_p95 = ts_data.get("latency_p95", [])
    
    if not timestamps:
        print("Warning: No time series data for combined plot")
        return
    
    time_offset = [t - test_start for t in timestamps]
    
    # Calculate error rates
    error_rates = []
    for fail, req in zip(failures_per_second, requests_per_second):
        if req > 0:
            error_rates.append((fail / req) * 100)
        else:
            error_rates.append(0)
    
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    
    # Throughput
    axes[0].plot(time_offset, requests_per_second, color='#2E86AB', linewidth=1.5)
    axes[0].fill_between(time_offset, requests_per_second, alpha=0.3, color='#2E86AB')
    axes[0].set_ylabel("Requests/s")
    axes[0].set_title("Throughput")
    
    # Latency
    axes[1].plot(time_offset, latency_p95, color='#F4A261', linewidth=1.5)
    axes[1].set_ylabel("P95 Latency (ms)")
    axes[1].set_title("Latency P95")
    
    # Error Rate
    axes[2].plot(time_offset, error_rates, color='#E94F37', linewidth=1.5)
    axes[2].fill_between(time_offset, error_rates, alpha=0.3, color='#E94F37')
    axes[2].set_ylabel("Error Rate (%)")
    axes[2].set_xlabel("Time (seconds)")
    axes[2].set_title("Error Rate")
    
    # Add injection markers to all plots
    if injection:
        inject_start = injection.get("inject_start_epoch", 0) - test_start
        inject_end = injection.get("inject_end_epoch", 0) - test_start
        
        for ax in axes:
            ax.axvline(x=inject_start, color='red', linestyle='--', linewidth=2, alpha=0.7)
            ax.axvline(x=inject_end, color='green', linestyle='--', linewidth=2, alpha=0.7)
            ax.axvspan(inject_start, inject_end, alpha=0.1, color='red')
    
    # Add legend
    failure_patch = mpatches.Patch(color='red', alpha=0.2, label='Failure Period')
    fig.legend(handles=[failure_patch], loc='upper right')
    
    target = injection.get("target_service", "unknown") if injection else "unknown"
    plt.suptitle(f"Microservices Resilience Analysis\nTarget: {target}", fontsize=14, y=1.02)
    
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")


def plot_recovery_analysis(results: Dict[str, Any], output_path: Path) -> None:
    """Plot focused view on recovery period after failure."""
    ts_data = results.get("time_series", {})
    injection = results.get("injection", {})
    test_start = results.get("test_start_epoch", 0)
    
    if not injection:
        print("Warning: No injection data for recovery analysis")
        return
    
    inject_end = injection.get("inject_end_epoch", 0) - test_start
    
    timestamps = ts_data.get("timestamps", [])
    requests_per_second = ts_data.get("requests_per_second", [])
    failures_per_second = ts_data.get("failures_per_second", [])
    
    if not timestamps:
        print("Warning: No time series data for recovery plot")
        return
    
    time_offset = [t - test_start for t in timestamps]
    
    # Focus on recovery window (from failure end to +30 seconds)
    recovery_window_end = inject_end + 30
    
    # Filter data to recovery window
    recovery_times = []
    recovery_throughput = []
    recovery_failures = []
    
    for t, req, fail in zip(time_offset, requests_per_second, failures_per_second):
        if inject_end - 10 <= t <= recovery_window_end:
            recovery_times.append(t - inject_end)  # Relative to failure end
            recovery_throughput.append(req)
            recovery_failures.append(fail)
    
    if not recovery_times:
        print("Warning: No recovery data available")
        return
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    
    ax1.plot(recovery_times, recovery_throughput, color='#2E86AB', linewidth=2, marker='o', markersize=4)
    ax1.axvline(x=0, color='green', linestyle='--', linewidth=2, label='Recovery Start')
    ax1.set_ylabel("Requests/s")
    ax1.set_title("Throughput Recovery")
    ax1.legend()
    
    ax2.plot(recovery_times, recovery_failures, color='#E94F37', linewidth=2, marker='o', markersize=4)
    ax2.axvline(x=0, color='green', linestyle='--', linewidth=2)
    ax2.set_ylabel("Failures/s")
    ax2.set_xlabel("Time relative to recovery start (seconds)")
    ax2.set_title("Error Recovery")
    
    plt.suptitle("Service Recovery Analysis", fontsize=14)
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")


def generate_failure_plots(results_dir: Path, plots_dir: Optional[Path] = None) -> Path:
    """Generate all plots from failure injection results."""
    if not MATPLOTLIB_AVAILABLE:
        print("Error: matplotlib is required for plotting")
        sys.exit(1)
    
    setup_plot_style()
    
    # Load results
    results = load_failure_results(results_dir)
    print(f"Loaded failure injection results from: {results_dir}")
    
    # Create plots directory
    if plots_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plots_dir = get_project_root() / "experiments" / "plots" / f"failure_{timestamp}"
    
    plots_dir.mkdir(parents=True, exist_ok=True)
    print(f"Generating plots in: {plots_dir}")
    
    # Generate plots
    plot_error_rate_over_time(results, plots_dir / "error_rate_over_time.png")
    plot_latency_over_time(results, plots_dir / "latency_over_time.png")
    plot_throughput_over_time(results, plots_dir / "throughput_over_time.png")
    plot_combined_failure_analysis(results, plots_dir / "combined_failure_analysis.png")
    plot_recovery_analysis(results, plots_dir / "recovery_analysis.png")
    
    print(f"\nAll plots saved to: {plots_dir}")
    return plots_dir


def main():
    parser = argparse.ArgumentParser(
        description="Generate plots from failure injection results"
    )
    
    parser.add_argument(
        "results_dir",
        type=str,
        help="Path to failure injection results directory"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output directory for plots"
    )
    
    args = parser.parse_args()
    
    results_dir = Path(args.results_dir)
    if not results_dir.exists():
        print(f"Error: Results directory not found: {results_dir}")
        sys.exit(1)
    
    plots_dir = Path(args.output) if args.output else None
    generate_failure_plots(results_dir, plots_dir)


if __name__ == "__main__":
    main()
