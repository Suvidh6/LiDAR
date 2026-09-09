"""
src/evaluation/scenarios.py
Continuous dynamic degradation scenario engine.

Controls frame-by-frame time-varying environmental events:
- Baseline nominal operation
- Progressive camera motion blur ramp
- Camera recovery
- Progressive LiDAR beam attenuation (dropout) ramp
- LiDAR recovery
- Camera darkness / tunnel plunge
- High-motion ego-vehicle agitation
- Dual combined degradation & final recovery
"""

import math
import numpy as np
from .degradation import (
    apply_camera_motion_blur,
    apply_camera_illumination_degrade,
    apply_camera_outage,
    apply_lidar_dropout,
    apply_lidar_noise,
    apply_lidar_outage
)
from ..utils.configuration import load_degradation_config

class DynamicScenarioEngine:
    """
    Manages continuous, time-varying multi-sensor degradation schedules.
    """
    def __init__(self, config=None):
        if config is None:
            try:
                config = load_degradation_config()
            except Exception:
                config = {}
        self.schedule = config.get("schedule", [])
        if not self.schedule:
            # Fallback default schedule across 70 frames
            self.schedule = [
                {"segment_id": "nominal_baseline", "frame_range": [0, 14], "description": "Nominal baseline"},
                {"segment_id": "camera_blur_ramp", "frame_range": [15, 24], "description": "Camera blur ramp", "progressive": True,
                 "camera": {"blur_kernel_start": 3, "blur_kernel_end": 21, "illumination_start": 1.0, "illumination_end": 0.4}},
                {"segment_id": "camera_recovery", "frame_range": [25, 34], "description": "Camera recovery", "progressive": True,
                 "camera": {"blur_kernel_start": 19, "blur_kernel_end": 0, "illumination_start": 0.45, "illumination_end": 1.0}},
                {"segment_id": "lidar_dropout_ramp", "frame_range": [35, 44], "description": "LiDAR dropout ramp", "progressive": True,
                 "lidar": {"dropout_ratio_start": 0.10, "dropout_ratio_end": 0.85, "noise_std_start": 0.05, "noise_std_end": 0.4, "spray_count_start": 20, "spray_count_end": 250}},
                {"segment_id": "lidar_recovery", "frame_range": [45, 54], "description": "LiDAR recovery", "progressive": True,
                 "lidar": {"dropout_ratio_start": 0.80, "dropout_ratio_end": 0.0, "noise_std_start": 0.35, "noise_std_end": 0.0, "spray_count_start": 200, "spray_count_end": 0}},
                {"segment_id": "camera_darkness_tunnel", "frame_range": [55, 59], "description": "Severe camera darkness",
                 "camera": {"blur_kernel": 5, "illumination_factor": 0.10}},
                {"segment_id": "high_motion_maneuver", "frame_range": [60, 64], "description": "High motion agitation",
                 "camera": {"blur_kernel": 7, "illumination_factor": 0.85}, "lidar": {"dropout_ratio": 0.15, "noise_std": 0.10, "spray_count": 30}},
                {"segment_id": "dual_degradation_recovery", "frame_range": [65, 69], "description": "Dual degradation & recovery", "progressive": True,
                 "camera": {"blur_kernel_start": 17, "blur_kernel_end": 0, "illumination_start": 0.20, "illumination_end": 0.90},
                 "lidar": {"dropout_ratio_start": 0.70, "dropout_ratio_end": 0.0, "noise_std_start": 0.30, "noise_std_end": 0.0, "spray_count_start": 150, "spray_count_end": 0}}
            ]

    def get_parameters(self, frame_idx: int) -> dict:
        """Returns the interpolated degradation parameters for a specific frame index."""
        active_segment = None
        for seg in self.schedule:
            r = seg["frame_range"]
            if r[0] <= frame_idx <= r[1]:
                active_segment = seg
                break

        if active_segment is None:
            active_segment = self.schedule[-1]

        r_start, r_end = active_segment["frame_range"]
        span = max(1, r_end - r_start)
        alpha = float(np.clip((frame_idx - r_start) / span, 0.0, 1.0))

        cam_cfg = active_segment.get("camera", {})
        lid_cfg = active_segment.get("lidar", {})
        is_prog = active_segment.get("progressive", False)

        # 1. Camera parameters
        if is_prog and "blur_kernel_start" in cam_cfg:
            k_start = cam_cfg["blur_kernel_start"]
            k_end = cam_cfg["blur_kernel_end"]
            k = int(round(k_start + alpha * (k_end - k_start)))
            blur_kernel = k if k % 2 != 0 else max(1, k + 1)
        else:
            blur_kernel = cam_cfg.get("blur_kernel", 0)

        if is_prog and "illumination_start" in cam_cfg:
            i_start = cam_cfg["illumination_start"]
            i_end = cam_cfg["illumination_end"]
            illumination_factor = float(i_start + alpha * (i_end - i_start))
        else:
            illumination_factor = float(cam_cfg.get("illumination_factor", 1.0))

        camera_outage = bool(cam_cfg.get("outage", False))

        # 2. LiDAR parameters
        if is_prog and "dropout_ratio_start" in lid_cfg:
            d_start = lid_cfg["dropout_ratio_start"]
            d_end = lid_cfg["dropout_ratio_end"]
            dropout_ratio = float(d_start + alpha * (d_end - d_start))
        else:
            dropout_ratio = float(lid_cfg.get("dropout_ratio", 0.0))

        if is_prog and "noise_std_start" in lid_cfg:
            n_start = lid_cfg["noise_std_start"]
            n_end = lid_cfg["noise_std_end"]
            noise_std = float(n_start + alpha * (n_end - n_start))
        else:
            noise_std = float(lid_cfg.get("noise_std", 0.0))

        if is_prog and "spray_count_start" in lid_cfg:
            s_start = lid_cfg["spray_count_start"]
            s_end = lid_cfg["spray_count_end"]
            spray_count = int(round(s_start + alpha * (s_end - s_start)))
        else:
            spray_count = int(lid_cfg.get("spray_count", 0))

        lidar_outage = bool(lid_cfg.get("outage", False))

        return {
            "frame_idx": frame_idx,
            "segment_id": active_segment["segment_id"],
            "description": active_segment["description"],
            "blur_kernel": max(0, blur_kernel),
            "illumination_factor": float(np.clip(illumination_factor, 0.02, 1.0)),
            "camera_outage": camera_outage,
            "dropout_ratio": float(np.clip(dropout_ratio, 0.0, 0.95)),
            "noise_std": max(0.0, noise_std),
            "spray_count": max(0, spray_count),
            "lidar_outage": lidar_outage
        }

    def apply_degradation(self, image_bgr, points_xyz, frame_idx: int, seed: int = 42):
        """
        Applies progressive continuous degradation to raw camera and LiDAR frames.
        Returns:
        - degraded_img: processed OpenCV BGR array (or None if outage)
        - degraded_pts: processed (N, 3) point cloud array
        - params: parameter dict
        """
        params = self.get_parameters(frame_idx)

        # Process Camera
        if params["camera_outage"]:
            deg_img = apply_camera_outage(image_bgr)
        else:
            deg_img = image_bgr.copy() if image_bgr is not None else None
            if deg_img is not None:
                if params["blur_kernel"] > 1:
                    deg_img = apply_camera_motion_blur(
                        deg_img, kernel_size=params["blur_kernel"], angle_deg=25.0
                    )
                if params["illumination_factor"] < 0.99:
                    deg_img = apply_camera_illumination_degrade(
                        deg_img, factor=params["illumination_factor"]
                    )

        # Process LiDAR
        if params["lidar_outage"]:
            deg_pts = apply_lidar_outage(points_xyz)
        else:
            deg_pts = points_xyz.copy() if points_xyz is not None else np.empty((0, 3))
            if len(deg_pts) > 0:
                if params["dropout_ratio"] > 0.02:
                    deg_pts = apply_lidar_dropout(
                        deg_pts, drop_ratio=params["dropout_ratio"], random_seed=seed + frame_idx
                    )
                if params["noise_std"] > 0.01 or params["spray_count"] > 0:
                    deg_pts = apply_lidar_noise(
                        deg_pts, noise_std=params["noise_std"],
                        num_spray=params["spray_count"], random_seed=seed + frame_idx
                    )

        return deg_img, deg_pts, params
