"""
tests/test_utils.py
Unit tests for configuration loading, path resolution, and reproducibility.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.utils.paths import get_project_root, get_config_dir, get_metrics_dir, get_plots_dir
from src.utils.configuration import load_default_config, load_degradation_config, load_experiment_config
from src.utils.reproducibility import get_system_metadata, set_seed

def test_paths_and_configs():
    assert get_project_root().exists(), "Project root does not exist."
    assert get_config_dir().exists(), "Config dir does not exist."
    assert get_metrics_dir().exists(), "Metrics dir does not exist."
    assert get_plots_dir().exists(), "Plots dir does not exist."

    def_cfg = load_default_config()
    assert "sensors" in def_cfg
    assert "camera" in def_cfg["sensors"]
    assert "lidar" in def_cfg["sensors"]
    assert "imu" in def_cfg["sensors"]

    deg_cfg = load_degradation_config()
    assert "schedule" in deg_cfg
    assert len(deg_cfg["schedule"]) > 0

    exp_cfg = load_experiment_config()
    assert "project_name" in exp_cfg
    print("test_paths_and_configs: PASSED")

def test_reproducibility():
    set_seed(123)
    meta = get_system_metadata()
    assert "python_version" in meta
    assert "platform" in meta
    assert "carla_target_version" in meta
    print("test_reproducibility: PASSED")

if __name__ == "__main__":
    test_paths_and_configs()
    test_reproducibility()
    print("All utility tests passed successfully!")
