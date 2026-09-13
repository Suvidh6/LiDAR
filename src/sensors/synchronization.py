"""
src/sensors/synchronization.py
Synchronous multi-sensor recording harness for CARLA 0.9.16.

Manages:
- Simulation lockstep at fixed delta time (20 Hz, dt = 0.05s).
- Queue-based synchronous sensor collection (Camera + LiDAR + IMU).
- Dynamic vehicle maneuver injection (accelerate, steer, cruise, brake).
- Multi-actor scenario population (vehicles and pedestrians).
- Authoritative Ground Truth recording directly from simulated CARLA actor state
  (independent of perception, sensors, or degradations).
- Persistent dataset serialization (PNG, PLY, CSV, JSON).
"""

import os
import csv
import json
import time
import math
import queue
import numpy as np

class SynchronousRecorder:
    """
    Spawns ego vehicle, surrounding actors, and sensors; records synchronized
    Camera, LiDAR, IMU data and authoritative Ground Truth from CARLA.
    """
    def __init__(self, host="localhost", port=2000, fixed_delta_seconds=0.05):
        self.host = host
        self.port = port
        self.dt = fixed_delta_seconds
        self.client = None
        self.world = None

    def record_dataset(self, num_frames=70, output_root=None, num_target_vehicles=4, num_pedestrians=2):
        """
        Records a synchronized dynamic maneuver sequence with authoritative ground truth.
        """
        try:
            import carla
        except ImportError:
            raise ImportError("CARLA Python API is required to run live recording.")

        if output_root is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            output_root = os.path.join(base_dir, "data", "dynamic_dataset")

        self.client = carla.Client(self.host, self.port)
        self.client.set_timeout(15.0)

        self.world = self.client.get_world()
        blueprints = self.world.get_blueprint_library()
        original_settings = self.world.get_settings()

        # Synchronous settings
        settings = self.world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = self.dt
        self.world.apply_settings(settings)

        camera_dir = os.path.join(output_root, "camera")
        lidar_dir = os.path.join(output_root, "lidar")
        imu_dir = os.path.join(output_root, "imu")
        gt_dir = os.path.join(output_root, "ground_truth")

        os.makedirs(camera_dir, exist_ok=True)
        os.makedirs(lidar_dir, exist_ok=True)
        os.makedirs(imu_dir, exist_ok=True)
        os.makedirs(gt_dir, exist_ok=True)

        actors = []
        target_actors = []
        imu_records = []
        master_gt = {}

        try:
            # 1. Spawn Ego vehicle
            vehicle_bp = blueprints.filter("vehicle.tesla.model3")[0]
            spawn_points = self.world.get_map().get_spawn_points()
            spawn_point = spawn_points[0] if spawn_points else carla.Transform()
            vehicle = self.world.try_spawn_actor(vehicle_bp, spawn_point)
            if vehicle is None:
                for sp in spawn_points[1:15]:
                    vehicle = self.world.try_spawn_actor(vehicle_bp, sp)
                    if vehicle is not None:
                        spawn_point = sp
                        break
            if vehicle is None:
                raise RuntimeError("Failed to spawn ego vehicle.")
            actors.append(vehicle)

            # 2. Spawn RGB Camera (x=1.5, z=2.4)
            camera_bp = blueprints.find("sensor.camera.rgb")
            camera_bp.set_attribute("image_size_x", "800")
            camera_bp.set_attribute("image_size_y", "600")
            camera_bp.set_attribute("fov", "90")
            camera = self.world.spawn_actor(camera_bp, carla.Transform(carla.Location(x=1.5, z=2.4)), attach_to=vehicle)
            actors.append(camera)

            # 3. Spawn LiDAR (x=0.0, z=2.5, 64 channels, 50m range)
            lidar_bp = blueprints.find("sensor.lidar.ray_cast")
            lidar_bp.set_attribute("channels", "64")
            lidar_bp.set_attribute("range", "50")
            lidar_bp.set_attribute("points_per_second", "130000")
            lidar_bp.set_attribute("rotation_frequency", "10")
            lidar = self.world.spawn_actor(lidar_bp, carla.Transform(carla.Location(x=0.0, z=2.5)), attach_to=vehicle)
            actors.append(lidar)

            # 4. Spawn IMU (x=0.0, z=2.0)
            imu_bp = blueprints.find("sensor.other.imu")
            imu = self.world.spawn_actor(imu_bp, carla.Transform(carla.Location(x=0.0, z=2.0)), attach_to=vehicle)
            actors.append(imu)

            # 5. Spawn Target Obstacle Actors (along ego maneuver corridor)
            fwd = spawn_point.get_forward_vector()
            right = carla.Vector3D(x=-fwd.y, y=fwd.x, z=0.0)

            target_blueprints = [
                blueprints.filter("vehicle.audi.tt")[0],
                blueprints.filter("vehicle.mercedes.coupe")[0],
                blueprints.filter("vehicle.ford.mustang")[0],
                blueprints.filter("vehicle.carlamotors.carlacola")[0],
                blueprints.filter("walker.pedestrian.0001")[0],
                blueprints.filter("walker.pedestrian.0002")[0]
            ]

            target_offsets = [
                (14.0, 1.2, target_blueprints[0]),   # Audi 14m ahead, slight right
                (24.0, -1.5, target_blueprints[1]),  # Mercedes 24m ahead, slight left
                (34.0, 0.8, target_blueprints[2]),   # Mustang 34m ahead
                (44.0, -1.0, target_blueprints[3]),  # Truck 44m ahead
                (18.0, 3.2, target_blueprints[4]),   # Pedestrian crossing
                (28.0, -3.0, target_blueprints[5])   # Pedestrian on left sidewalk
            ]

            for dist_fwd, dist_side, bp in target_offsets:
                tgt_sp = carla.Transform(
                    carla.Location(
                        x=spawn_point.location.x + fwd.x * dist_fwd + right.x * dist_side,
                        y=spawn_point.location.y + fwd.y * dist_fwd + right.y * dist_side,
                        z=spawn_point.location.z + 0.2
                    ),
                    spawn_point.rotation
                )
                tgt = self.world.try_spawn_actor(bp, tgt_sp)
                if tgt is not None:
                    actors.append(tgt)
                    target_actors.append(tgt)

            print(f"Spawned ego vehicle and {len(target_actors)} target obstacles in CARLA scene.")

            # Synchronous Queues
            cam_queue = queue.Queue()
            lid_queue = queue.Queue()
            imu_queue = queue.Queue()

            camera.listen(cam_queue.put)
            lidar.listen(lid_queue.put)
            imu.listen(imu_queue.put)

            # Warm-up ticks
            for _ in range(10):
                self.world.tick()
                cam_queue.get(timeout=2.0)
                lid_queue.get(timeout=2.0)
                imu_queue.get(timeout=2.0)

            print(f"Recording {num_frames} synchronized frames with authoritative ground truth...")
            for i in range(num_frames):
                # Dynamic Maneuver Profile
                if i < 15:
                    vehicle.apply_control(carla.VehicleControl(throttle=0.55, steer=0.0))
                elif i < 35:
                    vehicle.apply_control(carla.VehicleControl(throttle=0.40, steer=0.20))
                elif i < 50:
                    vehicle.apply_control(carla.VehicleControl(throttle=0.30, steer=-0.10))
                else:
                    vehicle.apply_control(carla.VehicleControl(throttle=0.0, steer=0.0, brake=0.75))

                self.world.tick()

                cam_data = cam_queue.get(timeout=5.0)
                lid_data = lid_queue.get(timeout=5.0)
                imu_data = imu_queue.get(timeout=5.0)

                v_transform = vehicle.get_transform()
                v_vel = vehicle.get_velocity()
                frame_id = cam_data.frame
                timestamp = imu_data.timestamp

                cam_path = os.path.join(camera_dir, f"frame_{frame_id:06d}.png")
                lid_path = os.path.join(lidar_dir, f"frame_{frame_id:06d}.ply")

                cam_data.save_to_disk(cam_path)
                lid_data.save_to_disk(lid_path)

                # Record IMU Telemetry
                imu_records.append({
                    "frame_id": frame_id,
                    "timestamp": timestamp,
                    "accel_x": imu_data.accelerometer.x,
                    "accel_y": imu_data.accelerometer.y,
                    "accel_z": imu_data.accelerometer.z,
                    "gyro_x": imu_data.gyroscope.x,
                    "gyro_y": imu_data.gyroscope.y,
                    "gyro_z": imu_data.gyroscope.z,
                    "compass": imu_data.compass,
                    "gt_x": v_transform.location.x,
                    "gt_y": v_transform.location.y,
                    "gt_z": v_transform.location.z,
                    "gt_pitch": v_transform.rotation.pitch,
                    "gt_yaw": v_transform.rotation.yaw,
                    "gt_roll": v_transform.rotation.roll,
                    "gt_vx": v_vel.x,
                    "gt_vy": v_vel.y,
                    "gt_vz": v_vel.z
                })

                # Authoritative CARLA Ground Truth for Obstacle Actors
                world_to_ego = np.array(v_transform.get_inverse_matrix())
                frame_gt_objects = []

                for tgt in target_actors:
                    if not tgt.is_alive:
                        continue
                    t_trans = tgt.get_transform()
                    t_loc = t_trans.location
                    t_rot = t_trans.rotation
                    t_vel = tgt.get_velocity()
                    bbox = tgt.bounding_box

                    # Position in ego frame
                    p_w = np.array([t_loc.x, t_loc.y, t_loc.z, 1.0])
                    p_ego = world_to_ego @ p_w
                    # Position in LiDAR frame: LiDAR mounted at (0.0, 0.0, 2.5) relative to ego
                    p_lidar = p_ego[:3] - np.array([0.0, 0.0, 2.5])
                    dist = float(np.linalg.norm(p_lidar[:2]))

                    # 3D bounding box corners
                    corners_local = [
                        [ bbox.extent.x,  bbox.extent.y,  bbox.extent.z, 1.0],
                        [ bbox.extent.x, -bbox.extent.y,  bbox.extent.z, 1.0],
                        [-bbox.extent.x, -bbox.extent.y,  bbox.extent.z, 1.0],
                        [-bbox.extent.x,  bbox.extent.y,  bbox.extent.z, 1.0],
                        [ bbox.extent.x,  bbox.extent.y, -bbox.extent.z, 1.0],
                        [ bbox.extent.x, -bbox.extent.y, -bbox.extent.z, 1.0],
                        [-bbox.extent.x, -bbox.extent.y, -bbox.extent.z, 1.0],
                        [-bbox.extent.x,  bbox.extent.y, -bbox.extent.z, 1.0],
                    ]
                    actor_to_world = np.array(t_trans.get_matrix())
                    corners_lidar = []
                    for c_loc in corners_local:
                        c_w = actor_to_world @ np.array(c_loc)
                        c_ego = world_to_ego @ c_w
                        c_lid = c_ego[:3] - np.array([0.0, 0.0, 2.5])
                        corners_lidar.append(c_lid)
                    corners_lidar = np.array(corners_lidar)

                    # Project to 2D camera bbox
                    # Camera mounted at (1.5, 0.0, 2.4) relative to ego -> [1.5, 0.0, -0.1] rel to lidar
                    from ..dataset.base import Calibration
                    calib = Calibration(image_width=800, image_height=600, fov=90.0)
                    bbox_2d = calib.project_bbox_3d_to_2d(corners_lidar)

                    # Visibility filter: in front of ego vehicle and within 50m
                    is_visible = (p_lidar[0] > 1.0) and (dist <= 50.0)

                    # Simplified class name
                    type_str = tgt.type_id.lower()
                    if "walker" in type_str or "pedestrian" in type_str:
                        class_name = "pedestrian"
                    elif "carlacola" in type_str or "truck" in type_str:
                        class_name = "truck"
                    else:
                        class_name = "vehicle"

                    frame_gt_objects.append({
                        "id": tgt.id,
                        "type": tgt.type_id,
                        "class_name": class_name,
                        "position_world": [round(t_loc.x, 3), round(t_loc.y, 3), round(t_loc.z, 3)],
                        "position_ego": [round(p_ego[0], 3), round(p_ego[1], 3), round(p_ego[2], 3)],
                        "position_lidar": [round(p_lidar[0], 3), round(p_lidar[1], 3), round(p_lidar[2], 3)],
                        "dimensions": [round(bbox.extent.x * 2, 2), round(bbox.extent.y * 2, 2), round(bbox.extent.z * 2, 2)],
                        "bbox_2d": bbox_2d,
                        "velocity": [round(t_vel.x, 3), round(t_vel.y, 3), round(t_vel.z, 3)],
                        "orientation": [round(t_rot.pitch, 2), round(t_rot.yaw, 2), round(t_rot.roll, 2)],
                        "radial_distance": round(dist, 2),
                        "is_visible": is_visible
                    })

                frame_gt_data = {
                    "frame_id": frame_id,
                    "timestamp": timestamp,
                    "ego_pose": {
                        "x": v_transform.location.x,
                        "y": v_transform.location.y,
                        "z": v_transform.location.z,
                        "pitch": v_transform.rotation.pitch,
                        "yaw": v_transform.rotation.yaw,
                        "roll": v_transform.rotation.roll
                    },
                    "objects": frame_gt_objects
                }

                # Save individual frame GT JSON
                gt_frame_path = os.path.join(gt_dir, f"frame_{frame_id:06d}.json")
                with open(gt_frame_path, "w") as f:
                    json.dump(frame_gt_data, f, indent=2)

                master_gt[str(frame_id)] = frame_gt_data

            # Save IMU Telemetry CSV
            csv_path = os.path.join(imu_dir, "imu_telemetry.csv")
            with open(csv_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=list(imu_records[0].keys()))
                writer.writeheader()
                writer.writerows(imu_records)

            # Save Master Ground Truth JSON
            master_gt_path = os.path.join(output_root, "ground_truth.json")
            with open(master_gt_path, "w") as f:
                json.dump(master_gt, f, indent=2)

            print(f"Dataset recording complete: {num_frames} frames saved.")
            print(f"Authoritative Ground Truth saved to: {master_gt_path} and {gt_dir}/")

        finally:
            for actor in reversed(actors):
                if actor is not None and actor.is_alive:
                    actor.destroy()
            self.world.apply_settings(original_settings)
