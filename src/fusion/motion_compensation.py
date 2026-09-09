"""
src/fusion/motion_compensation.py
Performs motion-aware alignment, point cloud compensation, and Camera-LiDAR fusion
using IMU ego-motion estimates.

Features:
- Warps LiDAR point clouds between consecutive frames using IMU SE(3) transformation.
- Evaluates quantitative point cloud alignment error (Nearest Neighbor Chamfer MSE).
- Implements Camera-LiDAR projection geometry with CARLA coordinates and camera intrinsics.
- Projects motion-compensated LiDAR point clouds onto RGB camera frames.
- Renders depth-coded fusion overlays.
"""

import os
import math
import numpy as np
import open3d as o3d
import cv2
from scipy.spatial import cKDTree

class MotionCompensator:
    """
    Applies IMU-derived ego-motion transformations to align multi-frame LiDAR
    and project motion-aware 3D point clouds onto 2D camera images.
    """
    def __init__(self, image_width=800, image_height=600, fov=90.0):
        self.width = int(image_width)
        self.height = int(image_height)
        self.fov = float(fov)

        f = self.width / (2.0 * math.tan(math.radians(self.fov) / 2.0))
        self.K = np.array([
            [f,   0.0, self.width / 2.0],
            [0.0, f,   self.height / 2.0],
            [0.0, 0.0, 1.0]
        ], dtype=np.float64)

        # Extrinsic Translation from LiDAR to Camera in vehicle/CARLA frame
        # Camera: (1.5, 0.0, 2.4), LiDAR: (0.0, 0.0, 2.5) -> [1.5, 0.0, -0.1]
        self.trans_lidar_to_cam = np.array([1.5, 0.0, -0.1], dtype=np.float64)

    @staticmethod
    def load_point_cloud(ply_path):
        """Loads PLY point cloud and returns numpy array of shape (N, 3)."""
        if not os.path.exists(ply_path):
            raise FileNotFoundError(f"PLY file not found: {ply_path}")
        pcd = o3d.io.read_point_cloud(ply_path)
        return np.asarray(pcd.points, dtype=np.float64)

    @staticmethod
    def apply_rigid_transform(points, T_4x4):
        """
        Transforms 3D points by a 4x4 SE(3) transformation matrix:
        P_transformed = (R @ P.T).T + t
        """
        if len(points) == 0:
            return points
        R = T_4x4[:3, :3]
        t = T_4x4[:3, 3]
        return (R @ points.T).T + t

    def compensate_lidar_frame(self, pts_prev, T_ego):
        """
        Warps LiDAR points from previous frame (t-1) into current frame (t)
        coordinate system using IMU ego-motion transformation T_ego.
        P_t = inv(T_ego) * P_{t-1}
        """
        if len(pts_prev) == 0 or T_ego is None:
            return pts_prev

        T_inv = np.linalg.inv(T_ego)
        return self.apply_rigid_transform(pts_prev, T_inv)

    @staticmethod
    def compute_alignment_error(pts_source, pts_target, max_correspondence_dist=1.5):
        """
        Computes Mean Squared Error (MSE) and Mean Absolute Error (MAE)
        of nearest-neighbor correspondences between two point clouds.
        """
        if len(pts_source) == 0 or len(pts_target) == 0:
            return float("nan"), float("nan")

        tree = cKDTree(pts_target)
        distances, _ = tree.query(pts_source, k=1)

        valid_mask = distances <= max_correspondence_dist
        if np.sum(valid_mask) == 0:
            return float("nan"), float("nan")

        valid_distances = distances[valid_mask]
        mae = float(np.mean(valid_distances))
        mse = float(np.mean(valid_distances**2))
        return mae, mse

    def project_lidar_to_camera(self, lidar_points):
        """
        Projects 3D LiDAR points in CARLA sensor frame onto 2D camera image plane.
        """
        if len(lidar_points) == 0:
            return np.empty((0, 2)), np.empty((0,))

        # 1. Translate from LiDAR to Camera coordinate origin
        pts_cam_carla = lidar_points - self.trans_lidar_to_cam

        # 2. Coordinate transformation to optical camera axes
        pts_optical = np.zeros_like(pts_cam_carla)
        pts_optical[:, 0] = pts_cam_carla[:, 1]   # X_opt = Y_carla (right)
        pts_optical[:, 1] = -pts_cam_carla[:, 2]  # Y_opt = -Z_carla (down)
        pts_optical[:, 2] = pts_cam_carla[:, 0]   # Z_opt = X_carla (forward depth)

        depth = pts_optical[:, 2]
        in_front = depth > 0.5
        pts_valid = pts_optical[in_front]
        valid_depth = depth[in_front]

        if len(pts_valid) == 0:
            return np.empty((0, 2)), np.empty((0,))

        # 3. Perspective projection
        pts_2d_homo = (self.K @ pts_valid.T).T
        u = pts_2d_homo[:, 0] / pts_2d_homo[:, 2]
        v = pts_2d_homo[:, 1] / pts_2d_homo[:, 2]

        in_image = (u >= 0) & (u < self.width) & (v >= 0) & (v < self.height)

        uvs = np.column_stack([u[in_image], v[in_image]])
        depths = valid_depth[in_image]

        return uvs, depths

    def render_fusion_overlay(self, image_bgr, uvs, depths, alpha=0.7):
        """
        Overlays projected LiDAR points onto an RGB image with depth colormap.
        """
        overlay = image_bgr.copy()
        if len(uvs) == 0:
            return overlay

        norm_depth = np.clip((depths - 2.0) / (35.0 - 2.0), 0.0, 1.0)
        colors = cv2.applyColorMap((norm_depth * 255).astype(np.uint8), cv2.COLORMAP_JET)

        for i, (pt, col) in enumerate(zip(uvs, colors)):
            x, y = int(pt[0]), int(pt[1])
            color = (int(col[0, 0]), int(col[0, 1]), int(col[0, 2]))
            cv2.circle(overlay, (x, y), 2, color, -1)

        blended = cv2.addWeighted(overlay, alpha, image_bgr, 1 - alpha, 0)
        return blended
