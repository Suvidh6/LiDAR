"""
src/sensors/synchronization.py
Synchronous multi-sensor recording harness for CARLA 0.9.16.

Manages:
- Simulation lockstep at fixed delta time (20 Hz, dt = 0.05s).
- Queue-based synchronous sensor collection (Camera + LiDAR + IMU).
- Dynamic vehicle maneuver injection (accelerate, steer, cruise, brake).
- Persistent dataset serialization (PNG, PLY, CSV).
"""

import os
import csv
import time
import math
import queue

class SynchronousRecorder:
    """
    Spawns sensors and records synchronized Camera, LiDAR, and IMU data from CARLA.
    """
    def __init__(self, host="localhost", port=2000, fixed_delta_seconds=0.05):
        self.host = host
        self.port = port
        self.dt = fixed_delta_seconds
        self.client = None
        self.world = None

    def record_dataset(self, num_frames=70, output_root=None):
        """Records a synchronized dynamic maneuver sequence."""
        try:
            import carla
        except ImportError:
            raise ImportError("CARLA Python API is required to run live recording.")

        if output_root is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            output_root = os.path.join(base_dir, "data", "dynamic_dataset")

        self.client = carla.Client(self.host, self.port)
        self.client.set_timeout(10.0)

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

        os.makedirs(camera_dir, exist_ok=True)
        os.makedirs(lidar_dir, exist_ok=True)
        os.makedirs(imu_dir, exist_ok=True)

        actors = []
        imu_records = []

        try:
            # Spawn ego vehicle
            vehicle_bp = blueprints.filter("vehicle.tesla.model3")[0]
            spawn_points = self.world.get_map().get_spawn_points()
            spawn_point = spawn_points[0] if spawn_points else carla.Transform()
            vehicle = self.world.try_spawn_actor(vehicle_bp, spawn_point)
            if vehicle is None:
                for sp in spawn_points[1:10]:
                    vehicle = self.world.try_spawn_actor(vehicle_bp, sp)
                    if vehicle is not None:
                        break
            if vehicle is None:
                raise RuntimeError("Failed to spawn vehicle.")
            actors.append(vehicle)

            # Spawn RGB Camera (x=1.5, z=2.4)
            camera_bp = blueprints.find("sensor.camera.rgb")
            camera_bp.set_attribute("image_size_x", "800")
            camera_bp.set_attribute("image_size_y", "600")
            camera_bp.set_attribute("fov", "90")
            camera = self.world.spawn_actor(camera_bp, carla.Transform(carla.Location(x=1.5, z=2.4)), attach_to=vehicle)
            actors.append(camera)

            # Spawn LiDAR (x=0.0, z=2.5, 64 channels, 50m range)
            lidar_bp = blueprints.find("sensor.lidar.ray_cast")
            lidar_bp.set_attribute("channels", "64")
            lidar_bp.set_attribute("range", "50")
            lidar_bp.set_attribute("points_per_second", "130000")
            lidar_bp.set_attribute("rotation_frequency", "10")
            lidar = self.world.spawn_actor(lidar_bp, carla.Transform(carla.Location(x=0.0, z=2.5)), attach_to=vehicle)
            actors.append(lidar)

            # Spawn IMU (x=0.0, z=2.0)
            imu_bp = blueprints.find("sensor.other.imu")
            imu = self.world.spawn_actor(imu_bp, carla.Transform(carla.Location(x=0.0, z=2.0)), attach_to=vehicle)
            actors.append(imu)

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

            print(f"Recording {num_frames} synchronized frames...")
            for i in range(num_frames):
                # Maneuver profile
                if i < 15:
                    vehicle.apply_control(carla.VehicleControl(throttle=0.6, steer=0.0))
                elif i < 35:
                    vehicle.apply_control(carla.VehicleControl(throttle=0.45, steer=0.25))
                elif i < 50:
                    vehicle.apply_control(carla.VehicleControl(throttle=0.35, steer=-0.1))
                else:
                    vehicle.apply_control(carla.VehicleControl(throttle=0.0, steer=0.0, brake=0.7))

                self.world.tick()

                cam_data = cam_queue.get(timeout=5.0)
                lid_data = lid_queue.get(timeout=5.0)
                imu_data = imu_queue.get(timeout=5.0)

                v_transform = vehicle.get_transform()
                v_vel = vehicle.get_velocity()
                frame_id = cam_data.frame

                cam_path = os.path.join(camera_dir, f"frame_{frame_id:06d}.png")
                lid_path = os.path.join(lidar_dir, f"frame_{frame_id:06d}.ply")

                cam_data.save_to_disk(cam_path)
                lid_data.save_to_disk(lid_path)

                imu_records.append({
                    "frame_id": frame_id,
                    "timestamp": imu_data.timestamp,
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

            csv_path = os.path.join(imu_dir, "imu_telemetry.csv")
            with open(csv_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=list(imu_records[0].keys()))
                writer.writeheader()
                writer.writerows(imu_records)

            print(f"Dataset recording complete: {num_frames} frames saved.")

        finally:
            for actor in reversed(actors):
                if actor is not None and actor.is_alive:
                    actor.destroy()
            self.world.apply_settings(original_settings)
