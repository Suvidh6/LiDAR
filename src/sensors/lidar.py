"""
src/sensors/lidar.py
LiDAR point cloud I/O and spatial pre-filtering utilities.
"""

import os
import numpy as np
import open3d as o3d

class PointCloudIO:
    """Utility class for loading, saving, and basic filtering of 3D point clouds."""

    @staticmethod
    def load(ply_path):
        """Loads PLY point cloud and returns (N, 3) numpy array."""
        if not os.path.exists(ply_path):
            raise FileNotFoundError(f"PLY file not found: {ply_path}")
        pcd = o3d.io.read_point_cloud(ply_path)
        return np.asarray(pcd.points, dtype=np.float64)

    @staticmethod
    def save(points, output_path):
        """Saves (N, 3) numpy array as PLY file."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(np.asarray(points, dtype=np.float64))
        o3d.io.write_point_cloud(output_path, pcd)

    @staticmethod
    def filter_roi(points, x_range=(0.0, 50.0), y_range=(-25.0, 25.0), z_range=(-2.5, 5.0)):
        """Filters points within region of interest (ROI) bounding box."""
        pts = np.asarray(points, dtype=np.float64)
        if len(pts) == 0:
            return pts
        mask = (
            (pts[:, 0] >= x_range[0]) & (pts[:, 0] <= x_range[1]) &
            (pts[:, 1] >= y_range[0]) & (pts[:, 1] <= y_range[1]) &
            (pts[:, 2] >= z_range[0]) & (pts[:, 2] <= z_range[1])
        )
        return pts[mask]
