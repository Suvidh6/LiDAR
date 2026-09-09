# IMU-Assisted Temporal Reliability-Aware Camera-LiDAR Sensor Fusion for Robust Autonomous-Driving Perception

A research-oriented multimodal perception and sensor fusion framework combining **RGB Camera, 64-channel LiDAR, and 6-DoF IMU telemetry** in **CARLA 0.9.16**. The system investigates the integration of **IMU-based ego-motion compensation**, **temporal multi-frame tracking**, and **multi-criteria physical reliability estimation** to maintain robust obstacle detection across continuous dynamic driving maneuvers and controlled sensor degradation regimes.

---

## Overview

Autonomous vehicle perception systems frequently encounter adverse environmental conditions—such as optical motion blur, darkness, rain-induced LiDAR beam attenuation, and sensor hardware degradation. Conventional late-fusion architectures with static weights (e.g., 50/50 averaging) cannot dynamically adapt when one modality fails, leading to corrupted confidence scores and localization dropouts.

This research framework investigates an end-to-end perception architecture that:
1. **Compensates for ego-motion** by warping historical point clouds into the current coordinate frame using gravity-corrected IMU kinematics ($SE(3)$).
2. **Maintains temporal context** using an IMU-propagated Kalman tracklet lifecycle with a multi-frame confirmation gate ($\text{min\_hits} \ge 2$) to reject transient false returns.
3. **Dynamically estimates sensor reliability** from measurable physical indicators (modified Laplacian sharpness, illumination deviation, range-normalized LiDAR point density, dynamic vehicle agitation, and cross-modal spatial agreement).
4. **Allocates normalized dynamic weights** ($w_{\text{cam}} + w_{\text{lidar}} = 1.0$) with exponential hysteresis smoothing to ensure stable modal transitions without high-frequency weight oscillations.

---

## Research Motivation

Multimodal perception is essential for level 4/5 autonomous driving. While cameras provide dense semantic information and LiDAR provides precise 3D spatial geometry, both modalities possess distinct physical failure modes:
- **Cameras** fail under rapid vehicle rotation (motion blur), low illumination (night/tunnels), and atmospheric scattering (fog/glare).
- **LiDARs** suffer beam attenuation in heavy rain, spray backscatter, and distance-dependent beam divergence ($1/d$).
- **Ego-vehicle motion** introduces spatial smearing and coordinate frame misalignment between consecutive time steps.

This framework explores how high-rate 6-DoF IMU kinematics can simultaneously assist spatial point cloud registration and dynamic reliability gating, enabling safe degradation hand-off between camera and LiDAR streams.

---

## Problem Definition

Given synchronized multi-sensor observations at time step $t$:
$$\mathcal{Z}_t = \left\{ \mathbf{I}_t \in \mathbb{R}^{H \times W \times 3}, \; \mathcal{P}_t \in \mathbb{R}^{N \times 3}, \; \mathbf{u}_{\text{imu}, t} = (\mathbf{a}_t, \boldsymbol{\omega}_t) \right\}$$

The objective is to estimate the set of 3D obstacle states $\mathcal{X}_t = \{\mathbf{x}_i = (x, y, z, \text{class}, c)_i\}$ such that:
1. Object localization remains accurate across dynamic maneuvers without coordinate frame smearing.
2. Transient single-frame noise is suppressed through multi-frame temporal confirmation.
3. Modality weights $w_{\text{cam}}(t)$ and $w_{\text{lidar}}(t)$ adaptively shift toward the healthy sensor stream when one modality degrades, while overall confidence $c$ is appropriately depressed when both modalities fail.

---

## Core Architecture

The architecture operates in a synchronous closed loop at 20 Hz ($\Delta t = 0.05\,\text{s}$):

```
                        CARLA 0.9.16 Synchronous Simulator (20 Hz)
                                            │
               ┌────────────────────────────┼────────────────────────────┐
               ▼                            ▼                            ▼
          RGB Camera                   64-Beam LiDAR                  6-DoF IMU
        800x600, FOV 90°             20 Hz, 3000 pts/frame         Specific Force + Gyro
               │                            │                            │
               ▼                            │                            ▼
       YOLOv8 2D Detector                   │                    Gravity Removal &
      + Sharpness & Illum                   │                    SE(3) Transform T_ego
               │                            │                            │
               │                            ▼                            │
               │                    RANSAC Ground Cut                    │
               │                    & DBSCAN Clustering                  │
               │                            │                            │
               └─────────────┬──────────────┘                            │
                             ▼                                           │
             Spatial Cross-Modal Association                             │
             (3D-to-2D Perspective Projection K)                         │
                             │                                           │
                             ▼                                           │
                Temporal Multi-Frame Gating ◄────────────────────────────┘
                (IMU-Warped Kalman Tracker)
                             │
                             ▼
             Dynamic Reliability Estimator
             - Sharpness & Illumination Deviation
             - Range-Calibrated Point Density (1/d)
             - Vehicle Dynamic Agitation Penalty
             - Cross-Modal Spatial Agreement
                             │
                             ▼
             Reliability-Aware Adaptive Fusion
             - Exponential Hysteresis Weight Smoothing
             - Health States (HEALTHY, DEGRADED, FAILED)
             - Trend Derivatives (ΔR / Δt)
                             │
                             ▼
                    Calibrated Fused Detections
```

---

## System Components

### 1. IMU Motion Processing (`src/sensors/imu.py`)
- Isolates gravity $\mathbf{g} = [0, 0, -9.81]^T\,\text{m/s}^2$ from measured specific force:
  $$\mathbf{a}_{\text{linear}} = [f_x, \; f_y, \; f_z - 9.81]^T\,\text{m/s}^2$$
- Integrates angular velocity $\boldsymbol{\omega}$ over $\Delta t = 0.05\,\text{s}$ to produce $\Delta R \in SO(3)$.
- Forms the inter-frame rigid transformation $T_{\text{ego}} = \begin{bmatrix} \Delta R & \Delta \mathbf{t} \\ \mathbf{0}^T & 1 \end{bmatrix} \in SE(3)$.
- Classifies vehicle motion states (`STATIONARY`, `ACCELERATING`, `BRAKING`, `TURNING_LEFT`, `TURNING_RIGHT`, `CRUISING`).

### 2. Motion Compensation & Spatial Association (`src/fusion/`)
- Warps point clouds between time steps via $\mathbf{p}_{t-1 \to t} = \Delta R^T (\mathbf{p}_{t-1} - \Delta \mathbf{t})$.
- Projects 3D cluster bounding corners to optical camera coordinates using calibration matrix $K$:
  $$K = \begin{bmatrix} 400.0 & 0.0 & 400.0 \\ 0.0 & 400.0 & 300.0 \\ 0.0 & 0.0 & 1.0 \end{bmatrix}$$
- Associates 2D camera detections and 3D LiDAR clusters via Hungarian bipartite matching on bounding box IoU.

### 3. Temporal Multi-Frame Tracking (`src/fusion/temporal_tracker.py`)
- Propagates tracklet states using $T_{\text{ego}}$ and applies a 6-DoF Kalman filter ($[x, y, z, v_x, v_y, v_z]^T$).
- Enforces an empirical confirmation gate ($\text{min\_hits} \ge 2$), eliminating unconfirmed single-frame false alarms.
- Computes persistence ratio ($\text{hits} / \text{age}$) to reward temporally stable obstacles.

### 4. Dynamic Reliability Estimation (`src/fusion/reliability_estimation.py`)
- **Camera Reliability ($R_{\text{cam}} \in [0.01, 0.99]$):**
  $$R_{\text{cam}} = c_{\text{det}} \cdot \psi_{\text{visual}} \cdot \psi_{\text{range}} \cdot \psi_{\text{motion}} \cdot \tau_{\text{temp}}$$
  where $\psi_{\text{visual}} = 0.5 \psi_{\text{sharp}} + 0.5 \psi_{\text{illum}}$, $\psi_{\text{range}} = \exp(-d / 45)$, and $\psi_{\text{motion}} = \exp(-0.08 (\|\mathbf{a}_{\text{lin}}\| + 5\|\boldsymbol{\omega}\|))$.
- **LiDAR Reliability ($R_{\text{lidar}} \in [0.01, 0.99]$):**
  $$R_{\text{lidar}} = (0.50 \gamma_{\text{geom}} + 0.50 \rho_{\text{density}}) \cdot \psi_{\text{health}} \cdot \tau_{\text{temp}}$$
  where $\rho_{\text{density}} = \min(1.0, N_{\text{cluster}} / (400 / (d + 1)))$ calibrates point density against physical beam divergence.
- **Health Classification:** Categorizes sensors as `HEALTHY` ($R \ge 0.70$), `DEGRADED` ($0.40 \le R < 0.70$), `SEVERELY_DEGRADED` ($0.15 \le R < 0.40$), or `FAILED` ($R < 0.15$).
- **Trend Derivatives:** Calculates $\dot{R} = \Delta R / \Delta t$ to identify `RAPIDLY_DEGRADING`, `DEGRADING`, `STABLE`, or `IMPROVING` operational trajectories.
- **Hysteresis Smoothing:** Filters raw weights with exponential parameter $\alpha = 0.65$ to prevent frame-to-frame switching chatter.

---

## Dynamic Degradation Framework

Rather than testing disconnected static conditions, the experimental framework executes a **continuous time-varying dynamic scenario** across the driving sequence:

```
[Frames 0-14]  Nominal baseline (clean operation)
      │
[Frames 15-24] Progressive camera motion blur ramp (Kernel 3x3 to 21x21) + dimming
      │
[Frames 25-34] Camera recovery to nominal sharpness and lighting
      │
[Frames 35-44] Progressive LiDAR beam attenuation (10% to 85% dropout) + backscatter spray
      │
[Frames 45-54] LiDAR recovery to nominal density
      │
[Frames 55-59] Severe camera darkness (0.10x illumination factor, tunnel plunge)
      │
[Frames 60-64] High-motion vehicle agitation (sharp turn + braking maneuver)
      │
[Frames 65-69] Combined dual degradation (blur + 70% dropout) & final recovery
```

---

## Baselines & Comparators

The framework benchmarks 7 distinct perception paradigms under identical inputs:
1. **Camera-Only (YOLOv8):** Vision-only detection without 3D spatial returns.
2. **LiDAR-Only (RANSAC + DBSCAN):** Geometry-only clustering without visual semantics.
3. **Late Fusion (Fixed 50/50):** Conventional static decision fusion assigning equal weight.
4. **Dempster-Shafer Evidential Fusion:** Simplified implementation inspired by Shafer's belief mass combination.
5. **Distance-Adaptive Fusion:** Simplified implementation inspired by heuristic range weighting.
6. **Temporal Multi-Frame Fusion:** Multi-frame Kalman tracking without reliability-based weighting.
7. **Proposed Reliability-Aware Adaptive Fusion:** Complete architecture integrating physical metrics, IMU motion awareness, hysteresis smoothing, and fail-safe fallbacks.

---

## Experimental Results

### 1. Inter-Frame Point Cloud Alignment Verification
Across 69 consecutive dynamic transitions, IMU ego-motion compensation consistently improves spatial registration:

| Metric | Raw (Uncompensated) | IMU-Compensated | Improvement |
| :--- | :---: | :---: | :---: |
| **Mean Absolute Error (MAE)** | 0.0964 m | 0.0888 m | **7.88%** error reduction |
| **Mean Squared Error (MSE)** | 0.0383 m² | 0.0315 m² | **17.75%** error reduction |
| **Peak Alignment Correction** | 0.4280 m² | 0.2810 m² | **34.35%** error reduction |
| **Temporal Displacement Jitter** | 0.8426 m | 0.5099 m | **39.48%** jitter reduction |

### 2. Multi-Condition Benchmark Summary

| Evaluation Regime | Perception Paradigm | Precision | Recall | F1-Score | Loc Error (m) | Fused Confidence | Throughput (FPS) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Clean Nominal** | LiDAR-Only | 0.9931 | 0.9775 | 0.9852 | 0.0137 | 0.2645 | 13.0 |
| | Late Fusion (Fixed) | 0.5636 | 0.9775 | 0.7150 | 0.0137 | 0.1862 | 12.9 |
| | Dempster-Shafer | 0.9931 | 0.9775 | 0.9852 | 0.0137 | 0.3948 | 12.9 |
| | Distance-Adaptive | 0.9931 | 0.9775 | 0.9852 | 0.0137 | 0.2334 | 13.0 |
| | Temporal Fusion | 0.3168 | 0.9752 | 0.4782 | 0.4565 | 0.1720 | 12.5 |
| | **Proposed Adaptive Fusion** | **0.9931** | **0.9775** | **0.9852** | **0.0137** | **0.2468** | **12.9** |
| **Camera Degraded** | LiDAR-Only | 0.9709 | 0.9841 | 0.9774 | 0.0179 | 0.2597 | 13.9 |
| (Motion Blur 19x19) | Late Fusion (Fixed) | 0.9709 | 0.9841 | 0.9774 | 0.0179 | 0.1528 | 13.9 |
| | **Proposed Adaptive Fusion** | **0.9709** | **0.9841** | **0.9774** | **0.0179** | **0.2452** | **13.8** |
| **LiDAR Degraded** | LiDAR-Only | 0.2195 | 0.0205 | 0.0376 | 1.5757 | 0.3960 | 12.3 |
| (85% Beam Dropout) | Late Fusion (Fixed) | 0.0241 | 0.0205 | 0.0222 | 1.5757 | 0.2276 | 12.3 |
| | **Proposed Adaptive Fusion** | **0.4000** | **0.0091** | **0.0179** | **1.1631** | **0.0673** | **12.3** |
| **Camera Outage** | Late Fusion (Fixed) | 0.9776 | 0.9932 | 0.9853 | 0.0151 | 0.1535 | 17.3 |
| (Blackout) | **Proposed Adaptive Fusion** | **0.9776** | **0.9932** | **0.9853** | **0.0151** | **0.2459** | **17.2** |

*(Detailed numerical logs and per-frame CSV files are available in `results/metrics/`)*.

---

## Project Structure

```
D:\SensorFusionResearch\
├── config/                                    # Centralized JSON configuration files
│   ├── default_config.json                    # Sensor geometry, thresholds, and tracker parameters
│   ├── degradation_config.json                # Time-varying progressive degradation schedule
│   └── experiment_config.json                 # Execution parameters, paths, and seeds
│
├── src/                                       # Modular research architecture
│   ├── sensors/                               # Sensor kinematics, modeling, and acquisition
│   │   ├── camera.py                          # Pinhole intrinsics K and 3D-to-2D projection
│   │   ├── lidar.py                           # Point cloud I/O and spatial ROI filtering
│   │   ├── imu.py                             # Gravity subtraction, specific force, SE(3) transforms
│   │   └── synchronization.py                 # CARLA lockstep multi-sensor synchronous recorder
│   ├── perception/                            # Single-modality detector engines
│   │   ├── camera_detector.py                 # YOLOv8 2D detector & Laplacian/luminance quality
│   │   └── lidar_detector.py                  # RANSAC ground extraction & Euclidean DBSCAN clustering
│   ├── fusion/                                # Cross-modal fusion, compensation, tracking, and reliability
│   │   ├── spatial_association.py             # Hungarian cross-modal 2D IoU matching
│   │   ├── motion_compensation.py             # SE(3) point cloud warping & KD-tree alignment metrics
│   │   ├── temporal_tracker.py                # Multi-frame Kalman tracklet lifecycle & gating
│   │   ├── reliability_estimation.py          # Physical reliability, health states, trends, smoothing
│   │   └── adaptive_fusion.py                 # Dynamic weighting & baseline comparator engines
│   ├── evaluation/                            # Benchmarking, synthetic degradation, and validation
│   │   ├── degradation.py                     # Synthetic blur, underexposure, dropout, noise, outage
│   │   ├── scenarios.py                       # Continuous dynamic progressive degradation engine
│   │   ├── metrics.py                         # Precision, recall, F1, localization error metrics
│   │   ├── benchmarking.py                    # Multi-paradigm comparator harness
│   │   └── visualization.py                   # 10 Dynamic research plots rendering engine
│   └── utils/                                 # Shared modular utilities
│       ├── paths.py                           # Reliable cross-platform path resolution
│       ├── logging.py                         # Structured research logger
│       ├── configuration.py                   # Schema-validated configuration loader
│       └── reproducibility.py                 # Deterministic seed setting & metadata provenance
│
├── experiments/                               # Experiment runners and scenario definitions
│   ├── run_full_experiment.py                 # Master experiment runner (Dynamic + Benchmark matrix)
│   ├── run_dynamic_experiment.py              # Continuous frame-by-frame dynamic experiment runner
│   └── scenarios/                             # Scenario definitions
│       └── dynamic_scenario.py
│
├── tests/                                     # Automated unit and integration test suite
│   ├── test_sensors.py                        # Intrinsics, IMU gravity, point cloud ROI tests
│   ├── test_perception.py                     # YOLOv8 quality checks & DBSCAN cluster tests
│   ├── test_fusion.py                         # IoU association, warping, tracking, reliability tests
│   ├── test_utils.py                          # Config loading, path resolution, reproducibility tests
│   └── test_carla_connection.py               # Integration test for CARLA simulation server availability
│
├── docs/                                      # Theoretical and technical documentation
│   ├── architecture.md                        # Component architecture and sensor specifications
│   ├── experimental_protocol.md               # Formal experimental protocol and metric definitions
│   ├── mathematical_formulations.md           # Mathematical derivations, coordinates, kinematics
│   └── technical_notes.md                     # Engineering trade-offs, limitations, literature context
│
├── data/                                      # Recorded multi-sensor datasets (git-ignored)
│   └── dynamic_dataset/                       # 70 synchronized frames @ 20 Hz
│
├── results/                                   # Evaluation metrics & publication figures
│   ├── metrics/                               # Numerical CSV and JSON outputs
│   └── plots/                                 # 10 Publication-quality time-series and comparative figures
│
├── run_full_experiment.py                     # Top-level entry point: complete experimental pipeline
├── run_tests.py                               # Top-level entry point: automated test suite
├── requirements.txt                           # Production environment dependencies
└── .gitignore                                 # Production exclusion rules
```

---

## Installation & Setup

### Prerequisites
- Windows 10/11 or Ubuntu 20.04/22.04 LTS
- Python 3.10 to 3.12
- CARLA Simulator 0.9.16 (optional for live acquisition; offline dataset provided)

### Environment Setup
```powershell
# Clone the repository
git clone https://github.com/Suvidh6/LiDAR.git
cd LiDAR

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # On Linux: source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Testing

Run the automated test suite to verify sensor models, perception detectors, fusion logic, and configuration loading:
```powershell
python run_tests.py
```

Expected output:
```
=================================================================
      RUNNING UNIFIED SENSOR FUSION TEST SUITE
=================================================================
--- 1. Sensor & Kinematic Tests ---
test_imu_kinematics: PASSED
test_camera_model: PASSED
test_pointcloud_io: PASSED
--- 2. Perception & Detector Tests ---
test_camera_detector_quality: PASSED
test_lidar_clustering: PASSED
--- 3. Multimodal Fusion Tests ---
test_spatial_association_iou: PASSED
test_motion_compensator: PASSED
test_temporal_tracker: PASSED
test_sensor_health_and_trend: PASSED
test_reliability_and_adaptive_fusion: PASSED
--- 4. Configuration, Path & Utility Tests ---
test_paths_and_configs: PASSED
test_reproducibility: PASSED
--- 5. Simulator Connection Check ---
CARLA connection SUCCESSFUL! Connected to map: Carla/Maps/Town10HD_Opt
=================================================================
      ALL UNIT AND INTEGRATION TESTS PASSED!
=================================================================
```

---

## Running the System

Execute the complete master experiment pipeline:
```powershell
python run_full_experiment.py
```

This single command:
1. Executes the continuous dynamic scenario frame-by-frame with time-varying degradation.
2. Evaluates all 7 baseline perception paradigms across 5 degradation regimes.
3. Generates all 10 dynamic time-series research plots in `results/plots/`.
4. Saves detailed frame-level and benchmark metrics in `results/metrics/`.
5. Logs experiment provenance metadata (`experiment_metadata.json`).

To run only the continuous dynamic experiment:
```powershell
python -m experiments.run_dynamic_experiment
```

---

## Generated Research Figures (`results/plots/`)

The framework automatically outputs 10 specialized figures:
1. `reliability_over_time.png`: Camera vs. LiDAR physical reliability across time.
2. `adaptive_weights_over_time.png`: Hysteresis-smoothed adaptive weights ($w_{\text{cam}}$ vs. $w_{\text{lidar}}$).
3. `motion_vs_reliability.png`: Vehicle kinematics (speed, acceleration, yaw rate) vs. reliability.
4. `confidence_over_time.png`: Calibrated fused confidence vs. raw modality confidences.
5. `performance_over_time.png`: Precision, Recall, and F1-score across continuous degradation.
6. `localization_error_over_time.png`: Mean 3D obstacle localization error across frames.
7. `degradation_response.png`: Degradation timeline (blur kernel, dropout ratio) vs. F1 robustness.
8. `temporal_tracking.png`: Tracklet persistence ratio and active confirmed track counts.
9. `modality_contribution_during_failure.png`: Proportional stack-plot of camera and LiDAR contribution.
10. `processing_time_fps.png`: Per-frame inference latency and real-time execution throughput (FPS).

---

## Research Status

### Verified & Implemented
- Synchronized lockstep multi-sensor data acquisition in CARLA 0.9.16 (Camera + LiDAR + IMU at 20 Hz).
- Inertial gravity decomposition and $SE(3)$ inter-frame point cloud motion compensation.
- Temporal Kalman tracking with empirical multi-frame confirmation gating ($\text{min\_hits} \ge 2$).
- Multi-criteria physical reliability estimation (Laplacian sharpness, illumination, range-normalized density, vehicle dynamic agitation).
- Dynamic sensor health classification (`HEALTHY`, `DEGRADED`, `SEVERELY_DEGRADED`, `FAILED`).
- Dynamic reliability trend tracking ($\Delta R / \Delta t$) and exponential weight hysteresis smoothing.
- Continuous time-varying degradation scenario engine and automated 10-figure visualization suite.
- Comparative benchmark matrix across 7 perception paradigms and 5 degradation conditions.

### Under Active Investigation
- Systematic literature-gap analysis against modern learned 3D multimodal backbones (e.g., BEVFusion, TransFusion).
- Quantitative ablation of individual reliability terms under real-world precipitation datasets (CADC, nuScenes-Foggy).
- Real-time closed-loop navigation coupling to measure safety metrics (minimum time-to-collision, intervention rates).

---

## Limitations

1. **Dead-Reckoning Drift:** Inter-frame IMU double integration over $\Delta t = 50\,\text{ms}$ is accurate for local scan registration, but accumulates quadratic drift ($O(t^2)$) over multi-second horizons without wheel odometry or absolute reference.
2. **Simplified 3D Detector:** LiDAR obstacle extraction utilizes RANSAC ground plane segmentation and Euclidean DBSCAN clustering rather than learned 3D anchor heads (e.g., PointPillars).
3. **Simulation-to-Real Domain Gap:** CARLA synthetic sensors do not replicate complex physical lens flare, water droplet refraction, or rolling-shutter artifacts.
4. **Proxy vs. Ground-Truth Metrics:** In real-world adverse weather where clean ground-truth scans are unavailable, system reliability serves as an operational proxy rather than a true ground-truth accuracy measure.

---

## Project Metadata

- **Project Lead:** Chiranthan Suvidh
- **Repository:** [https://github.com/Suvidh6/LiDAR](https://github.com/Suvidh6/LiDAR)
- **Framework:** PyTorch, Ultralytics YOLOv8, Open3D, CARLA Python API
- **License:** MIT License
