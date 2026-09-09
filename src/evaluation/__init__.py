"""
Evaluation, sensor degradation injection, and benchmarking harness.
"""

from .degradation import (
    apply_camera_motion_blur,
    apply_camera_illumination_degrade,
    apply_camera_fog_glare,
    apply_camera_outage,
    apply_lidar_dropout,
    apply_lidar_noise,
    apply_lidar_outage
)
from .metrics import evaluate_detection_performance, compute_trajectory_jitter

__all__ = [
    "apply_camera_motion_blur",
    "apply_camera_illumination_degrade",
    "apply_camera_fog_glare",
    "apply_camera_outage",
    "apply_lidar_dropout",
    "apply_lidar_noise",
    "apply_lidar_outage",
    "evaluate_detection_performance",
    "compute_trajectory_jitter"
]
