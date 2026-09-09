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
- Dynamic Health States: HEALTHY, DEGRADED, SEVERELY_DEGRADED, FAILED
- Dynamic Reliability Trends: RAPIDLY_DEGRADING, DEGRADING, STABLE, IMPROVING
- Temporal Weight Hysteresis / Smoothing
- Cross-Modal Spatial Consistency
"""

import numpy as np
from .spatial_association import compute_2d_iou

class SensorHealthState:
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    SEVERELY_DEGRADED = "SEVERELY_DEGRADED"
    FAILED = "FAILED"

class ReliabilityTrend:
    IMPROVING = "IMPROVING"
    STABLE = "STABLE"
    DEGRADING = "DEGRADING"
    RAPIDLY_DEGRADING = "RAPIDLY_DEGRADING"

class ReliabilityEstimator:
    """
    Computes physically-grounded reliability scores for Camera and LiDAR sensor streams,
    health classifications, temporal trends, cross-modal consistency, and smoothed weights.
    """
    def __init__(self, camera_max_range=45.0, nominal_lidar_points=2500,
                 health_thresholds=None, smoothing_alpha=0.65):
        self.camera_max_range = float(camera_max_range)
        self.nominal_lidar_points = float(nominal_lidar_points)
        self.smoothing_alpha = float(smoothing_alpha)

        # Configurable health state thresholds
        if health_thresholds is None:
            self.th_healthy = 0.70
            self.th_degraded = 0.40
            self.th_severely_degraded = 0.15
        else:
            self.th_healthy = float(health_thresholds.get("healthy", 0.70))
            self.th_degraded = float(health_thresholds.get("degraded", 0.40))
            self.th_severely_degraded = float(health_thresholds.get("severely_degraded", 0.15))

    def classify_health(self, reliability: float) -> str:
        """Classifies sensor operational health state from reliability metric."""
        r = float(reliability)
        if r >= self.th_healthy:
            return SensorHealthState.HEALTHY
        elif r >= self.th_degraded:
            return SensorHealthState.DEGRADED
        elif r >= self.th_severely_degraded:
            return SensorHealthState.SEVERELY_DEGRADED
        else:
            return SensorHealthState.FAILED

    def compute_trend(self, r_current: float, r_previous: float, dt: float = 0.05) -> tuple:
        """
        Computes the time-derivative of reliability (Delta R / Delta t)
        and categorizes the trend.
        """
        if dt <= 0.0:
            dt = 0.05
        derivative = (float(r_current) - float(r_previous)) / dt
        if derivative < -0.40:
            trend = ReliabilityTrend.RAPIDLY_DEGRADING
        elif derivative < -0.05:
            trend = ReliabilityTrend.DEGRADING
        elif derivative > 0.05:
            trend = ReliabilityTrend.IMPROVING
        else:
            trend = ReliabilityTrend.STABLE
        return derivative, trend

    def smooth_weights(self, w_cam_raw: float, w_lidar_raw: float,
                       w_cam_prev: float = None, w_lidar_prev: float = None) -> tuple:
        """
        Applies exponential hysteresis smoothing to sensor weights to prevent
        erratic frame-to-frame oscillations while preserving response to genuine failure.
        Enforces w_cam + w_lidar = 1.0.
        """
        if w_cam_prev is None or w_lidar_prev is None:
            denom = w_cam_raw + w_lidar_raw + 1e-6
            return w_cam_raw / denom, w_lidar_raw / denom

        alpha = self.smoothing_alpha
        w_cam_s = alpha * w_cam_raw + (1.0 - alpha) * w_cam_prev
        w_lidar_s = alpha * w_lidar_raw + (1.0 - alpha) * w_lidar_prev

        denom = w_cam_s + w_lidar_s + 1e-6
        return float(w_cam_s / denom), float(w_lidar_s / denom)

    def compute_cross_modal_consistency(self, cam_det, lidar_cluster, compensator) -> float:
        """
        Calculates cross-modal spatial agreement:
        Projects 3D LiDAR cluster bounding box to 2D image plane and calculates IoU
        against 2D camera detection.
        Returns consistency score in [0.0, 1.0].
        """
        if cam_det is None or lidar_cluster is None or compensator is None:
            return 0.0

        corners_3d = lidar_cluster.get_bounding_corners()
        uvs, depths = compensator.project_lidar_to_camera(corners_3d)
        if len(uvs) < 4:
            return 0.0

        u_min, v_min = np.min(uvs[:, 0]), np.min(uvs[:, 1])
        u_max, v_max = np.max(uvs[:, 0]), np.max(uvs[:, 1])
        lidar_2d_box = [u_min, v_min, u_max, v_max]

        iou = compute_2d_iou(cam_det.bbox, lidar_2d_box)
        return float(np.clip(iou, 0.0, 1.0))

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
