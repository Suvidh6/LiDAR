"""
experiments/run_full_experiment.py
The Complete Unified Autonomous-Driving Sensor Fusion Research Experiment Runner.

Executes the unified perception pipeline:
1. Validates synchronized multi-sensor telemetry (Camera + LiDAR + IMU).
2. Component 1: IMU Kinematic Ego-Motion Estimation & SE(3) Point Cloud Warping.
3. Component 2: Temporal Multi-Frame Fusion with Kalman Tracklet Lifecycle.
4. Component 3: Reliability-Aware Adaptive Sensor Fusion across 7 Methods and 5 Degradation Conditions.

Generates complete publication-ready metrics and figures in results/metrics/ and results/plots/.
"""

import os
import sys
import json
import time
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.sensors.imu import IMUMotionProcessor
from src.sensors.camera import CameraModel
from src.sensors.lidar import PointCloudIO
from src.perception.camera_detector import CameraDetector
from src.perception.lidar_detector import LiDARDetector
from src.fusion.spatial_association import associate_camera_and_lidar
from src.fusion.motion_compensation import MotionCompensator
from src.fusion.temporal_tracker import TemporalTracker
from src.fusion.adaptive_fusion import AdaptiveFusionEngine
from src.evaluation.metrics import evaluate_detection_performance
from src.evaluation.benchmarking import FusionBenchmarkHarness
from src.evaluation.degradation import (
    apply_camera_motion_blur,
    apply_camera_illumination_degrade,
    apply_camera_outage,
    apply_lidar_dropout,
    apply_lidar_noise
)

def run_all_experiments():
    print("=" * 82)
    print("  AUTONOMOUS-DRIVING SENSOR FUSION: UNIFIED RESEARCH EXPERIMENT PIPELINE")
    print("  IMU-Assisted Temporal Reliability-Aware Camera-LiDAR Sensor Fusion")
    print("=" * 82)

    data_root = os.path.join(PROJECT_ROOT, "data", "dynamic_dataset")
    results_dir = os.path.join(PROJECT_ROOT, "results")
    metrics_dir = os.path.join(results_dir, "metrics")
    plots_dir = os.path.join(results_dir, "plots")

    os.makedirs(metrics_dir, exist_ok=True)
    os.makedirs(plots_dir, exist_ok=True)

    # 1. Initialize Pipeline Modules
    print("\n[Step 1/4] Initializing calibrated sensor and perception modules...")
    imu_proc = IMUMotionProcessor(data_root=data_root)
    compensator = MotionCompensator(image_width=800, image_height=600, fov=90.0)
    cam_detector = CameraDetector(conf_thresh=0.25)
    lid_detector = LiDARDetector(ground_thresh=0.15, eps=0.8, min_cluster_points=8)
    fusion_engine = AdaptiveFusionEngine(camera_max_range=45.0, nominal_lidar_points=2500)
    tracker_with_imu = TemporalTracker(max_age=3, min_hits=2, dist_threshold=2.5, use_imu_compensation=True)
    tracker_no_imu = TemporalTracker(max_age=3, min_hits=2, dist_threshold=2.5, use_imu_compensation=False)

    frames = imu_proc.process_sequence()
    num_frames = len(frames)
    print(f" -> Indexed {num_frames} synchronized frames from CARLA dataset.")

    # 2. Component 1: IMU-Based Motion Compensation & Alignment
    print("\n[Step 2/4] Evaluating IMU Ego-Motion Compensation & Point Cloud Alignment...")
    align_metrics = []
    sample_visual_saved = False

    for i in range(1, num_frames):
        prev_f = frames[i - 1]
        curr_f = frames[i]
        if not (prev_f["has_lidar"] and curr_f["has_lidar"]):
            continue

        pts_prev = compensator.load_point_cloud(prev_f["lidar_path"])
        pts_curr = compensator.load_point_cloud(curr_f["lidar_path"])

        mae_raw, mse_raw = compensator.compute_alignment_error(pts_prev, pts_curr)
        pts_prev_comp = compensator.compensate_lidar_frame(pts_prev, curr_f["T_ego"])
        mae_comp, mse_comp = compensator.compute_alignment_error(pts_prev_comp, pts_curr)

        reduction_pct = ((mse_raw - mse_comp) / mse_raw) * 100.0 if (not np.isnan(mse_raw) and mse_raw > 0) else 0.0

        align_metrics.append({
            "frame_idx": i,
            "prev_frame_id": prev_f["frame_id"],
            "curr_frame_id": curr_f["frame_id"],
            "timestamp": curr_f["timestamp"],
            "motion_state": curr_f["motion_state"],
            "gt_speed_kmh": curr_f.get("gt_speed", 0.0) * 3.6,
            "mae_without_imu": mae_raw,
            "mse_without_imu": mse_raw,
            "mae_with_imu": mae_comp,
            "mse_with_imu": mse_comp,
            "improvement_pct": reduction_pct
        })

        if not sample_visual_saved and curr_f.get("gt_speed", 0.0) > 3.0 and abs(curr_f["gyro"][2]) > 0.08:
            sample_visual_saved = True
            save_imu_alignment_visual(curr_f, pts_prev, pts_curr, pts_prev_comp, compensator, plots_dir)

    align_df = pd.DataFrame(align_metrics)
    align_df.to_csv(os.path.join(metrics_dir, "frame_metrics.csv"), index=False)
    align_df.to_csv(os.path.join(results_dir, "frame_metrics.csv"), index=False)

    valid_align = align_df.dropna(subset=["mse_without_imu", "mse_with_imu"])
    avg_mse_without = float(valid_align["mse_without_imu"].mean())
    avg_mse_with = float(valid_align["mse_with_imu"].mean())
    overall_reduction = ((avg_mse_without - avg_mse_with) / avg_mse_without) * 100.0 if avg_mse_without > 0 else 0.0

    align_summary = {
        "total_frames_evaluated": len(align_df),
        "avg_mae_without_imu_m": round(float(valid_align["mae_without_imu"].mean()), 4),
        "avg_mae_with_imu_m": round(float(valid_align["mae_with_imu"].mean()), 4),
        "avg_mse_without_imu_m2": round(avg_mse_without, 4),
        "avg_mse_with_imu_m2": round(avg_mse_with, 4),
        "overall_mse_reduction_percentage": round(overall_reduction, 2)
    }
    with open(os.path.join(metrics_dir, "experiment_summary.json"), "w") as f:
        json.dump(align_summary, f, indent=4)
    with open(os.path.join(results_dir, "experiment_summary.json"), "w") as f:
        json.dump(align_summary, f, indent=4)

    # Plot IMU telemetry figures
    generate_imu_plots(frames, align_df, plots_dir)
    print(f" -> IMU alignment complete. MSE reduction: {overall_reduction:.2f}%.")

    # 3. Component 2: Temporal Multi-Frame Fusion Benchmark
    print("\n[Step 3/4] Evaluating Temporal Multi-Frame Fusion with Kalman Tracklet Lifecycle...")
    temp_records = []
    trajectories_no_imu = []
    trajectories_with_imu = []

    for i, frame in enumerate(frames):
        if not (frame["has_camera"] and frame["has_lidar"]):
            continue

        dt = frame["dt"]
        t_ego = frame["T_ego"]

        t_start = time.perf_counter()
        cam_dets, _ = cam_detector.detect(frame["camera_path"])
        lid_clusters, _ = lid_detector.detect(frame["lidar_path"])
        matched, _, un_lid = associate_camera_and_lidar(cam_dets, lid_clusters, compensator)

        curr_dets = [{"position": m["lidar_cluster"].centroid, "confidence": m["camera_det"].confidence, "class_name": m["camera_det"].class_name} for m in matched]
        for cl in un_lid:
            curr_dets.append({"position": cl.centroid, "confidence": cl.geometric_score * 0.8, "class_name": "vehicle"})

        tracks_no = tracker_no_imu.step(curr_dets, T_ego=None, dt=dt)
        tracks_with = tracker_with_imu.step(curr_dets, T_ego=t_ego, dt=dt)
        t_elapsed = (time.perf_counter() - t_start) * 1000.0

        if tracks_no:
            trajectories_no_imu.append(tracks_no[0].position[:2].copy())
        if tracks_with:
            trajectories_with_imu.append(tracks_with[0].position[:2].copy())

        persist_no = np.mean([t.persistence_ratio for t in tracks_no]) if tracks_no else 0.0
        persist_with = np.mean([t.persistence_ratio for t in tracks_with]) if tracks_with else 0.0

        top_no = tracks_no[0].position if tracks_no else [np.nan, np.nan, np.nan]
        top_with = tracks_with[0].position if tracks_with else [np.nan, np.nan, np.nan]

        temp_records.append({
            "frame_idx": i,
            "latency_ms": round(t_elapsed, 2),
            "single_frame_count": len(curr_dets),
            "temporal_no_imu_count": len(tracks_no),
            "temporal_with_imu_count": len(tracks_with),
            "persistence_no_imu": round(persist_no, 3),
            "persistence_with_imu": round(persist_with, 3),
            "pos_no_x": top_no[0],
            "pos_no_y": top_no[1],
            "pos_with_x": top_with[0],
            "pos_with_y": top_with[1]
        })

    temp_df = pd.DataFrame(temp_records)
    temp_df.to_csv(os.path.join(metrics_dir, "temporal_metrics.csv"), index=False)
    temp_df.to_csv(os.path.join(results_dir, "temporal_metrics.csv"), index=False)

    diff_no = np.diff(temp_df[["pos_no_x", "pos_no_y"]].dropna(), axis=0)
    jitter_no = float(np.mean(np.linalg.norm(diff_no, axis=1))) if len(diff_no) > 0 else 0.0
    diff_with = np.diff(temp_df[["pos_with_x", "pos_with_y"]].dropna(), axis=0)
    jitter_with = float(np.mean(np.linalg.norm(diff_with, axis=1))) if len(diff_with) > 0 else 0.0

    temp_summary = {
        "total_frames_evaluated": len(temp_df),
        "mean_latency_ms": round(float(temp_df["latency_ms"].mean()), 2),
        "fps": round(1000.0 / max(0.1, float(temp_df["latency_ms"].mean())), 1),
        "mean_persistence_no_imu": round(float(temp_df["persistence_no_imu"].mean()), 4),
        "mean_persistence_with_imu": round(float(temp_df["persistence_with_imu"].mean()), 4),
        "displacement_jitter_no_imu_m": round(jitter_no, 4),
        "displacement_jitter_with_imu_m": round(jitter_with, 4)
    }
    with open(os.path.join(metrics_dir, "temporal_fusion_summary.json"), "w") as f:
        json.dump(temp_summary, f, indent=4)
    with open(os.path.join(results_dir, "temporal_fusion_summary.json"), "w") as f:
        json.dump(temp_summary, f, indent=4)

    generate_temporal_plots(temp_df, plots_dir, trajectories_no_imu, trajectories_with_imu)
    print(f" -> Temporal fusion evaluation complete ({temp_summary['fps']} FPS).")

    # 4. Component 3: Reliability-Aware Adaptive Sensor Fusion Benchmark
    print("\n[Step 4/4] Benchmarking Reliability-Aware Adaptive Fusion across 7 Methods & 5 Conditions...")
    harness = FusionBenchmarkHarness(
        cam_detector=cam_detector,
        lid_detector=lid_detector,
        compensator=compensator,
        fusion_engine=fusion_engine,
        tracker=tracker_with_imu
    )

    benchmark_df, weights_df = harness.run_benchmark(frames, associate_camera_and_lidar)

    benchmark_df.to_csv(os.path.join(metrics_dir, "adaptive_degradation_benchmark.csv"), index=False)
    benchmark_df.to_csv(os.path.join(results_dir, "adaptive_degradation_benchmark.csv"), index=False)

    weights_df.to_csv(os.path.join(metrics_dir, "adaptive_metrics.csv"), index=False)
    weights_df.to_csv(os.path.join(results_dir, "adaptive_metrics.csv"), index=False)

    # Save visual overlay sample
    save_sample_adaptive_overlay(frames[20], cam_detector, lid_detector, compensator, fusion_engine, plots_dir)

    # Save Comparative Plots
    plot_adaptive_comparison(benchmark_df, plots_dir)
    plot_dynamic_weights_timeline(weights_df, plots_dir)

    # Also copy plots to root results/ for legacy viewers
    for f_name in os.listdir(plots_dir):
        src_p = os.path.join(plots_dir, f_name)
        dst_p = os.path.join(results_dir, f_name)
        if os.path.isfile(src_p):
            import shutil
            shutil.copy2(src_p, dst_p)

    adaptive_summary = {
        "experiment": "Unified IMU-Assisted Temporal Reliability-Aware Multimodal Perception",
        "conditions_evaluated": harness.CONDITIONS,
        "methods_evaluated": harness.METHODS,
        "clean_nominal_results": benchmark_df[benchmark_df["condition"] == "Clean_Nominal"][["method", "f1_score", "localization_error_m", "fps"]].to_dict(orient="records"),
        "camera_degraded_results": benchmark_df[benchmark_df["condition"] == "Camera_Degraded"][["method", "f1_score", "localization_error_m"]].to_dict(orient="records"),
        "lidar_degraded_results": benchmark_df[benchmark_df["condition"] == "LiDAR_Degraded"][["method", "f1_score", "localization_error_m"]].to_dict(orient="records")
    }
    with open(os.path.join(metrics_dir, "adaptive_fusion_summary.json"), "w") as f:
        json.dump(adaptive_summary, f, indent=4)
    with open(os.path.join(results_dir, "adaptive_fusion_summary.json"), "w") as f:
        json.dump(adaptive_summary, f, indent=4)

    print("\n" + "=" * 82)
    print("                      FULL EXPERIMENT BENCHMARK RESULTS")
    print("=" * 82)
    print(benchmark_df.to_string(index=False))
    print("=" * 82)
    print(f"\nAll metrics saved to: {metrics_dir}")
    print(f"All publication plots saved to: {plots_dir}")

def save_imu_alignment_visual(curr_f, pts_prev, pts_curr, pts_prev_comp, compensator, output_dir):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharex=True, sharey=True)
    axes[0].scatter(pts_curr[:, 1], pts_curr[:, 0], s=0.8, c="blue", label="Current Frame t", alpha=0.6)
    axes[0].scatter(pts_prev[:, 1], pts_prev[:, 0], s=0.8, c="red", label="Previous Frame t-1 (Raw)", alpha=0.5)
    axes[0].set_title("Without IMU Compensation (Raw Overlap)\nEgo-motion causes spatial smear", fontsize=11)
    axes[0].set_xlabel("Y (Lateral) [m]")
    axes[0].set_ylabel("X (Longitudinal) [m]")
    axes[0].set_xlim([-25, 25])
    axes[0].set_ylim([0, 45])
    axes[0].grid(True, linestyle="--", alpha=0.5)
    axes[0].legend(loc="upper right")

    axes[1].scatter(pts_curr[:, 1], pts_curr[:, 0], s=0.8, c="blue", label="Current Frame t", alpha=0.6)
    axes[1].scatter(pts_prev_comp[:, 1], pts_prev_comp[:, 0], s=0.8, c="green", label="Previous Frame t-1 (IMU Warped)", alpha=0.5)
    axes[1].set_title("With IMU Motion Compensation (SE(3) Warped)\nIMU ego-motion aligns static geometry", fontsize=11)
    axes[1].set_xlabel("Y (Lateral) [m]")
    axes[1].grid(True, linestyle="--", alpha=0.5)
    axes[1].legend(loc="upper right")

    plt.suptitle(f"Bird's Eye View (BEV) LiDAR Alignment (Frame {curr_f['frame_id']})", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "pointcloud_alignment_visual.png"), dpi=200)
    plt.close()

def generate_imu_plots(frames, metrics_df, output_dir):
    timestamps = [f["timestamp"] - frames[0]["timestamp"] for f in frames]
    accel_x = [f["linear_accel"][0] for f in frames]
    accel_y = [f["linear_accel"][1] for f in frames]
    gyro_z = [np.degrees(f["gyro"][2]) for f in frames]

    plt.figure(figsize=(10, 4))
    plt.plot(timestamps, accel_x, label="Longitudinal Accel (a_x)", color="navy", linewidth=1.8)
    plt.plot(timestamps, accel_y, label="Lateral Accel (a_y)", color="crimson", linewidth=1.5)
    plt.axhline(0, color="gray", linestyle=":", alpha=0.6)
    plt.title("IMU Linear Acceleration vs. Time", fontsize=12, fontweight="bold")
    plt.xlabel("Time [s]")
    plt.ylabel("Acceleration [m/s²]")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "imu_acceleration.png"), dpi=200)
    plt.close()

    plt.figure(figsize=(10, 4))
    plt.plot(timestamps, gyro_z, label="Yaw Rate (ω_z)", color="darkorange", linewidth=2.0)
    plt.axhline(0, color="gray", linestyle=":", alpha=0.6)
    plt.title("IMU Gyroscope Yaw Rate vs. Time", fontsize=12, fontweight="bold")
    plt.xlabel("Time [s]")
    plt.ylabel("Angular Velocity [deg/s]")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "imu_angular_velocity.png"), dpi=200)
    plt.close()

    plt.figure(figsize=(11, 4.8))
    plt.plot(metrics_df["frame_idx"], metrics_df["mse_without_imu"], label="Without IMU (Baseline)", color="crimson", linewidth=1.8)
    plt.plot(metrics_df["frame_idx"], metrics_df["mse_with_imu"], label="With IMU (Proposed)", color="forestgreen", linewidth=2.0)
    plt.fill_between(metrics_df["frame_idx"], metrics_df["mse_without_imu"], metrics_df["mse_with_imu"],
                     where=(metrics_df["mse_without_imu"] >= metrics_df["mse_with_imu"]), color="lightgreen", alpha=0.4)
    plt.title("Point Cloud Alignment Error Comparison (MSE)", fontsize=12, fontweight="bold")
    plt.xlabel("Consecutive Frame Pair Index")
    plt.ylabel("Mean Squared Error (MSE) [m²]")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "alignment_error_comparison.png"), dpi=200)
    plt.close()

def generate_temporal_plots(df, output_dir, traj_no, traj_with):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    ax1.plot(df["frame_idx"], df["single_frame_count"], label="Single-Frame (Raw)", color="gray", linestyle=":", linewidth=1.5)
    ax1.plot(df["frame_idx"], df["temporal_no_imu_count"], label="Temporal (Without IMU)", color="crimson", linewidth=1.8)
    ax1.plot(df["frame_idx"], df["temporal_with_imu_count"], label="Temporal (With IMU Motion Comp)", color="forestgreen", linewidth=2.0)
    ax1.set_ylabel("Confirmed Objects", fontweight="bold")
    ax1.set_title("Temporal Detection Stability vs. Single-Frame Baseline", fontsize=12, fontweight="bold")
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.legend()

    ax2.plot(df["frame_idx"], df["persistence_no_imu"], label="Persistence Ratio (No IMU)", color="crimson", linestyle="--", linewidth=1.8)
    ax2.plot(df["frame_idx"], df["persistence_with_imu"], label="Persistence Ratio (With IMU)", color="forestgreen", linewidth=2.0)
    ax2.set_xlabel("Frame Index")
    ax2.set_ylabel("Persistence (Hits/Age)", fontweight="bold")
    ax2.grid(True, linestyle="--", alpha=0.5)
    ax2.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "temporal_stability_comparison.png"), dpi=200)
    plt.close()

    if len(traj_no) > 5 and len(traj_with) > 5:
        arr_no = np.array(traj_no)
        arr_with = np.array(traj_with)
        plt.figure(figsize=(9, 6.5))
        plt.plot(arr_no[:, 1], arr_no[:, 0], "o-", color="crimson", label="Track Path (No IMU - Drifting)", markersize=4, linewidth=1.5, alpha=0.7)
        plt.plot(arr_with[:, 1], arr_with[:, 0], "s-", color="forestgreen", label="Track Path (With IMU Motion Comp)", markersize=4, linewidth=1.8)
        plt.title("Bird's Eye View (BEV) Tracklet Trajectory Consistency", fontsize=12, fontweight="bold")
        plt.xlabel("Lateral Position Y [m]")
        plt.ylabel("Longitudinal Position X [m]")
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "temporal_trajectory_visual.png"), dpi=200)
        plt.close()

def plot_adaptive_comparison(df, output_dir):
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    clean = df[df["condition"] == "Clean_Nominal"]
    cam_deg = df[df["condition"] == "Camera_Degraded"]
    lid_deg = df[df["condition"] == "LiDAR_Degraded"]

    methods = clean["method"].tolist()
    x = np.arange(len(methods))
    width = 0.26

    axes[0, 0].bar(x - width, clean["f1_score"], width, label="Clean Nominal", color="steelblue")
    axes[0, 0].bar(x, cam_deg["f1_score"], width, label="Camera Degraded", color="indianred")
    axes[0, 0].bar(x + width, lid_deg["f1_score"], width, label="LiDAR Degraded", color="darkorange")
    axes[0, 0].set_title("Perception F1-Score Across Conditions", fontsize=11, fontweight="bold")
    axes[0, 0].set_ylabel("F1-Score")
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(methods, rotation=25, ha="right", fontsize=9)
    axes[0, 0].grid(True, linestyle="--", alpha=0.5)
    axes[0, 0].legend()

    axes[0, 1].bar(x - width, clean["localization_error_m"], width, label="Clean Nominal", color="steelblue")
    axes[0, 1].bar(x, cam_deg["localization_error_m"], width, label="Camera Degraded", color="indianred")
    axes[0, 1].bar(x + width, lid_deg["localization_error_m"], width, label="LiDAR Degraded", color="darkorange")
    axes[0, 1].set_title("3D Localization Error [m] Across Conditions", fontsize=11, fontweight="bold")
    axes[0, 1].set_ylabel("Centroid Error [m]")
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(methods, rotation=25, ha="right", fontsize=9)
    axes[0, 1].grid(True, linestyle="--", alpha=0.5)
    axes[0, 1].legend()

    axes[1, 0].bar(x - width, clean["confidence"], width, label="Clean Nominal", color="steelblue")
    axes[1, 0].bar(x, cam_deg["confidence"], width, label="Camera Degraded", color="indianred")
    axes[1, 0].bar(x + width, lid_deg["confidence"], width, label="LiDAR Degraded", color="darkorange")
    axes[1, 0].set_title("Detection Confidence Across Conditions", fontsize=11, fontweight="bold")
    axes[1, 0].set_ylabel("Confidence Score")
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(methods, rotation=25, ha="right", fontsize=9)
    axes[1, 0].grid(True, linestyle="--", alpha=0.5)
    axes[1, 0].legend()

    axes[1, 1].bar(x, clean["fps"], width * 1.5, color="teal")
    axes[1, 1].axhline(20.0, color="crimson", linestyle="--", label="Sensor 20 Hz Target")
    axes[1, 1].set_title("Processing Throughput (FPS)", fontsize=11, fontweight="bold")
    axes[1, 1].set_ylabel("Frames Per Second (FPS)")
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(methods, rotation=25, ha="right", fontsize=9)
    axes[1, 1].grid(True, linestyle="--", alpha=0.5)
    axes[1, 1].legend()

    plt.suptitle("Unified Multimodal Sensor Fusion Benchmark", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "adaptive_fusion_comparison_bars.png"), dpi=200)
    plt.close()

def plot_dynamic_weights_timeline(wdf, output_dir):
    if wdf.empty:
        return
    plt.figure(figsize=(11, 5.0))
    idx = np.arange(len(wdf))
    plt.plot(idx, wdf["w_cam"], label="Camera Weight (w_cam)", color="navy", linewidth=2.0)
    plt.plot(idx, wdf["w_lidar"], label="LiDAR Weight (w_lidar)", color="forestgreen", linewidth=2.0)
    plt.axhline(0.5, color="gray", linestyle=":", alpha=0.7, label="Conventional Fixed Weight (0.50)")

    cond_changes = wdf[wdf["condition"] != wdf["condition"].shift(1)].index.tolist()
    for c_idx in cond_changes:
        if c_idx > 0:
            c_name = wdf.iloc[c_idx]["condition"]
            plt.axvline(c_idx, color="purple", linestyle="--", alpha=0.6)
            plt.text(c_idx + 1, 0.92, c_name.replace("_", " "), fontsize=8, color="purple", fontweight="bold")

    plt.title("Dynamic Sensor Weight Adaptation Under Controlled Degradation", fontsize=12, fontweight="bold")
    plt.xlabel("Evaluation Step Index")
    plt.ylabel("Normalized Sensor Weight [0.0 - 1.0]")
    plt.ylim([0.0, 1.05])
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(loc="lower left")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "sensor_weights_dynamic_timeline.png"), dpi=200)
    plt.close()

def save_sample_adaptive_overlay(frame, cam_detector, lid_detector, compensator, fusion_engine, output_dir):
    raw_img = cv2.imread(frame["camera_path"])
    pts_raw = compensator.load_point_cloud(frame["lidar_path"])

    blurred_img = apply_camera_motion_blur(raw_img, kernel_size=19, angle_deg=30.0)
    dark_blurred = apply_camera_illumination_degrade(blurred_img, factor=0.20)

    cam_dets, img_qual = cam_detector.detect(dark_blurred)
    lid_clusters, total_pts = lid_detector.detect(pts_raw)
    matched, un_c, un_l = associate_camera_and_lidar(cam_dets, lid_clusters, compensator)

    out_prop = fusion_engine.fuse_reliability_adaptive(matched, un_c, un_l, img_qual, total_pts, imu_state=frame)

    canvas = dark_blurred.copy()
    for det in out_prop:
        c_pts = np.array([det.position])
        uv, depth = compensator.project_lidar_to_camera(c_pts)
        if len(uv) > 0 and depth[0] > 0.5:
            u, v = int(uv[0, 0]), int(uv[0, 1])
            cv2.circle(canvas, (u, v), 8, (0, 255, 0), -1)
            cv2.circle(canvas, (u, v), 12, (0, 255, 255), 2)
            cv2.putText(canvas, f"{det.class_name} ({det.confidence:.2f})", (u - 40, max(25, v - 15)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)
            cv2.putText(canvas, f"w_c:{det.w_cam:.2f} | w_l:{det.w_lidar:.2f}", (u - 50, v + 22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)

    cv2.putText(canvas, "ADAPTIVE FUSION: CAMERA DEGRADED REGIME", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
    cv2.putText(canvas, "Vision degraded -> Trust dynamically transferred to LiDAR", (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
    cv2.imwrite(os.path.join(output_dir, "adaptive_fusion_overlay_sample.png"), canvas)

if __name__ == "__main__":
    run_all_experiments()
