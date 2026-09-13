"""
src/dataset/kitti_adapter.py
Adapter for future integration of the KITTI Vision Benchmark Suite dataset.
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

class KITTIDatasetAdapter(DatasetAdapter):
    """
    Adapter for KITTI object detection / raw tracking sequences.
    Translates KITTI camera intrinsics (P2), camera-LiDAR extrinsics (Tr_velo_to_cam),
    and 3D bounding box annotations into unified SensorFrame / GroundTruthFrame objects.
    """
    def __init__(self, data_root=None, sequence_id="0000", config=None):
        self.data_root = data_root or "data/kitti"
        self.sequence_id = sequence_id
        self.config = config or {}
        self.calibration = self._load_calibration()
        self.frames = []

    def _load_calibration(self) -> Calibration:
        """Loads and parses KITTI calib.txt into unified Calibration."""
        # Default placeholder KITTI calibration (P2 and Tr_velo_to_cam)
        K = np.array([
            [721.5377, 0.0, 609.5593],
            [0.0, 721.5377, 172.8540],
            [0.0, 0.0, 1.0]
        ], dtype=np.float64)
        return Calibration(
            image_width=1242,
            image_height=375,
            fov=80.0,
            intrinsic_matrix=K,
            trans_lidar_to_cam=np.array([0.27, -0.08, -0.08])
        )

    def __len__(self) -> int:
        return len(self.frames)

    def __getitem__(self, index: int) -> SensorFrame:
        if not self.frames:
            raise IndexError("KITTIDatasetAdapter has no frames loaded. Download KITTI dataset first.")
        return self.frames[index]

    def get_calibration(self) -> Calibration:
        return self.calibration

    def get_sequence(self) -> list:
        return self.frames
