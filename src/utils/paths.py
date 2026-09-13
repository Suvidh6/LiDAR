"""
src/utils/paths.py
Centralized path resolution utility for SensorFusionResearch.
Ensures reproducible absolute path resolution across all modules.
"""

import os
from pathlib import Path

# Project root is 2 levels up from src/utils/
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

def get_project_root() -> Path:
    return PROJECT_ROOT

def get_config_dir() -> Path:
    return PROJECT_ROOT / "config"

def get_data_dir() -> Path:
    return PROJECT_ROOT / "data" / "dynamic_dataset"

def get_results_dir() -> Path:
    return PROJECT_ROOT / "results"

def get_benchmark_dir() -> Path:
    p = get_results_dir() / "benchmark"
    p.mkdir(parents=True, exist_ok=True)
    return p

def get_ablation_dir() -> Path:
    p = get_results_dir() / "ablation"
    p.mkdir(parents=True, exist_ok=True)
    return p

def get_literature_comparison_dir() -> Path:
    p = get_results_dir() / "literature_comparison"
    p.mkdir(parents=True, exist_ok=True)
    return p

def get_figures_dir() -> Path:
    p = get_results_dir() / "figures"
    p.mkdir(parents=True, exist_ok=True)
    return p

def get_tables_dir() -> Path:
    p = get_results_dir() / "tables"
    p.mkdir(parents=True, exist_ok=True)
    return p

def get_summaries_dir() -> Path:
    p = get_results_dir() / "summaries"
    p.mkdir(parents=True, exist_ok=True)
    return p

# Backward-compatibility aliases mapping to clean results taxonomy
def get_metrics_dir() -> Path:
    return get_benchmark_dir()

def get_plots_dir() -> Path:
    return get_figures_dir()

def resolve_path(relative_or_abs: str) -> Path:
    p = Path(relative_or_abs)
    if p.is_absolute():
        return p
    return PROJECT_ROOT / p
