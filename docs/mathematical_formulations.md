# Mathematical Formulations and Spatial Conventions

This document provides the foundational mathematical derivations, coordinate systems, kinematic models, and projective geometry used in the **IMU-Assisted Temporal Reliability-Aware Multimodal Sensor Fusion** perception prototype.

---

## 1. Coordinate Systems & Spatial Conventions

### 1.1 CARLA Vehicle Coordinate Frame
CARLA employs Unreal Engine's **Left-Handed** 3D coordinate system:
- $\mathbf{X}$ (Longitudinal): Points forward along the vehicle's heading.
- $\mathbf{Y}$ (Lateral): Points to the vehicle's right.
- $\mathbf{Z}$ (Vertical): Points upward perpendicular to the ground plane.

Rotations follow the left-hand thumb rule:
- **Roll ($\phi$):** Rotation about $+X$ (Right side down is positive).
- **Pitch ($\theta$):** Rotation about $+Y$ (Vehicle nose up is positive).
- **Yaw ($\psi$):** Rotation about $+Z$ (Clockwise / turning right is positive).

### 1.2 Optical Camera Coordinate Frame
Standard computer vision algorithms (OpenCV / pinhole camera model) utilize a **Right-Handed** optical frame:
- $\mathbf{X}_{\text{opt}}$: Points to the right in the image plane.
- $\mathbf{Y}_{\text{opt}}$: Points downward in the image plane.
- $\mathbf{Z}_{\text{opt}}$: Points forward along the optical axis (depth).

The coordinate basis transformation from CARLA camera coordinates to optical camera coordinates is:
$$\begin{bmatrix} X_{\text{opt}} \\ Y_{\text{opt}} \\ Z_{\text{opt}} \end{bmatrix} = \begin{bmatrix} 0 & 1 & 0 \\ 0 & 0 & -1 \\ 1 & 0 & 0 \end{bmatrix} \begin{bmatrix} X_{\text{carla}} \\ Y_{\text{carla}} \\ Z_{\text{carla}} \end{bmatrix}$$

---

## 2. Sensor Extrinsics & Camera Calibration

### 2.1 Sensor Mounting Positions
Measured relative to the vehicle coordinate origin $(0, 0, 0)$:
- **RGB Camera:** $\mathbf{p}_{\text{cam}} = [1.5,\; 0.0,\; 2.4]^T\,\text{m}$
- **LiDAR:** $\mathbf{p}_{\text{lidar}} = [0.0,\; 0.0,\; 2.5]^T\,\text{m}$
- **IMU:** $\mathbf{p}_{\text{imu}} = [0.0,\; 0.0,\; 2.0]^T\,\text{m}$

### 2.2 Relative Extrinsic Transformation
The translation vector from the LiDAR sensor to the Camera sensor in the vehicle frame is:
$$\mathbf{t}_{\text{cam} \leftarrow \text{lidar}} = \mathbf{p}_{\text{cam}} - \mathbf{p}_{\text{lidar}} = \begin{bmatrix} 1.5 - 0.0 \\ 0.0 - 0.0 \\ 2.4 - 2.5 \end{bmatrix} = \begin{bmatrix} 1.5 \\ 0.0 \\ -0.1 \end{bmatrix}\,\text{m}$$

### 2.3 Camera Pinhole Intrinsics
For an image with width $W$, height $H$, and horizontal field of view $\text{FOV}_h$:
$$f_x = f_y = f = \frac{W}{2 \tan\left(\frac{\text{FOV}_h}{2}\right)}$$

For $W = 800\,\text{px}$, $H = 600\,\text{px}$, and $\text{FOV}_h = 90^\circ$:
$$\tan\left(\frac{90^\circ}{2}\right) = \tan(45^\circ) = 1.0 \implies f = \frac{800}{2 \times 1.0} = 400.0\,\text{px}$$

The principal point $(c_x, c_y)$ is at the geometric image center:
$$c_x = \frac{W}{2} = 400.0\,\text{px}, \quad c_y = \frac{H}{2} = 300.0\,\text{px}$$

The camera intrinsic matrix $K \in \mathbb{R}^{3 \times 3}$ is:
$$K = \begin{bmatrix} 400.0 & 0.0 & 400.0 \\ 0.0 & 400.0 & 300.0 \\ 0.0 & 0.0 & 1.0 \end{bmatrix}$$

---

## 3. IMU Kinematics & Specific Force Decomposition

### 3.1 Accelerometer Measurement Model
Real physical accelerometers (and the CARLA IMU) measure **specific force** $\mathbf{f}$:
$$\mathbf{f} = \mathbf{a}_{\text{linear}} - \mathbf{g}$$
where $\mathbf{g}$ is the gravitational acceleration vector.

In CARLA's level coordinate frame, gravity acts downward along $-Z$:
$$\mathbf{g} = [0, \; 0, \; -9.81]^T\,\text{m/s}^2$$

Linear acceleration free from gravity bias is recovered via:
$$\mathbf{a}_{\text{linear}} = [f_x, \; f_y, \; f_z - 9.81]^T\,\text{m/s}^2$$

### 3.2 Inter-Frame Ego-Motion Estimation in $SE(3)$
Over discrete time step $\Delta t = 0.05\,\text{s}$ ($20\,\text{Hz}$):
- **Relative Rotation ($\Delta R \in SO(3)$):**
  $$\Delta \phi = \omega_x \Delta t, \quad \Delta \theta = \omega_y \Delta t, \quad \Delta \psi = \omega_z \Delta t$$
  $$\Delta R = R_z(\Delta \psi) \cdot R_y(\Delta \theta) \cdot R_x(\Delta \phi)$$
- **Relative Translation ($\Delta \mathbf{t}$):**
  $$\Delta \mathbf{t} = \mathbf{v}_{k-1} \Delta t + \frac{1}{2} \mathbf{a}_{\text{linear}, k} \Delta t^2$$
- **Rigid-Body Transform Matrix ($T_{\text{ego}}$):**
  $$T_{\text{ego}} = \begin{bmatrix} \Delta R & \Delta \mathbf{t} \\ \mathbf{0}^T & 1 \end{bmatrix} \in SE(3)$$

---

## 4. Point Cloud Motion Compensation (Warping)

To map points observed at time $t-1$ into the current frame coordinate system at time $t$:
$$\mathbf{p}_{t-1 \to t} = \Delta R^T (\mathbf{p}_{t-1} - \Delta \mathbf{t})$$

### Quantitative Alignment Metrics (Nearest-Neighbor KD-Tree)
$$\text{MAE} = \frac{1}{N} \sum_{i=1}^N \min_j \|\mathbf{p}_i - \mathbf{q}_j\|_2$$
$$\text{MSE} = \frac{1}{N} \sum_{i=1}^N \min_j \|\mathbf{p}_i - \mathbf{q}_j\|_2^2$$

---

## 5. Dempster-Shafer Evidential Mass Combination

Let $\Theta = \{\text{Object}, \neg\text{Object}\}$ be the frame of discernment.
- Basic Probability Assignments (Masses):
  $$m_{\text{cam}}(\text{Obj}) = R_{\text{cam}}, \quad m_{\text{cam}}(\Theta) = 1 - R_{\text{cam}}$$
  $$m_{\text{lid}}(\text{Obj}) = R_{\text{lidar}}, \quad m_{\text{lid}}(\Theta) = 1 - R_{\text{lidar}}$$
- Dempster's Rule of Combination:
  $$m_{\text{fused}}(\text{Obj}) = m_{\text{cam}}(\text{Obj}) m_{\text{lid}}(\text{Obj}) + m_{\text{cam}}(\text{Obj}) m_{\text{lid}}(\Theta) + m_{\text{cam}}(\Theta) m_{\text{lid}}(\text{Obj})$$
