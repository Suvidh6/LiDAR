"""
tests/test_fusion.py
Unit tests for spatial association, motion compensation, temporal tracking,
reliability estimation, and adaptive fusion.
"""

import os
import sys
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.fusion.spatial_association import compute_2d_iou
from src.fusion.motion_compensation import MotionCompensator
from src.fusion.temporal_tracker import TemporalTracker, TemporalTrack
from src.fusion.reliability_estimation import ReliabilityEstimator
from src.fusion.adaptive_fusion import AdaptiveFusionEngine
from src.perception.camera_detector import CameraDetection
from src.perception.lidar_detector import LiDARCluster

def test_spatial_association_iou():
    boxA = [100, 100, 200, 200]
    boxB = [100, 100, 200, 200]
    assert compute_2d_iou(boxA, boxB) == 1.0, "Identical boxes should have IoU = 1.0."

    boxC = [300, 300, 400, 400]
    assert compute_2d_iou(boxA, boxC) == 0.0, "Disjoint boxes should have IoU = 0.0."

    boxD = [150, 100, 250, 200]  # Half overlap
    iou_d = compute_2d_iou(boxA, boxD)
    assert 0.30 <= iou_d <= 0.35, f"Expected IoU ~0.33, got {iou_d}"
    print("test_spatial_association_iou: PASSED")

def test_motion_compensator():
    comp = MotionCompensator()
    pts = np.array([[10.0, 0.0, 0.0], [20.0, 5.0, 0.0]])

    # Rigid translation by Delta X = 2.0
    T_ego = np.eye(4)
    T_ego[0, 3] = 2.0  # Vehicle moved forward 2.0 meters

    # Warping into new frame: P_curr = inv(T_ego) * P_prev -> X becomes X - 2.0
    warped = comp.compensate_lidar_frame(pts, T_ego)
    assert np.allclose(warped[0], [8.0, 0.0, 0.0]), f"Expected [8, 0, 0], got {warped[0]}"
    print("test_motion_compensator: PASSED")

def test_temporal_tracker():
    tracker = TemporalTracker(max_age=3, min_hits=2, dist_threshold=2.5, use_imu_compensation=True)

    det_f1 = [{"position": [15.0, 2.0, 0.0], "confidence": 0.85, "class_name": "vehicle"}]
    # Frame 1: track initialized (not yet confirmed)
    tracks_f1 = tracker.step(det_f1, T_ego=np.eye(4), dt=0.05)

    # Frame 2: observation confirmed
    det_f2 = [{"position": [15.1, 2.0, 0.0], "confidence": 0.88, "class_name": "vehicle"}]
    tracks_f2 = tracker.step(det_f2, T_ego=np.eye(4), dt=0.05)
    assert len(tracks_f2) == 1, "Track should be confirmed after 2 consecutive hits."
    assert tracks_f2[0].hits == 2
    assert tracks_f2[0].is_confirmed
    print("test_temporal_tracker: PASSED")

def test_reliability_and_adaptive_fusion():
    engine = AdaptiveFusionEngine(nominal_lidar_points=2500)

    # Camera detection and image quality
    cam_det = CameraDetection([100, 100, 200, 200], confidence=0.85, class_id=2, class_name="car")
    clean_quality = {"sharpness_score": 0.90, "illum_score": 0.90}
    r_cam_clean = engine.estimate_camera_reliability(cam_det, clean_quality, distance=10.0)

    # Degraded image quality (severe blur + darkness)
    degraded_quality = {"sharpness_score": 0.05, "illum_score": 0.10}
    r_cam_deg = engine.estimate_camera_reliability(cam_det, degraded_quality, distance=10.0)

    assert r_cam_clean > r_cam_deg * 5.0, f"Clean reliability ({r_cam_clean}) should far exceed degraded ({r_cam_deg})."

    # Synthetic cluster
    pts = np.random.uniform(0, 1, size=(50, 3))
    cluster = LiDARCluster(0, pts)
    r_lid_clean = engine.estimate_lidar_reliability(cluster, total_cloud_points=2800, distance=10.0)
    r_lid_deg = engine.estimate_lidar_reliability(cluster, total_cloud_points=350, distance=10.0)

    assert r_lid_clean > r_lid_deg * 4.0, f"Clean LiDAR ({r_lid_clean}) should exceed degraded ({r_lid_deg})."

    # Verify dynamic weight shift
    w_cam_clean = r_cam_clean / (r_cam_clean + r_lid_clean)
    w_cam_deg = r_cam_deg / (r_cam_deg + r_lid_clean)
    assert w_cam_clean > w_cam_deg, "Camera weight should drop when camera is degraded."
    print("test_reliability_and_adaptive_fusion: PASSED")

if __name__ == "__main__":
    test_spatial_association_iou()
    test_motion_compensator()
    test_temporal_tracker()
    test_reliability_and_adaptive_fusion()
    print("All fusion tests passed successfully!")
