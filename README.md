# IMU-Assisted Temporal Reliability-Aware Camera-LiDAR Sensor Fusion for Robust Autonomous-Driving Perception

[![CARLA 0.9.16](https://img.shields.io/badge/CARLA-0.9.16-blue.svg)](https://carla.org/)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-green.svg)](https://www.python.org/)
[![PyTorch YOLOv8](https://img.shields.io/badge/PyTorch-YOLOv8-orange.svg)](https://ultralytics.com/)
[![License MIT](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

An end-to-end, unified perception research framework combining **RGB Camera, 64-channel LiDAR, and 6-DoF IMU telemetry** in CARLA 0.9.16. The architecture unifies **IMU-based ego-motion compensation**, **temporal multi-frame tracklet filtering**, and **multi-criteria reliability-aware adaptive fusion** to maintain robust obstacle detection across clean and severely degraded environmental operating conditions.

---

## 1. System Architecture

The unified perception pipeline operates in a closed lockstep synchronous loop:

```
                      ┌─────────────────────────────────────────────────────────────┐
                      │              CARLA 0.9.16 Synchronous Simulator             │
                      │               Fixed Delta-t: 0.05 s (20 Hz)                 │
                      └──────────────────────────────┬──────────────────────────────┘
                                                     │
               ┌─────────────────────────────────────┼─────────────────────────────────────┐
               ▼                                     ▼                                     ▼
      ┌─────────────────┐                  ┌──────────────────┐                  ┌──────────────────┐
      │   RGB Camera    │                  │  64-Beam LiDAR   │                  │    6-DoF IMU     │
      │  800x600, FOV 90│                  │ 20 Hz, 3000 pts  │                  │ Accel + Gyro     │
      └────────┬────────┘                  └────────┬─────────┘                  └────────┬─────────┘
               │                                    │                                     │
               ▼                                    │                                     ▼
      ┌─────────────────┐                           │                            ┌──────────────────┐
      │  YOLOv8 2D BBox │                           │                            │ Gravity Removal  │
      │ + Image Quality │                           │                            │ & SE(3) Ego T_ego│
      └────────┬────────┘                           │                            └────────┬─────────┘
               │                                    │                                     │
               │                                    ▼                                     │
               │                           ┌──────────────────┐                           │
               │                           │ RANSAC Ground Cut│                           │
               │                           │ & DBSCAN 3D BBox │                           │
               │                           └────────┬─────────┘                           │
               │                                    │                                     │
               └─────────────────┬──────────────────┘                                     │
                                 ▼                                                        │
                      ┌──────────────────────────────────────┐                            │
                      │ Spatial Cross-Modal Association      │                            │
                      │ 3D-to-2D Perspective Projection (K)  │                            │
                      └──────────────────┬───────────────────┘                            │
                                         │                                                │
                                         ▼                                                │
                      ┌──────────────────────────────────────┐                            │
                      │ Temporal Multi-Frame Gating          │◄───────────────────────────┘
                      │ IMU-Warped Tracklets + Kalman Filter │  (Warping P_prev into P_curr)
                      └──────────────────┬───────────────────┘
                                         │
                                         ▼
                      ┌──────────────────────────────────────┐
                      │ Dynamic Reliability Estimator        │
                      │ Sharpness, Illum, Density, Agitation │
                      └──────────────────┬───────────────────┘
                                         │
                                         ▼
                      ┌──────────────────────────────────────┐
                      │ Reliability-Aware Adaptive Fusion    │
                      │ Dynamic Weighting & Evidential Dec.  │
                      └──────────────────────────────────────┘
```

---

## 2. Directory Structure

The repository is structured into modular domain packages:

```
D:\SensorFusionResearch\
├── .gitignore                         # Git exclusion rules (virtual environments, data, weights)
├── README.md                          # Comprehensive authoritative documentation & benchmarks
├── requirements.txt                   # Production environment dependencies
├── run_full_experiment.py             # Top-level entry point for complete experimental pipeline
├── run_tests.py                       # Top-level test runner for all sensor, perception, & fusion tests
│
├── src/                               # Modular core architecture
│   ├── sensors/                       # Sensor modeling, calibration, and synchronous acquisition
│   │   ├── camera.py                  # Pinhole intrinsic model, projection matrices, FOV geometry
│   │   ├── imu.py                     # IMU kinematics, gravity correction, SE(3) ego-motion integration
│   │   ├── lidar.py                   # Point cloud I/O, ROI spatial filtering, depth conversions
│   │   └── synchronization.py         # CARLA queue-based multi-sensor synchronous recorder
│   ├── perception/                    # Single-modality detector engines
│   │   ├── camera_detector.py         # YOLOv8 2D bounding box detection & Laplacian/luminance quality
│   │   └── lidar_detector.py          # 3D RANSAC ground plane segmentation & Euclidean DBSCAN
│   ├── fusion/                        # Cross-modal fusion, compensation, tracking, and reliability
│   │   ├── spatial_association.py     # 3D-to-2D projection and IoU Hungarian association
│   │   ├── motion_compensation.py     # SE(3) inter-frame point cloud warping and KD-Tree metrics
│   │   ├── temporal_tracker.py        # Multi-frame Kalman tracklet lifecycle and confirmation gating
│   │   ├── reliability_estimation.py  # Multi-criteria camera and LiDAR physical reliability estimators
│   │   └── adaptive_fusion.py         # Dynamic weighting and Dempster-Shafer evidential fusion engines
│   └── evaluation/                    # Benchmarking, synthetic degradation, and validation
│       ├── degradation.py             # Blur, illumination drop, beam dropout, noise, and outage models
│       ├── metrics.py                 # Precision, Recall, F1-score, and KD-tree alignment error metrics
│       └── benchmarking.py            # Systematic multi-paradigm comparator harness
│
├── experiments/                       # Reproducible research experiments
│   ├── configurations/                # JSON parameter configs for sensors, detectors, and trackers
│   │   └── default_config.json
│   └── run_full_experiment.py         # Master benchmark runner (Component 1, 2, and 3 evaluation)
│
├── tests/                             # Automated test suite
│   ├── test_sensors.py                # Unit tests for camera intrinsics, IMU gravity, point cloud ROI
│   ├── test_perception.py             # Unit tests for YOLOv8 and DBSCAN detectors
│   ├── test_fusion.py                 # Unit tests for IoU association, warping, tracking, and fusion
│   └── test_carla_connection.py       # Integration test for CARLA simulation server availability
│
├── docs/                              # Detailed mathematical and engineering documentation
│   ├── mathematical_formulations.md   # Mathematical derivations, coordinates, and kinematics
│   └── technical_notes.md             # Research evolution, design trade-offs, and literature context
│
├── data/                              # Dynamic multi-sensor dataset
│   └── dynamic_dataset/               # 70 synchronized frames @ 20 Hz (RGB PNG, LiDAR PLY, IMU JSON)
│
└── results/                           # Generated benchmark artifacts
    ├── metrics/                       # Comprehensive evaluation metrics (JSON and CSV files)
    │   ├── adaptive_fusion_benchmark.json
    │   ├── adaptive_fusion_benchmark.csv
    │   ├── temporal_fusion_metrics.json
    │   └── motion_compensation_metrics.json
    └── plots/                         # High-resolution publication-quality figures (PNG)
        ├── comprehensive_fusion_benchmark.png
        ├── dynamic_reliability_weights.png
        ├── pointcloud_motion_alignment.png
        └── multi_frame_trajectory_tracking.png
```

---

## 3. Mathematical Formulations & Calibration

### 3.1 Spatial Conventions & Sensor Extrinsics
- **CARLA Vehicle Frame (Left-Handed):** $+X$ points Forward, $+Y$ points Right, $+Z$ points Up.
- **Optical Camera Frame (Right-Handed):** $+X_{\text{opt}}$ points Right, $+Y_{\text{opt}}$ points Down, $+Z_{\text{opt}}$ points Forward (Optical Depth).

$$\begin{bmatrix} X_{\text{opt}} \\ Y_{\text{opt}} \\ Z_{\text{opt}} \end{bmatrix} = \begin{bmatrix} 0 & 1 & 0 \\ 0 & 0 & -1 \\ 1 & 0 & 0 \end{bmatrix} \begin{bmatrix} X_{\text{carla}} \\ Y_{\text{carla}} \\ Z_{\text{carla}} \end{bmatrix}$$

- **Sensor Mounting Offsets (Vehicle Origin):**
  - Camera: $\mathbf{p}_{\text{cam}} = [1.5, 0.0, 2.4]^T\,\text{m}$
  - LiDAR: $\mathbf{p}_{\text{lidar}} = [0.0, 0.0, 2.5]^T\,\text{m}$
  - IMU: $\mathbf{p}_{\text{imu}} = [0.0, 0.0, 2.0]^T\,\text{m}$
  - Relative Lever Arm: $\mathbf{t}_{\text{cam} \leftarrow \text{lidar}} = [1.5, 0.0, -0.1]^T\,\text{m}$

- **Pinhole Camera Intrinsics ($W=800\,\text{px}, H=600\,\text{px}, \text{FOV}=90^\circ$):**
  $$f_x = f_y = \frac{W}{2 \tan(45^\circ)} = 400.0\,\text{px}, \quad c_x = 400.0\,\text{px}, \quad c_y = 300.0\,\text{px}$$
  $$K = \begin{bmatrix} 400.0 & 0.0 & 400.0 \\ 0.0 & 400.0 & 300.0 \\ 0.0 & 0.0 & 1.0 \end{bmatrix}$$

### 3.2 IMU Kinematics & Inter-Frame $SE(3)$ Motion Estimation
The CARLA accelerometer measures specific force $\mathbf{f} = \mathbf{a}_{\text{linear}} - \mathbf{g}$. With gravity $\mathbf{g} = [0, 0, -9.81]^T\,\text{m/s}^2$ in CARLA coordinates:
$$\mathbf{a}_{\text{linear}} = [f_x, \; f_y, \; f_z - 9.81]^T\,\text{m/s}^2$$

Over fixed discretization interval $\Delta t = 0.05\,\text{s}$ ($20\,\text{Hz}$):
- **Rotation Increments ($SO(3)$):**
  $$\Delta \phi = \omega_x \Delta t, \quad \Delta \theta = \omega_y \Delta t, \quad \Delta \psi = \omega_z \Delta t$$
  $$\Delta R = R_z(\Delta \psi) \cdot R_y(\Delta \theta) \cdot R_x(\Delta \phi)$$
- **Translation Increments:**
  $$\Delta \mathbf{t} = \mathbf{v}_{k-1} \Delta t + \frac{1}{2} \mathbf{a}_{\text{linear}, k} \Delta t^2$$
- **Rigid Transformation Matrix:**
  $$T_{\text{ego}} = \begin{bmatrix} \Delta R & \Delta \mathbf{t} \\ \mathbf{0}^T & 1 \end{bmatrix} \in SE(3)$$

### 3.3 Point Cloud Motion Compensation (Warping)
Points $\mathbf{p}_{t-1}$ from time $t-1$ are warped into the reference frame at time $t$:
$$\mathbf{p}_{t-1 \to t} = \Delta R^T (\mathbf{p}_{t-1} - \Delta \mathbf{t})$$

Nearest-Neighbor Mean Absolute Error ($\text{MAE}$) and Mean Squared Error ($\text{MSE}$) evaluate spatial alignment:
$$\text{MAE} = \frac{1}{N} \sum_{i=1}^N \min_j \|\mathbf{p}_i - \mathbf{q}_j\|_2, \quad \text{MSE} = \frac{1}{N} \sum_{i=1}^N \min_j \|\mathbf{p}_i - \mathbf{q}_j\|_2^2$$

### 3.4 Multi-Criteria Sensor Reliability Estimation

#### Camera Reliability ($R_{\text{cam}} \in [0.05, 0.98]$):
$$R_{\text{cam}} = \text{clip}\left( c_i \cdot \psi_s \cdot \psi_l \cdot \psi_r \cdot \psi_{\text{mot}}, \; 0.05, \; 0.98 \right)$$
- $c_i$: YOLOv8 detection confidence.
- $\psi_s = \min(1.0, \text{Var}(\nabla^2 I) / 250.0)$: Modified Laplacian sharpness score.
- $\psi_l = 1.0 - \min(1.0, |\bar{L} - 128| / 128)$: Normalized illumination score from perceptual luminance.
- $\psi_r = \exp(-0.03 \cdot d_i)$: Atmospheric range attenuation factor.
- $\psi_{\text{mot}} = \exp(-0.08 \cdot (\|\mathbf{a}_{\text{lin}}\| + 5 \|\boldsymbol{\omega}\|))$: Vehicle dynamic agitation penalty.

#### LiDAR Reliability ($R_{\text{lidar}} \in [0.05, 0.98]$):
$$R_{\text{lidar}} = \text{clip}\left( \rho_d \cdot \rho_g \cdot \rho_c \cdot \rho_{\text{mot}} \cdot \rho_{\text{temp}}, \; 0.05, \; 0.98 \right)$$
- $\rho_d = \min(1.0, N_{\text{cluster}} / N_{\text{expected}}(d_i))$: Range-calibrated point density, where $N_{\text{expected}}(d) = 400.0 / (d + 1.0)$.
- $\rho_g = \min(1.0, 1.2 / (\sigma_x + \sigma_y + \sigma_z + 0.01))$: Geometric bounding compactness.
- $\rho_c = \min(1.0, N_{\text{cloud}} / 2500)$: Overall point cloud atmospheric transmission factor.
- $\rho_{\text{mot}} = \exp(-0.04 \cdot (\|\mathbf{a}_{\text{lin}}\| + 5 \|\boldsymbol{\omega}\|))$: LiDAR angular rate agitation penalty.
- $\rho_{\text{temp}} = 1.0 + 0.05 \cdot \min(5, \text{hits})$: Multi-frame tracklet stability bonus.

#### Dynamic Weight Allocation:
$$w_{\text{cam}} = \frac{R_{\text{cam}}}{R_{\text{cam}} + R_{\text{lidar}}}, \quad w_{\text{lidar}} = \frac{R_{\text{lidar}}}{R_{\text{cam}} + R_{\text{lidar}}}$$

---

## 4. Experimental Results & Benchmarks

The framework was evaluated across the 70-frame dynamic CARLA driving sequence containing vehicle maneuvers, accelerating, braking, and turning under 5 controlled environmental degradation conditions.

### Table 1: Comprehensive Perception Benchmark Comparison

| Evaluation Condition | Perception Paradigm | Precision | Recall | F1-Score | Fused Conf |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Clean Baseline** | Camera-Only (YOLOv8) | 0.9429 | 0.9429 | 0.9429 | 0.8872 |
| | LiDAR-Only (RANSAC+DBSCAN) | 0.9778 | 0.6286 | 0.7652 | 0.8000 |
| | Fixed Late Fusion (50/50) | 0.9778 | 0.6286 | 0.7652 | 0.8436 |
| | Dempster-Shafer Evidential | 0.9778 | 0.6286 | 0.7652 | 0.9774 |
| | Distance-Adaptive Late Fusion | 0.9778 | 0.6286 | 0.7652 | 0.8358 |
| | Temporal Multi-Frame Fusion | 0.9778 | 0.6286 | 0.7652 | 0.8436 |
| | **Proposed Reliability-Aware Adaptive** | **0.9778** | **0.6286** | **0.7652** | **0.8477** |
| **Camera Blur (Motion Blur)** | Camera-Only (YOLOv8) | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| | LiDAR-Only (RANSAC+DBSCAN) | 0.9778 | 0.6286 | 0.7652 | 0.8000 |
| | Fixed Late Fusion (50/50) | 0.9778 | 0.6286 | 0.7652 | 0.4000 |
| | Dempster-Shafer Evidential | 0.9778 | 0.6286 | 0.7652 | 0.8000 |
| | Distance-Adaptive Late Fusion | 0.9778 | 0.6286 | 0.7652 | 0.4800 |
| | Temporal Multi-Frame Fusion | 0.9778 | 0.6286 | 0.7652 | 0.4000 |
| | **Proposed Reliability-Aware Adaptive** | **0.9778** | **0.6286** | **0.7652** | **0.7646** |
| **Camera Darkness (Night/Tunnel)** | Camera-Only (YOLOv8) | 1.0000 | 0.9857 | 0.9928 | 0.8428 |
| | LiDAR-Only (RANSAC+DBSCAN) | 0.9778 | 0.6286 | 0.7652 | 0.8000 |
| | Fixed Late Fusion (50/50) | 0.9778 | 0.6286 | 0.7652 | 0.8214 |
| | Dempster-Shafer Evidential | 0.9778 | 0.6286 | 0.7652 | 0.9686 |
| | Distance-Adaptive Late Fusion | 0.9778 | 0.6286 | 0.7652 | 0.8171 |
| | Temporal Multi-Frame Fusion | 0.9778 | 0.6286 | 0.7652 | 0.8214 |
| | **Proposed Reliability-Aware Adaptive** | **0.9778** | **0.6286** | **0.7652** | **0.8239** |
| **LiDAR Dropout (85% Loss)** | Camera-Only (YOLOv8) | 0.9429 | 0.9429 | 0.9429 | 0.8872 |
| | LiDAR-Only (RANSAC+DBSCAN) | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| | Fixed Late Fusion (50/50) | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| | Dempster-Shafer Evidential | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| | Distance-Adaptive Late Fusion | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| | Temporal Multi-Frame Fusion | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| | **Proposed Reliability-Aware Adaptive** | **0.9429** | **0.9429** | **0.9429** | **0.8436** |
| **Severe Dual Degradation** | Camera-Only (YOLOv8) | 1.0000 | 0.9857 | 0.9928 | 0.8428 |
| | LiDAR-Only (RANSAC+DBSCAN) | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| | Fixed Late Fusion (50/50) | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| | Dempster-Shafer Evidential | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| | Distance-Adaptive Late Fusion | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| | Temporal Multi-Frame Fusion | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| | **Proposed Reliability-Aware Adaptive** | **1.0000** | **0.9857** | **0.9928** | **0.8014** |

### Table 2: IMU Ego-Motion Point Cloud Alignment Verification
Alignment accuracy between consecutive frames across 69 dynamic transitions:

| Metric | Uncompensated (Raw) | IMU-Compensated | Improvement |
| :--- | :---: | :---: | :---: |
| **Mean Absolute Error (MAE)** | 0.0964 m | 0.0888 m | **7.88%** error reduction |
| **Mean Squared Error (MSE)** | 0.0383 m² | 0.0315 m² | **17.75%** error reduction |
| **Peak Alignment Correction** | 0.4280 m² | 0.2810 m² | **34.35%** error reduction |

### Key Quantitative Findings:
1. **Dynamic Weight Shift Under Modality Failure:** When the camera experiences severe motion blur ($15\times 15$ kernel), its confidence drops to $0.0$. Fixed Late Fusion halves detection confidence to $0.4000$. The proposed adaptive engine dynamically drives $w_{\text{cam}} \to 0$ and allocates $w_{\text{lidar}} \to 0.95$, maintaining high fused confidence ($0.7646$).
2. **Resilience to LiDAR Dropout:** When LiDAR suffers $85\%$ point attenuation, all classical fusion pipelines (Fixed Late Fusion, Dempster-Shafer, and Distance-Adaptive) collapse completely to $F_1 = 0.0000$ due to lack of LiDAR clusters. The proposed reliability-aware engine detects the LiDAR density collapse ($\rho_c \to 0.15$), engages fallback preservation, and preserves camera-derived obstacles with calibrated confidence ($0.8436$), achieving $F_1 = 0.9429$.
3. **Motion Compensation Value:** Applying $T_{\text{ego}}$ inter-frame warping eliminates distortion during vehicle turning and braking, reducing nearest-neighbor registration error by up to $34.35\%$.

---

## 5. Execution & Reproduction Guide

### 5.1 Environment Prerequisites
- Windows 10/11 or Ubuntu 20.04/22.04 LTS
- Python 3.10 to 3.12
- CARLA Simulator 0.9.16 (optional for live acquisition; offline dataset provided)

### 5.2 Installation
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

### 5.3 Running the Unified Test Suite
Verify that all sensor kinematics, coordinate projections, detectors, and fusion modules are functional:
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
test_reliability_and_adaptive_fusion: PASSED
=================================================================
      ALL UNIT AND INTEGRATION TESTS PASSED!
=================================================================
```

### 5.4 Running the Master Experiment
Run the full unified research pipeline (evaluates IMU compensation, temporal tracking, and multi-condition adaptive fusion):
```powershell
python run_full_experiment.py
```
This script processes the dynamic dataset, performs controlled degradations, and exports updated metrics and publication figures into `results/metrics/` and `results/plots/`.

---

## 6. Research Limitations & Future Roadmap

1. **Dead-Reckoning Drift:** Inter-frame IMU double integration over $\Delta t = 50\,\text{ms}$ is precise for scan warping. However, integration over multi-second horizons suffers from $O(t^2)$ dead-reckoning drift. Integrating wheel tick odometry and factor graph optimization (e.g. GTSAM) will be explored in future work.
2. **Dense Depth Completion:** Current spatial association uses 3D-to-2D bounding box IoU assignment. Extending this to point-level dense depth completion networks (e.g. PENet or FusionPaint) will enable pixel-level semantic fusion.
3. **Sim-to-Real Domain Shift:** Experiments are evaluated within CARLA 0.9.16. Validating on real-world datasets (nuScenes, Waymo Open Dataset, KITTI-360) is the planned next phase.

---

## 7. Citation & References

```bibtex
@article{sensor_fusion_perception_2026,
  title={IMU-Assisted Temporal Reliability-Aware Camera-LiDAR Sensor Fusion for Robust Autonomous-Driving Perception},
  author={Suvidh, Chiranthan},
  journal={Autonomous Driving Perception Research},
  year={2026}
}
```
