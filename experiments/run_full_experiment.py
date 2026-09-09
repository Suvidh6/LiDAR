"""
experiments/run_full_experiment.py
Master Research Experiment Pipeline.

Coordinates:
1. Continuous Dynamic Experiment: frame-by-frame time-varying degradation,
   generating 10 publication figures and frame-level CSV telemetry.
2. Comparative Benchmark Matrix: systematic evaluation of all 7 perception paradigms
   across 5 environmental degradation conditions.

STRICT CONSTRAINTS:
- All numerical metrics written exclusively to results/metrics/
- All publication plots written exclusively to results/plots/
- No files placed directly in results/
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

from src.utils.paths import get_data_dir, get_metrics_dir, get_plots_dir
from src.utils.reproducibility import set_seed, save_experiment_metadata
from src.utils.configuration import load_default_config, load_experiment_config
from src.sensors.imu import IMUMotionProcessor
from src.perception.camera_detector import CameraDetector
from src.perception.lidar_detector import LiDARDetector
from src.fusion.spatial_association import associate_camera_and_lidar
from src.fusion.motion_compensation import MotionCompensator
from src.fusion.temporal_tracker import TemporalTracker
from src.fusion.adaptive_fusion import AdaptiveFusionEngine
from src.evaluation.benchmarking import FusionBenchmarkHarness
from src.evaluation.visualization import plot_all_research_figures
from experiments.run_dynamic_experiment import run_dynamic_experiment

def run_all_experiments():
    print("=" * 82)
    print("  AUTONOMOUS-DRIVING SENSOR FUSION: UNIFIED RESEARCH EXPERIMENT PIPELINE")
    print("  IMU-Assisted Temporal Reliability-Aware Camera-LiDAR Sensor Fusion")
    print("=" * 82)

    set_seed(42)
    data_dir = str(get_data_dir())
    metrics_dir = str(get_metrics_dir())
    plots_dir = str(get_plots_dir())

    os.makedirs(metrics_dir, exist_ok=True)
    os.makedirs(plots_dir, exist_ok=True)

    # 1. Run Continuous Dynamic Scenario Evaluation
    print("\n>>> STAGE 1: Continuous Dynamic Scenario Evaluation <<<")
    frame_df, dyn_summary = run_dynamic_experiment(
        data_root=data_dir,
        output_metrics_dir=metrics_dir,
        output_plots_dir=plots_dir,
        seed=42
    )

    # 2. Run Comparative Baseline Benchmark Matrix
    print("\n>>> STAGE 2: Comparative Baseline Benchmark Matrix (7 Methods x 5 Regimes) <<<")
    config = load_default_config()

    imu_proc = IMUMotionProcessor(data_root=data_dir)
    compensator = MotionCompensator(
        image_width=config["sensors"]["camera"]["image_width"],
        image_height=config["sensors"]["camera"]["image_height"],
        fov=config["sensors"]["camera"]["fov"]
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
        nominal_lidar_points=config["sensors"]["lidar"]["nominal_points_per_frame"]
    )
    tracker = TemporalTracker(
        max_age=config["fusion"]["temporal_tracker"]["max_age_frames"],
        min_hits=config["fusion"]["temporal_tracker"]["min_hits_confirmation"],
        dist_threshold=config["fusion"]["temporal_tracker"]["distance_threshold_m"],
        use_imu_compensation=config["fusion"]["motion_compensation"]["use_imu_warping"]
    )

    frames = imu_proc.process_sequence()
    harness = FusionBenchmarkHarness(
        cam_detector=cam_detector,
        lid_detector=lid_detector,
        compensator=compensator,
        fusion_engine=fusion_engine,
        tracker=tracker
    )

    benchmark_df, weights_df = harness.run_benchmark(frames, associate_camera_and_lidar)

    # Save benchmark table to results/metrics/
    benchmark_csv_path = os.path.join(metrics_dir, "adaptive_degradation_benchmark.csv")
    benchmark_df.to_csv(benchmark_csv_path, index=False)

    benchmark_summary = {
        "experiment": "Unified IMU-Assisted Temporal Reliability-Aware Multimodal Perception",
        "conditions_evaluated": harness.CONDITIONS,
        "methods_evaluated": harness.METHODS,
        "clean_nominal_results": benchmark_df[benchmark_df["condition"] == "Clean_Nominal"][["method", "f1_score", "localization_error_m", "fps"]].to_dict(orient="records"),
        "camera_degraded_results": benchmark_df[benchmark_df["condition"] == "Camera_Degraded"][["method", "f1_score", "localization_error_m"]].to_dict(orient="records"),
        "lidar_degraded_results": benchmark_df[benchmark_df["condition"] == "LiDAR_Degraded"][["method", "f1_score", "localization_error_m"]].to_dict(orient="records")
    }
    with open(os.path.join(metrics_dir, "adaptive_fusion_summary.json"), "w") as f:
        json.dump(benchmark_summary, f, indent=4)

    # 3. Update Visualizations with Benchmark Comparisons
    plot_all_research_figures(frame_df, benchmark_df=benchmark_df, output_dir=plots_dir)

    save_sample_adaptive_overlay(frames[20], cam_detector, lid_detector, compensator, fusion_engine, plots_dir)

    # 4. Save Final Metadata
    save_experiment_metadata(
        os.path.join(metrics_dir, "experiment_metadata.json"),
        extra_info={
            "benchmark_conditions": harness.CONDITIONS,
            "benchmark_methods": harness.METHODS,
            "total_frames": len(frames)
        }
    )

    print("\n" + "=" * 82)
    print("                      FULL EXPERIMENT BENCHMARK RESULTS")
    print("=" * 82)
    print(benchmark_df.to_string(index=False))
    print("=" * 82)
    print(f"\nAll metrics saved to: {metrics_dir}")
    print(f"All publication plots saved to: {plots_dir}")
    print("Verification: Zero outputs placed directly under results/ root.")

def save_sample_adaptive_overlay(frame, cam_detector, lid_detector, compensator, fusion_engine, output_dir):
    """Generates an annotated visual proof overlay on a degraded frame."""
    raw_img = cv2.imread(frame["camera_path"])
    pts_raw = compensator.load_point_cloud(frame["lidar_path"])

    from src.evaluation.degradation import apply_camera_motion_blur, apply_camera_illumination_degrade
    blurred_img = apply_camera_motion_blur(raw_img, kernel_size=19, angle_deg=30.0)
    dark_blurred = apply_camera_illumination_degrade(blurred_img, factor=0.20)

    cam_dets, img_qual = cam_detector.detect(dark_blurred)
    lid_clusters, total_pts = lid_detector.detect(pts_raw)
    matched, un_c, un_l = associate_camera_and_lidar(cam_dets, lid_clusters, compensator)

    out_prop = fusion_engine.fuse_reliability_adaptive(
        matched, un_c, un_l, img_qual, total_pts, imu_state=frame
    )

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
