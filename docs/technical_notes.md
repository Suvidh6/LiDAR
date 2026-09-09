# Technical Notes & Research Evolution

## 1. Project Background & Unified Vision
This repository encapsulates research on multimodal perception for autonomous driving in CARLA 0.9.16. Rather than treating ego-motion compensation, multi-frame tracking, and adaptive weighting as separate projects, they are consolidated into **one cohesive perception system**:
$$\text{Sensors (Cam + Lid + IMU)} \to \text{Spatial Association} \to \text{Ego-Motion Warping} \to \text{Temporal Tracking} \to \text{Reliability Estimation} \to \text{Adaptive Fusion}$$

---

## 2. Component Evolution & Findings

### Component 1: IMU-Based Motion Awareness
* **Problem:** Vehicle motion between consecutive frames causes spatial smearing and misalignment across sensor modalities.
* **Finding:** Integrating linear acceleration and angular velocity over $\Delta t = 50\,\text{ms}$ yields an accurate $SE(3)$ transformation $T_{\text{ego}}$ that reduces nearest-neighbor point cloud alignment error across 69 consecutive dynamic transitions.
* **Limitations:** Raw double-integration of acceleration drifts quadratically ($O(t^2)$). For single-interval frame warping ($\Delta t = 50\,\text{ms}$), dead-reckoning is highly reliable, but trajectory integration across seconds requires wheel odometry or GNSS.

### Component 2: Temporal Multi-Frame Sensor Fusion
* **Problem:** Single-frame perception suffers from transient occlusions, object flickering, and sensitivity to noise.
* **Finding:** A sliding window tracker with Kalman filtering and IMU ego-motion compensation stabilizes tracklet positions across frames, achieving smooth trajectory continuity and rejecting single-frame spurious returns.
* **Gating Design:** Tracklets require at least 2 consecutive observations before confirmation, preventing transient false positives from propagating into downstream path planning.

### Component 3: Reliability-Aware Adaptive Sensor Fusion
* **Problem:** Fixed $50/50$ late fusion fails when either modality becomes degraded by environmental conditions (motion blur, darkness, rain attenuation, spray noise) or hardware faults.
* **Finding:** Estimating physical reliability dynamically allows the perception system to automatically shift weights toward the healthy sensor modality:
  * When the camera is blurred or darkened, $w_{\text{cam}} \to 0$ and $w_{\text{lidar}} \to 1.0$, maintaining $0.9886$ F1-score.
  * When LiDAR undergoes $85\%$ beam dropout and backscatter spray, adaptive density gating preserves precision ($0.3333$ vs $0.0241$ for fixed fusion).
  * When both sensors are degraded, the system depresses fused confidence to $0.0801$ (instead of falsely reporting $0.2338$ like fixed fusion), alerting safety controllers.

---

## 3. Literature Positioning & Research Honesty
1. **Dynamic Weighting & Adaptive Fusion:** Known and established in literature (e.g. Dempster-Shafer, adaptive Kalman filtering). We do not claim dynamic weighting alone as novel.
2. **Research Gap:** Systematic, unified combination of physical optical sharpness/illumination metrics, range-normalized LiDAR point density models calibrated to beam divergence ($1/d$), and vehicle dynamic agitation penalties derived from high-rate IMU telemetry, evaluated under realistic degradation regimes in CARLA 0.9.16.
