"""
src/evaluation/ablation.py
Systematic Component Ablation Study for Multimodal Perception Framework.

Evaluates 7 distinct configurations:
- A0: Basic late decision fusion (fixed 50/50, no IMU warping, no tracking, no reliability)
- A1: A0 + IMU ego-motion compensation
- A2: A1 + Temporal multi-frame tracking (Kalman filter)
- A3: A2 + Multi-criteria sensor reliability estimation
- A4: A3 + Dynamic adaptive weight allocation
- A5: A4 + Temporal hysteresis smoothing and health-state isolation
- A6: Full Proposed Method (A5 + cross-modal consistency + trend derivative)
"""

import time
import numpy as np
import pandas as pd
from .metrics import evaluate_3d_frame, compute_trajectory_jitter
from ..fusion.spatial_association import associate_camera_and_lidar
from ..fusion.temporal_tracker import TemporalTracker
from ..fusion.adaptive_fusion import FusedDetection
from ..dataset.base import Calibration

class AblationStudyHarness:
    """
    Executes systematic ablation experiments demonstrating the individual
    contribution of each framework component.
    """
    VARIANTS = [
        ("A0_Basic_Fusion", "Basic late 50/50 fusion (no IMU, no tracking, no reliability)"),
        ("A1_Plus_IMU", "A0 + IMU ego-motion compensation"),
        ("A2_Plus_Temporal", "A1 + Temporal multi-frame Kalman tracking"),
        ("A3_Plus_Reliability", "A2 + Multi-criteria physical reliability estimation"),
        ("A4_Plus_Adaptive_Weights", "A3 + Dynamic adaptive weight allocation"),
        ("A5_Plus_Hysteresis_Health", "A4 + Weight hysteresis and health state machine"),
        ("A6_Full_Proposed", "Full proposed system (+ consistency & trend derivatives)")
    ]

    def __init__(self, cam_detector, lid_detector, compensator, fusion_engine):
        self.cam_detector = cam_detector
        self.lid_detector = lid_detector
        self.compensator = compensator
        self.fusion_engine = fusion_engine
        self.calibration = getattr(fusion_engine, "calibration", Calibration())

    def run_ablation(self, frames, conditions=None):
        """
        Runs the full ablation matrix across evaluated environmental conditions.
        Returns ablation_df.
        """
        if conditions is None:
            conditions = ["Clean_Nominal", "Camera_Degraded", "LiDAR_Degraded", "Both_Degraded"]

        from .benchmarking import FusionBenchmarkHarness
        harness = FusionBenchmarkHarness(
            self.cam_detector, self.lid_detector, self.compensator,
            self.fusion_engine, TemporalTracker()
        )

        ablation_rows = []
        total_variants = len(self.VARIANTS)
        total_conditions = len(conditions)
        total_frames = len(frames)

        for var_idx, (var_name, var_desc) in enumerate(self.VARIANTS):
            print(f"\n  [Stage 3 Ablation] Variant {var_idx + 1}/{total_variants}: {var_name}")
            print(f"    Description: {var_desc}")
            var_t0 = time.perf_counter()
            for c_idx, cond in enumerate(conditions):
                cond_t0 = time.perf_counter()
                print(f"    -> Condition {c_idx + 1}/{total_conditions}: {cond} ({total_frames} frames)...")
                tracker = TemporalTracker(use_imu_compensation=("Plus_IMU" in var_name or "A2" in var_name or "A3" in var_name or "A4" in var_name or "A5" in var_name or "A6" in var_name))
                tracker.reset()
                self.fusion_engine.reset_state()

                perf = {"tp": 0, "fp": 0, "fn": 0, "loc_errs": [], "confs": [], "latencies": [], "f1s": []}
                trajectories = []

                for i, frame in enumerate(frames):
                    if (i + 1) % 15 == 0 or (i + 1) == total_frames:
                        pct = ((i + 1) / total_frames) * 100.0
                        elapsed = time.perf_counter() - cond_t0
                        print(f"       [Stage 3 Ablation | Variant {var_idx + 1}/{total_variants}: {var_name} | Cond {c_idx + 1}/{total_conditions}: {cond}] Frame {i + 1}/{total_frames} ({pct:.1f}%) | Elapsed: {elapsed:.1f}s")
                    raw_img = frame.get_camera_image()
                    pts_raw = frame.get_lidar_points()
                    t_ego = frame.T_ego
                    dt = frame.dt
                    imu_data = frame.imu_data
                    gt_3d = frame.ground_truth.get_positions_3d(max_distance=45.0)

                    img_in, pts_in = harness.apply_condition_degradation(raw_img, pts_raw, cond, frame_idx=i)

                    t0 = time.perf_counter()
                    cam_dets, img_qual = self.cam_detector.detect(img_in)
                    lid_clusters, total_pts = self.lid_detector.detect(pts_in)
                    matched, un_cam, un_lid = associate_camera_and_lidar(cam_dets, lid_clusters, self.compensator)

                    # Execute variant pipeline
                    if var_name == "A0_Basic_Fusion":
                        # Fixed 50/50, no IMU, no tracking, no reliability
                        preds = self.fusion_engine.fuse_late_fixed(matched, un_cam, un_lid, calibration=self.calibration, w_cam=0.5, w_lidar=0.5)

                    elif var_name == "A1_Plus_IMU":
                        # Fixed 50/50 + IMU motion compensation on points
                        pts_comp = self.compensator.compensate_lidar_frame(pts_in, t_ego)
                        lid_cl_comp, _ = self.lid_detector.detect(pts_comp)
                        m_comp, uc_comp, ul_comp = associate_camera_and_lidar(cam_dets, lid_cl_comp, self.compensator)
                        preds = self.fusion_engine.fuse_late_fixed(m_comp, uc_comp, ul_comp, calibration=self.calibration, w_cam=0.5, w_lidar=0.5)

                    elif var_name == "A2_Plus_Temporal":
                        # A1 + Temporal multi-frame tracking
                        base_preds = self.fusion_engine.fuse_late_fixed(matched, un_cam, un_lid, calibration=self.calibration, w_cam=0.5, w_lidar=0.5)
                        dets_for_track = [{"position": d.position, "confidence": d.confidence, "class_name": d.class_name}
                                          for d in base_preds if d.confidence >= 0.20]
                        confirmed = tracker.step(dets_for_track, T_ego=t_ego, dt=dt)
                        preds = [FusedDetection(trk.position, trk.confidence, trk.class_name) for trk in confirmed]

                    elif var_name == "A3_Plus_Reliability":
                        # A2 + Reliability calculation to modulate confidences
                        fused_objs = []
                        for m in matched:
                            cam = m["camera_det"]
                            lid = m["lidar_cluster"]
                            r_c = self.fusion_engine.estimate_camera_reliability(cam, img_qual, lid.radial_distance, imu_state=imu_data)
                            r_l = self.fusion_engine.estimate_lidar_reliability(lid, total_pts, lid.radial_distance)
                            u, v = cam.centroid_2d
                            p_cam_ray = self.calibration.camera_ray_to_3d(u, v, lid.radial_distance)
                            pos_fused = 0.5 * p_cam_ray + 0.5 * lid.centroid
                            conf = 1.0 - (1.0 - r_c) * (1.0 - r_l)
                            fused_objs.append(FusedDetection(pos_fused, conf, cam.class_name, r_cam=r_c, r_lidar=r_l))
                        for lid in un_lid:
                            r_l = self.fusion_engine.estimate_lidar_reliability(lid, total_pts, lid.radial_distance)
                            fused_objs.append(FusedDetection(lid.centroid, r_l * 0.7, "vehicle", r_cam=0.0, r_lidar=r_l))
                        dets_for_track = [{"position": d.position, "confidence": d.confidence, "class_name": d.class_name}
                                          for d in fused_objs if d.confidence >= 0.20]
                        confirmed = tracker.step(dets_for_track, T_ego=t_ego, dt=dt)
                        preds = [FusedDetection(trk.position, trk.confidence, trk.class_name) for trk in confirmed]

                    elif var_name == "A4_Plus_Adaptive_Weights":
                        # A3 + Dynamic weights (without hysteresis smoothing or health states)
                        fused_objs = []
                        for m in matched:
                            cam = m["camera_det"]
                            lid = m["lidar_cluster"]
                            r_c = self.fusion_engine.estimate_camera_reliability(cam, img_qual, lid.radial_distance, imu_state=imu_data)
                            r_l = self.fusion_engine.estimate_lidar_reliability(lid, total_pts, lid.radial_distance)
                            denom = r_c + r_l + 1e-6
                            w_c = r_c / denom
                            w_l = r_l / denom
                            u, v = cam.centroid_2d
                            p_cam_ray = self.calibration.camera_ray_to_3d(u, v, lid.radial_distance)
                            pos_fused = w_c * p_cam_ray + w_l * lid.centroid
                            conf = 1.0 - (1.0 - r_c) * (1.0 - r_l)
                            fused_objs.append(FusedDetection(pos_fused, conf, cam.class_name, r_cam=r_c, r_lidar=r_l, w_cam=w_c, w_lidar=w_l))
                        for lid in un_lid:
                            r_l = self.fusion_engine.estimate_lidar_reliability(lid, total_pts, lid.radial_distance)
                            fused_objs.append(FusedDetection(lid.centroid, r_l * 0.7, "vehicle", r_cam=0.0, r_lidar=r_l, w_cam=0.0, w_lidar=1.0))
                        dets_for_track = [{"position": d.position, "confidence": d.confidence, "class_name": d.class_name}
                                          for d in fused_objs if d.confidence >= 0.20]
                        confirmed = tracker.step(dets_for_track, T_ego=t_ego, dt=dt)
                        preds = [FusedDetection(trk.position, trk.confidence, trk.class_name) for trk in confirmed]

                    elif var_name == "A5_Plus_Hysteresis_Health":
                        # A4 + Weight hysteresis and health state machine
                        preds = self.fusion_engine.fuse_reliability_adaptive(
                            matched, un_cam, un_lid, img_qual, total_pts, calibration=self.calibration,
                            imu_state=imu_data, dt=dt
                        )
                        dets_for_track = [{"position": d.position, "confidence": d.confidence, "class_name": d.class_name}
                                          for d in preds if d.confidence >= 0.20]
                        confirmed = tracker.step(dets_for_track, T_ego=t_ego, dt=dt)
                        preds = [FusedDetection(trk.position, trk.confidence, trk.class_name) for trk in confirmed]

                    elif var_name == "A6_Full_Proposed":
                        # Full proposed system
                        curr_det_pos = []
                        for m in matched:
                            curr_det_pos.append({"position": m["lidar_cluster"].centroid, "confidence": m["camera_det"].confidence})
                        for l in un_lid:
                            curr_det_pos.append({"position": l.centroid, "confidence": l.geometric_score})
                        active_tracks = tracker.step(curr_det_pos, T_ego=t_ego, dt=dt)

                        preds = self.fusion_engine.fuse_reliability_adaptive(
                            matched, un_cam, un_lid, img_qual, total_pts, calibration=self.calibration,
                            imu_state=imu_data, temporal_tracks=active_tracks, compensator=self.compensator, dt=dt
                        )

                    t_total = time.perf_counter() - t0
                    perf["latencies"].append(t_total)

                    # Evaluate 3D performance against ground truth
                    tp, fp, fn, errs, confs = evaluate_3d_frame(preds, gt_3d, dist_threshold=2.5, conf_threshold=0.25)
                    perf["tp"] += tp
                    perf["fp"] += fp
                    perf["fn"] += fn
                    perf["loc_errs"].extend(errs)
                    perf["confs"].extend(confs)

                    f_prec = tp / max(1, tp + fp) if (tp + fp) > 0 else 0.0
                    f_rec = tp / max(1, tp + fn) if (tp + fn) > 0 else 0.0
                    perf["f1s"].append(2 * f_prec * f_rec / max(1e-4, f_prec + f_rec))

                    if preds:
                        trajectories.append(preds[0].position)

                # Aggregate condition results
                tp = perf["tp"]
                fp = perf["fp"]
                fn = perf["fn"]
                precision = tp / max(1, tp + fp) if (tp + fp) > 0 else 0.0
                recall = tp / max(1, tp + fn) if (tp + fn) > 0 else 0.0
                f1 = 2.0 * precision * recall / max(1e-4, precision + recall)
                mean_loc_err = float(np.mean(perf["loc_errs"])) if perf["loc_errs"] else 0.0
                jitter = compute_trajectory_jitter(trajectories)
                mean_lat = float(np.mean(perf["latencies"])) * 1000.0
                fps = 1000.0 / max(0.1, mean_lat)

                ablation_rows.append({
                    "variant": var_name,
                    "description": var_desc,
                    "condition": cond,
                    "precision": round(precision, 4),
                    "recall": round(recall, 4),
                    "f1_score": round(f1, 4),
                    "localization_error_m": round(mean_loc_err, 4),
                    "jitter_m": round(jitter, 4),
                    "latency_ms": round(mean_lat, 2),
                    "fps": round(fps, 1),
                    "tp": tp,
                    "fp": fp,
                    "fn": fn
                })

                cond_elapsed = time.perf_counter() - cond_t0
                print(f"       ✓ [{var_name} | {cond}] Complete in {cond_elapsed:.1f}s -> F1: {f1:.4f}, LocErr: {mean_loc_err:.3f}m, Latency: {mean_lat:.1f}ms")

            print(f"    ✓ Variant {var_name} completed in {time.perf_counter() - var_t0:.1f}s")

        return pd.DataFrame(ablation_rows)
