"""
run_tests.py
Validation test runner executing all unit tests in tests/.
"""

import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from tests.test_sensors import test_imu_kinematics, test_camera_model, test_pointcloud_io
from tests.test_perception import test_camera_detector_quality, test_lidar_clustering
from tests.test_fusion import (
    test_spatial_association_iou,
    test_motion_compensator,
    test_temporal_tracker,
    test_sensor_health_and_trend,
    test_reliability_and_adaptive_fusion
)
from tests.test_utils import test_paths_and_configs, test_reproducibility
from tests.test_carla_connection import test_carla_connection

def run_suite():
    print("=" * 65)
    print("      RUNNING UNIFIED SENSOR FUSION TEST SUITE")
    print("=" * 65)

    print("\n--- 1. Sensor & Kinematic Tests ---")
    test_imu_kinematics()
    test_camera_model()
    test_pointcloud_io()

    print("\n--- 2. Perception & Detector Tests ---")
    test_camera_detector_quality()
    test_lidar_clustering()

    print("\n--- 3. Multimodal Fusion Tests ---")
    test_spatial_association_iou()
    test_motion_compensator()
    test_temporal_tracker()
    test_sensor_health_and_trend()
    test_reliability_and_adaptive_fusion()

    print("\n--- 4. Configuration, Path & Utility Tests ---")
    test_paths_and_configs()
    test_reproducibility()

    print("\n--- 5. Simulator Connection Check ---")
    test_carla_connection()

    print("\n" + "=" * 65)
    print("      ALL UNIT AND INTEGRATION TESTS PASSED!")
    print("=" * 65)

if __name__ == "__main__":
    run_suite()
