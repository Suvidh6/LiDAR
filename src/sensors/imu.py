"""
src/sensors/imu.py
Module for processing CARLA IMU telemetry and estimating inter-frame vehicle ego-motion.

Extracts:
- Accelerometer (X, Y, Z) in m/s^2
- Gyroscope (roll, pitch, yaw rate) in rad/s
- Timestamps and synchronized Frame IDs

Calculates:
- Gravity-compensated linear acceleration
- Angular velocity and integrated inter-frame rotation (Delta R in SO(3))
- Estimated inter-frame displacement (Delta t)
- Rigid-body SE(3) transformation matrix (T_ego)
- Discrete vehicle motion states (STATIONARY, ACCELERATING, BRAKING, TURNING, CRUISING)
- Association with synchronized Camera and LiDAR disk frames
"""

import os
import math
import numpy as np
import pandas as pd

class IMUMotionProcessor:
    """
    Processes IMU data streams or telemetry CSV files to produce motion-aware
    ego-motion estimates between consecutive perception frames.
    """
    GRAVITY_MAGNITUDE = 9.81  # Standard Earth gravity (m/s^2)

    def __init__(self, data_root=None):
        if data_root is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            data_root = os.path.join(base_dir, "data", "dynamic_dataset")
        self.data_root = data_root
        self.camera_dir = os.path.join(data_root, "camera")
        self.lidar_dir = os.path.join(data_root, "lidar")
        self.imu_csv_path = os.path.join(data_root, "imu", "imu_telemetry.csv")
        self.telemetry = None
        self.motion_frames = []

    def load_telemetry(self, csv_path=None):
        """Loads and indexes IMU telemetry CSV."""
        path = csv_path or self.imu_csv_path
        if not os.path.exists(path):
            raise FileNotFoundError(f"IMU telemetry file not found: {path}")
        self.telemetry = pd.read_csv(path)
        self.telemetry.sort_values(by="frame_id", inplace=True)
        self.telemetry.reset_index(drop=True, inplace=True)
        return self.telemetry

    def classify_motion_state(self, a_x, a_y, gyro_z, speed=None):
        """
        Rule-based motion state classifier based on longitudinal acceleration
        and yaw angular velocity.
        
        CARLA Unreal Left-Handed coordinates:
        - X: Forward
        - Y: Right
        - Z: Up
        - Yaw: Clockwise rotation about +Z (Right is positive yaw rate, Left is negative).
        """
        ACCEL_THRESH = 0.35      # m/s^2
        BRAKE_THRESH = -0.35     # m/s^2
        YAW_RATE_THRESH = 0.05   # rad/s (~2.8 deg/s)

        if speed is not None and speed < 0.15 and abs(a_x) < 0.2:
            return "STATIONARY"

        # Longitudinal classification
        if a_x > ACCEL_THRESH:
            longitudinal = "ACCELERATING"
        elif a_x < BRAKE_THRESH:
            longitudinal = "BRAKING"
        else:
            longitudinal = "CRUISING"

        # Lateral / rotational classification
        if gyro_z > YAW_RATE_THRESH:
            rotational = "TURNING_RIGHT"
        elif gyro_z < -YAW_RATE_THRESH:
            rotational = "TURNING_LEFT"
        else:
            rotational = "STRAIGHT"

        if rotational != "STRAIGHT":
            if longitudinal in ("ACCELERATING", "BRAKING"):
                return f"{rotational} + {longitudinal}"
            return rotational
        
        return longitudinal

    @staticmethod
    def compute_rotation_matrix(delta_roll, delta_pitch, delta_yaw):
        """
        Computes 3D rotation matrix Delta R for small/arbitrary angle rotations
        in CARLA coordinate convention (X forward, Y right, Z up).
        """
        # Rotation around Z (Yaw)
        cz, sz = math.cos(delta_yaw), math.sin(delta_yaw)
        R_z = np.array([
            [ cz, -sz, 0.0],
            [ sz,  cz, 0.0],
            [0.0, 0.0, 1.0]
        ], dtype=np.float64)

        # Rotation around Y (Pitch)
        cy, sy = math.cos(delta_pitch), math.sin(delta_pitch)
        R_y = np.array([
            [ cy, 0.0,  sy],
            [0.0, 1.0, 0.0],
            [-sy, 0.0,  cy]
        ], dtype=np.float64)

        # Rotation around X (Roll)
        cx, sx = math.cos(delta_roll), math.sin(delta_roll)
        R_x = np.array([
            [1.0, 0.0, 0.0],
            [0.0,  cx, -sx],
            [0.0,  sx,  cx]
        ], dtype=np.float64)

        return R_z @ R_y @ R_x

    def process_sequence(self):
        """
        Processes entire synchronized sequence:
        - Associates Camera, LiDAR, and IMU by frame ID.
        - Calculates gravity-compensated acceleration.
        - Computes inter-frame Delta R and Delta translation.
        - Classifies motion states.
        """
        if self.telemetry is None:
            self.load_telemetry()

        n_rows = len(self.telemetry)
        self.motion_frames = []

        est_velocity = np.array([0.0, 0.0, 0.0], dtype=np.float64)

        for i in range(n_rows):
            row = self.telemetry.iloc[i]
            frame_id = int(row["frame_id"])
            timestamp = float(row["timestamp"])

            # 1. Extract raw IMU telemetry
            raw_accel = np.array([row["accel_x"], row["accel_y"], row["accel_z"]], dtype=np.float64)
            gyro = np.array([row["gyro_x"], row["gyro_y"], row["gyro_z"]], dtype=np.float64)
            compass = float(row["compass"]) if "compass" in row else 0.0

            # 2. Gravity compensation
            linear_accel = np.array([
                raw_accel[0],
                raw_accel[1],
                raw_accel[2] - self.GRAVITY_MAGNITUDE
            ], dtype=np.float64)

            # Ground truth velocity & speed if logged
            has_gt = "gt_vx" in row
            gt_speed = math.sqrt(row["gt_vx"]**2 + row["gt_vy"]**2 + row["gt_vz"]**2) if has_gt else None

            # 3. Associate with Camera and LiDAR disk paths
            cam_path = os.path.join(self.camera_dir, f"frame_{frame_id:06d}.png")
            lid_path = os.path.join(self.lidar_dir, f"frame_{frame_id:06d}.ply")

            has_camera = os.path.exists(cam_path)
            has_lidar = os.path.exists(lid_path)

            # 4. Inter-frame ego-motion estimation
            if i == 0:
                dt = 0.05
                delta_rot = np.eye(3, dtype=np.float64)
                delta_trans = np.zeros(3, dtype=np.float64)
                motion_state = "INITIALIZING"
            else:
                prev_row = self.telemetry.iloc[i - 1]
                dt = max(timestamp - float(prev_row["timestamp"]), 0.001)

                delta_roll = gyro[0] * dt
                delta_pitch = gyro[1] * dt
                delta_yaw = gyro[2] * dt

                delta_rot = self.compute_rotation_matrix(delta_roll, delta_pitch, delta_yaw)

                if has_gt:
                    forward_speed = gt_speed
                    delta_trans = np.array([forward_speed * dt, 0.0, 0.0], dtype=np.float64)
                else:
                    est_velocity += linear_accel * dt
                    delta_trans = est_velocity * dt + 0.5 * linear_accel * (dt**2)

                motion_state = self.classify_motion_state(
                    linear_accel[0], linear_accel[1], gyro[2], speed=gt_speed
                )

            # Rigid-body SE(3) transformation matrix: T_ego = [R | t; 0 | 1]
            T_ego = np.eye(4, dtype=np.float64)
            T_ego[:3, :3] = delta_rot
            T_ego[:3, 3] = delta_trans

            frame_entry = {
                "index": i,
                "frame_id": frame_id,
                "timestamp": timestamp,
                "dt": dt,
                "raw_accel": raw_accel,
                "linear_accel": linear_accel,
                "gyro": gyro,
                "compass": compass,
                "motion_state": motion_state,
                "delta_rot": delta_rot,
                "delta_trans": delta_trans,
                "T_ego": T_ego,
                "camera_path": cam_path if has_camera else None,
                "lidar_path": lid_path if has_lidar else None,
                "has_camera": has_camera,
                "has_lidar": has_lidar
            }

            if has_gt:
                frame_entry["gt_speed"] = gt_speed
                frame_entry["gt_yaw"] = float(row["gt_yaw"])

            self.motion_frames.append(frame_entry)

        return self.motion_frames

    def get_motion_summary_df(self):
        """Returns structured DataFrame with extracted motion parameters."""
        if not self.motion_frames:
            self.process_sequence()

        records = []
        for f in self.motion_frames:
            records.append({
                "frame_id": f["frame_id"],
                "timestamp": f["timestamp"],
                "accel_x_lin": f["linear_accel"][0],
                "accel_y_lin": f["linear_accel"][1],
                "accel_z_lin": f["linear_accel"][2],
                "gyro_x": f["gyro"][0],
                "gyro_y": f["gyro"][1],
                "gyro_z": f["gyro"][2],
                "motion_state": f["motion_state"],
                "delta_x": f["delta_trans"][0],
                "delta_y": f["delta_trans"][1],
                "yaw_rate_deg": math.degrees(f["gyro"][2])
            })
        return pd.DataFrame(records)
