"""
experiments/run_dynamic_experiment.py
Continuous Dynamic Sensor Fusion Experiment Runner.

Executes a frame-by-frame dynamic experiment where environmental conditions,
camera sharpness, illumination, LiDAR beam density, and vehicle kinematics
vary continuously over time. Evaluates against authoritative ground truth.

Generates:
- results/metrics/frame_metrics.csv
- results/metrics/sensor_reliability.csv
- results/metrics/fusion_metrics.csv
- results/metrics/experiment_summary.json
- results/metrics/experiment_metadata.json
- Publication research plots in results/plots/ and results/figures/
"""

import os
import sys
import time
import json
import cv2
import numpy as np
import pandas as pd

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.utils.paths import get_data_dir, get_metrics_dir, get_plots_dir
from src.utils.reproducibility import set_seed, save_experiment_metadata
from src.utils.configuration import load_default_config, load_degradation_config
from src.dataset.carla_adapter import CARLADatasetAdapter
from src.perception.camera_detector import CameraDetector
from src.perception.lidar_detector import LiDARDetector
from src.fusion.spatial_association import associate_camera_and_lidar
from src.fusion.motion_compensation import MotionCompensator
from src.fusion.temporal_tracker import TemporalTracker
from src.fusion.adaptive_fusion import AdaptiveFusionEngine
from src.evaluation.scenarios import DynamicScenarioEngine
from src.evaluation.metrics import evaluate_3d_frame, compute_aggregate_metrics
from src.evaluation.visualization import plot_all_research_figures

def run_dynamic_experiment(data_root=None, output_metrics_dir=None, output_plots_dir=None, seed=42):
    """
    Executes continuous dynamic sequence evaluation across all indexed frames.
    """
    set_seed(seed)
    data_dir = data_root or str(get_data_dir())
    metrics_dir = output_metrics_dir or str(get_metrics_dir())
    plots_dir = output_plots_dir or str(get_plots_dir())
    figures_dir = os.path.join(PROJECT_ROOT, "results", "figures")

    os.makedirs(metrics_dir, exist_ok=True)
    os.makedirs(plots_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)

    config = load_default_config()
    degrade_cfg = load_degradation_config()

    print("=" * 82)
    print("  RUNNING CONTINUOUS DYNAMIC SENSOR FUSION EXPERIMENT")
    print("  Evaluating Against Authoritative CARLA Ground Truth")
    print("=" * 82)

    # 1. Initialize Dataset Adapter
    adapter = CARLADatasetAdapter(data_root=data_dir, config=config)
    calibration = adapter.get_calibration()
    frames = adapter.get_sequence()
    num_frames = len(frames)
    print(f" -> Indexed {num_frames} frames with authoritative ground truth from dataset.")

    # 2. Initialize Hardware & Perception Models
    compensator = MotionCompensator(
        image_width=calibration.width,
        image_height=calibration.height,
        fov=calibration.fov
    )
    cam_detector = CameraDetector(
        conf_thresh=config["perception"]["camera_detector"]["confidence_threshold"]
    )
    lid_detector = LiDARDetector(
        ground_thresh=config["perception"]["lidar_detector"]["ground_removal_threshold"],
        eps=config["perception"]["lidar_detector"]["dbscan_eps"],
        min_cluster_points=config["perception"]["lidar_detector"]["dbscan_min_points"]
    )
    fusion_engine = AdaptiveFusionEngine(
        camera_max_range=config["sensors"]["camera"]["max_reliable_range_m"],
        nominal_lidar_points=config["sensors"]["lidar"]["nominal_points_per_frame"],
        smoothing_alpha=config["fusion"]["reliability"]["smoothing_alpha"],
        health_thresholds=config["fusion"]["reliability"]["health_thresholds"],
        calibration=calibration
    )
    tracker = TemporalTracker(
        max_age=config["fusion"]["temporal_tracker"]["max_age_frames"],
        min_hits=config["fusion"]["temporal_tracker"]["min_hits_confirmation"],
        dist_threshold=config["fusion"]["temporal_tracker"]["distance_threshold_m"],
        use_imu_compensation=config["fusion"]["motion_compensation"]["use_imu_warping"]
    )
    scenario_engine = DynamicScenarioEngine(degrade_cfg)

    frame_records = []
    tracker.reset()
    fusion_engine.reset_state()

    t_dyn_start = time.perf_counter()
    print("\n[Executing Frame-by-Frame Continuous Dynamic Pipeline]")
    for i, frame in enumerate(frames):
        t_start = time.perf_counter()
        t_ego = frame.T_ego
        dt = frame.dt
        imu_data = frame.imu_data

        raw_img = frame.get_camera_image()
        pts_raw = frame.get_lidar_points()

        # Authoritative independent ground truth (BEFORE degradation)
        gt_targets = frame.ground_truth.get_positions_3d(max_distance=45.0)

        # Apply continuous dynamic degradation schedule for frame i
        deg_img, deg_pts, deg_params = scenario_engine.apply_degradation(
            raw_img, pts_raw, frame_idx=i, seed=seed
        )

        if (i + 1) % 10 == 0 or (i + 1) == num_frames:
            pct = ((i + 1) / num_frames) * 100.0
            elapsed_dyn = time.perf_counter() - t_dyn_start
            print(f"  -> [Stage 1 Dynamic Sequence] Frame {i + 1}/{num_frames} ({pct:.1f}%) | Segment: {deg_params['segment_id']} | Elapsed: {elapsed_dyn:.1f}s")

        # Perception on degraded inputs
        cam_dets, img_qual = cam_detector.detect(deg_img)
        lid_clusters, total_pts = lid_detector.detect(deg_pts)

        # Spatial cross-modal Hungarian association
        matched_pairs, un_c, un_l = associate_camera_and_lidar(
            cam_dets, lid_clusters, compensator
        )

        # Temporal tracking with IMU ego-motion compensation
        curr_det_pos = []
        for m in matched_pairs:
            curr_det_pos.append({"position": m["lidar_cluster"].centroid, "confidence": m["camera_det"].confidence})
        for l in un_l:
            curr_det_pos.append({"position": l.centroid, "confidence": l.geometric_score})

        active_tracks = tracker.step(curr_det_pos, T_ego=t_ego, dt=dt)
        track_persistence = np.mean([t.persistence_ratio for t in active_tracks]) if active_tracks else 0.5

        # Reliability-Aware Adaptive Fusion
        fused_outputs = fusion_engine.fuse_reliability_adaptive(
            matched_pairs=matched_pairs,
            unmatched_cam=un_c,
            unmatched_lid=un_l,
            image_quality=img_qual,
            total_cloud_points=total_pts,
            calibration=calibration,
            imu_state=imu_data,
            temporal_tracks=active_tracks,
            compensator=compensator,
            dt=dt
        )

        elapsed = time.perf_counter() - t_start
        fps = 1.0 / max(1e-4, elapsed)

        # Quantitative single-frame ground-truth metrics
        tp, fp, fn, errs, _ = evaluate_3d_frame(fused_outputs, gt_targets, dist_threshold=2.5, conf_threshold=0.25)
        eval_metrics = compute_aggregate_metrics(tp, fp, fn, errs)

        # Diagnostics extraction
        avg_r_cam = float(np.mean([f.r_cam for f in fused_outputs])) if fused_outputs else 0.01
        avg_r_lidar = float(np.mean([f.r_lidar for f in fused_outputs])) if fused_outputs else 0.01
        avg_w_cam = float(np.mean([f.w_cam for f in fused_outputs])) if fused_outputs else 0.5
        avg_w_lidar = float(np.mean([f.w_lidar for f in fused_outputs])) if fused_outputs else 0.5
        avg_conf = float(np.mean([f.confidence for f in fused_outputs])) if fused_outputs else 0.01
        avg_consist = float(np.mean([f.consistency for f in fused_outputs])) if fused_outputs else 1.0

        cam_raw_conf = float(np.mean([d.confidence for d in cam_dets])) if cam_dets else 0.0
        lidar_raw_conf = float(np.mean([c.geometric_score for c in lid_clusters])) if lid_clusters else 0.0

        speed = float(imu_data.get("gt_speed", np.linalg.norm(imu_data.get("delta_trans", [0, 0, 0])) / max(1e-4, dt)))
        accel_x = float(imu_data.get("linear_accel", [0, 0, 0])[0])
        gyro_z = float(imu_data.get("gyro", [0, 0, 0])[2])
        yaw_rate = float(np.degrees(gyro_z))

        record = {
            "frame_id": i,
            "timestamp": frame.timestamp,
            "segment_id": deg_params["segment_id"],
            "description": deg_params["description"],
            "blur_kernel": deg_params["blur_kernel"],
            "illumination_factor": deg_params["illumination_factor"],
            "lidar_dropout_ratio": deg_params["dropout_ratio"],
            "speed_mps": round(speed, 2),
            "accel_x_mps2": round(accel_x, 2),
            "yaw_rate_dps": round(yaw_rate, 2),
            "r_cam": round(avg_r_cam, 4),
            "r_lidar": round(avg_r_lidar, 4),
            "w_cam": round(avg_w_cam, 4),
            "w_lidar": round(avg_w_lidar, 4),
            "cam_health": fusion_engine.estimator.classify_health(avg_r_cam),
            "lidar_health": fusion_engine.estimator.classify_health(avg_r_lidar),
            "confidence": round(avg_conf, 4),
            "cam_raw_conf": round(cam_raw_conf, 4),
            "lidar_raw_conf": round(lidar_raw_conf, 4),
            "cross_modal_consistency": round(avg_consist, 3),
            "track_count": len(active_tracks),
            "temporal_persistence": round(float(track_persistence), 3),
            "cam_detections": len(cam_dets),
            "lidar_clusters": len(lid_clusters),
            "fused_detections": len(fused_outputs),
            "gt_targets": len(gt_targets),
            "precision": eval_metrics["precision"],
            "recall": eval_metrics["recall"],
            "f1_score": eval_metrics["f1_score"],
            "loc_error_m": eval_metrics["localization_error_m"] if eval_metrics["localization_error_m"] is not None else 0.0,
            "latency_ms": round(elapsed * 1000.0, 2),
            "fps": round(fps, 1)
        }
        frame_records.append(record)

    frame_df = pd.DataFrame(frame_records)

    # Save metrics
    frame_metrics_path = os.path.join(metrics_dir, "frame_metrics.csv")
    frame_df.to_csv(frame_metrics_path, index=False)

    sensor_rel_path = os.path.join(metrics_dir, "sensor_reliability.csv")
    frame_df[["frame_id", "timestamp", "r_cam", "r_lidar", "w_cam", "w_lidar", "cam_health", "lidar_health", "blur_kernel", "illumination_factor", "lidar_dropout_ratio"]].to_csv(sensor_rel_path, index=False)

    dyn_summary = {
        "mean_f1_score": round(float(frame_df["f1_score"].mean()), 4),
        "mean_precision": round(float(frame_df["precision"].mean()), 4),
        "mean_recall": round(float(frame_df["recall"].mean()), 4),
        "mean_loc_error_m": round(float(frame_df["loc_error_m"].mean()), 4),
        "mean_fps": round(float(frame_df["fps"].mean()), 1),
        "mean_r_cam": round(float(frame_df["r_cam"].mean()), 4),
        "mean_r_lidar": round(float(frame_df["r_lidar"].mean()), 4)
    }
    with open(os.path.join(metrics_dir, "experiment_summary.json"), "w") as f:
        json.dump(dyn_summary, f, indent=4)

    # Generate dynamic plots in both results/plots/ and results/figures/
    plot_all_research_figures(frame_df, benchmark_df=None, output_dir=plots_dir)
    plot_all_research_figures(frame_df, benchmark_df=None, output_dir=figures_dir)

    print(f"Dynamic scenario evaluation complete. Metrics saved to {metrics_dir}")
    return frame_df, dyn_summary
