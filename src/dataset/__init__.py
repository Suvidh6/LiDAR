"""
src/dataset/__init__.py
Dataset-agnostic perception abstraction layer for multimodal sensor fusion.
Supports CARLA, KITTI, nuScenes, and custom datasets through unified adapters.
"""

from .base import (
    Calibration,
    GroundTruthObject,
    GroundTruthFrame,
    SensorFrame,
    ClassMapper,
    DatasetAdapter
)
from .carla_adapter import CARLADatasetAdapter
from .kitti_adapter import KITTIDatasetAdapter
from .nuscenes_adapter import NuScenesDatasetAdapter
from .factory import create_dataset_adapter

__all__ = [
    "Calibration",
    "GroundTruthObject",
    "GroundTruthFrame",
    "SensorFrame",
    "ClassMapper",
    "DatasetAdapter",
    "CARLADatasetAdapter",
    "KITTIDatasetAdapter",
    "NuScenesDatasetAdapter",
    "create_dataset_adapter"
]
