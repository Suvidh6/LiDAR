"""
run_full_experiment.py
Top-level entry point to execute the complete unified multimodal sensor fusion research experiment.
"""

import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from experiments.run_full_experiment import run_all_experiments
from src.evaluation.degradation import (
    apply_camera_motion_blur,
    apply_camera_illumination_degrade,
    apply_camera_fog_glare,
    apply_camera_outage,
    apply_lidar_dropout,
    apply_lidar_noise,
    apply_lidar_outage,
)

if __name__ == "__main__":
    run_all_experiments()
