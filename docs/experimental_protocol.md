# Experimental Protocol & Evaluation Methodology

This document defines the formal experimental protocol, metric formulations, continuous dynamic scenarios, comparator paradigms, and execution guidelines for evaluating the multimodal sensor fusion framework.

---

## 1. Experimental Objectives

1. **Quantify Inter-Frame Motion Compensation:** Evaluate nearest-neighbor registration error reduction (MAE and MSE in meters) achieved by $SE(3)$ IMU point cloud warping during dynamic vehicle maneuvers (accelerating, braking, turning).
2. **Quantify Temporal Tracking Stability:** Measure tracklet persistence ratio and position displacement jitter (meters) with vs. without IMU ego-motion propagation.
3. **Quantify Dynamic Degradation Robustness:** Evaluate cross-modal perception resilience across a continuous time-varying scenario containing progressive optical blur, illumination deprivation, LiDAR beam dropout, sensor outage, and vehicle dynamic agitation.
4. **Benchmark Comparative Performance:** Compare the proposed reliability-aware adaptive fusion framework against 6 established and baseline perception paradigms under identical controlled conditions.

---

## 2. Distinction Between Metric Classes

To maintain strict scientific integrity, the framework explicitly separates **Ground-Truth Matched Metrics** from **System / Proxy Telemetry Metrics**:

### 2.1 Ground-Truth Matched Metrics
Computed by matching predicted 3D bounding box centroids against ground-truth obstacle positions extracted from nominal, un-degraded 3D LiDAR point clouds:
- **True Positives ($TP$):** Fused obstacle prediction whose centroid lies within Euclidean radius $d_{\text{match}} \le 3.0\,\text{m}$ of an unmatched ground-truth target.
- **False Positives ($FP$):** Fused prediction with no matching ground-truth target within $3.0\,\text{m}$.
- **False Negatives ($FN$):** Ground-truth target left unmatched by any fused prediction.
- **Precision:** $\frac{TP}{TP + FP}$
- **Recall:** $\frac{TP}{TP + FN}$
- **F1-Score:** $\frac{2 \cdot \text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$
- **3D Localization Error ($m$):** $\frac{1}{TP} \sum_{i=1}^{TP} \|\mathbf{p}_{\text{pred}, i} - \mathbf{p}_{\text{gt}, i}\|_2$

### 2.2 System & Proxy Telemetry Metrics
Signals internal to the perception pipeline (must never be called "accuracy"):
- **Detection Confidence ($c$):** Output classification probability or fused evidential belief.
- **Estimated Reliability ($R_{\text{cam}}, R_{\text{lidar}}$):** Normalized physical metric $[0.01, 0.99]$.
- **Sensor Weight ($w_{\text{cam}}, w_{\text{lidar}}$):** Normalized contribution where $w_{\text{cam}} + w_{\text{lidar}} = 1.0$.
- **Cross-Modal Consistency:** 2D bounding box IoU overlap between projected 3D LiDAR cluster and 2D camera detection.
- **Execution Throughput (FPS) & Latency ($ms$):** Wall-clock inference time per synchronized frame.

---

## 3. Continuous Dynamic Degradation Schedule

Rather than evaluating disconnected static batches, the primary experiment evaluates a continuous 70-frame sequence featuring 8 progressive operational segments:

| Segment ID | Frame Span | Operational Environment | Applied Degradation Profile |
| :--- | :---: | :--- | :--- |
| **nominal_baseline** | 0 – 14 | Clear daylight, cruising | None (Clean baseline) |
| **camera_blur_ramp** | 15 – 24 | Vibration / fast panning | Progressive linear motion blur (Kernel $3 \times 3 \to 21 \times 21$) + mild dimming |
| **camera_recovery** | 25 – 34 | Camera stabilization | Gradual recovery from blur ($21 \times 21 \to \text{clean}$) and illumination return |
| **lidar_dropout_ramp** | 35 – 44 | Laser beam attenuation (fog/rain) | Progressive pulse dropout ($10\% \to 85\%$) + airborne spray noise injection |
| **lidar_recovery** | 45 – 54 | Clearing weather | Progressive pulse recovery ($85\% \to \text{clean}$) |
| **camera_darkness_tunnel** | 55 – 59 | Night / unlit tunnel plunge | Extreme underexposure ($0.10\times$ luminance multiplier) |
| **high_motion_maneuver** | 60 – 64 | Agitated vehicle handling | Sharp turning ($\omega_z > 15^\circ/\text{s}$) + heavy braking ($a_x < -2.0\,\text{m/s}^2$) |
| **dual_degradation_recovery** | 65 – 69 | Severe combined failure | Simultaneous camera blur ($17 \times 17$) + $70\%$ LiDAR beam dropout |

---

## 4. Evaluated Perception Paradigms (Baselines)

1. **Camera-Only (YOLOv8):** Evaluates visual 2D detections without 3D spatial returns.
2. **LiDAR-Only (RANSAC + DBSCAN):** Evaluates 3D geometric clustering without semantic vision cues.
3. **Late Fusion (Fixed 50/50):** Static decision fusion assigning equal weight ($w_{\text{cam}} = 0.5, w_{\text{lidar}} = 0.5$) regardless of environmental conditions.
4. **Dempster-Shafer Evidential Fusion:** Simplified implementation inspired by Shafer's belief mass combination theory.
5. **Distance-Adaptive Fusion:** Simplified implementation inspired by range-heuristic weighting (prioritizing vision at long range, LiDAR at close range).
6. **Temporal Multi-Frame Fusion:** Multi-frame Kalman tracking without dynamic reliability weighting.
7. **Proposed Reliability-Aware Adaptive Fusion:** Full system integrating physical quality metrics, IMU motion awareness, hysteresis weight smoothing, and fail-safe modality fallbacks.

---

## 5. Execution & Hardware Awareness

Experiments are calibrated for execution on standard research development hardware (e.g., NVIDIA RTX 3050 6GB Laptop GPU / 16GB RAM):
- Sequential frame processing avoids storing multiple point cloud scans simultaneously in VRAM.
- PyTorch inference is set to evaluation mode (`torch.no_grad()`).
- Deterministic random seeds (`seed=42`) are enforced across NumPy, PyTorch, and Python runtimes.
