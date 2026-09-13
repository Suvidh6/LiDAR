"""
src/dataset/carla_adapter.py
Dataset adapter for CARLA 0.9.16 recorded sequences.
Reads synchronized Camera, LiDAR, IMU, and authoritative Ground Truth.
"""

import os
import json
import glob
import numpy as np
import pandas as pd
from .base import (
    DatasetAdapter,
    Calibration,
    GroundTruthObject,
    GroundTruthFrame,
    SensorFrame
)
from ..sensors.imu import IMUMotionProcessor

class CARLADatasetAdapter(DatasetAdapter):
    """
    Adapter for CARLA dynamic multi-sensor sequences.
    Exposes unified SensorFrame and GroundTruthFrame representations.
    """
    def __init__(self, data_root=None, config=None):
        if data_root is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            data_root = os.path.join(base_dir, "data", "dynamic_dataset")
        self.data_root = data_root
        self.config = config or {}

        # Calibration
        cam_cfg = self.config.get("sensors", {}).get("camera", {})
        self.calibration = Calibration(
            image_width=cam_cfg.get("image_width", 800),
            image_height=cam_cfg.get("image_height", 600),
            fov=cam_cfg.get("fov", 90.0)
        )

        self.imu_proc = IMUMotionProcessor(data_root=self.data_root)
        self.frames = []
        self._load_dataset()

    def _load_dataset(self):
        """Indexes sensor telemetry and ground truth frames."""
        motion_frames = self.imu_proc.process_sequence()
        gt_dir = os.path.join(self.data_root, "ground_truth")
        master_gt_path = os.path.join(self.data_root, "ground_truth.json")

        master_gt = {}
        if os.path.exists(master_gt_path):
            with open(master_gt_path, "r") as f:
                master_gt = json.load(f)

        for mf in motion_frames:
            fid = mf["frame_id"]
            ts = mf["timestamp"]

            # Load ground truth if available
            gt_objects = []
            gt_frame_path = os.path.join(gt_dir, f"frame_{fid:06d}.json")
            gt_data = None
            if str(fid) in master_gt:
                gt_data = master_gt[str(fid)]
            elif os.path.exists(gt_frame_path):
                with open(gt_frame_path, "r") as f:
                    gt_data = json.load(f)

            if gt_data is not None:
                for obj in gt_data.get("objects", []):
                    gt_objects.append(GroundTruthObject(
                        object_id=obj["id"],
                        class_name=obj.get("class_name", obj.get("type", "vehicle")),
                        position_world=obj.get("pos_world", obj.get("position_world", [0, 0, 0])),
                        position_ego=obj.get("pos_ego", obj.get("position_ego", [0, 0, 0])),
                        position_lidar=obj.get("pos_lidar", obj.get("position_lidar", [0, 0, 0])),
                        dimensions=obj.get("dimensions", [4.5, 1.8, 1.5]),
                        bbox_2d=obj.get("bbox_2d", None),
                        bbox_3d=obj.get("bbox_3d", None),
                        velocity=obj.get("velocity", [0, 0, 0]),
                        orientation=obj.get("orientation", [0, 0, 0]),
                        is_visible=obj.get("is_visible", True)
                    ))

            gt_frame = GroundTruthFrame(
                frame_id=fid,
                timestamp=ts,
                ego_pose=mf.get("T_ego"),
                objects=gt_objects
            )

            sensor_frame = SensorFrame(
                frame_id=fid,
                timestamp=ts,
                camera_path=mf.get("camera_path"),
                lidar_path=mf.get("lidar_path"),
                imu_data=mf,
                T_ego=mf.get("T_ego"),
                dt=mf.get("dt", 0.05),
                calibration=self.calibration,
                ground_truth=gt_frame,
                metadata={"source": "carla_0.9.16"}
            )
            self.frames.append(sensor_frame)

    def __len__(self) -> int:
        return len(self.frames)

    def __getitem__(self, index: int) -> SensorFrame:
        return self.frames[index]

    def get_calibration(self) -> Calibration:
        return self.calibration

    def get_sequence(self) -> list:
        return self.frames
