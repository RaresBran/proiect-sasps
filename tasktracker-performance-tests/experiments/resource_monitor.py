#!/usr/bin/env python3
"""
Resource Efficiency Monitor

Collects CPU and memory usage from Docker containers during load tests
and computes efficiency metrics (req/s per CPU, req/s per GB RAM).

Usage:
    python resource_monitor.py --architecture monolithic --duration 120
    python resource_monitor.py --architecture microservices --duration 120
"""

import subprocess
import json
import csv
import os
import sys
import time
import threading
import argparse
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional, Tuple
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'figure.figsize': (12, 7),
    'font.size': 12,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'figure.dpi': 150,
    'savefig.dpi': 300,
})

# Container configurations
MONO_CONTAINERS = {
    'tasktracker_app': 'App',
    'tasktracker_db': 'Database',
}

MICRO_CONTAINERS = {
    'tasktracker_api_gateway': 'API Gateway',
    'tasktracker_user_service': 'User Service',
    'tasktracker_task_service': 'Task Service',
    'tasktracker_stats_service': 'Stats Service',
    'tasktracker_user_db': 'User DB',
    'tasktracker_task_db': 'Task DB',
}


@dataclass
class ResourceSample:
    """Single sample of container resource usage."""
    timestamp: float
    container: str
    cpu_percent: float
    memory_mb: float
    memory_percent: float


@dataclass 
class TestMetrics:
    """Aggregated metrics from a test run."""
    architecture: str
    concurrency: int
    duration_sec: float
    total_requests: int
    requests_per_sec: float
    avg_response_time: float
    total_cpu_percent: float
    total_memory_mb: float
    # Efficiency metrics
    rps_per_cpu: float  # req/s per 1% CPU
    rps_per_gb_ram: float  # req/s per GB RAM
    cpu_samples: List[Dict] = field(default_factory=list)
    memory_samples: List[Dict] = field(default_factory=list)


class DockerStatsCollector:
    """Collects Docker stats in a background thread."""
    
    def __init__(self, containers: Dict[str, str], interval: float = 1.0):
        self.containers = containers
        self.interval = interval
        self.samples: List[ResourceSample] = []
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
    
    def start(self):
        """Start collecting stats in background."""
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._collect_loop, daemon=True)
        self._thread.start()
    
    def stop(self) -> List[ResourceSample]:
        """Stop collecting and return samples."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        return self.samples
    
    def _collect_loop(self):
        """Main collection loop."""
        while not self._stop_event.is_set():
            timestamp = time.time()
            
            for container_name in self.containers.keys():
                sample = self._get_container_stats(container_name, timestamp)
                if sample:
                    self.samples.append(sample)
            
            # Sleep for interval
            elapsed = time.time() - timestamp
            sleep_time = max(0, self.interval - elapsed)
            self._stop_event.wait(sleep_time)
    
    def _get_container_stats(self, container: str, timestamp: float) -> Optional[ResourceSample]:
        """Get stats for a single container."""
        try:
            result = subprocess.run(
                ['docker', 'stats', container, '--no-stream', '--format', 
                 '{{.CPUPerc}},{{.MemUsage}},{{.MemPerc}}'],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode != 0:
                return None
            
            line = result.stdout.strip()
            if not line:
                return None
            
            parts = line.split(',')
            if len(parts) < 3:
                return None
            
            # Parse CPU percentage (e.g., "1.23%")
            cpu_str = parts[0].replace('%', '').strip()
            cpu_percent = float(cpu_str) if cpu_str else 0.0
            
            # Parse memory (e.g., "256MiB / 8GiB")
            mem_str = parts[1].split('/')[0].strip()
            memory_mb = self._parse_memory(mem_str)
            
            # Parse memory percentage
            mem_pct_str = parts[2].replace('%', '').strip()
            mem_percent = float(mem_pct_str) if mem_pct_str else 0.0
            
            return ResourceSample(
                timestamp=timestamp,
                container=container,
                cpu_percent=cpu_percent,
                memory_mb=memory_mb,
                memory_percent=mem_percent
            )
        except Exception as e:
            return None
    
    @staticmethod
    def _parse_memory(mem_str: str) -> float:
        """Parse memory string like '256MiB' to MB."""
        mem_str = mem_str.strip().upper()
        
        if 'GIB' in mem_str or 'GB' in mem_str:
            num = float(mem_str.replace('GIB', '').replace('GB', '').strip())
            return num * 1024
        elif 'MIB' in mem_str or 'MB' in mem_str:
            num = float(mem_str.replace('MIB', '').replace('MB', '').strip())
            return num
        elif 'KIB' in mem_str or 'KB' in mem_str:
            num = float(mem_str.replace('KIB', '').replace('KB', '').strip())
            return num / 1024
        else:
            try:
                return float(mem_str)
            except:
                return 0.0


def run_load_test(
    architecture: str,
    users: int,
    spawn_rate: int,
    run_time: str,
    output_dir: Path
) -> Tuple[Optional[pd.DataFrame], float]:
    """Run a load test and return the stats DataFrame."""
    
    script_dir = Path(__file__).parent.parent
    
    if architecture == 'monolithic':
        locustfile = script_dir / 'locustfile_monolithic.py'
    else:
        locustfile = script_dir / 'locustfile_microservices.py'
    
    csv_prefix = output_dir / "stats"
    
    cmd = [
        'locust',
        '-f', str(locustfile),
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
    subprocess.run(cmd, capture_output=True, text=True)
    duration = time.time() - start_time
    
    stats_file = output_dir / "stats_stats.csv"
    if stats_file.exists():
        return pd.read_csv(stats_file), duration
    return None, duration


def compute_metrics(
    architecture: str,
    concurrency: int,
    duration: float,
    stats_df: Optional[pd.DataFrame],
    samples: List[ResourceSample],
    containers: Dict[str, str]
) -> TestMetrics:
    """Compute aggregated metrics from test results and resource samples."""
    
    # Parse load test results
    total_requests = 0
    rps = 0.0
    avg_rt = 0.0
    
    if stats_df is not None and not stats_df.empty:
        agg = stats_df[stats_df['Name'] == 'Aggregated']
        if not agg.empty:
            agg = agg.iloc[0]
            total_requests = int(agg['Request Count'])
            rps = float(agg['Requests/s'])
            avg_rt = float(agg['Average Response Time'])
    
    # Aggregate resource samples
    cpu_by_time = defaultdict(float)
    mem_by_time = defaultdict(float)
    
    for sample in samples:
        if sample.container in containers:
            # Round timestamp to nearest second for grouping
            t = int(sample.timestamp)
            cpu_by_time[t] += sample.cpu_percent
            mem_by_time[t] += sample.memory_mb
    
    # Calculate averages
    avg_cpu = np.mean(list(cpu_by_time.values())) if cpu_by_time else 0.0
    avg_mem = np.mean(list(mem_by_time.values())) if mem_by_time else 0.0
    
    # Efficiency metrics
    rps_per_cpu = rps / avg_cpu if avg_cpu > 0 else 0.0
    rps_per_gb = rps / (avg_mem / 1024) if avg_mem > 0 else 0.0
    
    # Prepare time series for plotting
    times = sorted(cpu_by_time.keys())
    base_time = times[0] if times else 0
    
    cpu_series = [{'time': t - base_time, 'value': cpu_by_time[t]} for t in times]
    mem_series = [{'time': t - base_time, 'value': mem_by_time[t]} for t in times]
    
    return TestMetrics(
        architecture=architecture,
        concurrency=concurrency,
        duration_sec=duration,
        total_requests=total_requests,
        requests_per_sec=rps,
        avg_response_time=avg_rt,
        total_cpu_percent=avg_cpu,
        total_memory_mb=avg_mem,
        rps_per_cpu=rps_per_cpu,
        rps_per_gb_ram=rps_per_gb,
        cpu_samples=cpu_series,
        memory_samples=mem_series
    )


def run_resource_test(
    architecture: str,
    users: int,
    run_time: str,
    spawn_rate: int,
    output_dir: Path
) -> TestMetrics:
    """Run a single test with resource monitoring."""
    
    containers = MONO_CONTAINERS if architecture == 'monolithic' else MICRO_CONTAINERS
    
    print(f"\n  Starting resource collector for {len(containers)} containers...")
    collector = DockerStatsCollector(containers, interval=1.0)
    collector.start()
    
    print(f"  Running load test ({run_time})...")
    stats_df, duration = run_load_test(
        architecture=architecture,
        users=users,
        spawn_rate=spawn_rate,
        run_time=run_time,
        output_dir=output_dir
    )
    
    print(f"  Stopping resource collector...")
    samples = collector.stop()
    print(f"  Collected {len(samples)} resource samples")
    
    metrics = compute_metrics(
        architecture=architecture,
        concurrency=users,
        duration=duration,
        stats_df=stats_df,
        samples=samples,
        containers=containers
    )
    
    return metrics


def run_sweep(
    concurrency_levels: List[int],
    run_time: str,
    spawn_rate: int,
    output_base: Path
) -> List[TestMetrics]:
    """Run resource efficiency sweep for both architectures."""
    
    all_metrics = []
    total_tests = len(concurrency_levels) * 2
    test_num = 0
    
    for users in concurrency_levels:
        # Monolithic
        test_num += 1
        print(f"\n[{test_num}/{total_tests}] Monolithic @ {users} users")
        mono_dir = output_base / f"mono_{users}u"
        mono_dir.mkdir(parents=True, exist_ok=True)
        
        metrics = run_resource_test('monolithic', users, run_time, spawn_rate, mono_dir)
        all_metrics.append(metrics)
        print(f"    ✓ {metrics.requests_per_sec:.1f} req/s | CPU: {metrics.total_cpu_percent:.1f}% | RAM: {metrics.total_memory_mb:.0f} MB")
        print(f"    ✓ Efficiency: {metrics.rps_per_cpu:.2f} req/s per %CPU | {metrics.rps_per_gb_ram:.2f} req/s per GB")
        
        time.sleep(3)
        
        # Microservices
        test_num += 1
        print(f"\n[{test_num}/{total_tests}] Microservices @ {users} users")
        micro_dir = output_base / f"micro_{users}u"
        micro_dir.mkdir(parents=True, exist_ok=True)
        
        metrics = run_resource_test('microservices', users, run_time, spawn_rate, micro_dir)
        all_metrics.append(metrics)
        print(f"    ✓ {metrics.requests_per_sec:.1f} req/s | CPU: {metrics.total_cpu_percent:.1f}% | RAM: {metrics.total_memory_mb:.0f} MB")
        print(f"    ✓ Efficiency: {metrics.rps_per_cpu:.2f} req/s per %CPU | {metrics.rps_per_gb_ram:.2f} req/s per GB")
        
        time.sleep(3)
    
    return all_metrics


def save_results(metrics: List[TestMetrics], output_dir: Path):
    """Save metrics to CSV and JSON."""
    
    # CSV (without time series)
    csv_data = []
    for m in metrics:
        row = {
            'architecture': m.architecture,
            'concurrency': m.concurrency,
            'duration_sec': m.duration_sec,
            'total_requests': m.total_requests,
            'requests_per_sec': m.requests_per_sec,
            'avg_response_time': m.avg_response_time,
            'total_cpu_percent': m.total_cpu_percent,
            'total_memory_mb': m.total_memory_mb,
            'rps_per_cpu': m.rps_per_cpu,
            'rps_per_gb_ram': m.rps_per_gb_ram,
        }
        csv_data.append(row)
    
    csv_path = output_dir / 'resource_metrics.csv'
    pd.DataFrame(csv_data).to_csv(csv_path, index=False)
    print(f"\n✓ Saved: {csv_path}")
    
    # JSON (full data including time series)
    json_path = output_dir / 'resource_metrics.json'
    with open(json_path, 'w') as f:
        json.dump([asdict(m) for m in metrics], f, indent=2)
    print(f"✓ Saved: {json_path}")


def create_plots(metrics: List[TestMetrics], output_dir: Path):
    """Generate resource efficiency plots."""
    
    mono = [m for m in metrics if m.architecture == 'monolithic']
    micro = [m for m in metrics if m.architecture == 'microservices']
    
    mono_users = [m.concurrency for m in mono]
    micro_users = [m.concurrency for m in micro]
    
    MONO_COLOR = '#2563EB'
    MICRO_COLOR = '#DC2626'
    
    # ========== PLOT 1: CPU Usage vs Concurrency ==========
    fig, ax = plt.subplots(figsize=(12, 7))
    
    ax.plot(mono_users, [m.total_cpu_percent for m in mono],
            'o-', color=MONO_COLOR, linewidth=2.5, markersize=10, label='Monolithic')
    ax.plot(micro_users, [m.total_cpu_percent for m in micro],
            's-', color=MICRO_COLOR, linewidth=2.5, markersize=10, label='Microservices')
    
    ax.set_xlabel('Concurrent Users', fontweight='bold')
    ax.set_ylabel('Total CPU Usage (%)', fontweight='bold')
    ax.set_title('CPU Usage vs Concurrency', fontweight='bold', fontsize=16)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    plt.savefig(output_dir / 'resource_cpu_usage.png')
    print(f"✓ Created: {output_dir}/resource_cpu_usage.png")
    plt.close()
    
    # ========== PLOT 2: Memory Usage vs Concurrency ==========
    fig, ax = plt.subplots(figsize=(12, 7))
    
    ax.plot(mono_users, [m.total_memory_mb for m in mono],
            'o-', color=MONO_COLOR, linewidth=2.5, markersize=10, label='Monolithic')
    ax.plot(micro_users, [m.total_memory_mb for m in micro],
            's-', color=MICRO_COLOR, linewidth=2.5, markersize=10, label='Microservices')
    
    ax.set_xlabel('Concurrent Users', fontweight='bold')
    ax.set_ylabel('Total Memory Usage (MB)', fontweight='bold')
    ax.set_title('Memory Usage vs Concurrency', fontweight='bold', fontsize=16)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    plt.savefig(output_dir / 'resource_memory_usage.png')
    print(f"✓ Created: {output_dir}/resource_memory_usage.png")
    plt.close()
    
    # ========== PLOT 3: Efficiency Metrics ==========
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # RPS per CPU
    ax1.plot(mono_users, [m.rps_per_cpu for m in mono],
             'o-', color=MONO_COLOR, linewidth=2, markersize=8, label='Monolithic')
    ax1.plot(micro_users, [m.rps_per_cpu for m in micro],
             's-', color=MICRO_COLOR, linewidth=2, markersize=8, label='Microservices')
    ax1.set_xlabel('Concurrent Users', fontweight='bold')
    ax1.set_ylabel('req/s per 1% CPU', fontweight='bold')
    ax1.set_title('CPU Efficiency', fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # RPS per GB RAM
    ax2.plot(mono_users, [m.rps_per_gb_ram for m in mono],
             'o-', color=MONO_COLOR, linewidth=2, markersize=8, label='Monolithic')
    ax2.plot(micro_users, [m.rps_per_gb_ram for m in micro],
             's-', color=MICRO_COLOR, linewidth=2, markersize=8, label='Microservices')
    ax2.set_xlabel('Concurrent Users', fontweight='bold')
    ax2.set_ylabel('req/s per GB RAM', fontweight='bold')
    ax2.set_title('Memory Efficiency', fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'resource_efficiency.png')
    print(f"✓ Created: {output_dir}/resource_efficiency.png")
    plt.close()
    
    # ========== PLOT 4: Dashboard ==========
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # CPU
    axes[0, 0].plot(mono_users, [m.total_cpu_percent for m in mono],
                    'o-', color=MONO_COLOR, linewidth=2, markersize=8, label='Monolithic')
    axes[0, 0].plot(micro_users, [m.total_cpu_percent for m in micro],
                    's-', color=MICRO_COLOR, linewidth=2, markersize=8, label='Microservices')
    axes[0, 0].set_xlabel('Concurrent Users')
    axes[0, 0].set_ylabel('Total CPU (%)')
    axes[0, 0].set_title('CPU Usage', fontweight='bold')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Memory
    axes[0, 1].plot(mono_users, [m.total_memory_mb for m in mono],
                    'o-', color=MONO_COLOR, linewidth=2, markersize=8, label='Monolithic')
    axes[0, 1].plot(micro_users, [m.total_memory_mb for m in micro],
                    's-', color=MICRO_COLOR, linewidth=2, markersize=8, label='Microservices')
    axes[0, 1].set_xlabel('Concurrent Users')
    axes[0, 1].set_ylabel('Total Memory (MB)')
    axes[0, 1].set_title('Memory Usage', fontweight='bold')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # CPU Efficiency
    axes[1, 0].plot(mono_users, [m.rps_per_cpu for m in mono],
                    'o-', color=MONO_COLOR, linewidth=2, markersize=8, label='Monolithic')
    axes[1, 0].plot(micro_users, [m.rps_per_cpu for m in micro],
                    's-', color=MICRO_COLOR, linewidth=2, markersize=8, label='Microservices')
    axes[1, 0].set_xlabel('Concurrent Users')
    axes[1, 0].set_ylabel('req/s per %CPU')
    axes[1, 0].set_title('CPU Efficiency', fontweight='bold')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # Memory Efficiency
    axes[1, 1].plot(mono_users, [m.rps_per_gb_ram for m in mono],
                    'o-', color=MONO_COLOR, linewidth=2, markersize=8, label='Monolithic')
    axes[1, 1].plot(micro_users, [m.rps_per_gb_ram for m in micro],
                    's-', color=MICRO_COLOR, linewidth=2, markersize=8, label='Microservices')
    axes[1, 1].set_xlabel('Concurrent Users')
    axes[1, 1].set_ylabel('req/s per GB RAM')
    axes[1, 1].set_title('Memory Efficiency', fontweight='bold')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    fig.suptitle('Resource Efficiency Analysis: Monolithic vs Microservices',
                 fontsize=18, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'resource_dashboard.png')
    print(f"✓ Created: {output_dir}/resource_dashboard.png")
    plt.close()


def check_app_health(port: int, name: str) -> bool:
    """Check if an application is running."""
    try:
        result = subprocess.run(
            ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', f'http://localhost:{port}/health'],
            capture_output=True, text=True, timeout=5
        )
        if result.stdout.strip() == '200':
            print(f"  ✓ {name} running on port {port}")
            return True
    except:
        pass
    print(f"  ✗ {name} NOT running on port {port}")
    return False


def main():
    parser = argparse.ArgumentParser(description='Resource efficiency monitoring')
    parser.add_argument('--concurrency-levels', type=str, default='50,100,150,200',
                       help='Comma-separated concurrency levels')
    parser.add_argument('--run-time', type=str, default='60s',
                       help='Duration for each test')
    parser.add_argument('--spawn-rate', type=int, default=10,
                       help='Users spawned per second')
    parser.add_argument('--output', type=str, default=None,
                       help='Output directory')
    
    args = parser.parse_args()
    
    concurrency_levels = [int(x.strip()) for x in args.concurrency_levels.split(',')]
    
    print("=" * 60)
    print("RESOURCE EFFICIENCY MONITORING")
    print("=" * 60)
    print(f"Concurrency levels: {concurrency_levels}")
    print(f"Run time per test: {args.run_time}")
    print("")
    
    print("Checking applications...")
    mono_ok = check_app_health(9000, "Monolithic")
    micro_ok = check_app_health(8000, "Microservices")
    
    if not mono_ok or not micro_ok:
        print("\n❌ Both apps must be running!")
        sys.exit(1)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    if args.output:
        output_dir = Path(args.output)
    else:
        output_dir = Path(__file__).parent.parent / 'results' / f'resource_{timestamp}'
    
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nOutput: {output_dir}")
    
    print("\n" + "=" * 60)
    print("STARTING RESOURCE MONITORING SWEEP")
    print("=" * 60)
    
    metrics = run_sweep(
        concurrency_levels=concurrency_levels,
        run_time=args.run_time,
        spawn_rate=args.spawn_rate,
        output_base=output_dir
    )
    
    print("\n" + "=" * 60)
    print("SAVING RESULTS")
    print("=" * 60)
    save_results(metrics, output_dir)
    
    print("\n" + "=" * 60)
    print("GENERATING PLOTS")
    print("=" * 60)
    create_plots(metrics, output_dir)
    
    print("\n" + "=" * 60)
    print("✅ RESOURCE MONITORING COMPLETE!")
    print("=" * 60)
    print(f"\nResults: {output_dir}")


if __name__ == '__main__':
    main()
