# System Architecture & Component Specification

This document details the software architecture, data flow, synchronization mechanisms, and component interfaces of the **IMU-Assisted Temporal Reliability-Aware Multimodal Sensor Fusion** perception framework.

---

## 1. Top-Level Architectural Pipeline

The system is organized into a modular layered architecture executing lockstep synchronous cycles in **CARLA 0.9.16**:

```
[CARLA Simulator (20 Hz)]
      │
      ├──────────────────────┬──────────────────────┐
      ▼                      ▼                      ▼
  [RGB Camera]          [64-Beam LiDAR]         [6-DoF IMU]
      │                      │                      │
      ▼                      ▼                      ▼
[2D YOLOv8 Detector]   [3D RANSAC + DBSCAN]   [Specific Force Gravity Removal]
+ Image Quality        + Spatial BBoxes       + Inter-Frame SE(3) Transform T_ego
      │                      │                      │
      └──────────┬───────────┘                      │
                 ▼                                  │
  [Spatial Cross-Modal Association]                 │
  (3D-to-2D Perspective Projection via K)           │
                 │                                  │
                 ▼                                  │
  [Temporal Multi-Frame Gating] ◄───────────────────┘
  (SE(3) Warped Tracklets + Kalman Filter)
                 │
                 ▼
  [Dynamic Reliability Estimator]
  - Optical Laplacian Sharpness & Illumination
  - LiDAR Range-Normalized Density (1/d)
  - Vehicle Kinematic Agitation Penalty
  - Cross-Modal Spatial Agreement
                 │
                 ▼
  [Reliability-Aware Adaptive Fusion Engine]
  - Exponential Hysteresis Weight Smoothing
  - Health Classification (HEALTHY, DEGRADED, SEVERELY_DEGRADED, FAILED)
  - Dynamic Derivative Trend Tracking
  - Fail-Safe Fallback Preservation
                 │
                 ▼
  [Perception Telemetry & Metric Logging]
```

---

## 2. Sensor Specifications & Verified Mounting

All measurements are expressed in the CARLA Unreal Engine left-handed vehicle coordinate frame ($+X$: Forward, $+Y$: Right, $+Z$: Up):

| Sensor Modality | Mounting Position $(X, Y, Z)$ [m] | Orientation $(\text{Roll}, \text{Pitch}, \text{Yaw})$ | Operational Specifications |
| :--- | :---: | :---: | :--- |
| **RGB Camera** | $[1.5, \; 0.0, \; 2.4]$ | $[0^\circ, \; 0^\circ, \; 0^\circ]$ | Resolution: $800 \times 600\,\text{px}$, Horizontal FOV: $90^\circ$, Pinhole $f_x=f_y=400.0\,\text{px}$ |
| **LiDAR** | $[0.0, \; 0.0, \; 2.5]$ | $[0^\circ, \; 0^\circ, \; 0^\circ]$ | 64 Channels, Range: $50\,\text{m}$, Rate: $130{,}000\,\text{pts/s}$, $10\,\text{Hz}$ spin ($\approx 2500\text{--}3000\,\text{pts/frame}$) |
| **IMU** | $[0.0, \; 0.0, \; 2.0]$ | $[0^\circ, \; 0^\circ, \; 0^\circ]$ | 6-DoF Accelerometer ($m/s^2$) + Gyroscope ($rad/s$), Gravity: $9.81\,\text{m/s}^2$ downward |

---

## 3. Subsystem Breakdown

### 3.1 Sensor Acquisition & Synchronous Engine (`src/sensors/`)
- `synchronization.py`: Spawns vehicle and sensor actors in CARLA, configures fixed time-step $\Delta t = 0.05\,\text{s}$ ($20\,\text{Hz}$), and synchronizes data retrieval using FIFO queues.
- `camera.py`: Encapsulates camera intrinsics matrix $K$ and optical frame basis transforms.
- `lidar.py`: Manages PLY point cloud loading, writing, and Region of Interest (ROI) filtering.
- `imu.py`: Isolates gravity from measured specific force, estimates $SO(3)$ rotation increments and translation displacements, and produces inter-frame $SE(3)$ transform $T_{\text{ego}}$.

### 3.2 Single-Modality Perception (`src/perception/`)
- `camera_detector.py`: Evaluates 2D bounding boxes using YOLOv8 (`yolov8n.pt`) and calculates modified Laplacian variance (optical sharpness) and mean luminance (illumination quality).
- `lidar_detector.py`: Implements RANSAC ground plane removal followed by Euclidean DBSCAN clustering to identify 3D obstacle bounding boxes, centroids, volumes, and aspect ratios.

### 3.3 Multimodal Fusion & Temporal Tracking (`src/fusion/`)
- `spatial_association.py`: Projects 3D cluster corners into the 2D optical frame using camera calibration matrix $K$ and performs Hungarian IoU cross-modal matching.
- `motion_compensation.py`: Warps previous scan point clouds into current frame coordinates via $T_{\text{ego}}^{-1}$.
- `temporal_tracker.py`: Tracks 3D objects over a sliding window with Kalman filtering, IMU ego-motion propagation, and an empirical multi-frame confirmation gate ($\text{min\_hits} \ge 2$).
- `reliability_estimation.py`: Evaluates physical health, dynamic trend derivatives, and cross-modal consistency.
- `adaptive_fusion.py`: Computes normalized dynamic weights $w_{\text{cam}} + w_{\text{lidar}} = 1.0$ with hysteresis smoothing and fail-safe fallbacks.

### 3.4 Evaluation & Scenarios (`src/evaluation/`)
- `degradation.py`: Injects physically calibrated optical blur, underexposure, LiDAR beam dropout, and backscatter spray.
- `scenarios.py`: Orchestrates time-varying progressive degradation transitions.
- `metrics.py`: Computes ground-truth matched precision, recall, F1-score, and 3D Euclidean localization error.
- `visualization.py`: Renders time-series and comparative research figures.
