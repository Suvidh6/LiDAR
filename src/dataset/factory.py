"""
src/dataset/factory.py
Factory function for configuration-driven dataset instantiation.
"""

from .carla_adapter import CARLADatasetAdapter
from .kitti_adapter import KITTIDatasetAdapter
from .nuscenes_adapter import NuScenesDatasetAdapter

def create_dataset_adapter(config: dict = None, data_root: str = None):
    """
    Creates and returns a concrete DatasetAdapter based on configuration.
    
    Example configuration:
        {
            "dataset": {
                "name": "carla",
                "root": "data/dynamic_dataset"
            }
        }
    """
    cfg = config or {}
    dataset_cfg = cfg.get("dataset", {})
    name = dataset_cfg.get("name", "carla").lower()
    root = data_root or dataset_cfg.get("root", None)

    if name == "carla":
        return CARLADatasetAdapter(data_root=root, config=cfg)
    elif name == "kitti":
        return KITTIDatasetAdapter(data_root=root, config=cfg)
    elif name in ("nuscenes", "nu_scenes"):
        return NuScenesDatasetAdapter(data_root=root, config=cfg)
    else:
        raise ValueError(f"Unknown dataset adapter name: '{name}'. Supported: 'carla', 'kitti', 'nuscenes'.")
