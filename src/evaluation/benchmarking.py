"""
src/evaluation/benchmarking.py
Comprehensive benchmark execution harness for multimodal sensor fusion.

Coordinates:
- Iteration over environmental degradation conditions.
- Running all 7 fusion methods.
- Logging dynamic sensor weights and telemetry.
- Tabulating aggregate comparative metrics.
"""

import time
import numpy as np
import pandas as pd
from .metrics import evaluate_detection_performance
from .degradation import (
    apply_camera_motion_blur,
    apply_camera_illumination_degrade,
    apply_camera_outage,
    apply_lidar_dropout,
    apply_lidar_noise
)

class FusionBenchmarkHarness:
    """
    Executes standardized benchmarks comparing all 7 perception paradigms
    under controlled environmental degradation scenarios.
    """
    CONDITIONS = [
        "Clean_Nominal",
        "Camera_Degraded",
        "LiDAR_Degraded",
        "Both_Degraded",
        "Camera_Outage"
    ]

    METHODS = [
        "Camera-Only",
        "LiDAR-Only",
        "Late Fusion (Fixed)",
        "Dempster-Shafer",
        "Distance-Adaptive",
        "Temporal Fusion",
        "Proposed Adaptive Fusion"
    ]

    def __init__(self, cam_detector, lid_detector, compensator, fusion_engine, tracker):
        self.cam_detector = cam_detector
        self.lid_detector = lid_detector
        self.compensator = compensator
        self.fusion_engine = fusion_engine
        self.tracker = tracker

    def run_benchmark(self, frames, spatial_associate_fn):
        """
        Runs the full benchmark suite across all frames and conditions.
        Returns:
        - benchmark_df: DataFrame with Precision, Recall, F1, Loc Error, Confidence, Latency, FPS.
        - weights_df: DataFrame with dynamic sensor weights log.
        """
        benchmark_rows = []
        weights_log = []

        for cond in self.CONDITIONS:
            self.tracker.reset()
            perf = {m: {"tp": 0, "fp": 0, "fn": 0, "loc_errs": [], "confs": [], "latencies": []} for m in self.METHODS}

            for i, frame in enumerate(frames):
                if not (frame["has_camera"] and frame["has_lidar"]):
                    continue

                t_ego = frame["T_ego"]
                dt = frame["dt"]

                import cv2
                raw_img = cv2.imread(frame["camera_path"])
                pts_raw = self.compensator.load_point_cloud(frame["lidar_path"])

                clean_clusters, _ = self.lid_detector.detect(pts_raw)
                gt_targets = [c.centroid for c in clean_clusters if c.radial_distance < 35.0]

                img_in = raw_img.copy() if raw_img is not None else None
                pts_in = pts_raw.copy()

                if cond == "Camera_Degraded":
                    img_in = apply_camera_motion_blur(img_in, kernel_size=19, angle_deg=30.0)
                    img_in = apply_camera_illumination_degrade(img_in, factor=0.15)
                elif cond == "LiDAR_Degraded":
                    pts_in = apply_lidar_dropout(pts_in, drop_ratio=0.85, random_seed=i)
                    pts_in = apply_lidar_noise(pts_in, noise_std=0.4, num_spray=200, random_seed=i)
                elif cond == "Both_Degraded":
                    img_in = apply_camera_motion_blur(img_in, kernel_size=15, angle_deg=20.0)
                    img_in = apply_camera_illumination_degrade(img_in, factor=0.25)
                    pts_in = apply_lidar_dropout(pts_in, drop_ratio=0.75, random_seed=i)
                elif cond == "Camera_Outage":
                    img_in = apply_camera_outage(img_in)

                t0 = time.perf_counter()
                cam_dets, img_qual = self.cam_detector.detect(img_in)
                lid_clusters, total_pts = self.lid_detector.detect(pts_in)
                matched, un_cam, un_lid = spatial_associate_fn(cam_dets, lid_clusters, self.compensator)
                t_det = time.perf_counter() - t0

                # 1. Camera-Only
                t_m0 = time.perf_counter()
                out_cam = self.fusion_engine.fuse_camera_only(matched, un_cam)
                perf["Camera-Only"]["latencies"].append(t_det + (time.perf_counter() - t_m0))

                # 2. LiDAR-Only
                t_m0 = time.perf_counter()
                out_lid = self.fusion_engine.fuse_lidar_only(matched, un_lid)
                perf["LiDAR-Only"]["latencies"].append(t_det + (time.perf_counter() - t_m0))

                # 3. Late Fixed
                t_m0 = time.perf_counter()
                out_late = self.fusion_engine.fuse_late_fixed(matched, un_cam, un_lid)
                perf["Late Fusion (Fixed)"]["latencies"].append(t_det + (time.perf_counter() - t_m0))

                # 4. Dempster-Shafer
                t_m0 = time.perf_counter()
                out_ds = self.fusion_engine.fuse_dempster_shafer(matched, un_cam, un_lid, img_qual, total_pts)
                perf["Dempster-Shafer"]["latencies"].append(t_det + (time.perf_counter() - t_m0))

                # 5. Distance-Adaptive
                t_m0 = time.perf_counter()
                out_dist = self.fusion_engine.fuse_distance_adaptive(matched, un_cam, un_lid)
                perf["Distance-Adaptive"]["latencies"].append(t_det + (time.perf_counter() - t_m0))

                # 6. Temporal Fusion
                t_m0 = time.perf_counter()
                dets_for_track = [{"position": d.position, "confidence": d.confidence, "class_name": d.class_name} for d in out_late]
                confirmed_tracks = self.tracker.step(dets_for_track, T_ego=t_ego, dt=dt)
                out_temp = [
                    type("Obj", (), {
                        "position": trk.position,
                        "confidence": trk.confidence,
                        "class_name": trk.class_name,
                        "distance": float(np.linalg.norm(trk.position[:2]))
                    })() for trk in confirmed_tracks
                ]
                perf["Temporal Fusion"]["latencies"].append(t_det + (time.perf_counter() - t_m0))

                # 7. Proposed Reliability-Aware Adaptive Fusion
                t_m0 = time.perf_counter()
                out_prop = self.fusion_engine.fuse_reliability_adaptive(
                    matched, un_cam, un_lid,
                    image_quality=img_qual,
                    total_cloud_points=total_pts,
                    imu_state=frame,
                    temporal_tracks=confirmed_tracks
                )
                perf["Proposed Adaptive Fusion"]["latencies"].append(t_det + (time.perf_counter() - t_m0))

                if out_prop:
                    weights_log.append({
                        "condition": cond,
                        "frame_idx": i,
                        "w_cam": float(np.mean([d.w_cam for d in out_prop])),
                        "w_lidar": float(np.mean([d.w_lidar for d in out_prop])),
                        "r_cam": float(np.mean([d.r_cam for d in out_prop])),
                        "r_lidar": float(np.mean([d.r_lidar for d in out_prop]))
                    })

                methods_outputs = {
                    "Camera-Only": out_cam,
                    "LiDAR-Only": out_lid,
                    "Late Fusion (Fixed)": out_late,
                    "Dempster-Shafer": out_ds,
                    "Distance-Adaptive": out_dist,
                    "Temporal Fusion": out_temp,
                    "Proposed Adaptive Fusion": out_prop
                }

                for m_name, preds in methods_outputs.items():
                    evaluate_detection_performance(preds, gt_targets, perf[m_name], match_dist=3.0)

            for m_name in self.METHODS:
                p_data = perf[m_name]
                tp = p_data["tp"]
                fp = p_data["fp"]
                fn = p_data["fn"]

                precision = tp / max(1, tp + fp)
                recall = tp / max(1, tp + fn)
                f1 = 2.0 * precision * recall / max(1e-4, precision + recall)
                mean_loc_err = float(np.mean(p_data["loc_errs"])) if p_data["loc_errs"] else 0.0
                mean_conf = float(np.mean(p_data["confs"])) if p_data["confs"] else 0.0
                mean_lat = float(np.mean(p_data["latencies"])) * 1000.0
                fps = 1000.0 / max(0.1, mean_lat)

                benchmark_rows.append({
                    "condition": cond,
                    "method": m_name,
                    "precision": round(precision, 4),
                    "recall": round(recall, 4),
                    "f1_score": round(f1, 4),
                    "localization_error_m": round(mean_loc_err, 4),
                    "confidence": round(mean_conf, 4),
                    "latency_ms": round(mean_lat, 2),
                    "fps": round(fps, 1)
                })

        return pd.DataFrame(benchmark_rows), pd.DataFrame(weights_log)
