"""
Docker container metrics collection using docker stats.
"""
import subprocess
import json
import time
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
import re


@dataclass
class ContainerSample:
    """A single sample of container metrics."""
    timestamp: float
    container_name: str
    cpu_percent: float
    mem_usage_bytes: int
    mem_limit_bytes: int
    mem_percent: float
    net_io_rx_bytes: int = 0
    net_io_tx_bytes: int = 0


@dataclass
class ContainerTimeSeries:
    """Time series of container metrics."""
    container_name: str
    samples: List[ContainerSample] = field(default_factory=list)
    
    def add_sample(self, sample: ContainerSample) -> None:
        self.samples.append(sample)
    
    def get_avg_cpu(self) -> float:
        if not self.samples:
            return 0.0
        return sum(s.cpu_percent for s in self.samples) / len(self.samples)
    
    def get_peak_cpu(self) -> float:
        if not self.samples:
            return 0.0
        return max(s.cpu_percent for s in self.samples)
    
    def get_avg_mem(self) -> float:
        if not self.samples:
            return 0.0
        return sum(s.mem_usage_bytes for s in self.samples) / len(self.samples)
    
    def get_peak_mem(self) -> int:
        if not self.samples:
            return 0
        return max(s.mem_usage_bytes for s in self.samples)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "container_name": self.container_name,
            "samples": [asdict(s) for s in self.samples],
            "summary": {
                "avg_cpu_percent": self.get_avg_cpu(),
                "peak_cpu_percent": self.get_peak_cpu(),
                "avg_mem_bytes": self.get_avg_mem(),
                "peak_mem_bytes": self.get_peak_mem()
            }
        }


@dataclass
class ResourceMetricsSummary:
    """Summary of resource metrics across all containers."""
    containers: Dict[str, ContainerTimeSeries] = field(default_factory=dict)
    
    def get_total_avg_cpu(self) -> float:
        """Get total average CPU across all containers."""
        return sum(c.get_avg_cpu() for c in self.containers.values())
    
    def get_total_peak_cpu(self) -> float:
        """Get total peak CPU (approximation - sum of peaks)."""
        return sum(c.get_peak_cpu() for c in self.containers.values())
    
    def get_total_avg_mem(self) -> float:
        """Get total average memory across all containers."""
        return sum(c.get_avg_mem() for c in self.containers.values())
    
    def get_total_peak_mem(self) -> int:
        """Get total peak memory (approximation - sum of peaks)."""
        return sum(c.get_peak_mem() for c in self.containers.values())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "containers": {name: ts.to_dict() for name, ts in self.containers.items()},
            "totals": {
                "avg_cpu_percent": self.get_total_avg_cpu(),
                "peak_cpu_percent": self.get_total_peak_cpu(),
                "avg_mem_bytes": self.get_total_avg_mem(),
                "peak_mem_bytes": self.get_total_peak_mem(),
                "avg_mem_gb": self.get_total_avg_mem() / (1024**3),
                "peak_mem_gb": self.get_total_peak_mem() / (1024**3)
            }
        }


def parse_memory_string(mem_str: str) -> int:
    """Parse memory string like '100MiB' or '1.5GiB' to bytes."""
    mem_str = mem_str.strip()
    units = {
        'B': 1,
        'KiB': 1024,
        'MiB': 1024**2,
        'GiB': 1024**3,
        'KB': 1000,
        'MB': 1000**2,
        'GB': 1000**3,
        'kB': 1000,
    }
    
    for unit, multiplier in sorted(units.items(), key=lambda x: -len(x[0])):
        if mem_str.endswith(unit):
            value = float(mem_str[:-len(unit)])
            return int(value * multiplier)
    
    # Try parsing as raw bytes
    try:
        return int(float(mem_str))
    except ValueError:
        return 0


def parse_percentage(pct_str: str) -> float:
    """Parse percentage string like '15.5%' to float."""
    pct_str = pct_str.strip().rstrip('%')
    try:
        return float(pct_str)
    except ValueError:
        return 0.0


def sample_container_stats(container_names: List[str]) -> Dict[str, ContainerSample]:
    """Sample stats for multiple containers using docker stats --no-stream."""
    samples = {}
    timestamp = time.time()
    
    try:
        # Use docker stats with JSON format for easier parsing
        result = subprocess.run(
            ["docker", "stats", "--no-stream", "--format", 
             "{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            print(f"Warning: docker stats failed: {result.stderr}")
            return samples
        
        for line in result.stdout.strip().split('\n'):
            if not line.strip():
                continue
            
            parts = line.split('\t')
            if len(parts) < 4:
                continue
            
            name = parts[0].strip()
            if name not in container_names:
                continue
            
            cpu_pct = parse_percentage(parts[1])
            
            # Parse memory usage (e.g., "100MiB / 1GiB")
            mem_parts = parts[2].split('/')
            mem_usage = parse_memory_string(mem_parts[0].strip()) if len(mem_parts) > 0 else 0
            mem_limit = parse_memory_string(mem_parts[1].strip()) if len(mem_parts) > 1 else 0
            
            mem_pct = parse_percentage(parts[3])
            
            samples[name] = ContainerSample(
                timestamp=timestamp,
                container_name=name,
                cpu_percent=cpu_pct,
                mem_usage_bytes=mem_usage,
                mem_limit_bytes=mem_limit,
                mem_percent=mem_pct
            )
    
    except subprocess.TimeoutExpired:
        print("Warning: docker stats timed out")
    except Exception as e:
        print(f"Warning: Error sampling docker stats: {e}")
    
    return samples


class ResourceMonitor:
    """Continuous resource monitoring in a background thread."""
    
    def __init__(self, container_names: List[str], sample_interval: float = 1.0):
        self.container_names = container_names
        self.sample_interval = sample_interval
        self.metrics = ResourceMetricsSummary()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        
        # Initialize time series for each container
        for name in container_names:
            self.metrics.containers[name] = ContainerTimeSeries(container_name=name)
    
    def start(self) -> None:
        """Start monitoring in background thread."""
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
    
    def stop(self) -> ResourceMetricsSummary:
        """Stop monitoring and return collected metrics."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
        return self.metrics
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self._running:
            try:
                samples = sample_container_stats(self.container_names)
                for name, sample in samples.items():
                    if name in self.metrics.containers:
                        self.metrics.containers[name].add_sample(sample)
            except Exception as e:
                print(f"Warning: Error in monitoring loop: {e}")
            
            time.sleep(self.sample_interval)
    
    def get_current_metrics(self) -> ResourceMetricsSummary:
        """Get current metrics without stopping."""
        return self.metrics


def compute_efficiency_metrics(throughput_rps: float, 
                               resource_summary: ResourceMetricsSummary) -> Dict[str, float]:
    """Compute efficiency metrics from throughput and resource usage."""
    total_avg_cpu = resource_summary.get_total_avg_cpu()
    total_avg_mem_gb = resource_summary.get_total_avg_mem() / (1024**3)
    
    # CPU efficiency: requests per CPU "unit" (100% = 1 vCPU equivalent)
    cpu_units = total_avg_cpu / 100.0 if total_avg_cpu > 0 else 1.0
    rps_per_cpu = throughput_rps / cpu_units if cpu_units > 0 else 0.0
    
    # Memory efficiency: requests per GB
    rps_per_gb_mem = throughput_rps / total_avg_mem_gb if total_avg_mem_gb > 0 else 0.0
    
    return {
        "rps_per_cpu_unit": rps_per_cpu,
        "rps_per_gb_mem": rps_per_gb_mem,
        "total_cpu_units": cpu_units,
        "total_mem_gb": total_avg_mem_gb
    }
