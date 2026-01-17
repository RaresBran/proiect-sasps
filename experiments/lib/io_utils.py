"""
I/O utilities for experiment results management.
"""
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


def create_results_dir(base_dir: str = "experiments/results", 
                       timestamp: Optional[str] = None) -> Path:
    """Create a timestamped results directory."""
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    project_root = get_project_root()
    results_path = project_root / base_dir / timestamp
    results_path.mkdir(parents=True, exist_ok=True)
    return results_path


def create_plots_dir(base_dir: str = "experiments/plots",
                     timestamp: Optional[str] = None) -> Path:
    """Create a timestamped plots directory."""
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    project_root = get_project_root()
    plots_path = project_root / base_dir / timestamp
    plots_path.mkdir(parents=True, exist_ok=True)
    return plots_path


def write_json(data: Any, filepath: Path) -> None:
    """Write data to a JSON file."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)


def append_jsonl(data: Dict[str, Any], filepath: Path) -> None:
    """Append a single JSON object to a JSONL file."""
    with open(filepath, 'a') as f:
        f.write(json.dumps(data, default=str) + '\n')


def read_json(filepath: Path) -> Any:
    """Read data from a JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def read_jsonl(filepath: Path) -> List[Dict[str, Any]]:
    """Read all lines from a JSONL file."""
    results = []
    with open(filepath, 'r') as f:
        for line in f:
            if line.strip():
                results.append(json.loads(line))
    return results


def write_text(content: str, filepath: Path) -> None:
    """Write text content to a file."""
    with open(filepath, 'w') as f:
        f.write(content)
