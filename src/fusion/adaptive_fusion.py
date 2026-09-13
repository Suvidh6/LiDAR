"""
src/fusion/adaptive_fusion.py
Unified Multimodal Fusion Engine implementing adaptive weighting,
health states, reliability trends, and baseline comparators.

Paradigms implemented:
1. Camera-Only Baseline (monocular 2D, strictly independent of LiDAR)
2. LiDAR-Only Baseline (3D point cloud, strictly independent of camera)
3. Late Fusion (Fixed 50/50 weights)
4. Dempster-Shafer Evidential Fusion
5. Distance-Adaptive Fusion
6. Temporal Multi-Frame Fusion (Kalman filter with IMU ego-motion compensation)
7. Reliability-Aware Adaptive Fusion (Proposed framework)
"""

import numpy as np
from .reliability_estimation import ReliabilityEstimator, SensorHealthState, ReliabilityTrend
from ..dataset.base import Calibration

class FusedDetection:
    """Represents a fused perception object output with full diagnostic metadata."""
    def __init__(self, position, confidence, class_name,
                 r_cam=0.0, r_lidar=0.0, w_cam=0.0, w_lidar=0.0,
                 source_mode="fused", bbox_2d=None, bbox_3d=None,
                 cam_health=None, lidar_health=None,
                 cam_trend=None, lidar_trend=None, consistency=1.0):
        self.position = np.asarray(position, dtype=np.float64)  # [x, y, z] in LiDAR/vehicle frame
        self.confidence = float(np.clip(confidence, 0.01, 0.99))
        self.class_name = str(class_name)
        self.r_cam = float(r_cam)
        self.r_lidar = float(r_lidar)
        self.w_cam = float(w_cam)
        self.w_lidar = float(w_lidar)
        self.source_mode = str(source_mode)
        self.bbox_2d = bbox_2d
        self.bbox_3d = bbox_3d
        self.distance = float(np.linalg.norm(self.position[:2]))
        self.cam_health = cam_health or SensorHealthState.HEALTHY
        self.lidar_health = lidar_health or SensorHealthState.HEALTHY
        self.cam_trend = cam_trend or ReliabilityTrend.STABLE
        self.lidar_trend = lidar_trend or ReliabilityTrend.STABLE
        self.consistency = float(consistency)

    def to_dict(self):
        return {
            "position": [round(float(p), 3) for p in self.position],
            "distance": round(self.distance, 3),
            "confidence": round(self.confidence, 4),
            "class_name": self.class_name,
            "r_cam": round(self.r_cam, 4),
            "r_lidar": round(self.r_lidar, 4),
            "w_cam": round(self.w_cam, 4),
            "w_lidar": round(self.w_lidar, 4),
            "source_mode": self.source_mode,
            "cam_health": self.cam_health,
            "lidar_health": self.lidar_health,
            "cam_trend": self.cam_trend,
            "lidar_trend": self.lidar_trend,
            "consistency": round(self.consistency, 3)
        }

class AdaptiveFusionEngine:
    """
    Multimodal fusion engine supporting dynamic reliability weighting,
    hysteresis smoothing, health state transitions, and benchmark baselines.
    """
    def __init__(self, camera_max_range=45.0, nominal_lidar_points=2500,
                 smoothing_alpha=0.65, health_thresholds=None, calibration=None):
        self.estimator = ReliabilityEstimator(
            camera_max_range=camera_max_range,
            nominal_lidar_points=nominal_lidar_points,
            health_thresholds=health_thresholds,
            smoothing_alpha=smoothing_alpha
        )
        self.calibration = calibration or Calibration()
        self.prev_w_cam = 0.5
        self.prev_w_lidar = 0.5
        self.prev_r_cam = 0.8
        self.prev_r_lidar = 0.8

    def reset_state(self):
        """Resets temporal smoothing states."""
        self.prev_w_cam = 0.5
        self.prev_w_lidar = 0.5
        self.prev_r_cam = 0.8
        self.prev_r_lidar = 0.8

    def estimate_camera_reliability(self, *args, **kwargs):
        return self.estimator.estimate_camera_reliability(*args, **kwargs)

    def estimate_lidar_reliability(self, *args, **kwargs):
        return self.estimator.estimate_lidar_reliability(*args, **kwargs)

    # -------------------------------------------------------------
    # 1. CAMERA-ONLY BASELINE (Method 1)
    # -------------------------------------------------------------
    def fuse_camera_only(self, camera_dets):
        """
        Method 1: Camera-only perception baseline.
        Input: 2D detections from CameraDetector.detect().
        STRICT ISOLATION:
        - Does NOT access LiDAR point clouds.
        - Does NOT access LiDAR detections.
        - Does NOT access LiDAR-camera association.
        - Does NOT invent arbitrary pseudo-3D positions.
        Returns list of CameraDetection objects evaluated on 2D Ground Truth.
        """
        return list(camera_dets)

    # -------------------------------------------------------------
    # 2. LIDAR-ONLY BASELINE (Method 2)
    # -------------------------------------------------------------
    def fuse_lidar_only(self, lidar_clusters):
        """
        Method 2: LiDAR-only perception baseline.
        Input: 3D clusters from LiDARDetector.detect().
        STRICT ISOLATION:
        - Does NOT access Camera images.
        - Does NOT access Camera detections.
        Returns list of FusedDetection objects with 3D centroids.
        """
        fused = []
        for lid in lidar_clusters:
            fused.append(FusedDetection(
                position=lid.centroid,
                confidence=lid.geometric_score,
                class_name="vehicle",
                r_cam=0.0,
                r_lidar=lid.geometric_score,
                w_cam=0.0,
                w_lidar=1.0,
                source_mode="lidar_only",
                bbox_3d=lid.min_bound.tolist() + lid.max_bound.tolist()
            ))
        return fused

    # -------------------------------------------------------------
    # 3. LATE FIXED 50/50 FUSION (Method 3)
    # -------------------------------------------------------------
    def fuse_late_fixed(self, matched_pairs, unmatched_cam, unmatched_lid,
                        calibration=None, w_cam=0.5, w_lidar=0.5):
        """
        Method 3: Late decision fusion with fixed static weights (50/50).
        Blends camera bearing back-projection and LiDAR centroid for matched pairs.
        """
        calib = calibration or self.calibration
        fused = []
        for m in matched_pairs:
            cam = m["camera_det"]
            lid = m["lidar_cluster"]
            u, v = cam.centroid_2d
            depth = max(1.0, lid.radial_distance)
            p_cam_ray = calib.camera_ray_to_3d(u, v, depth)

            pos_fused = w_cam * p_cam_ray + w_lidar * lid.centroid
            conf = w_cam * cam.confidence + w_lidar * lid.geometric_score

            fused.append(FusedDetection(
                position=pos_fused,
                confidence=conf,
                class_name=cam.class_name,
                r_cam=cam.confidence,
                r_lidar=lid.geometric_score,
                w_cam=w_cam,
                w_lidar=w_lidar,
                source_mode="late_fixed",
                bbox_2d=cam.bbox,
                bbox_3d=lid.min_bound.tolist() + lid.max_bound.tolist()
            ))

        for lid in unmatched_lid:
            fused.append(FusedDetection(
                position=lid.centroid,
                confidence=lid.geometric_score * w_lidar,
                class_name="vehicle",
                r_cam=0.0,
                r_lidar=lid.geometric_score,
                w_cam=0.0,
                w_lidar=w_lidar,
                source_mode="late_fixed_lidar",
                bbox_3d=lid.min_bound.tolist() + lid.max_bound.tolist()
            ))
        return fused

    # -------------------------------------------------------------
    # 4. DEMPSTER-SHAFER EVIDENTIAL FUSION (Method 4)
    # -------------------------------------------------------------
    def fuse_dempster_shafer(self, matched_pairs, unmatched_cam, unmatched_lid,
                             image_quality, total_cloud_points, calibration=None):
        """
        Method 4: Dempster-Shafer evidential fusion.
        Constructs belief masses for object hypothesis and uncertainty theta,
        combines via Dempster's rule, and allocates weights proportionally to evidence.
        """
        calib = calibration or self.calibration
        fused = []
        for m in matched_pairs:
            cam = m["camera_det"]
            lid = m["lidar_cluster"]
            d = max(1.0, lid.radial_distance)

            m_cam_obj = self.estimate_camera_reliability(cam, image_quality, d)
            m_cam_theta = 1.0 - m_cam_obj

            m_lid_obj = self.estimate_lidar_reliability(lid, total_cloud_points, d)
            m_lid_theta = 1.0 - m_lid_obj

            m_fused_obj = (m_cam_obj * m_lid_obj +
                           m_cam_obj * m_lid_theta +
                           m_cam_theta * m_lid_obj)

            denom = m_cam_obj + m_lid_obj + 1e-6
            w_c = m_cam_obj / denom
            w_l = m_lid_obj / denom

            u, v = cam.centroid_2d
            p_cam_ray = calib.camera_ray_to_3d(u, v, d)
            pos_fused = w_c * p_cam_ray + w_l * lid.centroid

            fused.append(FusedDetection(
                position=pos_fused,
                confidence=m_fused_obj,
                class_name=cam.class_name,
                r_cam=m_cam_obj,
                r_lidar=m_lid_obj,
                w_cam=w_c,
                w_lidar=w_l,
                source_mode="dempster_shafer",
                bbox_2d=cam.bbox,
                bbox_3d=lid.min_bound.tolist() + lid.max_bound.tolist()
            ))

        for lid in unmatched_lid:
            m_lid = self.estimate_lidar_reliability(lid, total_cloud_points, lid.radial_distance)
            fused.append(FusedDetection(
                position=lid.centroid,
                confidence=m_lid * 0.80,
                class_name="vehicle",
                r_cam=0.0,
                r_lidar=m_lid,
                w_cam=0.0,
                w_lidar=1.0,
                source_mode="ds_lidar",
                bbox_3d=lid.min_bound.tolist() + lid.max_bound.tolist()
            ))
        return fused

    # -------------------------------------------------------------
    # 5. DISTANCE-ADAPTIVE FUSION (Method 5)
    # -------------------------------------------------------------
    def fuse_distance_adaptive(self, matched_pairs, unmatched_cam, unmatched_lid, calibration=None):
        """
        Method 5: Distance-adaptive heuristic fusion.
        Shifts weight from camera to LiDAR purely as a function of radial distance d.
        Blind to noise, fog, blur, or sensor dropouts.
        """
        calib = calibration or self.calibration
        fused = []
        for m in matched_pairs:
            cam = m["camera_det"]
            lid = m["lidar_cluster"]
            d = max(1.0, lid.radial_distance)

            # Heuristic distance curve: camera favored at short range, lidar favored at long range
            w_cam = float(np.clip(1.0 / (1.0 + (d / 18.0)**1.5), 0.10, 0.90))
            w_lid = 1.0 - w_cam

            u, v = cam.centroid_2d
            p_cam_ray = calib.camera_ray_to_3d(u, v, d)
            pos_fused = w_cam * p_cam_ray + w_lid * lid.centroid
            conf = w_cam * cam.confidence + w_lid * lid.geometric_score

            fused.append(FusedDetection(
                position=pos_fused,
                confidence=conf,
                class_name=cam.class_name,
                r_cam=cam.confidence,
                r_lidar=lid.geometric_score,
                w_cam=w_cam,
                w_lidar=w_lid,
                source_mode="distance_adaptive",
                bbox_2d=cam.bbox,
                bbox_3d=lid.min_bound.tolist() + lid.max_bound.tolist()
            ))

        for lid in unmatched_lid:
            d = max(1.0, lid.radial_distance)
            w_lid = float(np.clip(1.0 - 1.0 / (1.0 + (d / 18.0)**1.5), 0.10, 0.90))
            fused.append(FusedDetection(
                position=lid.centroid,
                confidence=lid.geometric_score * w_lid,
                class_name="vehicle",
                r_cam=0.0,
                r_lidar=lid.geometric_score,
                w_cam=0.0,
                w_lidar=w_lid,
                source_mode="dist_lidar",
                bbox_3d=lid.min_bound.tolist() + lid.max_bound.tolist()
            ))
        return fused

    # -------------------------------------------------------------
    # 7. PROPOSED RELIABILITY-AWARE ADAPTIVE SENSOR FUSION (Method 7)
    # -------------------------------------------------------------
    def fuse_reliability_adaptive(self, matched_pairs, unmatched_cam, unmatched_lid,
                                  image_quality, total_cloud_points, calibration=None,
                                  imu_state=None, temporal_tracks=None, compensator=None, dt=0.05):
        """
        Method 7: Proposed Reliability-Aware Adaptive Multimodal Perception.
        Integrates:
        - Multi-criteria physical reliability (R_cam and R_lidar)
        - Dynamic health state machine (HEALTHY, DEGRADED, SEVERELY_DEGRADED, FAILED)
        - Trend derivative classification (RAPIDLY_DEGRADING, DEGRADING, STABLE, IMPROVING)
        - Temporal hysteresis smoothing of sensor weights
        - Cross-modal spatial consistency evaluation
        - Camera bearing ray projection and adaptive position refinement
        - Calibrated confidence estimation
        - Failure fallback isolation
        """
        calib = calibration or self.calibration
        fused = []

        # 1. Matched Multimodal Detections
        for m in matched_pairs:
            cam = m["camera_det"]
            lid = m["lidar_cluster"]
            d = max(1.0, lid.radial_distance)

            # Query temporal track persistence if available
            persistence = 1.0
            if temporal_tracks:
                dists = [np.linalg.norm(trk.position - lid.centroid) for trk in temporal_tracks]
                if dists and min(dists) < 3.0:
                    best_trk = temporal_tracks[int(np.argmin(dists))]
                    persistence = best_trk.persistence_ratio

            r_cam = self.estimate_camera_reliability(
                cam, image_quality, d, imu_state=imu_state, persistence=persistence
            )
            r_lidar = self.estimate_lidar_reliability(
                lid, total_cloud_points, d, persistence=persistence
            )

            # Health classification
            cam_health = self.estimator.classify_health(r_cam)
            lidar_health = self.estimator.classify_health(r_lidar)

            # Trend derivatives
            _, cam_trend = self.estimator.compute_trend(r_cam, self.prev_r_cam, dt=dt)
            _, lidar_trend = self.estimator.compute_trend(r_lidar, self.prev_r_lidar, dt=dt)
            self.prev_r_cam = r_cam
            self.prev_r_lidar = r_lidar

            # Raw weight calculation with health-state isolation
            if cam_health == SensorHealthState.FAILED or cam_health == SensorHealthState.SEVERELY_DEGRADED:
                w_c_raw = 0.05
                w_l_raw = 0.95
            elif lidar_health == SensorHealthState.FAILED or lidar_health == SensorHealthState.SEVERELY_DEGRADED:
                w_c_raw = 0.95
                w_l_raw = 0.05
            else:
                denom = r_cam + r_lidar + 1e-6
                w_c_raw = r_cam / denom
                w_l_raw = r_lidar / denom

            # Temporal hysteresis smoothing
            w_cam, w_lidar = self.estimator.smooth_weights(
                w_c_raw, w_l_raw, self.prev_w_cam, self.prev_w_lidar
            )
            self.prev_w_cam = w_cam
            self.prev_w_lidar = w_lidar

            # Position fusion: Camera ray refinement
            u, v = cam.centroid_2d
            p_cam_ray = calib.camera_ray_to_3d(u, v, d)

            if cam_health == SensorHealthState.FAILED:
                pos_fused = lid.centroid.copy()
            elif lidar_health == SensorHealthState.FAILED:
                pos_fused = p_cam_ray.copy()
            else:
                pos_fused = w_cam * p_cam_ray + w_lidar * lid.centroid

            # Cross-modal consistency
            consistency = 1.0
            if compensator is not None:
                consistency = self.estimator.compute_cross_modal_consistency(cam, lid, compensator)

            # Calibrated fused confidence
            conf_fused = 1.0 - (1.0 - r_cam) * (1.0 - r_lidar)

            fused.append(FusedDetection(
                position=pos_fused,
                confidence=conf_fused,
                class_name=cam.class_name,
                r_cam=r_cam,
                r_lidar=r_lidar,
                w_cam=w_cam,
                w_lidar=w_lidar,
                source_mode="adaptive_fused",
                bbox_2d=cam.bbox,
                bbox_3d=lid.min_bound.tolist() + lid.max_bound.tolist(),
                cam_health=cam_health,
                lidar_health=lidar_health,
                cam_trend=cam_trend,
                lidar_trend=lidar_trend,
                consistency=consistency
            ))

        # 2. Unmatched LiDAR Clusters (Admit only if healthy)
        for lid in unmatched_lid:
            d = max(1.0, lid.radial_distance)
            r_lidar = self.estimate_lidar_reliability(
                lid, total_cloud_points, distance=d, persistence=0.5
            )
            lidar_health = self.estimator.classify_health(r_lidar)
            _, lidar_trend = self.estimator.compute_trend(r_lidar, self.prev_r_lidar, dt=dt)

            if r_lidar >= 0.15 and lidar_health != SensorHealthState.FAILED:
                fused.append(FusedDetection(
                    position=lid.centroid,
                    confidence=r_lidar,
                    class_name="vehicle",
                    r_cam=0.01,
                    r_lidar=r_lidar,
                    w_cam=0.0,
                    w_lidar=1.0,
                    source_mode="adaptive_lidar_fallback",
                    bbox_3d=lid.min_bound.tolist() + lid.max_bound.tolist(),
                    cam_health=SensorHealthState.FAILED,
                    lidar_health=lidar_health,
                    cam_trend=ReliabilityTrend.STABLE,
                    lidar_trend=lidar_trend,
                    consistency=0.5
                ))

        return fused
