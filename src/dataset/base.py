"""
src/dataset/base.py
Core abstractions for dataset-agnostic sensor fusion research.

Defines:
- Calibration: Pinhole camera intrinsics, extrinsics, coordinate frame projections.
- GroundTruthObject: Authoritative state of a single dynamic or static object.
- GroundTruthFrame: Collection of ground truth objects for a single timestep.
- SensorFrame: Unified container for synchronized camera, LiDAR, IMU, and calibration.
- ClassMapper: Standardizes object taxonomies across CARLA, KITTI, nuScenes.
- DatasetAdapter: Abstract Base Class defining the dataset interface.
"""

import os
from abc import ABC, abstractmethod
import math
import numpy as np
import cv2

class Calibration:
    """
    Sensor calibration abstraction supporting camera intrinsics,
    LiDAR-to-Camera extrinsics, and bidirectional 2D/3D projections.
    """
    def __init__(self, image_width=800, image_height=600, fov=90.0,
                 trans_lidar_to_cam=None, intrinsic_matrix=None):
        self.width = int(image_width)
        self.height = int(image_height)
        self.fov = float(fov)

        if intrinsic_matrix is not None:
            self.K = np.asarray(intrinsic_matrix, dtype=np.float64)
        else:
            f = self.width / (2.0 * math.tan(math.radians(self.fov) / 2.0))
            self.K = np.array([
                [f,   0.0, self.width / 2.0],
                [0.0, f,   self.height / 2.0],
                [0.0, 0.0, 1.0]
            ], dtype=np.float64)

        if trans_lidar_to_cam is not None:
            self.trans_lidar_to_cam = np.asarray(trans_lidar_to_cam, dtype=np.float64)
        else:
            # Default CARLA mounting: Camera at (1.5, 0.0, 2.4), LiDAR at (0.0, 0.0, 2.5)
            self.trans_lidar_to_cam = np.array([1.5, 0.0, -0.1], dtype=np.float64)

    @staticmethod
    def carla_to_optical(pts_carla):
        """Converts CARLA vehicle frame (X: fwd, Y: right, Z: up) to Optical (X: right, Y: down, Z: fwd)."""
        pts = np.asarray(pts_carla, dtype=np.float64)
        if pts.ndim == 1:
            return np.array([pts[1], -pts[2], pts[0]], dtype=np.float64)
        opt = np.zeros_like(pts)
        opt[:, 0] = pts[:, 1]   # X_opt = Y_carla (Right)
        opt[:, 1] = -pts[:, 2]  # Y_opt = -Z_carla (Down)
        opt[:, 2] = pts[:, 0]   # Z_opt = X_carla (Forward/Depth)
        return opt

    @staticmethod
    def optical_to_carla(pts_optical):
        """Converts Optical frame (X: right, Y: down, Z: fwd) to CARLA vehicle frame (X: fwd, Y: right, Z: up)."""
        pts = np.asarray(pts_optical, dtype=np.float64)
        if pts.ndim == 1:
            return np.array([pts[2], pts[0], -pts[1]], dtype=np.float64)
        carla_pts = np.zeros_like(pts)
        carla_pts[:, 0] = pts[:, 2]  # X_carla = Z_opt (Forward)
        carla_pts[:, 1] = pts[:, 0]  # Y_carla = X_opt (Right)
        carla_pts[:, 2] = -pts[:, 1] # Z_carla = -Y_opt (Up)
        return carla_pts

    def project_lidar_to_camera(self, lidar_points):
        """
        Projects 3D LiDAR points onto the 2D camera image plane.
        Returns:
            uvs: (M, 2) pixel coordinates
            depths: (M,) optical forward depths in meters
        """
        if len(lidar_points) == 0:
            return np.empty((0, 2)), np.empty((0,))

        pts = np.asarray(lidar_points, dtype=np.float64)
        if pts.ndim == 1:
            pts = pts.reshape(1, 3)

        # 1. LiDAR to camera sensor origin
        pts_cam = pts - self.trans_lidar_to_cam

        # 2. Convert to camera optical axes
        pts_opt = self.carla_to_optical(pts_cam)

        depth = pts_opt[:, 2]
        in_front = depth > 0.5
        pts_front = pts_opt[in_front]
        valid_depth = depth[in_front]

        if len(pts_front) == 0:
            return np.empty((0, 2)), np.empty((0,))

        # 3. Perspective projection
        homo = (self.K @ pts_front.T).T
        u = homo[:, 0] / homo[:, 2]
        v = homo[:, 1] / homo[:, 2]

        in_image = (u >= 0) & (u < self.width) & (v >= 0) & (v < self.height)
        uvs = np.column_stack([u[in_image], v[in_image]])
        depths = valid_depth[in_image]

        return uvs, depths

    def project_bbox_3d_to_2d(self, corners_3d):
        """
        Projects 8 corners of a 3D bounding box to a 2D bounding box [x1, y1, x2, y2].
        Returns bbox [x1, y1, x2, y2] or None if outside frustum.
        """
        corners = np.asarray(corners_3d, dtype=np.float64)
        if len(corners) < 4:
            return None

        uvs, depths = self.project_lidar_to_camera(corners)
        if len(uvs) < 2 or len(depths) < 2:
            return None

        u_min = max(0.0, float(np.min(uvs[:, 0])))
        u_max = min(self.width - 1.0, float(np.max(uvs[:, 0])))
        v_min = max(0.0, float(np.min(uvs[:, 1])))
        v_max = min(self.height - 1.0, float(np.max(uvs[:, 1])))

        if u_max <= u_min or v_max <= v_min:
            return None

        return [round(u_min, 1), round(v_min, 1), round(u_max, 1), round(v_max, 1)]

    def camera_ray_to_3d(self, u, v, depth):
        """
        Back-projects a 2D pixel coordinate (u, v) with known depth into 3D LiDAR/sensor coordinates.
        Uses optical inverse projection followed by optical-to-CARLA rotation and extrinsic translation.
        """
        fx = self.K[0, 0]
        fy = self.K[1, 1]
        cx = self.K[0, 2]
        cy = self.K[1, 2]

        z_opt = float(depth)
        x_opt = (float(u) - cx) * z_opt / fx
        y_opt = (float(v) - cy) * z_opt / fy

        p_opt = np.array([x_opt, y_opt, z_opt], dtype=np.float64)
        p_carla_cam = self.optical_to_carla(p_opt)
        p_lidar = p_carla_cam + self.trans_lidar_to_cam
        return p_lidar


class ClassMapper:
    """Standardizes dataset-specific class annotations into unified perception categories."""
    SYNONYM_MAP = {
        # Vehicles
        "car": "vehicle",
        "vehicle": "vehicle",
        "automobile": "vehicle",
        "truck": "vehicle",
        "bus": "vehicle",
        "van": "vehicle",
        "vehicle.tesla.model3": "vehicle",
        "vehicle.audi.tt": "vehicle",
        "vehicle.mercedes.coupe": "vehicle",
        "vehicle.ford.mustang": "vehicle",
        "vehicle.carlamotors.carlacola": "vehicle",
        "vehicle.dodge.charger_police": "vehicle",
        "vehicle.nissan.patrol": "vehicle",
        "vehicle.toyota.prius": "vehicle",
        # Pedestrians
        "pedestrian": "pedestrian",
        "walker": "pedestrian",
        "person": "pedestrian",
        "person_sitting": "pedestrian",
        "walker.pedestrian.0001": "pedestrian",
        "walker.pedestrian.0002": "pedestrian",
        # Cyclists
        "cyclist": "cyclist",
        "bicycle": "cyclist",
        "motorcycle": "cyclist",
        "bike": "cyclist",
        # Traffic elements
        "traffic_light": "traffic_light",
        "traffic light": "traffic_light",
        "traffic_sign": "traffic_sign",
        "stop sign": "traffic_sign"
    }

    @classmethod
    def map_class(cls, raw_class: str) -> str:
        """Maps any dataset class string to standard taxonomy."""
        key = str(raw_class).lower().strip()
        if key in cls.SYNONYM_MAP:
            return cls.SYNONYM_MAP[key]
        for prefix, target in [("vehicle.", "vehicle"), ("walker.", "pedestrian")]:
            if key.startswith(prefix):
                return target
        return key


class GroundTruthObject:
    """Represents the authoritative ground-truth state of an object."""
    def __init__(self, object_id, class_name, position_world, position_ego,
                 position_lidar, dimensions=None, bbox_2d=None, bbox_3d=None,
                 velocity=None, orientation=None, is_visible=True):
        self.object_id = int(object_id) if str(object_id).isdigit() else str(object_id)
        self.class_name = ClassMapper.map_class(class_name)
        self.raw_class = str(class_name)
        self.position_world = np.asarray(position_world, dtype=np.float64)
        self.position_ego = np.asarray(position_ego, dtype=np.float64)
        self.position_lidar = np.asarray(position_lidar, dtype=np.float64)
        self.dimensions = np.asarray(dimensions if dimensions is not None else [4.5, 1.8, 1.5], dtype=np.float64)
        self.bbox_2d = [float(x) for x in bbox_2d] if bbox_2d is not None else None
        self.bbox_3d = bbox_3d
        self.velocity = np.asarray(velocity if velocity is not None else [0.0, 0.0, 0.0], dtype=np.float64)
        self.orientation = orientation if orientation is not None else [0.0, 0.0, 0.0]  # [pitch, yaw, roll] in degrees
        self.radial_distance = float(np.linalg.norm(self.position_lidar[:2]))
        self.is_visible = bool(is_visible)

    def to_dict(self):
        return {
            "id": self.object_id,
            "class_name": self.class_name,
            "raw_class": self.raw_class,
            "position_world": [round(float(p), 3) for p in self.position_world],
            "position_ego": [round(float(p), 3) for p in self.position_ego],
            "position_lidar": [round(float(p), 3) for p in self.position_lidar],
            "dimensions": [round(float(d), 3) for d in self.dimensions],
            "bbox_2d": self.bbox_2d,
            "velocity": [round(float(v), 3) for v in self.velocity],
            "orientation": [round(float(o), 2) for o in self.orientation],
            "radial_distance": round(self.radial_distance, 3),
            "is_visible": self.is_visible
        }


class GroundTruthFrame:
    """Encapsulates authoritative ground truth for a single frame."""
    def __init__(self, frame_id, timestamp, ego_pose=None, objects=None):
        self.frame_id = int(frame_id)
        self.timestamp = float(timestamp)
        self.ego_pose = ego_pose if ego_pose is not None else {}
        self.objects = objects if objects is not None else []

    def get_positions_3d(self, max_distance=45.0, visible_only=True):
        """Returns list of 3D positions in LiDAR sensor frame for ground truth evaluation."""
        positions = []
        for obj in self.objects:
            if visible_only and not obj.is_visible:
                continue
            if obj.radial_distance <= max_distance:
                positions.append(obj.position_lidar)
        return positions

    def get_boxes_2d(self, min_area=25.0):
        """Returns list of 2D bounding boxes for camera evaluation."""
        boxes = []
        for obj in self.objects:
            if obj.bbox_2d is not None:
                w = obj.bbox_2d[2] - obj.bbox_2d[0]
                h = obj.bbox_2d[3] - obj.bbox_2d[1]
                if (w * h) >= min_area:
                    boxes.append({
                        "bbox": obj.bbox_2d,
                        "class_name": obj.class_name,
                        "id": obj.object_id
                    })
        return boxes

    def get_visible_objects(self, max_distance=45.0):
        return [obj for obj in self.objects if obj.is_visible and obj.radial_distance <= max_distance]


class SensorFrame:
    """Unified container for synchronized multimodal data in a single timestep."""
    def __init__(self, frame_id, timestamp, camera_image=None, camera_path=None,
                 lidar_points=None, lidar_path=None, imu_data=None, T_ego=None,
                 dt=0.05, calibration=None, ground_truth=None, metadata=None):
        self.frame_id = int(frame_id)
        self.timestamp = float(timestamp)
        self.camera_image = camera_image
        self.camera_path = camera_path
        self.lidar_points = lidar_points
        self.lidar_path = lidar_path
        self.imu_data = imu_data if imu_data is not None else {}
        self.T_ego = T_ego if T_ego is not None else np.eye(4, dtype=np.float64)
        self.dt = float(dt)
        self.calibration = calibration or Calibration()
        self.ground_truth = ground_truth or GroundTruthFrame(frame_id, timestamp)
        self.metadata = metadata if metadata is not None else {}

    @property
    def has_camera(self):
        return self.camera_image is not None or (self.camera_path and cv2.haveImageReader(self.camera_path))

    @property
    def has_lidar(self):
        return self.lidar_points is not None or (self.lidar_path and os.path.exists(self.lidar_path))

    def get_camera_image(self):
        """Loads and returns camera image as BGR numpy array."""
        if self.camera_image is not None:
            return self.camera_image
        if self.camera_path and os.path.exists(self.camera_path):
            self.camera_image = cv2.imread(self.camera_path)
            return self.camera_image
        return None

    def get_lidar_points(self):
        """Loads and returns LiDAR points as (N, 3) numpy array."""
        if self.lidar_points is not None:
            return self.lidar_points
        if self.lidar_path and os.path.exists(self.lidar_path):
            import open3d as o3d
            pcd = o3d.io.read_point_cloud(self.lidar_path)
            self.lidar_points = np.asarray(pcd.points, dtype=np.float64)
            return self.lidar_points
        return np.empty((0, 3), dtype=np.float64)


class DatasetAdapter(ABC):
    """Abstract Base Class for dataset adapters (CARLA, KITTI, nuScenes, etc.)."""
    @abstractmethod
    def __len__(self) -> int:
        pass

    @abstractmethod
    def __getitem__(self, index: int) -> SensorFrame:
        pass

    @abstractmethod
    def get_calibration(self) -> Calibration:
        pass

    @abstractmethod
    def get_sequence(self) -> list:
        pass
