#!/usr/bin/env python3
"""
Resilience / Failure Injection Experiment

Runs steady load on microservices, then intentionally stops a service
mid-run to demonstrate fault isolation and recovery.

Generates a timeline plot showing:
- Error rate over time
- Throughput over time
- Latency over time
- Markers for fault injection and recovery

Usage:
    python resilience_test.py --target-service task-service
"""

import subprocess
import json
import csv
import os
import sys
import time
import threading
import signal
import argparse
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'figure.figsize': (14, 8),
    'font.size': 12,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'figure.dpi': 150,
    'savefig.dpi': 300,
})

# Service mapping (name -> container name)
SERVICES = {
    'task-service': 'tasktracker_task_service',
    'user-service': 'tasktracker_user_service',
    'stats-service': 'tasktracker_stats_service',
    'api-gateway': 'tasktracker_api_gateway',
}


@dataclass
class TimeSeriesPoint:
    """A single point in time with metrics."""
    timestamp: float
    elapsed_sec: float
    requests: int
    failures: int
    avg_response_time: float
    requests_per_sec: float
    failure_rate: float
    event: str = ""  # e.g., "fault_start", "fault_end"


class MetricsCollector:
    """Collects time-series metrics during the test."""
    
    def __init__(self, base_url: str = "http://localhost:8000", interval: float = 1.0):
        self.base_url = base_url
        self.interval = interval
        self.data_points: List[TimeSeriesPoint] = []
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._start_time: float = 0
        self._events: List[Tuple[float, str]] = []
        
        # Rolling window for rate calculation
        self._prev_requests = 0
        self._prev_failures = 0
        self._prev_time = 0
    
    def add_event(self, event_name: str):
        """Add an event marker at the current time."""
        self._events.append((time.time(), event_name))
    
    def start(self):
        """Start collecting metrics."""
        self._stop_event.clear()
        self._start_time = time.time()
        self._prev_time = self._start_time
        self._thread = threading.Thread(target=self._collect_loop, daemon=True)
        self._thread.start()
    
    def stop(self) -> List[TimeSeriesPoint]:
        """Stop collecting and return data points."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        
        # Annotate events
        for event_time, event_name in self._events:
            elapsed = event_time - self._start_time
            # Find closest data point
            for point in self.data_points:
                if abs(point.elapsed_sec - elapsed) < self.interval:
                    point.event = event_name
                    break
        
        return self.data_points
    
    def _collect_loop(self):
        """Main collection loop - polls the API for health/requests info."""
        # Note: Since we can't easily get real-time stats from Locust,
        # we'll parse the CSV history file periodically
        pass  # We'll use the Locust CSV history instead


def stop_container(container: str) -> bool:
    """Stop a Docker container."""
    try:
        result = subprocess.run(
            ['docker', 'stop', container],
            capture_output=True, text=True, timeout=30
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error stopping {container}: {e}")
        return False


def start_container(container: str) -> bool:
    """Start a Docker container."""
    try:
        result = subprocess.run(
            ['docker', 'start', container],
            capture_output=True, text=True, timeout=30
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error starting {container}: {e}")
        return False


def wait_for_healthy(container: str, timeout: int = 60) -> bool:
    """Wait for a container to become healthy."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            result = subprocess.run(
                ['docker', 'inspect', '--format', '{{.State.Health.Status}}', container],
                capture_output=True, text=True, timeout=5
            )
            status = result.stdout.strip()
            if status == 'healthy':
                return True
            time.sleep(2)
        except:
            time.sleep(2)
    return False


def run_resilience_test(
    target_service: str,
    users: int,
    spawn_rate: int,
    total_duration: int,  # seconds
    fault_start: int,  # seconds after test start to inject fault
    fault_duration: int,  # seconds to keep service down
    output_dir: Path
) -> Tuple[List[TimeSeriesPoint], Dict]:
    """
    Run the resilience test:
    1. Start load test
    2. After fault_start seconds, stop the target service
    3. After fault_duration seconds, restart the service
    4. Continue test until total_duration
    """
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    container = SERVICES.get(target_service)
    if not container:
        print(f"❌ Unknown service: {target_service}")
        return [], {}
    
    script_dir = Path(__file__).parent.parent
    locustfile = script_dir / 'locustfile_microservices.py'
    csv_prefix = output_dir / "stats"
    
    # Prepare Locust command
    cmd = [
        'locust',
        '-f', str(locustfile),
        '--headless',
        '--users', str(users),
        '--spawn-rate', str(spawn_rate),
        '--run-time', f'{total_duration}s',
        '--csv', str(csv_prefix),
        '--csv-full-history',
        '--logfile', str(output_dir / 'locust.log'),
        '--loglevel', 'WARNING',
    ]
    
    # Event log
    events = []
    test_start = time.time()
    
    def inject_fault():
        """Background thread to inject/recover fault."""
        nonlocal events
        
        # Wait until fault_start
        time.sleep(fault_start)
        
        # Inject fault
        print(f"\n🔥 INJECTING FAULT: Stopping {target_service}...")
        events.append({'time': time.time() - test_start, 'event': 'fault_start', 'service': target_service})
        stop_container(container)
        
        # Wait for fault_duration
        time.sleep(fault_duration)
        
        # Recover
        print(f"\n🔧 RECOVERING: Starting {target_service}...")
        events.append({'time': time.time() - test_start, 'event': 'fault_end', 'service': target_service})
        start_container(container)
        
        # Wait for healthy
        print(f"⏳ Waiting for {target_service} to become healthy...")
        if wait_for_healthy(container, timeout=60):
            recovery_time = time.time() - test_start
            events.append({'time': recovery_time, 'event': 'service_healthy', 'service': target_service})
            print(f"✅ {target_service} is healthy again!")
        else:
            print(f"⚠️ {target_service} did not become healthy in time")
    
    # Start fault injection thread
    fault_thread = threading.Thread(target=inject_fault, daemon=True)
    
    print(f"\n🚀 Starting load test...")
    print(f"   Duration: {total_duration}s")
    print(f"   Fault injection at: {fault_start}s")
    print(f"   Fault duration: {fault_duration}s")
    print(f"   Target service: {target_service}")
    
    # Start Locust
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Start fault injection
    fault_thread.start()
    
    # Wait for test to complete
    try:
        stdout, stderr = process.communicate(timeout=total_duration + 60)
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()
    
    print(f"\n✅ Load test completed!")
    
    # Parse the history CSV for time series data
    history_file = output_dir / "stats_stats_history.csv"
    data_points = []
    
    if history_file.exists():
        df = pd.read_csv(history_file)
        
        for _, row in df.iterrows():
            elapsed = float(row['Timestamp']) - test_start if 'Timestamp' in row.columns else 0
            
            total_reqs = int(row.get('Total Request Count', 0))
            total_fails = int(row.get('Total Failure Count', 0))
            rps = float(row.get('Requests/s', 0))
            fail_rate = (total_fails / total_reqs * 100) if total_reqs > 0 else 0
            
            # Get response time (use Total Average if available)
            avg_rt = 0
            for col in ['Total Average Response Time', 'Average Response Time']:
                if col in row and pd.notna(row[col]):
                    avg_rt = float(row[col])
                    break
            
            point = TimeSeriesPoint(
                timestamp=row.get('Timestamp', 0),
                elapsed_sec=elapsed,
                requests=total_reqs,
                failures=total_fails,
                avg_response_time=avg_rt,
                requests_per_sec=rps,
                failure_rate=fail_rate
            )
            data_points.append(point)
    
    # Build event info
    event_info = {
        'test_start': 0,
        'fault_start': fault_start,
        'fault_end': fault_start + fault_duration,
        'events': events
    }
    
    return data_points, event_info


def create_timeline_plot(
    data_points: List[TimeSeriesPoint],
    event_info: Dict,
    output_dir: Path,
    target_service: str
):
    """Create the timeline visualization with fault markers."""
    
    if not data_points:
        print("⚠️ No data points to plot")
        return
    
    times = [p.elapsed_sec for p in data_points]
    rps = [p.requests_per_sec for p in data_points]
    fail_rate = [p.failure_rate for p in data_points]
    latency = [p.avg_response_time for p in data_points]
    
    fault_start = event_info.get('fault_start', 0)
    fault_end = event_info.get('fault_end', 0)
    
    # Create figure with 3 subplots
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 12), sharex=True)
    
    # Colors
    LINE_COLOR = '#2563EB'
    FAULT_COLOR = '#DC2626'
    RECOVERY_COLOR = '#059669'
    
    # ========== PLOT 1: Throughput ==========
    ax1.plot(times, rps, color=LINE_COLOR, linewidth=2)
    ax1.fill_between(times, rps, alpha=0.2, color=LINE_COLOR)
    ax1.set_ylabel('Throughput (req/s)', fontweight='bold')
    ax1.set_title(f'Resilience Test: Fault Injection on {target_service}', fontweight='bold', fontsize=16)
    ax1.grid(True, alpha=0.3)
    
    # Add fault zone shading
    ax1.axvspan(fault_start, fault_end, alpha=0.2, color=FAULT_COLOR, label='Fault Period')
    ax1.axvline(x=fault_start, color=FAULT_COLOR, linestyle='--', linewidth=2, label='Fault Injected')
    ax1.axvline(x=fault_end, color=RECOVERY_COLOR, linestyle='--', linewidth=2, label='Service Restarted')
    
    # ========== PLOT 2: Error Rate ==========
    ax2.plot(times, fail_rate, color=FAULT_COLOR, linewidth=2)
    ax2.fill_between(times, fail_rate, alpha=0.2, color=FAULT_COLOR)
    ax2.set_ylabel('Error Rate (%)', fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(bottom=0)
    
    # Add fault zone shading
    ax2.axvspan(fault_start, fault_end, alpha=0.2, color=FAULT_COLOR)
    ax2.axvline(x=fault_start, color=FAULT_COLOR, linestyle='--', linewidth=2)
    ax2.axvline(x=fault_end, color=RECOVERY_COLOR, linestyle='--', linewidth=2)
    
    # ========== PLOT 3: Latency ==========
    ax3.plot(times, latency, color='#7C3AED', linewidth=2)
    ax3.fill_between(times, latency, alpha=0.2, color='#7C3AED')
    ax3.set_ylabel('Avg Response Time (ms)', fontweight='bold')
    ax3.set_xlabel('Time (seconds)', fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # Add fault zone shading
    ax3.axvspan(fault_start, fault_end, alpha=0.2, color=FAULT_COLOR)
    ax3.axvline(x=fault_start, color=FAULT_COLOR, linestyle='--', linewidth=2)
    ax3.axvline(x=fault_end, color=RECOVERY_COLOR, linestyle='--', linewidth=2)
    
    # Add legend
    legend_elements = [
        mpatches.Patch(facecolor=FAULT_COLOR, alpha=0.2, label='Fault Period'),
        Line2D([0], [0], color=FAULT_COLOR, linestyle='--', linewidth=2, label=f'{target_service} Stopped'),
        Line2D([0], [0], color=RECOVERY_COLOR, linestyle='--', linewidth=2, label=f'{target_service} Restarted'),
    ]
    fig.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.98, 0.98))
    
    # Add annotations
    ax1.annotate('Fault Injected', xy=(fault_start, ax1.get_ylim()[1] * 0.9),
                 fontsize=10, fontweight='bold', color=FAULT_COLOR,
                 ha='center', va='top')
    ax1.annotate('Service Recovered', xy=(fault_end, ax1.get_ylim()[1] * 0.9),
                 fontsize=10, fontweight='bold', color=RECOVERY_COLOR,
                 ha='center', va='top')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'resilience_timeline.png')
    print(f"✓ Created: {output_dir}/resilience_timeline.png")
    plt.close()
    
    # ========== Create Summary Plot ==========
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Plot all three on same axes (normalized)
    ax2 = ax.twinx()
    ax3 = ax.twinx()
    ax3.spines['right'].set_position(('outward', 60))
    
    l1, = ax.plot(times, rps, color=LINE_COLOR, linewidth=2, label='Throughput')
    l2, = ax2.plot(times, fail_rate, color=FAULT_COLOR, linewidth=2, label='Error Rate')
    l3, = ax3.plot(times, latency, color='#7C3AED', linewidth=2, label='Latency')
    
    ax.set_xlabel('Time (seconds)', fontweight='bold')
    ax.set_ylabel('Throughput (req/s)', color=LINE_COLOR, fontweight='bold')
    ax2.set_ylabel('Error Rate (%)', color=FAULT_COLOR, fontweight='bold')
    ax3.set_ylabel('Latency (ms)', color='#7C3AED', fontweight='bold')
    
    ax.tick_params(axis='y', labelcolor=LINE_COLOR)
    ax2.tick_params(axis='y', labelcolor=FAULT_COLOR)
    ax3.tick_params(axis='y', labelcolor='#7C3AED')
    
    # Fault zone
    ax.axvspan(fault_start, fault_end, alpha=0.15, color=FAULT_COLOR)
    ax.axvline(x=fault_start, color=FAULT_COLOR, linestyle='--', linewidth=2)
    ax.axvline(x=fault_end, color=RECOVERY_COLOR, linestyle='--', linewidth=2)
    
    ax.set_title(f'Microservices Resilience: {target_service} Failure & Recovery',
                 fontweight='bold', fontsize=16)
    
    lines = [l1, l2, l3]
    labels = ['Throughput', 'Error Rate', 'Latency']
    ax.legend(lines, labels, loc='upper left')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'resilience_summary.png')
    print(f"✓ Created: {output_dir}/resilience_summary.png")
    plt.close()


def save_results(data_points: List[TimeSeriesPoint], event_info: Dict, output_dir: Path):
    """Save results to files."""
    
    # Save data points as CSV
    csv_path = output_dir / 'resilience_timeseries.csv'
    with open(csv_path, 'w', newline='') as f:
        if data_points:
            writer = csv.DictWriter(f, fieldnames=asdict(data_points[0]).keys())
            writer.writeheader()
            for p in data_points:
                writer.writerow(asdict(p))
    print(f"✓ Saved: {csv_path}")
    
    # Save event info as JSON
    json_path = output_dir / 'resilience_events.json'
    with open(json_path, 'w') as f:
        json.dump(event_info, f, indent=2)
    print(f"✓ Saved: {json_path}")


def check_microservices() -> bool:
    """Check if microservices are running."""
    try:
        result = subprocess.run(
            ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', 'http://localhost:8000/health'],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip() == '200'
    except:
        return False


def main():
    parser = argparse.ArgumentParser(description='Resilience / Failure Injection Test')
    parser.add_argument('--target-service', type=str, default='task-service',
                       choices=list(SERVICES.keys()),
                       help='Service to stop during test')
    parser.add_argument('--users', type=int, default=50,
                       help='Number of concurrent users')
    parser.add_argument('--spawn-rate', type=int, default=10,
                       help='Users spawned per second')
    parser.add_argument('--duration', type=int, default=120,
                       help='Total test duration in seconds')
    parser.add_argument('--fault-start', type=int, default=30,
                       help='Seconds after start to inject fault')
    parser.add_argument('--fault-duration', type=int, default=30,
                       help='Seconds to keep service down')
    parser.add_argument('--output', type=str, default=None,
                       help='Output directory')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("RESILIENCE / FAILURE INJECTION TEST")
    print("=" * 60)
    print(f"Target service: {args.target_service}")
    print(f"Users: {args.users}")
    print(f"Duration: {args.duration}s")
    print(f"Fault at: {args.fault_start}s (for {args.fault_duration}s)")
    print("")
    
    # Check microservices
    print("Checking microservices...")
    if not check_microservices():
        print("❌ Microservices must be running!")
        print("Start with: cd ../tasktracker-micro && docker compose up -d")
        sys.exit(1)
    print("✓ Microservices are running")
    
    # Setup output
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    if args.output:
        output_dir = Path(args.output)
    else:
        output_dir = Path(__file__).parent.parent / 'results' / f'resilience_{timestamp}'
    
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nOutput: {output_dir}")
    
    print("\n" + "=" * 60)
    print("STARTING RESILIENCE TEST")
    print("=" * 60)
    
    data_points, event_info = run_resilience_test(
        target_service=args.target_service,
        users=args.users,
        spawn_rate=args.spawn_rate,
        total_duration=args.duration,
        fault_start=args.fault_start,
        fault_duration=args.fault_duration,
        output_dir=output_dir
    )
    
    print("\n" + "=" * 60)
    print("SAVING RESULTS")
    print("=" * 60)
    save_results(data_points, event_info, output_dir)
    
    print("\n" + "=" * 60)
    print("GENERATING PLOTS")
    print("=" * 60)
    create_timeline_plot(data_points, event_info, output_dir, args.target_service)
    
    print("\n" + "=" * 60)
    print("✅ RESILIENCE TEST COMPLETE!")
    print("=" * 60)
    print(f"\nResults: {output_dir}")
    print(f"  - resilience_timeline.png     (3-panel timeline)")
    print(f"  - resilience_summary.png      (combined view)")
    print(f"  - resilience_timeseries.csv   (raw data)")
    print(f"  - resilience_events.json      (event markers)")
    
    # Print summary
    if data_points:
        fault_start = args.fault_start
        fault_end = args.fault_start + args.fault_duration
        
        before = [p for p in data_points if p.elapsed_sec < fault_start]
        during = [p for p in data_points if fault_start <= p.elapsed_sec < fault_end]
        after = [p for p in data_points if p.elapsed_sec >= fault_end]
        
        print("\n📊 SUMMARY:")
        if before:
            print(f"  Before fault: {np.mean([p.requests_per_sec for p in before]):.1f} req/s, {np.mean([p.failure_rate for p in before]):.1f}% errors")
        if during:
            print(f"  During fault: {np.mean([p.requests_per_sec for p in during]):.1f} req/s, {np.mean([p.failure_rate for p in during]):.1f}% errors")
        if after:
            print(f"  After recovery: {np.mean([p.requests_per_sec for p in after]):.1f} req/s, {np.mean([p.failure_rate for p in after]):.1f}% errors")


if __name__ == '__main__':
    main()
