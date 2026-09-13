"""
src/evaluation/benchmarking.py
Comprehensive benchmark execution harness for multimodal sensor fusion.

Coordinates:
- Iteration over 8 controlled environmental degradation conditions.
- Running all 7 perception paradigms under strictly identical, synchronized feeds.
- Evaluation against authoritative Ground Truth (independent of sensor detections).
- Detailed diagnostic logging (weights, reliabilities, contributions, modes).
- Tabulating standardized comparative metrics across all conditions.
"""

import time
import cv2
import numpy as np
import pandas as pd
from .metrics import (
    evaluate_3d_frame,
    evaluate_2d_frame,
    compute_trajectory_jitter,
    compute_aggregate_metrics
)
from .degradation import (
    apply_camera_motion_blur,
    apply_camera_illumination_degrade,
    apply_camera_fog_glare,
    apply_camera_outage,
    apply_lidar_dropout,
    apply_lidar_noise,
    apply_lidar_outage
)
from ..fusion.spatial_association import associate_camera_and_lidar
from ..fusion.adaptive_fusion import FusedDetection
from ..fusion.temporal_tracker import TemporalTracker

class FusionBenchmarkHarness:
    """
    Executes standardized benchmarks comparing all 7 perception paradigms
    under controlled environmental degradation scenarios.
    """
    CONDITIONS = [
        "Clean_Nominal",
        "Camera_Degraded",
        "LiDAR_Degraded",
        "Camera_Outage",
        "Both_Degraded",
        "Severe_Camera_Degraded",
        "Severe_LiDAR_Degraded",
        "Combined_Severe_Degraded"
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
        self.temp_fusion_tracker = TemporalTracker(
            max_age=3, min_hits=2, dist_threshold=2.5, use_imu_compensation=True
        )

    def apply_condition_degradation(self, raw_img, pts_raw, condition, frame_idx):
        """Applies controlled physical degradation according to benchmark protocol."""
        img_in = raw_img.copy() if raw_img is not None else None
        pts_in = pts_raw.copy() if pts_raw is not None else np.empty((0, 3), dtype=np.float64)

        if condition == "Clean_Nominal":
            pass
        elif condition == "Camera_Degraded":
            img_in = apply_camera_motion_blur(img_in, kernel_size=19, angle_deg=30.0)
            img_in = apply_camera_illumination_degrade(img_in, factor=0.15)
        elif condition == "LiDAR_Degraded":
            pts_in = apply_lidar_dropout(pts_in, drop_ratio=0.85, random_seed=frame_idx)
            pts_in = apply_lidar_noise(pts_in, noise_std=0.40, num_spray=200, random_seed=frame_idx)
        elif condition == "Camera_Outage":
            img_in = apply_camera_outage(img_in)
        elif condition == "Both_Degraded":
            img_in = apply_camera_motion_blur(img_in, kernel_size=15, angle_deg=20.0)
            img_in = apply_camera_illumination_degrade(img_in, factor=0.25)
            pts_in = apply_lidar_dropout(pts_in, drop_ratio=0.75, random_seed=frame_idx)
            pts_in = apply_lidar_noise(pts_in, noise_std=0.30, num_spray=150, random_seed=frame_idx)
        elif condition == "Severe_Camera_Degraded":
            img_in = apply_camera_motion_blur(img_in, kernel_size=31, angle_deg=45.0)
            img_in = apply_camera_illumination_degrade(img_in, factor=0.05)
        elif condition == "Severe_LiDAR_Degraded":
            pts_in = apply_lidar_dropout(pts_in, drop_ratio=0.95, random_seed=frame_idx)
            pts_in = apply_lidar_noise(pts_in, noise_std=0.70, num_spray=400, random_seed=frame_idx)
        elif condition == "Combined_Severe_Degraded":
            img_in = apply_camera_motion_blur(img_in, kernel_size=25, angle_deg=35.0)
            img_in = apply_camera_illumination_degrade(img_in, factor=0.08)
            pts_in = apply_lidar_dropout(pts_in, drop_ratio=0.90, random_seed=frame_idx)
            pts_in = apply_lidar_noise(pts_in, noise_std=0.60, num_spray=350, random_seed=frame_idx)

        return img_in, pts_in

    def run_benchmark(self, frames, spatial_associate_fn=None):
        """
        Runs the full standardized benchmark suite across all conditions and frames.
        Returns:
            benchmark_df: DataFrame of aggregate performance metrics.
            weights_df: DataFrame of dynamic sensor reliability and weight logs.
            diagnostic_df: Detailed frame-level diagnostic log for representative frames.
        """
        if spatial_associate_fn is None:
            spatial_associate_fn = associate_camera_and_lidar

        benchmark_rows = []
        weights_log = []
        diagnostic_log = []

        calib = getattr(self.fusion_engine, "calibration", None)
        if calib is None:
            from ..dataset.base import Calibration
            calib = Calibration()

        total_conditions = len(self.CONDITIONS)
        total_frames = len(frames)

        for cond_idx, cond in enumerate(self.CONDITIONS):
            print(f"\n  [Stage 2 Benchmark] Condition {cond_idx + 1}/{total_conditions}: {cond} ({total_frames} frames)...")
            cond_t0 = time.perf_counter()
            self.tracker.reset()
            self.temp_fusion_tracker.reset()
            self.fusion_engine.reset_state()

            # Tracking telemetry per method for jitter calculation
            method_trajectories = {m: [] for m in self.METHODS}
            perf = {m: {
                "tp": 0, "fp": 0, "fn": 0,
                "loc_errs": [], "confs": [], "latencies": [],
                "frame_precisions": [], "frame_recalls": [], "frame_f1s": []
            } for m in self.METHODS}

            for i, frame in enumerate(frames):
                if (i + 1) % 10 == 0 or (i + 1) == total_frames:
                    pct = ((i + 1) / total_frames) * 100.0
                    elapsed = time.perf_counter() - cond_t0
                    print(f"    -> [Stage 2 Benchmark | Cond {cond_idx + 1}/{total_conditions}: {cond}] Frame {i + 1}/{total_frames} ({pct:.1f}%) | 7 Methods | Elapsed: {elapsed:.1f}s")
                # Retrieve raw data
                if hasattr(frame, "get_camera_image"):
                    raw_img = frame.get_camera_image()
                    pts_raw = frame.get_lidar_points()
                    t_ego = frame.T_ego
                    dt = frame.dt
                    imu_data = frame.imu_data
                    gt_positions_3d = frame.ground_truth.get_positions_3d(max_distance=45.0)
                    gt_boxes_2d = frame.ground_truth.get_boxes_2d()
                else:
                    raw_img = cv2.imread(frame["camera_path"])
                    pts_raw = self.compensator.load_point_cloud(frame["lidar_path"])
                    t_ego = frame["T_ego"]
                    dt = frame["dt"]
                    imu_data = frame
                    gt_positions_3d = frame.get("gt_positions_3d", [])
                    gt_boxes_2d = frame.get("gt_boxes_2d", [])

                # Apply environmental degradation
                img_in, pts_in = self.apply_condition_degradation(raw_img, pts_raw, cond, frame_idx=i)

                # Perception timings
                t0 = time.perf_counter()
                cam_dets, img_qual = self.cam_detector.detect(img_in)
                lid_clusters, total_pts = self.lid_detector.detect(pts_in)
                matched, un_cam, un_lid = spatial_associate_fn(cam_dets, lid_clusters, self.compensator)
                t_det = time.perf_counter() - t0

                # -------------------------------------------------------------
                # 1. Camera-Only
                # -------------------------------------------------------------
                t_m = time.perf_counter()
                out_cam = self.fusion_engine.fuse_camera_only(cam_dets)
                perf["Camera-Only"]["latencies"].append(t_det + (time.perf_counter() - t_m))

                # -------------------------------------------------------------
                # 2. LiDAR-Only
                # -------------------------------------------------------------
                t_m = time.perf_counter()
                out_lid = self.fusion_engine.fuse_lidar_only(lid_clusters)
                perf["LiDAR-Only"]["latencies"].append(t_det + (time.perf_counter() - t_m))

                # -------------------------------------------------------------
                # 3. Late Fixed (50/50)
                # -------------------------------------------------------------
                t_m = time.perf_counter()
                out_late = self.fusion_engine.fuse_late_fixed(
                    matched, un_cam, un_lid, calibration=calib, w_cam=0.5, w_lidar=0.5
                )
                perf["Late Fusion (Fixed)"]["latencies"].append(t_det + (time.perf_counter() - t_m))

                # -------------------------------------------------------------
                # 4. Dempster-Shafer
                # -------------------------------------------------------------
                t_m = time.perf_counter()
                out_ds = self.fusion_engine.fuse_dempster_shafer(
                    matched, un_cam, un_lid, img_qual, total_pts, calibration=calib
                )
                perf["Dempster-Shafer"]["latencies"].append(t_det + (time.perf_counter() - t_m))

                # -------------------------------------------------------------
                # 5. Distance-Adaptive
                # -------------------------------------------------------------
                t_m = time.perf_counter()
                out_dist = self.fusion_engine.fuse_distance_adaptive(
                    matched, un_cam, un_lid, calibration=calib
                )
                perf["Distance-Adaptive"]["latencies"].append(t_det + (time.perf_counter() - t_m))

                # -------------------------------------------------------------
                # 6. Temporal Fusion
                # -------------------------------------------------------------
                t_m = time.perf_counter()
                dets_for_track = [{"position": d.position, "confidence": d.confidence, "class_name": d.class_name}
                                  for d in out_late if d.confidence >= 0.20]
                confirmed_tracks = self.temp_fusion_tracker.step(dets_for_track, T_ego=t_ego, dt=dt)
                out_temp = [
                    FusedDetection(
                        position=trk.position,
                        confidence=trk.confidence,
                        class_name=trk.class_name,
                        source_mode="temporal_fused"
                    ) for trk in confirmed_tracks
                ]
                perf["Temporal Fusion"]["latencies"].append(t_det + (time.perf_counter() - t_m))

                # -------------------------------------------------------------
                # 7. Proposed Reliability-Aware Adaptive Fusion
                # -------------------------------------------------------------
                t_m = time.perf_counter()
                # Run tracker with current multimodal detections
                curr_det_pos = []
                for m in matched:
                    curr_det_pos.append({"position": m["lidar_cluster"].centroid, "confidence": m["camera_det"].confidence})
                for l in un_lid:
                    curr_det_pos.append({"position": l.centroid, "confidence": l.geometric_score})

                active_tracks = self.tracker.step(curr_det_pos, T_ego=t_ego, dt=dt)
                out_prop = self.fusion_engine.fuse_reliability_adaptive(
                    matched, un_cam, un_lid,
                    image_quality=img_qual,
                    total_cloud_points=total_pts,
                    calibration=calib,
                    imu_state=imu_data,
                    temporal_tracks=active_tracks,
                    compensator=self.compensator,
                    dt=dt
                )
                perf["Proposed Adaptive Fusion"]["latencies"].append(t_det + (time.perf_counter() - t_m))

                # Logging dynamic weights
                if out_prop:
                    w_c_mean = float(np.mean([d.w_cam for d in out_prop]))
                    w_l_mean = float(np.mean([d.w_lidar for d in out_prop]))
                    r_c_mean = float(np.mean([d.r_cam for d in out_prop]))
                    r_l_mean = float(np.mean([d.r_lidar for d in out_prop]))
                    weights_log.append({
                        "condition": cond,
                        "frame_idx": i,
                        "w_cam": round(w_c_mean, 4),
                        "w_lidar": round(w_l_mean, 4),
                        "r_cam": round(r_c_mean, 4),
                        "r_lidar": round(r_l_mean, 4)
                    })

                # Diagnostic log on key frames
                if i % 10 == 0:
                    for m_name, preds in [
                        ("Camera-Only", out_cam),
                        ("LiDAR-Only", out_lid),
                        ("Late Fusion (Fixed)", out_late),
                        ("Dempster-Shafer", out_ds),
                        ("Distance-Adaptive", out_dist),
                        ("Temporal Fusion", out_temp),
                        ("Proposed Adaptive Fusion", out_prop)
                    ]:
                        for p_idx, p in enumerate(preds[:3]):  # up to 3 objects per frame
                            diagnostic_log.append({
                                "condition": cond,
                                "frame_idx": i,
                                "method": m_name,
                                "pred_id": p_idx,
                                "w_cam": getattr(p, "w_cam", 0.0),
                                "w_lidar": getattr(p, "w_lidar", 0.0),
                                "r_cam": getattr(p, "r_cam", 0.0),
                                "r_lidar": getattr(p, "r_lidar", 0.0),
                                "confidence": getattr(p, "confidence", 0.0),
                                "source_mode": getattr(p, "source_mode", "det"),
                                "pos_x": p.position[0] if hasattr(p, "position") else None,
                                "pos_y": p.position[1] if hasattr(p, "position") else None,
                                "pos_z": p.position[2] if hasattr(p, "position") else None
                            })

                # -------------------------------------------------------------
                # Evaluation of each method against authoritative Ground Truth
                # -------------------------------------------------------------
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
                    if m_name == "Camera-Only":
                        # Camera-Only 2D evaluation track
                        tp, fp, fn, _, confs = evaluate_2d_frame(preds, gt_boxes_2d, iou_threshold=0.50, conf_threshold=0.25)
                        perf[m_name]["tp"] += tp
                        perf[m_name]["fp"] += fp
                        perf[m_name]["fn"] += fn
                        perf[m_name]["confs"].extend(confs)
                    else:
                        # 3D evaluation track against authoritative 3D positions
                        tp, fp, fn, errs, confs = evaluate_3d_frame(preds, gt_positions_3d, dist_threshold=2.5, conf_threshold=0.25)
                        perf[m_name]["tp"] += tp
                        perf[m_name]["fp"] += fp
                        perf[m_name]["fn"] += fn
                        perf[m_name]["loc_errs"].extend(errs)
                        perf[m_name]["confs"].extend(confs)

                        # Record positions for jitter tracking
                        if preds:
                            method_trajectories[m_name].append(preds[0].position)

                    f_prec = tp / max(1, tp + fp) if (tp + fp) > 0 else 0.0
                    f_rec = tp / max(1, tp + fn) if (tp + fn) > 0 else 0.0
                    f_f1 = 2 * f_prec * f_rec / max(1e-4, f_prec + f_rec)
                    perf[m_name]["frame_precisions"].append(f_prec)
                    perf[m_name]["frame_recalls"].append(f_rec)
                    perf[m_name]["frame_f1s"].append(f_f1)

            # Aggregate metrics for condition
            for m_name in self.METHODS:
                p_data = perf[m_name]
                tp = p_data["tp"]
                fp = p_data["fp"]
                fn = p_data["fn"]

                precision = tp / max(1, tp + fp) if (tp + fp) > 0 else 0.0
                recall = tp / max(1, tp + fn) if (tp + fn) > 0 else 0.0
                f1 = 2.0 * precision * recall / max(1e-4, precision + recall)

                prec_std = float(np.std(p_data["frame_precisions"])) if p_data["frame_precisions"] else 0.0
                rec_std = float(np.std(p_data["frame_recalls"])) if p_data["frame_recalls"] else 0.0
                f1_std = float(np.std(p_data["frame_f1s"])) if p_data["frame_f1s"] else 0.0

                if m_name == "Camera-Only":
                    mean_loc_err = None
                    jitter = None
                else:
                    mean_loc_err = float(np.mean(p_data["loc_errs"])) if p_data["loc_errs"] else 0.0
                    jitter = compute_trajectory_jitter(method_trajectories[m_name])

                mean_conf = float(np.mean(p_data["confs"])) if p_data["confs"] else 0.0
                mean_lat = float(np.mean(p_data["latencies"])) * 1000.0
                fps = 1000.0 / max(0.1, mean_lat)

                benchmark_rows.append({
                    "condition": cond,
                    "method": m_name,
                    "precision": round(precision, 4),
                    "precision_std": round(prec_std, 4),
                    "recall": round(recall, 4),
                    "recall_std": round(rec_std, 4),
                    "f1_score": round(f1, 4),
                    "f1_std": round(f1_std, 4),
                    "localization_error_m": round(mean_loc_err, 4) if mean_loc_err is not None else None,
                    "jitter_m": round(jitter, 4) if jitter is not None else None,
                    "confidence": round(mean_conf, 4),
                    "latency_ms": round(mean_lat, 2),
                    "fps": round(fps, 1),
                    "tp": tp,
                    "fp": fp,
                    "fn": fn
                })

            cond_elapsed = time.perf_counter() - cond_t0
            prop_f1 = benchmark_rows[-1]["f1_score"] if benchmark_rows else 0.0
            print(f"    ✓ Completed condition: {cond} in {cond_elapsed:.1f}s (Proposed F1: {prop_f1:.4f})")

        return pd.DataFrame(benchmark_rows), pd.DataFrame(weights_log), pd.DataFrame(diagnostic_log)
