"""
src/evaluation module
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
from .scenarios import DynamicScenarioEngine
from .metrics import (
    compute_aggregate_metrics,
    evaluate_single_frame,
    evaluate_detection_performance,
    compute_trajectory_jitter
)
from .benchmarking import FusionBenchmarkHarness
from .visualization import plot_all_research_figures
