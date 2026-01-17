#!/usr/bin/env python3
"""
Parameter sweep experiment runner.

Runs load tests across multiple concurrency levels for both architectures,
collecting performance metrics and resource usage data.

Usage:
    python run_sweep.py --arch both --concurrency-levels 10,25,50,100,200
    python run_sweep.py --arch monolith --duration-seconds 60 --warmup-seconds 10
"""
import argparse
import sys
import os
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from experiments.config import (
    DEFAULT_CONCURRENCY_LEVELS,
    DEFAULT_DURATION_SECONDS,
    DEFAULT_WARMUP_SECONDS,
    DEFAULT_SPAWN_RATE,
    MONOLITH_BASE_URL,
    MICROSERVICES_BASE_URL,
    MONOLITH_CONTAINERS,
    MICROSERVICES_CONTAINERS
)
from experiments.lib.io_utils import (
    create_results_dir,
    write_json,
    append_jsonl,
    get_project_root
)
from experiments.lib.loadtest_runner import (
    run_load_test,
    check_service_health,
    LoadTestResult
)
from experiments.lib.docker_metrics import (
    ResourceMonitor,
    compute_efficiency_metrics
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run parameter sweep experiments for architecture comparison"
    )
    
    parser.add_argument(
        "--arch",
        choices=["monolith", "microservices", "both"],
        default="both",
        help="Architecture to test (default: both)"
    )
    
    parser.add_argument(
        "--concurrency-levels",
        type=str,
        default=",".join(map(str, DEFAULT_CONCURRENCY_LEVELS)),
        help=f"Comma-separated concurrency levels (default: {','.join(map(str, DEFAULT_CONCURRENCY_LEVELS))})"
    )
    
    parser.add_argument(
        "--duration-seconds",
        type=int,
        default=DEFAULT_DURATION_SECONDS,
        help=f"Test duration in seconds (default: {DEFAULT_DURATION_SECONDS})"
    )
    
    parser.add_argument(
        "--warmup-seconds",
        type=int,
        default=DEFAULT_WARMUP_SECONDS,
        help=f"Warmup time in seconds (default: {DEFAULT_WARMUP_SECONDS})"
    )
    
    parser.add_argument(
        "--spawn-rate",
        type=int,
        default=DEFAULT_SPAWN_RATE,
        help=f"User spawn rate per second (default: {DEFAULT_SPAWN_RATE})"
    )
    
    parser.add_argument(
        "--base-url-monolith",
        type=str,
        default=MONOLITH_BASE_URL,
        help=f"Monolith base URL (default: {MONOLITH_BASE_URL})"
    )
    
    parser.add_argument(
        "--base-url-micro",
        type=str,
        default=MICROSERVICES_BASE_URL,
        help=f"Microservices base URL (default: {MICROSERVICES_BASE_URL})"
    )
    
    parser.add_argument(
        "--outdir",
        type=str,
        default=None,
        help="Output directory (default: experiments/results/<timestamp>)"
    )
    
    parser.add_argument(
        "--sample-interval",
        type=float,
        default=1.0,
        help="Docker stats sample interval in seconds (default: 1.0)"
    )
    
    parser.add_argument(
        "--skip-health-check",
        action="store_true",
        help="Skip health check before running tests"
    )
    
    return parser.parse_args()


def run_single_test(
    arch: str,
    concurrency: int,
    args: argparse.Namespace,
    results_dir: Path,
    run_index: int
) -> Dict[str, Any]:
    """Run a single test for one architecture at one concurrency level."""
    
    # Determine base URL and containers
    if arch == "monolith":
        base_url = args.base_url_monolith
        containers = MONOLITH_CONTAINERS
    else:
        base_url = args.base_url_micro
        containers = MICROSERVICES_CONTAINERS
    
    # Create run-specific output directory
    run_dir = results_dir / f"run_{run_index:03d}_{arch}_c{concurrency}"
    run_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"Running test: {arch} @ {concurrency} concurrent users")
    print(f"Duration: {args.duration_seconds}s + {args.warmup_seconds}s warmup")
    print(f"Output: {run_dir}")
    print(f"{'='*60}")
    
    # Start resource monitoring
    print("Starting resource monitoring...")
    resource_monitor = ResourceMonitor(
        container_names=containers,
        sample_interval=args.sample_interval
    )
    resource_monitor.start()
    
    try:
        # Run load test
        print("Running load test...")
        result = run_load_test(
            arch=arch,
            concurrency=concurrency,
            duration_s=args.duration_seconds,
            warmup_s=args.warmup_seconds,
            spawn_rate=args.spawn_rate,
            output_dir=run_dir,
            base_url=base_url
        )
        
    finally:
        # Stop resource monitoring
        print("Stopping resource monitoring...")
        resource_metrics = resource_monitor.stop()
    
    # Compute efficiency metrics
    efficiency = compute_efficiency_metrics(
        throughput_rps=result.throughput_rps,
        resource_summary=resource_metrics
    )
    
    # Combine all results
    combined_result = {
        **result.to_dict(),
        "resources": resource_metrics.to_dict(),
        "efficiency": efficiency
    }
    
    # Save per-run results
    write_json(combined_result, run_dir / "results.json")
    
    # Print summary
    print(f"\n--- Results Summary ---")
    print(f"Throughput: {result.throughput_rps:.2f} req/s")
    print(f"Latency P50: {result.latency_p50_ms:.2f} ms")
    print(f"Latency P95: {result.latency_p95_ms:.2f} ms")
    print(f"Latency P99: {result.latency_p99_ms:.2f} ms")
    print(f"Error Rate: {result.error_rate:.2f}%")
    print(f"Total Requests: {result.total_requests}")
    print(f"CPU Units Used: {efficiency['total_cpu_units']:.2f}")
    print(f"Memory Used: {efficiency['total_mem_gb']:.2f} GB")
    print(f"RPS per CPU: {efficiency['rps_per_cpu_unit']:.2f}")
    print(f"RPS per GB: {efficiency['rps_per_gb_mem']:.2f}")
    
    return combined_result


def main():
    args = parse_args()
    
    # Parse concurrency levels
    concurrency_levels = [int(x.strip()) for x in args.concurrency_levels.split(",")]
    
    # Determine architectures to test
    if args.arch == "both":
        architectures = ["monolith", "microservices"]
    else:
        architectures = [args.arch]
    
    # Create results directory
    if args.outdir:
        results_dir = Path(args.outdir)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = get_project_root() / "experiments" / "results" / f"sweep_{timestamp}"
    
    results_dir.mkdir(parents=True, exist_ok=True)
    
    print("="*60)
    print("PARAMETER SWEEP EXPERIMENT")
    print("="*60)
    print(f"Architectures: {architectures}")
    print(f"Concurrency levels: {concurrency_levels}")
    print(f"Duration: {args.duration_seconds}s + {args.warmup_seconds}s warmup")
    print(f"Spawn rate: {args.spawn_rate} users/s")
    print(f"Results directory: {results_dir}")
    print("="*60)
    
    # Health checks
    if not args.skip_health_check:
        print("\nChecking service health...")
        for arch in architectures:
            if arch == "monolith":
                url = args.base_url_monolith
            else:
                url = args.base_url_micro
            
            if check_service_health(url):
                print(f"  ✓ {arch} is healthy at {url}")
            else:
                print(f"  ✗ {arch} is NOT healthy at {url}")
                print(f"\nPlease start the {arch} service and try again.")
                print(f"  For monolith: cd tasktracker-mono && docker compose up -d")
                print(f"  For microservices: cd tasktracker-micro && docker compose up -d")
                sys.exit(1)
    
    # Save experiment configuration
    config = {
        "architectures": architectures,
        "concurrency_levels": concurrency_levels,
        "duration_seconds": args.duration_seconds,
        "warmup_seconds": args.warmup_seconds,
        "spawn_rate": args.spawn_rate,
        "base_url_monolith": args.base_url_monolith,
        "base_url_micro": args.base_url_micro,
        "sample_interval": args.sample_interval,
        "start_time": datetime.now().isoformat()
    }
    write_json(config, results_dir / "config.json")
    
    # Run experiments
    all_results = []
    run_index = 0
    results_jsonl = results_dir / "results.jsonl"
    
    for concurrency in concurrency_levels:
        for arch in architectures:
            try:
                result = run_single_test(
                    arch=arch,
                    concurrency=concurrency,
                    args=args,
                    results_dir=results_dir,
                    run_index=run_index
                )
                all_results.append(result)
                append_jsonl(result, results_jsonl)
                run_index += 1
                
                # Brief pause between tests
                print("\nPausing 5 seconds before next test...")
                time.sleep(5)
                
            except Exception as e:
                print(f"\nError running test {arch}@{concurrency}: {e}")
                import traceback
                traceback.print_exc()
                continue
    
    # Save all results
    write_json(all_results, results_dir / "all_results.json")
    
    # Update config with end time
    config["end_time"] = datetime.now().isoformat()
    config["total_runs"] = len(all_results)
    write_json(config, results_dir / "config.json")
    
    print("\n" + "="*60)
    print("SWEEP COMPLETE")
    print("="*60)
    print(f"Total runs: {len(all_results)}")
    print(f"Results saved to: {results_dir}")
    print(f"\nTo generate plots, run:")
    print(f"  python experiments/plot_results.py {results_dir}")


if __name__ == "__main__":
    main()
