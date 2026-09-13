"""
src/dataset/nuscenes_adapter.py
Adapter for future integration of the nuScenes autonomous driving dataset.
Implements the DatasetAdapter interface without modifying perception or fusion modules.
"""

import os
import numpy as np
from .base import (
    DatasetAdapter,
    Calibration,
    GroundTruthObject,
    GroundTruthFrame,
    SensorFrame
)

class NuScenesDatasetAdapter(DatasetAdapter):
    """
    Adapter for nuScenes 3D perception sequences.
    Standardizes 32-beam LiDAR, multi-camera, and IMU ego-motion into unified SensorFrames.
    """
    def __init__(self, data_root=None, version="v1.0-mini", config=None):
        self.data_root = data_root or "data/nuscenes"
        self.version = version
        self.config = config or {}
        self.calibration = Calibration(
            image_width=1600,
            image_height=900,
            fov=70.0
        )
        self.frames = []

    def __len__(self) -> int:
        return len(self.frames)

    def __getitem__(self, index: int) -> SensorFrame:
        if not self.frames:
            raise IndexError("NuScenesDatasetAdapter has no frames loaded. Download nuScenes dataset first.")
        return self.frames[index]

    def get_calibration(self) -> Calibration:
        return self.calibration

    def get_sequence(self) -> list:
        return self.frames
