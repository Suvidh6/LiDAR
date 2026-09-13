"""
tests/test_dataset.py
Unit tests for the dataset-agnostic abstraction layer.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import numpy as np
from src.dataset.base import (
    Calibration,
    ClassMapper,
    GroundTruthObject,
    GroundTruthFrame,
    SensorFrame
)
from src.dataset.factory import create_dataset_adapter
from src.dataset.carla_adapter import CARLADatasetAdapter
from src.dataset.kitti_adapter import KITTIDatasetAdapter
from src.dataset.nuscenes_adapter import NuScenesDatasetAdapter

def test_calibration_projection():
    calib = Calibration(image_width=800, image_height=600, fov=90.0)
    pt_lidar = np.array([[15.0, 0.0, 0.0]])
    uvs, depths = calib.project_lidar_to_camera(pt_lidar)
    assert len(uvs) == 1, "Should project 1 point"
    assert len(depths) == 1, "Should have 1 depth"
    assert abs(uvs[0, 0] - 400.0) < 5.0, f"Expected u ~ 400, got {uvs[0, 0]}"
    assert abs(depths[0] - 13.5) < 0.1, f"Expected depth ~ 13.5, got {depths[0]}"

    p_back = calib.camera_ray_to_3d(uvs[0, 0], uvs[0, 1], depths[0])
    assert np.allclose(p_back, pt_lidar[0], atol=0.01), f"Back-projection mismatch: {p_back} vs {pt_lidar[0]}"
    print("test_calibration_projection: PASSED")

def test_class_mapper():
    assert ClassMapper.map_class("vehicle.audi.tt") == "vehicle"
    assert ClassMapper.map_class("Car") == "vehicle"
    assert ClassMapper.map_class("walker.pedestrian.0001") == "pedestrian"
    assert ClassMapper.map_class("Pedestrian") == "pedestrian"
    assert ClassMapper.map_class("Cyclist") == "cyclist"
    print("test_class_mapper: PASSED")

def test_ground_truth_structures():
    gt_obj = GroundTruthObject(
        object_id=1,
        class_name="vehicle.tesla.model3",
        position_world=[10, 20, 0],
        position_ego=[12, 1.5, 0],
        position_lidar=[12, 1.5, -2.5],
        bbox_2d=[100, 100, 200, 200],
        is_visible=True
    )
    assert gt_obj.class_name == "vehicle"
    assert gt_obj.radial_distance > 10.0

    gt_frame = GroundTruthFrame(frame_id=1, timestamp=0.05, objects=[gt_obj])
    pos_3d = gt_frame.get_positions_3d(max_distance=45.0)
    assert len(pos_3d) == 1
    boxes_2d = gt_frame.get_boxes_2d()
    assert len(boxes_2d) == 1
    print("test_ground_truth_structures: PASSED")

def test_adapter_factory():
    carla_adapter = create_dataset_adapter({"dataset": {"name": "carla"}})
    assert isinstance(carla_adapter, CARLADatasetAdapter)
    assert len(carla_adapter) > 0

    kitti_adapter = create_dataset_adapter({"dataset": {"name": "kitti"}})
    assert isinstance(kitti_adapter, KITTIDatasetAdapter)

    nuscenes_adapter = create_dataset_adapter({"dataset": {"name": "nuscenes"}})
    assert isinstance(nuscenes_adapter, NuScenesDatasetAdapter)
    print("test_adapter_factory: PASSED")

if __name__ == "__main__":
    test_calibration_projection()
    test_class_mapper()
    test_ground_truth_structures()
    test_adapter_factory()
    print("All dataset unit tests passed successfully!")
