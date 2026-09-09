"""
Multimodal Sensor Fusion package:
- Spatial Camera-LiDAR 2D/3D association
- IMU-based SE(3) motion compensation
- Temporal multi-frame tracking
- Physical sensor reliability estimation
- Adaptive and baseline fusion engines
"""

from .spatial_association import associate_camera_and_lidar, project_cluster_to_camera, compute_2d_iou
from .motion_compensation import MotionCompensator
from .temporal_tracker import TemporalTracker, TemporalTrack
from .reliability_estimation import ReliabilityEstimator
from .adaptive_fusion import AdaptiveFusionEngine, FusedDetection

__all__ = [
    "associate_camera_and_lidar",
    "project_cluster_to_camera",
    "compute_2d_iou",
    "MotionCompensator",
    "TemporalTracker",
    "TemporalTrack",
    "ReliabilityEstimator",
    "AdaptiveFusionEngine",
    "FusedDetection"
]
