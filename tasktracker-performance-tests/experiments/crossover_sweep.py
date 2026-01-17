#!/usr/bin/env python3
"""
Crossover Curves - Parameter Sweep Experiment

Runs load tests at multiple concurrency levels for both architectures
and generates plots showing the crossover point where microservices
starts outperforming monolithic.

Usage:
    python crossover_sweep.py [--concurrency-levels "25,50,100,150,200,250"]
"""

import subprocess
import json
import csv
import os
import sys
import time
import argparse
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure matplotlib for publication-quality plots
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'figure.figsize': (12, 7),
    'font.size': 12,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'legend.fontsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})


@dataclass
class TestResult:
    """Holds results from a single test run."""
    architecture: str
    concurrency: int
    total_requests: int
    requests_per_sec: float
    avg_response_time: float
    median_response_time: float
    p95_response_time: float
    p99_response_time: float
    failure_count: int
    failure_rate: float
    test_duration_sec: float


def check_app_health(port: int, name: str) -> bool:
    """Check if an application is running on the given port."""
    try:
        result = subprocess.run(
            ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', f'http://localhost:{port}/health'],
            capture_output=True, text=True, timeout=5
        )
        if result.stdout.strip() == '200':
            print(f"  ✓ {name} is running on port {port}")
            return True
    except Exception:
        pass
    print(f"  ✗ {name} is NOT running on port {port}")
    return False


def run_locust_test(
    locustfile: str,
    users: int,
    spawn_rate: int,
    run_time: str,
    output_dir: Path,
    architecture: str
) -> Optional[TestResult]:
    """Run a single Locust test and return results."""
    
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_prefix = output_dir / "stats"
    
    cmd = [
        'locust',
        '-f', locustfile,
        '--headless',
        '--users', str(users),
        '--spawn-rate', str(spawn_rate),
        '--run-time', run_time,
        '--csv', str(csv_prefix),
        '--csv-full-history',
        '--logfile', str(output_dir / 'locust.log'),
        '--loglevel', 'WARNING',
    ]
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 min max per test
        )
    except subprocess.TimeoutExpired:
        print(f"    ⚠ Test timed out for {architecture} @ {users} users")
        return None
    
    duration = time.time() - start_time
    
    # Parse the stats CSV
    stats_file = output_dir / "stats_stats.csv"
    if not stats_file.exists():
        print(f"    ⚠ No stats file generated for {architecture} @ {users} users")
        return None
    
    try:
        df = pd.read_csv(stats_file)
        # Get aggregated row
        agg = df[df['Name'] == 'Aggregated']
        
        if agg.empty:
            print(f"    ⚠ No aggregated stats for {architecture} @ {users} users")
            return None
        
        agg = agg.iloc[0]
        
        total_requests = int(agg['Request Count'])
        failure_count = int(agg['Failure Count'])
        
        return TestResult(
            architecture=architecture,
            concurrency=users,
            total_requests=total_requests,
            requests_per_sec=float(agg['Requests/s']),
            avg_response_time=float(agg['Average Response Time']),
            median_response_time=float(agg['Median Response Time']),
            p95_response_time=float(agg['95%']),
            p99_response_time=float(agg['99%']),
            failure_count=failure_count,
            failure_rate=(failure_count / total_requests * 100) if total_requests > 0 else 0,
            test_duration_sec=duration,
        )
    except Exception as e:
        print(f"    ⚠ Error parsing results: {e}")
        return None


def run_sweep(
    concurrency_levels: List[int],
    run_time: str,
    spawn_rate: int,
    output_base: Path
) -> List[TestResult]:
    """Run the full parameter sweep for both architectures."""
    
    results = []
    script_dir = Path(__file__).parent.parent
    
    total_tests = len(concurrency_levels) * 2
    test_num = 0
    
    for users in concurrency_levels:
        # Run monolithic test
        test_num += 1
        print(f"\n[{test_num}/{total_tests}] Testing Monolithic @ {users} users...")
        
        mono_dir = output_base / f"mono_{users}u"
        result = run_locust_test(
            locustfile=str(script_dir / "locustfile_monolithic.py"),
            users=users,
            spawn_rate=spawn_rate,
            run_time=run_time,
            output_dir=mono_dir,
            architecture="monolithic"
        )
        if result:
            results.append(result)
            print(f"    ✓ {result.requests_per_sec:.1f} req/s, {result.avg_response_time:.1f}ms avg, {result.failure_rate:.2f}% errors")
        
        # Small delay between tests
        time.sleep(3)
        
        # Run microservices test
        test_num += 1
        print(f"\n[{test_num}/{total_tests}] Testing Microservices @ {users} users...")
        
        micro_dir = output_base / f"micro_{users}u"
        result = run_locust_test(
            locustfile=str(script_dir / "locustfile_microservices.py"),
            users=users,
            spawn_rate=spawn_rate,
            run_time=run_time,
            output_dir=micro_dir,
            architecture="microservices"
        )
        if result:
            results.append(result)
            print(f"    ✓ {result.requests_per_sec:.1f} req/s, {result.avg_response_time:.1f}ms avg, {result.failure_rate:.2f}% errors")
        
        time.sleep(3)
    
    return results


def save_results(results: List[TestResult], output_dir: Path):
    """Save results to CSV and JSON for reproducibility."""
    
    # Save as CSV
    csv_path = output_dir / "sweep_results.csv"
    with open(csv_path, 'w', newline='') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=asdict(results[0]).keys())
            writer.writeheader()
            for r in results:
                writer.writerow(asdict(r))
    print(f"\n✓ Results saved to {csv_path}")
    
    # Save as JSON
    json_path = output_dir / "sweep_results.json"
    with open(json_path, 'w') as f:
        json.dump([asdict(r) for r in results], f, indent=2)
    print(f"✓ Results saved to {json_path}")


def create_plots(results: List[TestResult], output_dir: Path):
    """Generate all crossover comparison plots."""
    
    if not results:
        print("⚠ No results to plot")
        return
    
    # Separate by architecture
    mono = [r for r in results if r.architecture == 'monolithic']
    micro = [r for r in results if r.architecture == 'microservices']
    
    mono_users = [r.concurrency for r in mono]
    micro_users = [r.concurrency for r in micro]
    
    # Color scheme
    MONO_COLOR = '#2563EB'   # Blue
    MICRO_COLOR = '#DC2626'  # Red
    
    # ========== PLOT 1: Throughput vs Concurrency ==========
    fig, ax = plt.subplots(figsize=(12, 7))
    
    ax.plot(mono_users, [r.requests_per_sec for r in mono], 
            'o-', color=MONO_COLOR, linewidth=2.5, markersize=10, label='Monolithic')
    ax.plot(micro_users, [r.requests_per_sec for r in micro], 
            's-', color=MICRO_COLOR, linewidth=2.5, markersize=10, label='Microservices')
    
    ax.set_xlabel('Concurrent Users', fontweight='bold')
    ax.set_ylabel('Throughput (req/s)', fontweight='bold')
    ax.set_title('Throughput vs Concurrency: Crossover Curve', fontweight='bold', fontsize=16)
    ax.legend(loc='best', framealpha=0.9)
    ax.grid(True, alpha=0.3)
    
    # Add annotation for crossover point if exists
    if mono and micro:
        mono_rps = np.array([r.requests_per_sec for r in mono])
        micro_rps = np.array([r.requests_per_sec for r in micro])
        users_arr = np.array(mono_users)
        
        # Find approximate crossover
        diff = mono_rps - micro_rps
        sign_changes = np.where(np.diff(np.sign(diff)))[0]
        if len(sign_changes) > 0:
            crossover_idx = sign_changes[0]
            crossover_users = (users_arr[crossover_idx] + users_arr[crossover_idx + 1]) / 2
            crossover_rps = (mono_rps[crossover_idx] + micro_rps[crossover_idx]) / 2
            ax.axvline(x=crossover_users, color='gray', linestyle='--', alpha=0.7)
            ax.annotate(f'Crossover ~{crossover_users:.0f} users',
                       xy=(crossover_users, crossover_rps),
                       xytext=(crossover_users + 20, crossover_rps + 5),
                       fontsize=11, fontweight='bold',
                       arrowprops=dict(arrowstyle='->', color='gray'))
    
    plt.savefig(output_dir / 'crossover_throughput.png')
    print(f"✓ Created: {output_dir}/crossover_throughput.png")
    plt.close()
    
    # ========== PLOT 2: Response Time vs Concurrency ==========
    fig, ax = plt.subplots(figsize=(12, 7))
    
    ax.plot(mono_users, [r.avg_response_time for r in mono], 
            'o-', color=MONO_COLOR, linewidth=2.5, markersize=10, label='Monolithic (Avg)')
    ax.plot(micro_users, [r.avg_response_time for r in micro], 
            's-', color=MICRO_COLOR, linewidth=2.5, markersize=10, label='Microservices (Avg)')
    
    ax.set_xlabel('Concurrent Users', fontweight='bold')
    ax.set_ylabel('Average Response Time (ms)', fontweight='bold')
    ax.set_title('Response Time vs Concurrency', fontweight='bold', fontsize=16)
    ax.legend(loc='best', framealpha=0.9)
    ax.grid(True, alpha=0.3)
    
    plt.savefig(output_dir / 'crossover_response_time.png')
    print(f"✓ Created: {output_dir}/crossover_response_time.png")
    plt.close()
    
    # ========== PLOT 3: P95/P99 Latencies ==========
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # P95
    ax1.plot(mono_users, [r.p95_response_time for r in mono], 
             'o-', color=MONO_COLOR, linewidth=2, markersize=8, label='Monolithic')
    ax1.plot(micro_users, [r.p95_response_time for r in micro], 
             's-', color=MICRO_COLOR, linewidth=2, markersize=8, label='Microservices')
    ax1.set_xlabel('Concurrent Users', fontweight='bold')
    ax1.set_ylabel('P95 Response Time (ms)', fontweight='bold')
    ax1.set_title('95th Percentile Latency', fontweight='bold')
    ax1.legend(loc='best', framealpha=0.9)
    ax1.grid(True, alpha=0.3)
    
    # P99
    ax2.plot(mono_users, [r.p99_response_time for r in mono], 
             'o-', color=MONO_COLOR, linewidth=2, markersize=8, label='Monolithic')
    ax2.plot(micro_users, [r.p99_response_time for r in micro], 
             's-', color=MICRO_COLOR, linewidth=2, markersize=8, label='Microservices')
    ax2.set_xlabel('Concurrent Users', fontweight='bold')
    ax2.set_ylabel('P99 Response Time (ms)', fontweight='bold')
    ax2.set_title('99th Percentile Latency', fontweight='bold')
    ax2.legend(loc='best', framealpha=0.9)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'crossover_percentiles.png')
    print(f"✓ Created: {output_dir}/crossover_percentiles.png")
    plt.close()
    
    # ========== PLOT 4: Error Rate vs Concurrency ==========
    fig, ax = plt.subplots(figsize=(12, 7))
    
    ax.plot(mono_users, [r.failure_rate for r in mono], 
            'o-', color=MONO_COLOR, linewidth=2.5, markersize=10, label='Monolithic')
    ax.plot(micro_users, [r.failure_rate for r in micro], 
            's-', color=MICRO_COLOR, linewidth=2.5, markersize=10, label='Microservices')
    
    ax.set_xlabel('Concurrent Users', fontweight='bold')
    ax.set_ylabel('Error Rate (%)', fontweight='bold')
    ax.set_title('Error Rate vs Concurrency', fontweight='bold', fontsize=16)
    ax.legend(loc='best', framealpha=0.9)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(bottom=0)
    
    plt.savefig(output_dir / 'crossover_error_rate.png')
    print(f"✓ Created: {output_dir}/crossover_error_rate.png")
    plt.close()
    
    # ========== PLOT 5: Combined Dashboard ==========
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Throughput
    axes[0, 0].plot(mono_users, [r.requests_per_sec for r in mono], 
                    'o-', color=MONO_COLOR, linewidth=2, markersize=8, label='Monolithic')
    axes[0, 0].plot(micro_users, [r.requests_per_sec for r in micro], 
                    's-', color=MICRO_COLOR, linewidth=2, markersize=8, label='Microservices')
    axes[0, 0].set_xlabel('Concurrent Users')
    axes[0, 0].set_ylabel('Throughput (req/s)')
    axes[0, 0].set_title('Throughput', fontweight='bold')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Response Time
    axes[0, 1].plot(mono_users, [r.avg_response_time for r in mono], 
                    'o-', color=MONO_COLOR, linewidth=2, markersize=8, label='Monolithic')
    axes[0, 1].plot(micro_users, [r.avg_response_time for r in micro], 
                    's-', color=MICRO_COLOR, linewidth=2, markersize=8, label='Microservices')
    axes[0, 1].set_xlabel('Concurrent Users')
    axes[0, 1].set_ylabel('Avg Response Time (ms)')
    axes[0, 1].set_title('Response Time', fontweight='bold')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # P99 Latency
    axes[1, 0].plot(mono_users, [r.p99_response_time for r in mono], 
                    'o-', color=MONO_COLOR, linewidth=2, markersize=8, label='Monolithic')
    axes[1, 0].plot(micro_users, [r.p99_response_time for r in micro], 
                    's-', color=MICRO_COLOR, linewidth=2, markersize=8, label='Microservices')
    axes[1, 0].set_xlabel('Concurrent Users')
    axes[1, 0].set_ylabel('P99 Response Time (ms)')
    axes[1, 0].set_title('P99 Tail Latency', fontweight='bold')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # Error Rate
    axes[1, 1].plot(mono_users, [r.failure_rate for r in mono], 
                    'o-', color=MONO_COLOR, linewidth=2, markersize=8, label='Monolithic')
    axes[1, 1].plot(micro_users, [r.failure_rate for r in micro], 
                    's-', color=MICRO_COLOR, linewidth=2, markersize=8, label='Microservices')
    axes[1, 1].set_xlabel('Concurrent Users')
    axes[1, 1].set_ylabel('Error Rate (%)')
    axes[1, 1].set_title('Error Rate', fontweight='bold')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 1].set_ylim(bottom=0)
    
    fig.suptitle('Performance Crossover Analysis: Monolithic vs Microservices', 
                 fontsize=18, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'crossover_dashboard.png')
    print(f"✓ Created: {output_dir}/crossover_dashboard.png")
    plt.close()
    
    print(f"\n✅ All crossover plots saved to {output_dir}/")


def main():
    parser = argparse.ArgumentParser(description='Run crossover curve parameter sweep')
    parser.add_argument('--concurrency-levels', type=str, default='25,50,75,100,150,200',
                       help='Comma-separated concurrency levels to test')
    parser.add_argument('--run-time', type=str, default='90s',
                       help='Duration for each test (e.g., 60s, 2m)')
    parser.add_argument('--spawn-rate', type=int, default=10,
                       help='Users spawned per second')
    parser.add_argument('--output', type=str, default=None,
                       help='Output directory (default: results/crossover_TIMESTAMP)')
    
    args = parser.parse_args()
    
    # Parse concurrency levels
    concurrency_levels = [int(x.strip()) for x in args.concurrency_levels.split(',')]
    
    print("=" * 60)
    print("CROSSOVER CURVE PARAMETER SWEEP")
    print("=" * 60)
    print(f"Concurrency levels: {concurrency_levels}")
    print(f"Run time per test: {args.run_time}")
    print(f"Spawn rate: {args.spawn_rate} users/sec")
    print("")
    
    # Check if both apps are running
    print("Checking application status...")
    mono_ok = check_app_health(9000, "Monolithic")
    micro_ok = check_app_health(8000, "Microservices")
    
    if not mono_ok or not micro_ok:
        print("\n❌ ERROR: Both applications must be running!")
        print("Start them with:")
        print("  cd ../tasktracker-mono && docker compose up -d")
        print("  cd ../tasktracker-micro && docker compose up -d")
        sys.exit(1)
    
    # Setup output directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    if args.output:
        output_dir = Path(args.output)
    else:
        output_dir = Path(__file__).parent.parent / 'results' / f'crossover_{timestamp}'
    
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nOutput directory: {output_dir}")
    
    # Run the sweep
    print("\n" + "=" * 60)
    print("STARTING PARAMETER SWEEP")
    print("=" * 60)
    
    results = run_sweep(
        concurrency_levels=concurrency_levels,
        run_time=args.run_time,
        spawn_rate=args.spawn_rate,
        output_base=output_dir
    )
    
    # Save results
    print("\n" + "=" * 60)
    print("SAVING RESULTS")
    print("=" * 60)
    save_results(results, output_dir)
    
    # Create plots
    print("\n" + "=" * 60)
    print("GENERATING PLOTS")
    print("=" * 60)
    create_plots(results, output_dir)
    
    print("\n" + "=" * 60)
    print("✅ SWEEP COMPLETE!")
    print("=" * 60)
    print(f"\nResults: {output_dir}")
    print(f"  - sweep_results.csv")
    print(f"  - sweep_results.json")
    print(f"  - crossover_throughput.png")
    print(f"  - crossover_response_time.png")
    print(f"  - crossover_percentiles.png")
    print(f"  - crossover_error_rate.png")
    print(f"  - crossover_dashboard.png")


if __name__ == '__main__':
    main()
