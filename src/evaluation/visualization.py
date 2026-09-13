"""
src/evaluation/visualization.py
Publication-grade research visualization engine for sensor fusion benchmarking.

Generates the 11 specialized research figures specified in Phase 16:
1. F1 vs condition
2. Precision vs condition
3. Recall vs condition
4. Localization Error vs condition
5. Jitter vs condition
6. Latency / FPS comparison
7. Camera reliability over time
8. LiDAR reliability over time
9. Camera vs LiDAR adaptive weights
10. Reliability vs degradation
11. Ablation comparison

Outputs to results/figures/ and results/plots/.
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
        "xtick.labelsize": 8.5,
        "ytick.labelsize": 8.5,
        "legend.fontsize": 8.5,
        "figure.titlesize": 12,
        "figure.dpi": 200
    })

def plot_all_research_figures(frame_df: pd.DataFrame, benchmark_df: pd.DataFrame,
                              output_dir: str, ablation_df: pd.DataFrame = None):
    """
    Generates all 11 publication-grade figures and saves to output_dir.
    """
    os.makedirs(output_dir, exist_ok=True)
    set_plot_style()

    frames = frame_df["frame_id"].to_numpy() if frame_df is not None and not frame_df.empty else np.arange(70)

    # 1. F1 vs Condition
    if benchmark_df is not None and not benchmark_df.empty:
        plot_metric_vs_condition(benchmark_df, "f1_score", "F1-Score [0.0 - 1.0]",
                                 "Perception F1-Score Across Degradation Conditions",
                                 os.path.join(output_dir, "f1_vs_condition.png"), ylim=(0, 1.05))

    # 2. Precision vs Condition
    if benchmark_df is not None and not benchmark_df.empty:
        plot_metric_vs_condition(benchmark_df, "precision", "Precision [0.0 - 1.0]",
                                 "Object Detection Precision Across Degradation Conditions",
                                 os.path.join(output_dir, "precision_vs_condition.png"), ylim=(0, 1.05))

    # 3. Recall vs Condition
    if benchmark_df is not None and not benchmark_df.empty:
        plot_metric_vs_condition(benchmark_df, "recall", "Recall [0.0 - 1.0]",
                                 "Object Detection Recall Across Degradation Conditions",
                                 os.path.join(output_dir, "recall_vs_condition.png"), ylim=(0, 1.05))

    # 4. Localization Error vs Condition
    if benchmark_df is not None and not benchmark_df.empty:
        plot_metric_vs_condition(benchmark_df, "localization_error_m", "Mean Absolute Error [meters]",
                                 "3D Localization Error Across Degradation Conditions",
                                 os.path.join(output_dir, "localization_error_vs_condition.png"),
                                 ylim=None, exclude_camera=True)

    # 5. Jitter vs Condition
    if benchmark_df is not None and not benchmark_df.empty:
        plot_metric_vs_condition(benchmark_df, "jitter_m", "Trajectory Jitter (Std Dev) [meters]",
                                 "Temporal Trajectory Jitter Across Degradation Conditions",
                                 os.path.join(output_dir, "jitter_vs_condition.png"),
                                 ylim=None, exclude_camera=True)

    # 6. Latency / FPS Comparison
    if benchmark_df is not None and not benchmark_df.empty:
        plot_latency_fps_comparison(benchmark_df, os.path.join(output_dir, "latency_fps_comparison.png"))

    # 7. Camera Reliability Over Time
    if frame_df is not None and not frame_df.empty:
        fig, ax = plt.subplots(figsize=(9, 4))
        ax.plot(frames, frame_df["r_cam"], label="Camera Reliability (R_cam)", color="#1f77b4", linewidth=2.0)
        ax.axhline(0.70, color="green", linestyle=":", alpha=0.6, label="Healthy Threshold (0.70)")
        ax.axhline(0.40, color="orange", linestyle=":", alpha=0.6, label="Degraded Threshold (0.40)")
        ax.axhline(0.15, color="red", linestyle=":", alpha=0.6, label="Failure Threshold (0.15)")
        ax.set_title("Camera Reliability Evolution Over Time", fontweight="bold")
        ax.set_xlabel("Frame Index")
        ax.set_ylabel("Reliability Metric R_cam [0.0 - 1.0]")
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(loc="lower left")
        fig.tight_layout()
        fig.savefig(os.path.join(output_dir, "camera_reliability_over_time.png"))
        plt.close(fig)

    # 8. LiDAR Reliability Over Time
    if frame_df is not None and not frame_df.empty:
        fig, ax = plt.subplots(figsize=(9, 4))
        ax.plot(frames, frame_df["r_lidar"], label="LiDAR Reliability (R_lidar)", color="#2ca02c", linewidth=2.0)
        ax.axhline(0.70, color="green", linestyle=":", alpha=0.6, label="Healthy Threshold (0.70)")
        ax.axhline(0.40, color="orange", linestyle=":", alpha=0.6, label="Degraded Threshold (0.40)")
        ax.axhline(0.15, color="red", linestyle=":", alpha=0.6, label="Failure Threshold (0.15)")
        ax.set_title("LiDAR Reliability Evolution Over Time", fontweight="bold")
        ax.set_xlabel("Frame Index")
        ax.set_ylabel("Reliability Metric R_lidar [0.0 - 1.0]")
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(loc="lower left")
        fig.tight_layout()
        fig.savefig(os.path.join(output_dir, "lidar_reliability_over_time.png"))
        plt.close(fig)

    # 9. Camera vs LiDAR Adaptive Weights
    if frame_df is not None and not frame_df.empty:
        fig, ax = plt.subplots(figsize=(9, 4.2))
        ax.plot(frames, frame_df["w_cam"], label="Camera Weight (w_cam)", color="#0d47a1", linewidth=2.2)
        ax.plot(frames, frame_df["w_lidar"], label="LiDAR Weight (w_lidar)", color="#1b5e20", linewidth=2.2)
        ax.axhline(0.50, color="gray", linestyle="--", alpha=0.7, label="Static 50/50 Baseline")
        ax.set_title("Adaptive Sensor Weight Allocation (Hysteresis-Smoothed)", fontweight="bold")
        ax.set_xlabel("Frame Index")
        ax.set_ylabel("Normalized Weight [0.0 - 1.0]")
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(loc="lower left")
        fig.tight_layout()
        fig.savefig(os.path.join(output_dir, "camera_vs_lidar_adaptive_weights.png"))
        fig.savefig(os.path.join(output_dir, "adaptive_weights_over_time.png"))
        plt.close(fig)

    # 10. Reliability vs Degradation
    if frame_df is not None and not frame_df.empty:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
        ax1.plot(frames, frame_df["blur_kernel"], label="Camera Blur Kernel", color="#3949ab", linewidth=1.8)
        ax1_t = ax1.twinx()
        ax1_t.plot(frames, frame_df["lidar_dropout_ratio"] * 100.0, label="LiDAR Dropout (%)", color="#d32f2f", linestyle="--", linewidth=1.8)
        ax1.set_ylabel("Blur Kernel Size")
        ax1_t.set_ylabel("LiDAR Dropout (%)")
        ax1.set_title("Environmental Degradation Schedule vs. Dynamic Sensor Reliability", fontweight="bold")
        ax1.grid(True, linestyle="--", alpha=0.5)
        l1, lab1 = ax1.get_legend_handles_labels()
        l2, lab2 = ax1_t.get_legend_handles_labels()
        ax1.legend(l1 + l2, lab1 + lab2, loc="upper left")

        ax2.plot(frames, frame_df["r_cam"], label="Camera Reliability (R_cam)", color="#1976d2", linewidth=2.0)
        ax2.plot(frames, frame_df["r_lidar"], label="LiDAR Reliability (R_lidar)", color="#388e3c", linewidth=2.0)
        ax2.set_xlabel("Frame Index")
        ax2.set_ylabel("Reliability Score")
        ax2.set_ylim(-0.05, 1.05)
        ax2.grid(True, linestyle="--", alpha=0.5)
        ax2.legend(loc="lower left")
        fig.tight_layout()
        fig.savefig(os.path.join(output_dir, "reliability_vs_degradation.png"))
        plt.close(fig)

    # 11. Ablation Comparison
    if ablation_df is not None and not ablation_df.empty:
        plot_ablation_comparison(ablation_df, os.path.join(output_dir, "ablation_comparison.png"))

    # Also generate general comparative bar chart
    if benchmark_df is not None and not benchmark_df.empty:
        plot_benchmark_comparison_bars(benchmark_df, output_dir)


def plot_metric_vs_condition(benchmark_df: pd.DataFrame, metric_col: str, ylabel: str,
                             title: str, output_path: str, ylim=None, exclude_camera=False):
    """Plots comparative grouped bar chart for a single metric across conditions."""
    df = benchmark_df.copy()
    if exclude_camera:
        df = df[df["method"] != "Camera-Only"]

    conditions = df["condition"].unique()
    methods = df["method"].unique()

    fig, ax = plt.subplots(figsize=(11, 5))
    x = np.arange(len(conditions))
    n_methods = len(methods)
    bar_width = 0.80 / max(1, n_methods)

    # Color palette
    cmap = plt.get_cmap("tab10")

    for idx, method in enumerate(methods):
        sub = df[df["method"] == method]
        vals = []
        for cond in conditions:
            row = sub[sub["condition"] == cond]
            val = row[metric_col].values[0] if not row.empty and row[metric_col].values[0] is not None else 0.0
            vals.append(val if not pd.isna(val) else 0.0)
        offset = (idx - n_methods / 2.0 + 0.5) * bar_width
        ax.bar(x + offset, vals, width=bar_width, label=method, color=cmap(idx % 10), edgecolor="black", linewidth=0.5)

    ax.set_title(title, fontweight="bold")
    ax.set_ylabel(ylabel)
    ax.set_xticks(x)
    ax.set_xticklabels([c.replace("_", " ") for c in conditions], rotation=20, ha="right")
    if ylim:
        ax.set_ylim(ylim)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="upper right", framealpha=0.9)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def plot_latency_fps_comparison(benchmark_df: pd.DataFrame, output_path: str):
    """Plots comparative latency and FPS bar charts."""
    clean_df = benchmark_df[benchmark_df["condition"] == "Clean_Nominal"]
    if clean_df.empty:
        clean_df = benchmark_df.groupby("method").mean(numeric_only=True).reset_index()

    methods = clean_df["method"].tolist()
    latency = clean_df["latency_ms"].tolist()
    fps = clean_df["fps"].tolist()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
    x = np.arange(len(methods))

    ax1.barh(x, latency, color="#37474f", edgecolor="black", height=0.6)
    ax1.set_yticks(x)
    ax1.set_yticklabels(methods)
    ax1.set_xlabel("Processing Latency (ms)")
    ax1.set_title("Per-Frame Processing Latency", fontweight="bold")
    ax1.grid(True, linestyle="--", alpha=0.5)

    ax2.barh(x, fps, color="#00838f", edgecolor="black", height=0.6)
    ax2.axvline(20.0, color="red", linestyle="--", label="Target Rate (20 Hz)")
    ax2.set_yticks(x)
    ax2.set_yticklabels([""] * len(methods))
    ax2.set_xlabel("Throughput (Frames Per Second)")
    ax2.set_title("Perception Pipeline FPS", fontweight="bold")
    ax2.grid(True, linestyle="--", alpha=0.5)
    ax2.legend(loc="lower right")

    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def plot_ablation_comparison(ablation_df: pd.DataFrame, output_path: str):
    """Plots ablation study performance across components."""
    variants = ablation_df["variant"].unique()
    conditions = ablation_df["condition"].unique()

    fig, ax = plt.subplots(figsize=(11, 5))
    x = np.arange(len(variants))
    n_conds = len(conditions)
    bar_width = 0.80 / max(1, n_conds)

    cmap = plt.get_cmap("Set2")

    for idx, cond in enumerate(conditions):
        sub = ablation_df[ablation_df["condition"] == cond]
        f1s = [sub[sub["variant"] == v]["f1_score"].values[0] if not sub[sub["variant"] == v].empty else 0.0 for v in variants]
        offset = (idx - n_conds / 2.0 + 0.5) * bar_width
        ax.bar(x + offset, f1s, width=bar_width, label=cond.replace("_", " "), color=cmap(idx % 8), edgecolor="black", linewidth=0.5)

    ax.set_title("Ablation Study: Progressive Component Contribution to F1-Score", fontweight="bold")
    ax.set_ylabel("F1-Score [0.0 - 1.0]")
    ax.set_xticks(x)
    ax.set_xticklabels([v.replace("_", " ") for v in variants], rotation=25, ha="right")
    ax.set_ylim(0, 1.05)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="lower left", framealpha=0.9)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def plot_benchmark_comparison_bars(benchmark_df: pd.DataFrame, output_dir: str):
    """Plots comparative overview grid across methods and conditions."""
    conditions = benchmark_df["condition"].unique()[:4]
    methods = benchmark_df["method"].unique()

    fig, axes = plt.subplots(2, 2, figsize=(14, 8))
    x = np.arange(len(methods))

    for i, cond in enumerate(conditions):
        sub = benchmark_df[benchmark_df["condition"] == cond]
        r = i // 2
        c = i % 2
        f1_vals = [sub[sub["method"] == m]["f1_score"].values[0] if not sub[sub["method"] == m].empty else 0.0 for m in methods]
        axes[r, c].bar(x, f1_vals, width=0.6, color="#1976d2", edgecolor="black", linewidth=0.5)
        axes[r, c].set_title(f"Condition: {cond.replace('_', ' ')}", fontweight="bold")
        axes[r, c].set_ylabel("F1-Score")
        axes[r, c].set_ylim(0, 1.05)
        axes[r, c].set_xticks(x)
        axes[r, c].set_xticklabels(methods, rotation=25, ha="right", fontsize=8)
        axes[r, c].grid(True, linestyle="--", alpha=0.5)

    fig.suptitle("Overview: Perception F1-Score Across Benchmark Regimes", fontsize=12, fontweight="bold")
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "benchmark_comparison.png"))
    plt.close(fig)
