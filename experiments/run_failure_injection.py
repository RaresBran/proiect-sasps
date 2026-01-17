#!/usr/bin/env python3
"""
Failure injection experiment runner.

Runs a steady load test against the microservices architecture while injecting
a failure (restart or stop) of a specific service, measuring the impact and recovery.

Usage:
    python run_failure_injection.py
    python run_failure_injection.py --target-service tasktracker_task_service --downtime 10
"""
import argparse
import subprocess
import sys
import os
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from experiments.config import (
    DEFAULT_FAILURE_CONCURRENCY,
    DEFAULT_FAILURE_DURATION,
    DEFAULT_INJECT_AT_SECONDS,
    DEFAULT_DOWNTIME_SECONDS,
    DEFAULT_TARGET_SERVICE,
    MICROSERVICES_BASE_URL,
    MICROSERVICES_CONTAINERS,
    LOCUSTFILE_MICROSERVICES
)
from experiments.lib.io_utils import (
    create_results_dir,
    write_json,
    get_project_root
)
from experiments.lib.loadtest_runner import (
    run_locust_test,
    parse_locust_stats,
    parse_locust_history,
    check_service_health
)
from experiments.lib.docker_metrics import (
    ResourceMonitor
)


def docker_restart_service(container_name: str) -> bool:
    """Restart a Docker container."""
    try:
        result = subprocess.run(
            ["docker", "restart", container_name],
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error restarting {container_name}: {e}")
        return False


def docker_stop_service(container_name: str) -> bool:
    """Stop a Docker container."""
    try:
        result = subprocess.run(
            ["docker", "stop", container_name],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error stopping {container_name}: {e}")
        return False


def docker_start_service(container_name: str) -> bool:
    """Start a Docker container."""
    try:
        result = subprocess.run(
            ["docker", "start", container_name],
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error starting {container_name}: {e}")
        return False


def inject_failure(
    target_service: str,
    downtime_seconds: int,
    failure_mode: str = "restart"
) -> Dict[str, Any]:
    """
    Inject a failure into the target service.
    
    Args:
        target_service: Container name to fail
        downtime_seconds: How long to keep service down (for stop-start mode)
        failure_mode: "restart" or "stop-start"
    
    Returns:
        Dictionary with injection details
    """
    inject_start = datetime.now().isoformat()
    inject_start_ts = time.time()
    
    print(f"\n{'!'*60}")
    print(f"INJECTING FAILURE: {failure_mode} on {target_service}")
    print(f"{'!'*60}")
    
    if failure_mode == "restart":
        success = docker_restart_service(target_service)
        actual_downtime = 0  # Docker restart is atomic-ish
    else:  # stop-start
        stop_success = docker_stop_service(target_service)
        if stop_success:
            print(f"Service stopped. Waiting {downtime_seconds} seconds...")
            time.sleep(downtime_seconds)
            start_success = docker_start_service(target_service)
            success = start_success
            actual_downtime = downtime_seconds
        else:
            success = False
            actual_downtime = 0
    
    inject_end = datetime.now().isoformat()
    inject_end_ts = time.time()
    
    print(f"Failure injection complete. Success: {success}")
    print(f"{'!'*60}\n")
    
    return {
        "target_service": target_service,
        "failure_mode": failure_mode,
        "downtime_seconds": actual_downtime,
        "inject_start_ts": inject_start,
        "inject_end_ts": inject_end,
        "inject_start_epoch": inject_start_ts,
        "inject_end_epoch": inject_end_ts,
        "success": success
    }


def schedule_failure_injection(
    target_service: str,
    inject_at_seconds: int,
    downtime_seconds: int,
    failure_mode: str,
    results_container: Dict[str, Any]
) -> threading.Thread:
    """
    Schedule failure injection to occur after a delay.
    
    Returns a thread that will execute the injection.
    """
    def injection_thread():
        print(f"\nWaiting {inject_at_seconds}s before injecting failure...")
        time.sleep(inject_at_seconds)
        result = inject_failure(target_service, downtime_seconds, failure_mode)
        results_container["injection"] = result
    
    thread = threading.Thread(target=injection_thread, daemon=True)
    return thread


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run failure injection experiment on microservices"
    )
    
    parser.add_argument(
        "--concurrency",
        type=int,
        default=DEFAULT_FAILURE_CONCURRENCY,
        help=f"Number of concurrent users (default: {DEFAULT_FAILURE_CONCURRENCY})"
    )
    
    parser.add_argument(
        "--duration-seconds",
        type=int,
        default=DEFAULT_FAILURE_DURATION,
        help=f"Total test duration in seconds (default: {DEFAULT_FAILURE_DURATION})"
    )
    
    parser.add_argument(
        "--inject-at",
        type=int,
        default=DEFAULT_INJECT_AT_SECONDS,
        help=f"Seconds after test start to inject failure (default: {DEFAULT_INJECT_AT_SECONDS})"
    )
    
    parser.add_argument(
        "--downtime",
        type=int,
        default=DEFAULT_DOWNTIME_SECONDS,
        help=f"Seconds to keep service down in stop-start mode (default: {DEFAULT_DOWNTIME_SECONDS})"
    )
    
    parser.add_argument(
        "--target-service",
        type=str,
        default=DEFAULT_TARGET_SERVICE,
        help=f"Container to fail (default: {DEFAULT_TARGET_SERVICE})"
    )
    
    parser.add_argument(
        "--failure-mode",
        choices=["restart", "stop-start"],
        default="restart",
        help="Failure mode: restart (quick) or stop-start (with downtime)"
    )
    
    parser.add_argument(
        "--base-url",
        type=str,
        default=MICROSERVICES_BASE_URL,
        help=f"Microservices base URL (default: {MICROSERVICES_BASE_URL})"
    )
    
    parser.add_argument(
        "--spawn-rate",
        type=int,
        default=20,
        help="User spawn rate per second (default: 20)"
    )
    
    parser.add_argument(
        "--outdir",
        type=str,
        default=None,
        help="Output directory (default: experiments/results/failure_<timestamp>)"
    )
    
    parser.add_argument(
        "--skip-health-check",
        action="store_true",
        help="Skip health check before running test"
    )
    
    return parser.parse_args()


def main():
    args = parse_args()
    
    # Create results directory
    if args.outdir:
        results_dir = Path(args.outdir)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = get_project_root() / "experiments" / "results" / f"failure_{timestamp}"
    
    results_dir.mkdir(parents=True, exist_ok=True)
    
    print("="*60)
    print("FAILURE INJECTION EXPERIMENT")
    print("="*60)
    print(f"Architecture: Microservices")
    print(f"Concurrency: {args.concurrency} users")
    print(f"Duration: {args.duration_seconds}s")
    print(f"Failure injection at: {args.inject_at}s")
    print(f"Target service: {args.target_service}")
    print(f"Failure mode: {args.failure_mode}")
    print(f"Downtime: {args.downtime}s (for stop-start mode)")
    print(f"Results directory: {results_dir}")
    print("="*60)
    
    # Health check
    if not args.skip_health_check:
        print("\nChecking service health...")
        if check_service_health(args.base_url):
            print(f"  ✓ Microservices healthy at {args.base_url}")
        else:
            print(f"  ✗ Microservices NOT healthy at {args.base_url}")
            print("\nPlease start the microservices stack:")
            print("  cd tasktracker-micro && docker compose up -d")
            sys.exit(1)
    
    # Save experiment configuration
    config = {
        "arch": "microservices",
        "concurrency": args.concurrency,
        "duration_seconds": args.duration_seconds,
        "inject_at_seconds": args.inject_at,
        "downtime_seconds": args.downtime,
        "target_service": args.target_service,
        "failure_mode": args.failure_mode,
        "spawn_rate": args.spawn_rate,
        "base_url": args.base_url,
        "start_time": datetime.now().isoformat()
    }
    write_json(config, results_dir / "config.json")
    
    # Container for injection results (to be filled by thread)
    injection_results: Dict[str, Any] = {}
    
    # Schedule failure injection
    injection_thread = schedule_failure_injection(
        target_service=args.target_service,
        inject_at_seconds=args.inject_at,
        downtime_seconds=args.downtime,
        failure_mode=args.failure_mode,
        results_container=injection_results
    )
    
    # Start resource monitoring
    print("\nStarting resource monitoring...")
    resource_monitor = ResourceMonitor(
        container_names=MICROSERVICES_CONTAINERS,
        sample_interval=1.0
    )
    resource_monitor.start()
    
    test_start_time = time.time()
    
    try:
        # Start injection thread (will wait and then inject)
        injection_thread.start()
        
        # Run load test
        print("\nRunning load test...")
        output_files = run_locust_test(
            locustfile=LOCUSTFILE_MICROSERVICES,
            users=args.concurrency,
            spawn_rate=args.spawn_rate,
            duration_seconds=args.duration_seconds,
            output_dir=results_dir,
            host=args.base_url
        )
        
        # Wait for injection thread to complete (if not already)
        injection_thread.join(timeout=5)
        
    finally:
        # Stop resource monitoring
        print("\nStopping resource monitoring...")
        resource_metrics = resource_monitor.stop()
    
    test_end_time = time.time()
    
    # Parse results
    stats = parse_locust_stats(output_files["stats_csv"])
    time_series = parse_locust_history(output_files["history_csv"])
    
    # Combine all results
    failure_results = {
        "config": config,
        "injection": injection_results.get("injection", {}),
        "stats": stats,
        "time_series": time_series.to_dict(),
        "resources": resource_metrics.to_dict(),
        "test_start_epoch": test_start_time,
        "test_end_epoch": test_end_time,
        "end_time": datetime.now().isoformat()
    }
    
    # Save results
    write_json(failure_results, results_dir / "failure_results.json")
    
    # Print summary
    print("\n" + "="*60)
    print("EXPERIMENT COMPLETE")
    print("="*60)
    print(f"\nOverall Results:")
    print(f"  Total Requests: {stats['total_requests']}")
    print(f"  Total Failures: {stats['total_failures']}")
    print(f"  Error Rate: {stats['error_rate']:.2f}%")
    print(f"  Throughput: {stats['throughput_rps']:.2f} req/s")
    print(f"  Latency P95: {stats['latency_p95_ms']:.2f} ms")
    print(f"  Latency P99: {stats['latency_p99_ms']:.2f} ms")
    
    if "injection" in injection_results:
        inj = injection_results["injection"]
        print(f"\nFailure Injection:")
        print(f"  Target: {inj.get('target_service', 'N/A')}")
        print(f"  Mode: {inj.get('failure_mode', 'N/A')}")
        print(f"  Success: {inj.get('success', False)}")
    
    print(f"\nResults saved to: {results_dir}")
    print(f"\nTo generate plots, run:")
    print(f"  python experiments/plot_failure_results.py {results_dir}")


if __name__ == "__main__":
    main()
