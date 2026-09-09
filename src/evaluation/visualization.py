"""
src/evaluation/visualization.py
Publication-grade dynamic research visualization engine.

Generates 10 specialized time-series and comparative figures:
1. Camera vs. LiDAR reliability over time
2. Adaptive sensor weights over time
3. Vehicle motion vs. sensor reliability
4. Detection confidence over time
5. Precision, Recall, and F1 over time
6. Localization error over time
7. Sensor degradation vs. fusion performance
8. Temporal tracking consistency & trajectory continuity
9. Modality contribution during sensor failure
10. Processing latency and throughput (FPS) over time
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def set_plot_style():
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.size": 10,
        "axes.labelsize": 10,
        "axes.titlesize": 11,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "figure.titlesize": 12,
        "figure.dpi": 200
    })

def plot_all_research_figures(frame_df: pd.DataFrame, benchmark_df: pd.DataFrame, output_dir: str):
    """
    Generates all 10 comprehensive dynamic figures and benchmark visualizations.
    """
    os.makedirs(output_dir, exist_ok=True)
    set_plot_style()

    frames = frame_df["frame_id"].to_numpy()

    # 1. Camera vs LiDAR Reliability Over Time
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(frames, frame_df["r_cam"], label="Camera Reliability (R_cam)", color="#1f77b4", linewidth=2.0)
    ax.plot(frames, frame_df["r_lidar"], label="LiDAR Reliability (R_lidar)", color="#2ca02c", linewidth=2.0)
    ax.axhline(0.70, color="green", linestyle=":", alpha=0.5, label="Healthy Threshold (0.70)")
    ax.axhline(0.40, color="orange", linestyle=":", alpha=0.5, label="Degraded Threshold (0.40)")
    ax.axhline(0.15, color="red", linestyle=":", alpha=0.5, label="Failure Threshold (0.15)")
    ax.set_title("Multi-Criteria Sensor Reliability Over Continuous Dynamic Sequence", fontweight="bold")
    ax.set_xlabel("Frame Index")
    ax.set_ylabel("Reliability Metric [0.0 - 1.0]")
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="lower left", framealpha=0.9)
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "reliability_over_time.png"))
    plt.close(fig)

    # 2. Adaptive Sensor Weights Over Time
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(frames, frame_df["w_cam"], label="Camera Weight (w_cam)", color="#08306b", linewidth=2.2)
    ax.plot(frames, frame_df["w_lidar"], label="LiDAR Weight (w_lidar)", color="#006d2c", linewidth=2.2)
    ax.axhline(0.50, color="gray", linestyle="--", alpha=0.6, label="Conventional Fixed Weight (0.50)")
    ax.set_title("Adaptive Sensor Weight Allocation (Hysteresis-Smoothed)", fontweight="bold")
    ax.set_xlabel("Frame Index")
    ax.set_ylabel("Normalized Fusion Weight [0.0 - 1.0]")
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="lower left", framealpha=0.9)
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "adaptive_weights_over_time.png"))
    plt.close(fig)

    # 3. Vehicle Motion vs Sensor Reliability
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    ax1.plot(frames, frame_df["speed_mps"], label="Vehicle Speed (m/s)", color="#4a148c", linewidth=1.8)
    ax1.plot(frames, frame_df["accel_x_mps2"], label="Longitudinal Accel (m/s²)", color="#b71c1c", linewidth=1.5, linestyle="--")
    ax1.plot(frames, frame_df["yaw_rate_dps"], label="Yaw Rate (deg/s)", color="#e65100", linewidth=1.5, linestyle=":")
    ax1.set_title("Ego-Vehicle Kinematics vs. Dynamic Sensor Reliability", fontweight="bold")
    ax1.set_ylabel("Kinematic Value")
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.legend(loc="upper left")

    ax2.plot(frames, frame_df["r_cam"], label="Camera Reliability", color="#1f77b4", linewidth=1.8)
    ax2.plot(frames, frame_df["r_lidar"], label="LiDAR Reliability", color="#2ca02c", linewidth=1.8)
    ax2.set_xlabel("Frame Index")
    ax2.set_ylabel("Reliability [0.0 - 1.0]")
    ax2.grid(True, linestyle="--", alpha=0.5)
    ax2.legend(loc="lower left")
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "motion_vs_reliability.png"))
    plt.close(fig)

    # 4. Detection Confidence Over Time
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(frames, frame_df["confidence"], label="Fused Confidence", color="#8e24aa", linewidth=2.0)
    ax.plot(frames, frame_df["cam_raw_conf"], label="Raw Camera Conf", color="#1976d2", linestyle=":", alpha=0.7)
    ax.plot(frames, frame_df["lidar_raw_conf"], label="Raw LiDAR Conf", color="#388e3c", linestyle=":", alpha=0.7)
    ax.set_title("Detection Confidence Evolution Over Continuous Sequence", fontweight="bold")
    ax.set_xlabel("Frame Index")
    ax.set_ylabel("Confidence Score [0.0 - 1.0]")
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="lower left")
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "confidence_over_time.png"))
    plt.close(fig)

    # 5. Precision, Recall, and F1 Over Time
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(frames, frame_df["precision"], label="Precision", color="#1565c0", linewidth=1.8)
    ax.plot(frames, frame_df["recall"], label="Recall", color="#2e7d32", linewidth=1.8)
    ax.plot(frames, frame_df["f1_score"], label="F1-Score", color="#c62828", linewidth=2.2)
    ax.set_title("Perception Performance (Precision, Recall, F1) Over Time", fontweight="bold")
    ax.set_xlabel("Frame Index")
    ax.set_ylabel("Score [0.0 - 1.0]")
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="lower left")
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "performance_over_time.png"))
    plt.close(fig)

    # 6. Localization Error Over Time
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(frames, frame_df["loc_error_m"], label="3D Localization Error (m)", color="#d84315", linewidth=2.0)
    ax.axhline(np.mean(frame_df["loc_error_m"]), color="black", linestyle="--", label=f"Mean Error: {np.mean(frame_df['loc_error_m']):.3f} m")
    ax.set_title("Mean 3D Obstacle Localization Error Across Frames", fontweight="bold")
    ax.set_xlabel("Frame Index")
    ax.set_ylabel("Error [meters]")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "localization_error_over_time.png"))
    plt.close(fig)

    # 7. Sensor Degradation vs Fusion Performance
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    ax1.plot(frames, frame_df["blur_kernel"], label="Motion Blur Kernel", color="#3949ab", linewidth=1.8)
    ax1_twin = ax1.twinx()
    ax1_twin.plot(frames, frame_df["lidar_dropout_ratio"] * 100.0, label="LiDAR Dropout (%)", color="#e53935", linewidth=1.8, linestyle="--")
    ax1.set_title("Controlled Environmental Degradation Schedule vs. F1 Robustness", fontweight="bold")
    ax1.set_ylabel("Blur Kernel Size")
    ax1_twin.set_ylabel("LiDAR Dropout (%)")
    ax1.grid(True, linestyle="--", alpha=0.5)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1_twin.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    ax2.plot(frames, frame_df["f1_score"], label="Adaptive F1-Score", color="#00897b", linewidth=2.2)
    ax2.set_xlabel("Frame Index")
    ax2.set_ylabel("F1-Score")
    ax2.set_ylim(-0.05, 1.05)
    ax2.grid(True, linestyle="--", alpha=0.5)
    ax2.legend(loc="lower left")
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "degradation_response.png"))
    plt.close(fig)

    # 8. Temporal Tracking Consistency
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(frames, frame_df["temporal_persistence"], label="Tracklet Persistence Ratio (Hits/Age)", color="#5e35b1", linewidth=2.0)
    ax.plot(frames, frame_df["track_count"], label="Active Confirmed Tracks", color="#00acc1", linewidth=1.8, linestyle="--")
    ax.set_title("Temporal Tracking Continuity and Tracklet Persistence", fontweight="bold")
    ax.set_xlabel("Frame Index")
    ax.set_ylabel("Persistence / Count")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="lower left")
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "temporal_tracking.png"))
    plt.close(fig)

    # 9. Modality Contribution During Sensor Failure
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.stackplot(frames, frame_df["w_cam"], frame_df["w_lidar"], labels=["Camera Contribution", "LiDAR Contribution"], colors=["#90caf9", "#a5d6a7"], alpha=0.85)
    ax.set_title("Proportional Modality Contribution During Sensor Failure and Recovery", fontweight="bold")
    ax.set_xlabel("Frame Index")
    ax.set_ylabel("Relative Contribution (Sum = 1.0)")
    ax.set_ylim(0, 1.0)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "modality_contribution_during_failure.png"))
    plt.close(fig)

    # 10. Processing Time / FPS Over Time
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(frames, frame_df["fps"], label="System Throughput (FPS)", color="#00838f", linewidth=1.8)
    ax.axhline(20.0, color="crimson", linestyle="--", label="Target Rate (20 Hz)")
    ax.set_title("Real-Time Execution Profile Over Continuous Dynamic Sequence", fontweight="bold")
    ax.set_xlabel("Frame Index")
    ax.set_ylabel("Frames Per Second (FPS)")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="lower left")
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "processing_time_fps.png"))
    plt.close(fig)

    # 11. Benchmark Comparison Bar Chart across all 7 methods and conditions
    if benchmark_df is not None and not benchmark_df.empty:
        plot_benchmark_comparison_bars(benchmark_df, output_dir)

def plot_benchmark_comparison_bars(benchmark_df: pd.DataFrame, output_dir: str):
    """Plots comparative bar charts across all methods and evaluation conditions."""
    conditions = benchmark_df["condition"].unique().tolist()
    methods = benchmark_df["method"].unique().tolist()

    fig, axes = plt.subplots(2, 2, figsize=(15, 9))
    x = np.arange(len(methods))
    width = 0.15

    for i, cond in enumerate(conditions[:4]):
        sub = benchmark_df[benchmark_df["condition"] == cond]
        r = i // 2
        c = i % 2
        axes[r, c].bar(x, sub["f1_score"], width=0.6, color="steelblue")
        axes[r, c].set_title(f"F1-Score: {cond.replace('_', ' ')}", fontweight="bold")
        axes[r, c].set_ylabel("F1-Score")
        axes[r, c].set_ylim(0, 1.05)
        axes[r, c].set_xticks(x)
        axes[r, c].set_xticklabels(methods, rotation=25, ha="right", fontsize=8)
        axes[r, c].grid(True, linestyle="--", alpha=0.5)

    fig.suptitle("Comparative Evaluation Across Sensor Fusion Paradigms", fontsize=13, fontweight="bold")
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "benchmark_comparison.png"))
    plt.close(fig)
