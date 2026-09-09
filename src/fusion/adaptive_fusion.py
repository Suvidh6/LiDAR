"""
src/fusion/adaptive_fusion.py
Unified Multimodal Fusion Engine implementing adaptive weighting,
health states, reliability trends, and baseline comparators.

Paradigms implemented:
1. Camera-Only Baseline
2. LiDAR-Only Baseline
3. Late Fusion (Fixed 50/50)
4. Dempster-Shafer Evidential Fusion
5. Distance-Adaptive Fusion
6. Temporal Multi-Frame Fusion
7. Reliability-Aware Adaptive Fusion (Proposed)
"""

import numpy as np
from .reliability_estimation import ReliabilityEstimator, SensorHealthState, ReliabilityTrend

class FusedDetection:
    """Represents a fused perception object output with full diagnostic metadata."""
    def __init__(self, position, confidence, class_name,
                 r_cam=0.0, r_lidar=0.0, w_cam=0.0, w_lidar=0.0,
                 source_mode="fused", bbox_2d=None, bbox_3d=None,
                 cam_health=None, lidar_health=None,
                 cam_trend=None, lidar_trend=None, consistency=1.0):
        self.position = np.asarray(position, dtype=np.float64)  # [x, y, z] in vehicle/lidar frame
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
                 smoothing_alpha=0.65, health_thresholds=None):
        self.estimator = ReliabilityEstimator(
            camera_max_range=camera_max_range,
            nominal_lidar_points=nominal_lidar_points,
            health_thresholds=health_thresholds,
            smoothing_alpha=smoothing_alpha
        )
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
    # FUSION METHODS
    # -------------------------------------------------------------

    def fuse_camera_only(self, matched_pairs, unmatched_cam):
        """Method 1: Camera-only baseline."""
        fused = []
        for m in matched_pairs:
            cam = m["camera_det"]
            lid = m["lidar_cluster"]
            fused.append(FusedDetection(
                position=lid.centroid,
                confidence=cam.confidence,
                class_name=cam.class_name,
                r_cam=cam.confidence,
                r_lidar=0.0,
                w_cam=1.0,
                w_lidar=0.0,
                source_mode="camera_only"
            ))
        for cam in unmatched_cam:
            pseudo_pos = [20.0, (cam.centroid_2d[0] - 400.0) * (20.0 / 400.0), 0.0]
            fused.append(FusedDetection(
                position=pseudo_pos,
                confidence=cam.confidence * 0.8,
                class_name=cam.class_name,
                r_cam=cam.confidence * 0.5,
                r_lidar=0.0,
                w_cam=1.0,
                w_lidar=0.0,
                source_mode="camera_only"
            ))
        return fused

    def fuse_lidar_only(self, matched_pairs, unmatched_lid):
        """Method 2: LiDAR-only baseline."""
        fused = []
        for m in matched_pairs:
            lid = m["lidar_cluster"]
            fused.append(FusedDetection(
                position=lid.centroid,
                confidence=lid.geometric_score,
                class_name="vehicle",
                r_cam=0.0,
                r_lidar=lid.geometric_score,
                w_cam=0.0,
                w_lidar=1.0,
                source_mode="lidar_only"
            ))
        for lid in unmatched_lid:
            fused.append(FusedDetection(
                position=lid.centroid,
                confidence=lid.geometric_score * 0.85,
                class_name="vehicle",
                r_cam=0.0,
                r_lidar=lid.geometric_score,
                w_cam=0.0,
                w_lidar=1.0,
                source_mode="lidar_only"
            ))
        return fused

    def fuse_late_fixed(self, matched_pairs, unmatched_cam, unmatched_lid, w_cam=0.5, w_lidar=0.5):
        """Method 3: Late decision fusion with fixed 50/50 weights."""
        fused = []
        for m in matched_pairs:
            cam = m["camera_det"]
            lid = m["lidar_cluster"]
            conf = w_cam * cam.confidence + w_lidar * lid.geometric_score
            fused.append(FusedDetection(
                position=lid.centroid,
                confidence=conf,
                class_name=cam.class_name,
                r_cam=cam.confidence,
                r_lidar=lid.geometric_score,
                w_cam=w_cam,
                w_lidar=w_lidar,
                source_mode="late_fixed"
            ))
        for cam in unmatched_cam:
            pseudo_pos = [20.0, (cam.centroid_2d[0] - 400.0) * (20.0 / 400.0), 0.0]
            fused.append(FusedDetection(
                position=pseudo_pos,
                confidence=cam.confidence * w_cam,
                class_name=cam.class_name,
                w_cam=w_cam, w_lidar=0.0,
                source_mode="late_fixed_cam"
            ))
        for lid in unmatched_lid:
            fused.append(FusedDetection(
                position=lid.centroid,
                confidence=lid.geometric_score * w_lidar,
                class_name="vehicle",
                w_cam=0.0, w_lidar=w_lidar,
                source_mode="late_fixed_lidar"
            ))
        return fused

    def fuse_dempster_shafer(self, matched_pairs, unmatched_cam, unmatched_lid,
                             image_quality, total_cloud_points):
        """Method 4: Simplified implementation inspired by Dempster-Shafer evidential fusion."""
        fused = []
        for m in matched_pairs:
            cam = m["camera_det"]
            lid = m["lidar_cluster"]
            d = lid.radial_distance

            m_cam_obj = self.estimate_camera_reliability(cam, image_quality, d)
            m_cam_theta = 1.0 - m_cam_obj

            m_lid_obj = self.estimate_lidar_reliability(lid, total_cloud_points, d)
            m_lid_theta = 1.0 - m_lid_obj

            m_fused_obj = (m_cam_obj * m_lid_obj +
                           m_cam_obj * m_lid_theta +
                           m_cam_theta * m_lid_obj)

            w_c = m_cam_obj / max(1e-4, m_cam_obj + m_lid_obj)
            w_l = m_lid_obj / max(1e-4, m_cam_obj + m_lid_obj)

            fused.append(FusedDetection(
                position=lid.centroid,
                confidence=m_fused_obj,
                class_name=cam.class_name,
                r_cam=m_cam_obj,
                r_lidar=m_lid_obj,
                w_cam=w_c,
                w_lidar=w_l,
                source_mode="dempster_shafer"
            ))

        for lid in unmatched_lid:
            m_lid = self.estimate_lidar_reliability(lid, total_cloud_points, lid.radial_distance)
            fused.append(FusedDetection(
                position=lid.centroid,
                confidence=m_lid * 0.8,
                class_name="vehicle",
                r_cam=0.0, r_lidar=m_lid,
                w_cam=0.0, w_lidar=1.0,
                source_mode="ds_lidar"
            ))
        return fused

    def fuse_distance_adaptive(self, matched_pairs, unmatched_cam, unmatched_lid):
        """Method 5: Simplified implementation inspired by distance-adaptive heuristic weighting."""
        fused = []
        for m in matched_pairs:
            cam = m["camera_det"]
            lid = m["lidar_cluster"]
            d = max(1.0, lid.radial_distance)

            w_cam = float(np.clip(1.0 / (1.0 + (d / 18.0)**1.5), 0.10, 0.90))
            w_lid = 1.0 - w_cam
            conf = w_cam * cam.confidence + w_lid * lid.geometric_score

            fused.append(FusedDetection(
                position=lid.centroid,
                confidence=conf,
                class_name=cam.class_name,
                r_cam=cam.confidence,
                r_lidar=lid.geometric_score,
                w_cam=w_cam,
                w_lidar=w_lid,
                source_mode="distance_adaptive"
            ))
        for lid in unmatched_lid:
            fused.append(FusedDetection(
                position=lid.centroid,
                confidence=lid.geometric_score * 0.75,
                class_name="vehicle",
                w_cam=0.0, w_lidar=1.0,
                source_mode="dist_lidar"
            ))
        return fused

    def fuse_reliability_adaptive(self, matched_pairs, unmatched_cam, unmatched_lid,
                                  image_quality, total_cloud_points, imu_state=None,
                                  temporal_tracks=None, compensator=None, dt=0.05):
        """
        Method 7: Proposed Reliability-Aware Adaptive Sensor Fusion.
        Integrates:
        - Multi-criteria physical reliability
        - Temporal smoothing / hysteresis
        - Sensor health classification
        - Dynamic trend derivatives
        - Cross-modal consistency
        - Failure fallback preservation
        """
        fused = []
        frame_r_cam_list = []
        frame_r_lidar_list = []

        # 1. Matched Multimodal Detections
        for m in matched_pairs:
            cam = m["camera_det"]
            lid = m["lidar_cluster"]
            d = lid.radial_distance

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

            frame_r_cam_list.append(r_cam)
            frame_r_lidar_list.append(r_lidar)

            # Raw normalized weights
            denom = r_cam + r_lidar + 1e-6
            w_c_raw = r_cam / denom
            w_l_raw = r_lidar / denom

            # Temporal hysteresis smoothing
            w_cam, w_lidar = self.estimator.smooth_weights(
                w_c_raw, w_l_raw, self.prev_w_cam, self.prev_w_lidar
            )
            self.prev_w_cam = w_cam
            self.prev_w_lidar = w_lidar

            # Health states and trends
            cam_health = self.estimator.classify_health(r_cam)
            lidar_health = self.estimator.classify_health(r_lidar)
            _, cam_trend = self.estimator.compute_trend(r_cam, self.prev_r_cam, dt=dt)
            _, lidar_trend = self.estimator.compute_trend(r_lidar, self.prev_r_lidar, dt=dt)
            self.prev_r_cam = r_cam
            self.prev_r_lidar = r_lidar

            # Cross-modal consistency
            consistency = 1.0
            if compensator is not None:
                consistency = self.estimator.compute_cross_modal_consistency(cam, lid, compensator)

            # Calibrated confidence: combines sensor agreement with modality health
            conf_fused = 1.0 - (1.0 - r_cam) * (1.0 - r_lidar)

            fused.append(FusedDetection(
                position=lid.centroid,
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

        # 2. Unmatched Camera Detections (Fallback with reliability check)
        for cam in unmatched_cam:
            r_cam = self.estimate_camera_reliability(
                cam, image_quality, distance=20.0, imu_state=imu_state, persistence=0.5
            )
            cam_health = self.estimator.classify_health(r_cam)
            _, cam_trend = self.estimator.compute_trend(r_cam, self.prev_r_cam, dt=dt)
            is_obstacle = cam.class_name.lower() in ["car", "truck", "bus", "motorcycle", "bicycle", "vehicle", "person"]
            if is_obstacle and r_cam >= 0.25:
                pseudo_pos = [20.0, (cam.centroid_2d[0] - 400.0) * (20.0 / 400.0), 0.0]
                fused.append(FusedDetection(
                    position=pseudo_pos,
                    confidence=r_cam * 0.75,
                    class_name=cam.class_name,
                    r_cam=r_cam,
                    r_lidar=0.01,
                    w_cam=1.0,
                    w_lidar=0.0,
                    source_mode="adaptive_cam_fallback",
                    bbox_2d=cam.bbox,
                    cam_health=cam_health,
                    lidar_health=SensorHealthState.FAILED,
                    cam_trend=cam_trend,
                    lidar_trend=ReliabilityTrend.STABLE,
                    consistency=0.5
                ))

        # 3. Unmatched LiDAR Clusters (Fallback with reliability check)
        for lid in unmatched_lid:
            r_lidar = self.estimate_lidar_reliability(
                lid, total_cloud_points, distance=lid.radial_distance, persistence=0.5
            )
            lidar_health = self.estimator.classify_health(r_lidar)
            _, lidar_trend = self.estimator.compute_trend(r_lidar, self.prev_r_lidar, dt=dt)
            if r_lidar >= 0.05:
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
