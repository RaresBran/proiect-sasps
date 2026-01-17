"""
Load test runner that wraps the existing Locust tests.
"""
import subprocess
import csv
import time
import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime

from .io_utils import get_project_root


@dataclass
class LoadTestResult:
    """Results from a single load test run."""
    arch: str
    concurrency: int
    duration_s: int
    warmup_s: int
    spawn_rate: int
    throughput_rps: float
    latency_p50_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    latency_avg_ms: float
    latency_min_ms: float
    latency_max_ms: float
    error_rate: float
    total_requests: int
    total_failures: int
    start_ts: str
    end_ts: str
    raw_csv_path: Optional[str] = None
    history_csv_path: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TimeSeriesMetrics:
    """Per-second time series metrics from a load test."""
    timestamps: List[float]
    user_counts: List[int]
    requests_per_second: List[float]
    failures_per_second: List[float]
    latency_p50: List[float]
    latency_p95: List[float]
    latency_p99: List[float]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def check_service_health(base_url: str, timeout: int = 5) -> bool:
    """Check if a service is healthy."""
    import requests
    try:
        response = requests.get(f"{base_url}/health", timeout=timeout)
        return response.status_code == 200
    except Exception:
        return False


def run_locust_test(
    locustfile: str,
    users: int,
    spawn_rate: int,
    duration_seconds: int,
    output_dir: Path,
    host: Optional[str] = None,
    extra_args: Optional[List[str]] = None
) -> Dict[str, Path]:
    """
    Run a Locust test and return paths to output files.
    
    Args:
        locustfile: Path to the locustfile (relative to project root)
        users: Number of concurrent users
        spawn_rate: User spawn rate per second
        duration_seconds: Test duration in seconds
        output_dir: Directory to store output files
        host: Override host URL (optional)
        extra_args: Additional Locust arguments
    
    Returns:
        Dictionary with paths to output files
    """
    project_root = get_project_root()
    locustfile_path = project_root / locustfile
    
    if not locustfile_path.exists():
        raise FileNotFoundError(f"Locustfile not found: {locustfile_path}")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_prefix = output_dir / "stats"
    html_path = output_dir / "report.html"
    log_path = output_dir / "locust.log"
    
    cmd = [
        "locust",
        "-f", str(locustfile_path),
        "--headless",
        "--users", str(users),
        "--spawn-rate", str(spawn_rate),
        "--run-time", f"{duration_seconds}s",
        "--csv", str(csv_prefix),
        "--html", str(html_path),
        "--logfile", str(log_path),
        "--loglevel", "INFO"
    ]
    
    if host:
        cmd.extend(["--host", host])
    
    if extra_args:
        cmd.extend(extra_args)
    
    # Run from the performance tests directory for proper imports
    perf_tests_dir = project_root / "tasktracker-performance-tests"
    
    env = os.environ.copy()
    env["PYTHONPATH"] = str(perf_tests_dir) + ":" + env.get("PYTHONPATH", "")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(perf_tests_dir),
            env=env,
            capture_output=True,
            text=True,
            timeout=duration_seconds + 120  # Extra time for setup/teardown
        )
        
        if result.returncode != 0:
            print(f"Warning: Locust returned non-zero exit code: {result.returncode}")
            print(f"Stderr: {result.stderr[:1000] if result.stderr else 'None'}")
    
    except subprocess.TimeoutExpired:
        print("Warning: Locust test timed out")
    except Exception as e:
        print(f"Error running Locust: {e}")
    
    return {
        "stats_csv": output_dir / "stats_stats.csv",
        "history_csv": output_dir / "stats_stats_history.csv",
        "failures_csv": output_dir / "stats_failures.csv",
        "exceptions_csv": output_dir / "stats_exceptions.csv",
        "html_report": html_path,
        "log": log_path
    }


def parse_locust_stats(stats_csv_path: Path) -> Dict[str, Any]:
    """Parse the Locust stats CSV file to extract aggregated metrics."""
    if not stats_csv_path.exists():
        return {
            "throughput_rps": 0.0,
            "latency_p50_ms": 0.0,
            "latency_p95_ms": 0.0,
            "latency_p99_ms": 0.0,
            "latency_avg_ms": 0.0,
            "latency_min_ms": 0.0,
            "latency_max_ms": 0.0,
            "error_rate": 0.0,
            "total_requests": 0,
            "total_failures": 0
        }
    
    with open(stats_csv_path, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Find the Aggregated row
    aggregated = None
    for row in rows:
        if row.get('Name') == 'Aggregated' or row.get('Name', '').strip() == '':
            aggregated = row
            break
    
    if not aggregated:
        return {
            "throughput_rps": 0.0,
            "latency_p50_ms": 0.0,
            "latency_p95_ms": 0.0,
            "latency_p99_ms": 0.0,
            "latency_avg_ms": 0.0,
            "latency_min_ms": 0.0,
            "latency_max_ms": 0.0,
            "error_rate": 0.0,
            "total_requests": 0,
            "total_failures": 0
        }
    
    total_requests = int(aggregated.get('Request Count', 0))
    total_failures = int(aggregated.get('Failure Count', 0))
    
    error_rate = (total_failures / total_requests * 100) if total_requests > 0 else 0.0
    
    return {
        "throughput_rps": float(aggregated.get('Requests/s', 0)),
        "latency_p50_ms": float(aggregated.get('50%', 0)),
        "latency_p95_ms": float(aggregated.get('95%', 0)),
        "latency_p99_ms": float(aggregated.get('99%', 0)),
        "latency_avg_ms": float(aggregated.get('Average Response Time', 0)),
        "latency_min_ms": float(aggregated.get('Min Response Time', 0)),
        "latency_max_ms": float(aggregated.get('Max Response Time', 0)),
        "error_rate": error_rate,
        "total_requests": total_requests,
        "total_failures": total_failures
    }


def parse_locust_history(history_csv_path: Path) -> TimeSeriesMetrics:
    """Parse the Locust history CSV file for time series data."""
    timestamps = []
    user_counts = []
    requests_per_second = []
    failures_per_second = []
    latency_p50 = []
    latency_p95 = []
    latency_p99 = []
    
    if not history_csv_path.exists():
        return TimeSeriesMetrics(
            timestamps=timestamps,
            user_counts=user_counts,
            requests_per_second=requests_per_second,
            failures_per_second=failures_per_second,
            latency_p50=latency_p50,
            latency_p95=latency_p95,
            latency_p99=latency_p99
        )
    
    with open(history_csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Only include Aggregated rows
            if row.get('Name', '').strip() != 'Aggregated':
                continue
            
            try:
                ts = float(row.get('Timestamp', 0))
                timestamps.append(ts)
                user_counts.append(int(row.get('User Count', 0)))
                requests_per_second.append(float(row.get('Requests/s', 0)))
                failures_per_second.append(float(row.get('Failures/s', 0)))
                
                # Handle N/A values in percentiles
                p50 = row.get('50%', '0')
                p95 = row.get('95%', '0')
                p99 = row.get('99%', '0')
                
                latency_p50.append(float(p50) if p50 != 'N/A' else 0.0)
                latency_p95.append(float(p95) if p95 != 'N/A' else 0.0)
                latency_p99.append(float(p99) if p99 != 'N/A' else 0.0)
            except (ValueError, TypeError) as e:
                continue
    
    return TimeSeriesMetrics(
        timestamps=timestamps,
        user_counts=user_counts,
        requests_per_second=requests_per_second,
        failures_per_second=failures_per_second,
        latency_p50=latency_p50,
        latency_p95=latency_p95,
        latency_p99=latency_p99
    )


def run_load_test(
    arch: str,
    concurrency: int,
    duration_s: int,
    warmup_s: int,
    spawn_rate: int,
    output_dir: Path,
    base_url: Optional[str] = None
) -> LoadTestResult:
    """
    Run a complete load test and return parsed results.
    
    Args:
        arch: Architecture type ('monolith' or 'microservices')
        concurrency: Number of concurrent users
        duration_s: Test duration in seconds (excluding warmup)
        warmup_s: Warmup time (user count ramp-up considered as warmup)
        spawn_rate: User spawn rate per second
        output_dir: Directory to store output files
        base_url: Optional base URL override
    
    Returns:
        LoadTestResult with all metrics
    """
    from experiments.config import LOCUSTFILE_MONOLITH, LOCUSTFILE_MICROSERVICES
    
    start_ts = datetime.now().isoformat()
    
    # Select locustfile based on architecture
    if arch == "monolith":
        locustfile = LOCUSTFILE_MONOLITH
    elif arch == "microservices":
        locustfile = LOCUSTFILE_MICROSERVICES
    else:
        raise ValueError(f"Unknown architecture: {arch}")
    
    # Total duration includes warmup (Locust handles ramp-up internally)
    total_duration = duration_s + warmup_s
    
    # Run the test
    output_files = run_locust_test(
        locustfile=locustfile,
        users=concurrency,
        spawn_rate=spawn_rate,
        duration_seconds=total_duration,
        output_dir=output_dir,
        host=base_url
    )
    
    end_ts = datetime.now().isoformat()
    
    # Parse results
    stats = parse_locust_stats(output_files["stats_csv"])
    
    return LoadTestResult(
        arch=arch,
        concurrency=concurrency,
        duration_s=duration_s,
        warmup_s=warmup_s,
        spawn_rate=spawn_rate,
        throughput_rps=stats["throughput_rps"],
        latency_p50_ms=stats["latency_p50_ms"],
        latency_p95_ms=stats["latency_p95_ms"],
        latency_p99_ms=stats["latency_p99_ms"],
        latency_avg_ms=stats["latency_avg_ms"],
        latency_min_ms=stats["latency_min_ms"],
        latency_max_ms=stats["latency_max_ms"],
        error_rate=stats["error_rate"],
        total_requests=stats["total_requests"],
        total_failures=stats["total_failures"],
        start_ts=start_ts,
        end_ts=end_ts,
        raw_csv_path=str(output_files["stats_csv"]),
        history_csv_path=str(output_files["history_csv"])
    )
