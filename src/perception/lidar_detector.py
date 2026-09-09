"""
src/perception/lidar_detector.py
Modular 3D LiDAR Object Detector using RANSAC Ground Removal and DBSCAN Clustering.

Provides:
- LiDARCluster structured class (centroid, bounding box, dimensions, point count, geometric priors).
- LiDARDetector class.
"""

import os
import numpy as np
import open3d as o3d

class LiDARCluster:
    """Represents a clustered 3D object from LiDAR returns."""
    def __init__(self, cluster_id, points):
        self.cluster_id = int(cluster_id)
        self.points = np.asarray(points, dtype=np.float64)
        self.num_points = int(len(self.points))
        self.centroid = np.mean(self.points, axis=0)  # [x, y, z] in LiDAR frame

        self.min_bound = np.min(self.points, axis=0)
        self.max_bound = np.max(self.points, axis=0)
        self.dimensions = self.max_bound - self.min_bound  # [dx, dy, dz]
        self.volume = max(0.01, float(self.dimensions[0] * self.dimensions[1] * self.dimensions[2]))

        # Radial distance in horizontal ground plane
        self.radial_distance = float(np.linalg.norm(self.centroid[:2]))

        # Geometric fitness to standard vehicular priors
        vol_score = float(np.exp(-0.5 * ((np.log(max(self.volume, 0.1)) - np.log(8.0)) / 1.5)**2))
        aspect_ratio = self.dimensions[0] / max(self.dimensions[1], 0.2)
        aspect_score = 1.0 if (0.5 <= aspect_ratio <= 3.5) else 0.5
        self.geometric_score = float(np.clip(vol_score * aspect_score, 0.1, 1.0))

    def get_bounding_corners(self):
        """Returns the 8 corners of the 3D axis-aligned bounding box."""
        min_b = self.min_bound
        max_b = self.max_bound
        return np.array([
            [min_b[0], min_b[1], min_b[2]],
            [max_b[0], min_b[1], min_b[2]],
            [max_b[0], max_b[1], min_b[2]],
            [min_b[0], max_b[1], min_b[2]],
            [min_b[0], min_b[1], max_b[2]],
            [max_b[0], min_b[1], max_b[2]],
            [max_b[0], max_b[1], max_b[2]],
            [min_b[0], max_b[1], max_b[2]],
        ], dtype=np.float64)

    def to_dict(self):
        return {
            "cluster_id": self.cluster_id,
            "num_points": self.num_points,
            "centroid": [round(float(c), 3) for c in self.centroid],
            "dimensions": [round(float(d), 3) for d in self.dimensions],
            "volume": round(self.volume, 3),
            "radial_distance": round(self.radial_distance, 3),
            "geometric_score": round(self.geometric_score, 3)
        }

class LiDARDetector:
    """
    RANSAC plane segmentation ground removal + DBSCAN Euclidean clustering detector.
    """
    def __init__(self, ground_thresh=0.15, eps=0.8, min_cluster_points=8):
        self.ground_thresh = ground_thresh
        self.eps = eps
        self.min_cluster_points = min_cluster_points

    def detect(self, pcd_input):
        """
        Processes a point cloud path, open3d.geometry.PointCloud, or (N, 3) numpy array.
        Returns (list of LiDARCluster, total_points_count).
        """
        if isinstance(pcd_input, str):
            if not os.path.exists(pcd_input):
                raise FileNotFoundError(f"PLY point cloud not found: {pcd_input}")
            pcd = o3d.io.read_point_cloud(pcd_input)
        elif isinstance(pcd_input, np.ndarray):
            pcd = o3d.geometry.PointCloud()
            pcd.points = o3d.utility.Vector3dVector(pcd_input)
        else:
            pcd = pcd_input

        points = np.asarray(pcd.points)
        total_pts = len(points)
        if total_pts < self.min_cluster_points:
            return [], total_pts

        # 1. RANSAC Ground plane removal
        try:
            _, inliers = pcd.segment_plane(
                distance_threshold=self.ground_thresh,
                ransac_n=3,
                num_iterations=400
            )
            non_ground = pcd.select_by_index(inliers, invert=True)
        except Exception:
            non_ground = pcd

        non_ground_pts = np.asarray(non_ground.points)
        if len(non_ground_pts) < self.min_cluster_points:
            return [], total_pts

        # 2. DBSCAN Clustering
        labels = np.array(
            non_ground.cluster_dbscan(
                eps=self.eps,
                min_points=self.min_cluster_points,
                print_progress=False
            )
        )

        num_clusters = labels.max() + 1 if len(labels) > 0 else 0
        clusters = []

        for cid in range(num_clusters):
            cluster_indices = np.where(labels == cid)[0]
            if len(cluster_indices) < self.min_cluster_points:
                continue
            cluster_pts = non_ground_pts[cluster_indices]
            clusters.append(LiDARCluster(cid, cluster_pts))

        clusters.sort(key=lambda c: c.radial_distance)
        return clusters, total_pts
