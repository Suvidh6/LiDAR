"""
tests/test_perception.py
Unit tests for Camera and LiDAR perception detectors.
"""

import os
import sys
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.perception.camera_detector import CameraDetector
from src.perception.lidar_detector import LiDARDetector

def test_camera_detector_quality():
    # Test on synthetic sharp and blurred image
    sharp_img = np.zeros((300, 400, 3), dtype=np.uint8)
    # Add checkerboard texture for high Laplacian variance
    sharp_img[::20, ::20] = 255
    q_sharp = CameraDetector.evaluate_image_quality(sharp_img)
    assert q_sharp["sharpness_score"] > 0.05, "Sharpness score should be positive."

    dark_img = np.zeros((300, 400, 3), dtype=np.uint8)
    q_dark = CameraDetector.evaluate_image_quality(dark_img)
    assert q_dark["mean_brightness"] == 0.0, "Dark image should have zero mean brightness."
    assert q_dark["illum_score"] < 0.20, "Dark image should receive low illumination score."
    print("test_camera_detector_quality: PASSED")

def test_lidar_clustering():
    detector = LiDARDetector(ground_thresh=0.15, eps=0.8, min_cluster_points=8)

    # Generate synthetic ground plane + 1 distinct 3D obstacle cluster
    ground = np.random.uniform(-10, 10, size=(500, 3))
    ground[:, 2] = -2.0  # Flat ground plane at Z = -2.0

    obstacle = np.random.uniform(0, 1.5, size=(40, 3))
    obstacle[:, 0] += 10.0  # Center at X=10, Y=2, Z=0
    obstacle[:, 1] += 2.0
    obstacle[:, 2] += 0.0

    cloud = np.vstack([ground, obstacle])
    clusters, total_pts = detector.detect(cloud)

    assert total_pts == 540, f"Expected 540 points, got {total_pts}"
    assert len(clusters) >= 1, "Failed to detect synthetic obstacle cluster."
    c = clusters[0]
    assert 9.0 <= c.centroid[0] <= 12.0, f"Cluster X centroid out of expected bounds: {c.centroid[0]}"
    print("test_lidar_clustering: PASSED")

if __name__ == "__main__":
    test_camera_detector_quality()
    test_lidar_clustering()
    print("All perception tests passed successfully!")
