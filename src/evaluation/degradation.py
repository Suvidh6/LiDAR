"""
src/evaluation/degradation.py
Controlled, reproducible degradation injection for Camera and LiDAR sensors.

Provides:
1. Camera Motion Blur (simulates high-speed turns / vibrations).
2. Camera Illumination Deprivation (simulates night/tunnel/extreme underexposure).
3. Camera Fog and Specular Glare (simulates atmospheric scattering / lens flare).
4. Camera Complete Outage (simulates lens occlusion / transmission loss).
5. LiDAR Return Dropout (simulates heavy rain / fog laser attenuation).
6. LiDAR Backscatter Noise (simulates spray / airborne particulates).
7. LiDAR Complete Outage (simulates sensor hardware loss / disconnect).
"""

import cv2
import numpy as np

def apply_camera_motion_blur(image_bgr, kernel_size=17, angle_deg=25.0):
    """Applies realistic directional linear motion blur to camera images."""
    if image_bgr is None or kernel_size <= 1:
        return image_bgr

    kernel = np.zeros((kernel_size, kernel_size), dtype=np.float32)
    center = kernel_size // 2
    theta = np.radians(angle_deg)
    dx = np.cos(theta)
    dy = np.sin(theta)

    for i in range(-center, center + 1):
        x = int(round(center + i * dx))
        y = int(round(center + i * dy))
        if 0 <= x < kernel_size and 0 <= y < kernel_size:
            kernel[y, x] = 1.0

    k_sum = np.sum(kernel)
    if k_sum > 0:
        kernel /= k_sum
    else:
        kernel[center, center] = 1.0

    return cv2.filter2D(image_bgr, -1, kernel)

def apply_camera_illumination_degrade(image_bgr, factor=0.12):
    """Simulates extreme underexposure or nighttime illumination plunge."""
    if image_bgr is None:
        return image_bgr
    degraded = image_bgr.astype(np.float32) * factor
    return np.clip(degraded, 0, 255).astype(np.uint8)

def apply_camera_fog_glare(image_bgr, fog_density=0.6, glare_intensity=0.7):
    """Simulates atmospheric fog scattering and localized glare blooming."""
    if image_bgr is None:
        return image_bgr
    h, w, _ = image_bgr.shape
    fog_layer = np.full((h, w, 3), fill_value=210, dtype=np.uint8)
    blended = cv2.addWeighted(image_bgr, 1.0 - fog_density, fog_layer, fog_density, 0)

    center = (w // 2, int(h * 0.3))
    glare = np.zeros((h, w, 3), dtype=np.float32)
    cv2.circle(glare, center, int(min(w, h) * 0.35), (255, 255, 255), -1)
    glare = cv2.GaussianBlur(glare, (101, 101), 0)
    result = blended.astype(np.float32) + glare * glare_intensity
    return np.clip(result, 0, 255).astype(np.uint8)

def apply_camera_outage(image_bgr):
    """Simulates complete camera feed failure (blackout)."""
    if image_bgr is None:
        return None
    return np.zeros_like(image_bgr)

def apply_lidar_dropout(points_xyz, drop_ratio=0.85, random_seed=42):
    """
    Simulates optical beam attenuation (e.g. dense rain / fog) by dropping
    a significant fraction of returning laser pulses.
    """
    if len(points_xyz) == 0:
        return points_xyz
    rng = np.random.default_rng(random_seed)
    n_pts = len(points_xyz)
    keep_count = max(10, int(n_pts * (1.0 - drop_ratio)))
    indices = rng.choice(n_pts, size=keep_count, replace=False)
    return points_xyz[indices]

def apply_lidar_noise(points_xyz, noise_std=0.35, num_spray=250, random_seed=42):
    """
    Simulates water spray and backscatter noise in 3D point clouds.
    """
    if len(points_xyz) == 0:
        return points_xyz
    rng = np.random.default_rng(random_seed)

    jittered = points_xyz + rng.normal(0, noise_std, size=points_xyz.shape)

    spray_x = rng.uniform(0.0, 30.0, size=num_spray)
    spray_y = rng.uniform(-15.0, 15.0, size=num_spray)
    spray_z = rng.uniform(-1.5, 3.0, size=num_spray)
    spray_pts = np.column_stack([spray_x, spray_y, spray_z])

    return np.vstack([jittered, spray_pts])

def apply_lidar_outage(points_xyz):
    """Simulates complete LiDAR hardware or bus communication loss."""
    return np.empty((0, 3), dtype=np.float64)
