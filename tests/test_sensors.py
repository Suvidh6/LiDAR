"""
tests/test_sensors.py
Unit tests for sensor modeling, kinematics, and calibrations.
"""

import os
import sys
import math
import numpy as np

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.sensors.imu import IMUMotionProcessor
from src.sensors.camera import CameraModel
from src.sensors.lidar import PointCloudIO

def test_imu_kinematics():
    processor = IMUMotionProcessor()

    # Test gravity compensation on flat surface at rest
    raw_accel = np.array([0.0, 0.0, 9.81])
    lin_accel = raw_accel - np.array([0.0, 0.0, processor.GRAVITY_MAGNITUDE])
    assert np.allclose(lin_accel, [0.0, 0.0, 0.0]), "Gravity compensation failed."

    # Test SO(3) rotation matrix identity for zero angles
    R_zero = processor.compute_rotation_matrix(0.0, 0.0, 0.0)
    assert np.allclose(R_zero, np.eye(3)), "Zero rotation should yield identity matrix."

    # Test 90 degree yaw rotation around Z
    R_yaw90 = processor.compute_rotation_matrix(0.0, 0.0, np.pi / 2.0)
    expected_R = np.array([
        [0.0, -1.0, 0.0],
        [1.0,  0.0, 0.0],
        [0.0,  0.0, 1.0]
    ])
    assert np.allclose(R_yaw90, expected_R, atol=1e-5), "Yaw 90 deg rotation mismatch."

    # Test motion state classification
    assert processor.classify_motion_state(1.2, 0.0, 0.0, speed=5.0) == "ACCELERATING"
    assert processor.classify_motion_state(-1.2, 0.0, 0.0, speed=5.0) == "BRAKING"
    assert processor.classify_motion_state(0.0, 0.0, 0.15, speed=5.0) == "TURNING_RIGHT"
    assert processor.classify_motion_state(0.0, 0.0, -0.15, speed=5.0) == "TURNING_LEFT"
    assert processor.classify_motion_state(0.0, 0.0, 0.0, speed=0.05) == "STATIONARY"
    print("test_imu_kinematics: PASSED")

def test_camera_model():
    cam = CameraModel(image_width=800, image_height=600, fov=90.0)
    assert math.isclose(cam.fx, 400.0, rel_tol=1e-5), f"Expected fx=400.0, got {cam.fx}"
    assert math.isclose(cam.cx, 400.0, rel_tol=1e-5), f"Expected cx=400.0, got {cam.cx}"
    assert math.isclose(cam.cy, 300.0, rel_tol=1e-5), f"Expected cy=300.0, got {cam.cy}"

    # Forward optical point at (X=0, Y=0, Z=10m) should project to image center (400, 300)
    optical_pts = np.array([[0.0, 0.0, 10.0]])
    uvs, depths = cam.project_3d_to_2d(optical_pts)
    assert len(uvs) == 1, "Should project exactly 1 point."
    assert np.allclose(uvs[0], [400.0, 300.0]), f"Expected (400, 300), got {uvs[0]}"
    assert depths[0] == 10.0, f"Expected depth=10.0, got {depths[0]}"
    print("test_camera_model: PASSED")

def test_pointcloud_io():
    sample_pts = np.random.uniform(-10, 10, size=(100, 3))
    filtered = PointCloudIO.filter_roi(sample_pts, x_range=(0, 5), y_range=(-5, 5), z_range=(-2, 2))
    assert np.all(filtered[:, 0] >= 0) and np.all(filtered[:, 0] <= 5), "ROI filtering failed on X."
    print("test_pointcloud_io: PASSED")

if __name__ == "__main__":
    test_imu_kinematics()
    test_camera_model()
    test_pointcloud_io()
    print("All sensor tests passed successfully!")
