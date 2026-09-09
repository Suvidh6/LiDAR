"""
src/sensors/camera.py
Pinhole camera model, intrinsic matrix calibration, and coordinate transformations.
"""

import math
import numpy as np

class CameraModel:
    """
    Models pinhole perspective camera geometry for CARLA RGB sensor.
    Handles intrinsics K, optical frame conversion, and perspective projection.
    """
    def __init__(self, image_width=800, image_height=600, fov=90.0):
        self.width = int(image_width)
        self.height = int(image_height)
        self.fov = float(fov)

        # Focal length: fx = fy = W / (2 * tan(FOV / 2))
        f = self.width / (2.0 * math.tan(math.radians(self.fov) / 2.0))
        self.fx = f
        self.fy = f
        self.cx = self.width / 2.0
        self.cy = self.height / 2.0

        # Intrinsic Matrix K (3x3)
        self.K = np.array([
            [self.fx, 0.0,     self.cx],
            [0.0,     self.fy, self.cy],
            [0.0,     0.0,     1.0]
        ], dtype=np.float64)

    @staticmethod
    def carla_to_optical(pts_carla):
        """
        Converts coordinates from CARLA vehicle frame (X: forward, Y: right, Z: up)
        to OpenCV standard optical frame (X: right, Y: down, Z: forward depth).
        """
        pts = np.asarray(pts_carla, dtype=np.float64)
        if len(pts) == 0:
            return np.empty((0, 3), dtype=np.float64)

        pts_optical = np.zeros_like(pts)
        pts_optical[:, 0] = pts[:, 1]   # X_opt = Y_carla (Right)
        pts_optical[:, 1] = -pts[:, 2]  # Y_opt = -Z_carla (Down)
        pts_optical[:, 2] = pts[:, 0]   # Z_opt = X_carla (Forward)
        return pts_optical

    def project_3d_to_2d(self, pts_optical):
        """
        Applies intrinsic matrix K to 3D optical points and performs perspective division.
        Returns:
        - uvs: (M, 2) array of pixel coordinates within image boundaries
        - depths: (M,) array of forward depths in meters
        - in_image_mask: boolean mask of valid projections
        """
        pts = np.asarray(pts_optical, dtype=np.float64)
        if len(pts) == 0:
            return np.empty((0, 2)), np.empty((0,)), np.array([], dtype=bool)

        depth = pts[:, 2]
        in_front = depth > 0.5
        if not np.any(in_front):
            return np.empty((0, 2)), np.empty((0,)), np.zeros(len(pts), dtype=bool)

        pts_valid = pts[in_front]
        valid_depth = depth[in_front]

        # Perspective projection: [u, v, 1]^T = (1/Z) * K @ [X, Y, Z]^T
        pts_homo = (self.K @ pts_valid.T).T
        u = pts_homo[:, 0] / pts_homo[:, 2]
        v = pts_homo[:, 1] / pts_homo[:, 2]

        in_bounds = (u >= 0) & (u < self.width) & (v >= 0) & (v < self.height)

        uvs = np.column_stack([u[in_bounds], v[in_bounds]])
        depths = valid_depth[in_bounds]

        return uvs, depths
