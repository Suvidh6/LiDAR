"""
src/fusion/reliability_estimation.py
Physical and contextual sensor reliability estimation module.

Calculates:
- Camera Reliability R_cam:
    f(confidence, Laplacian sharpness, illumination, range attenuation,
      IMU vehicle dynamic agitation, temporal track consistency)
- LiDAR Reliability R_lidar:
    f(range-normalized point density, 3D geometric regularity,
      operational sensor health, temporal track consistency)
"""

import numpy as np

class ReliabilityEstimator:
    """
    Computes grounded reliability scores for Camera and LiDAR sensor streams.
    """
    def __init__(self, camera_max_range=45.0, nominal_lidar_points=2500):
        self.camera_max_range = float(camera_max_range)
        self.nominal_lidar_points = float(nominal_lidar_points)

    def estimate_camera_reliability(self, cam_det, image_quality, distance, imu_state=None, persistence=1.0):
        """
        Calculates Camera Reliability R_cam in [0.01, 0.99].
        Factors:
        - c_det: YOLO detection confidence.
        - psi_visual: Balanced blend of Laplacian sharpness and illumination quality.
        - psi_range: Exponential range attenuation (1/d^2 pixel shrinking).
        - psi_motion: Ego-vehicle dynamic agitation penalty (from IMU yaw-rate & accel).
        - tau_temp: Temporal persistence bonus.
        """
        if cam_det is None:
            return 0.01

        c_det = float(cam_det.confidence)
        psi_sharp = float(image_quality.get("sharpness_score", 0.8))
        psi_illum = float(image_quality.get("illum_score", 0.8))
        psi_visual = 0.5 * psi_sharp + 0.5 * psi_illum

        d = max(1.0, float(distance))
        psi_range = float(np.exp(-d / self.camera_max_range))

        psi_motion = 1.0
        if imu_state is not None:
            gyro = imu_state.get("gyro", [0, 0, 0])
            lin_acc = imu_state.get("linear_accel", [0, 0, 0])
            yaw_rate_deg = abs(np.degrees(gyro[2]))
            lin_accel_x = abs(lin_acc[0])
            agitation = yaw_rate_deg * 0.03 + lin_accel_x * 0.05
            psi_motion = float(np.exp(-agitation))

        tau_temp = float(np.clip(persistence, 0.4, 1.0))

        r_cam = c_det * psi_visual * psi_range * psi_motion * tau_temp
        return float(np.clip(r_cam, 0.01, 0.99))

    def estimate_lidar_reliability(self, lidar_cluster, total_cloud_points, distance, persistence=1.0):
        """
        Calculates LiDAR Reliability R_lidar in [0.01, 0.99].
        Factors:
        - rho_density: Range-normalized point density relative to 1/d physical beam divergence.
        - gamma_geom: Geometric prior regularity (bounding volume and vehicular aspect ratio).
        - psi_health: Operational sensor health (penalizes dropouts / beam blockage).
        - tau_temp: Temporal persistence bonus.
        """
        if lidar_cluster is None:
            return 0.01

        d = max(1.5, float(distance))
        n_pts = float(lidar_cluster.num_points)

        # Expected laser pulses for standard obstacle at distance d in ~2500-3000 point scan
        n_expected = 400.0 / (d + 1.0)
        rho_density = float(np.clip(n_pts / max(1.0, n_expected), 0.15, 1.0))

        gamma_geom = float(lidar_cluster.geometric_score)
        psi_health = float(np.clip(total_cloud_points / float(self.nominal_lidar_points), 0.10, 1.0))
        tau_temp = float(np.clip(persistence, 0.4, 1.0))

        spatial_quality = 0.50 * gamma_geom + 0.50 * rho_density
        r_lidar = spatial_quality * psi_health * tau_temp
        return float(np.clip(r_lidar, 0.01, 0.99))
