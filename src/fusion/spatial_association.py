"""
src/fusion/spatial_association.py
Performs 2D-3D spatial projection and cross-modal association between Camera and LiDAR.

Features:
- Projects 3D LiDAR bounding boxes and centroids onto 2D camera image planes using pinhole intrinsics.
- Computes 2D Intersection-over-Union (IoU) and spatial distance metrics.
- Solves global bipartite matching via Hungarian algorithm (scipy linear_sum_assignment).
- Partitions detections into matched multimodal pairs and modality-specific singletons.
"""

import numpy as np
from scipy.optimize import linear_sum_assignment

def compute_2d_iou(boxA, boxB):
    """
    Computes standard 2D Intersection-over-Union between two boxes [x1, y1, x2, y2].
    """
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    inter_area = max(0.0, xB - xA) * max(0.0, yB - yA)
    boxA_area = max(1e-4, (boxA[2] - boxA[0]) * (boxA[3] - boxA[1]))
    boxB_area = max(1e-4, (boxB[2] - boxB[0]) * (boxB[3] - boxB[1]))

    iou = inter_area / float(boxA_area + boxB_area - inter_area)
    return float(np.clip(iou, 0.0, 1.0))

def project_cluster_to_camera(cluster, compensator):
    """
    Projects a 3D LiDARCluster's bounding box and centroid onto the 2D camera image.
    Returns:
    - proj_bbox: [u_min, v_min, u_max, v_max] or None if out of frustum.
    - centroid_2d: [u, v]
    - depth: optical depth Z_opt in meters.
    """
    corners = cluster.get_bounding_corners()
    uvs, depths = compensator.project_lidar_to_camera(corners)

    # Also project centroid
    c_pts = np.array([cluster.centroid])
    c_uv, c_depth = compensator.project_lidar_to_camera(c_pts)

    if len(uvs) < 2 or len(c_uv) == 0:
        return None, None, None

    u_min = float(np.min(uvs[:, 0]))
    u_max = float(np.max(uvs[:, 0]))
    v_min = float(np.min(uvs[:, 1]))
    v_max = float(np.max(uvs[:, 1]))

    margin_u = max(6.0, (u_max - u_min) * 0.1)
    margin_v = max(6.0, (v_max - v_min) * 0.1)

    proj_bbox = [
        max(0.0, u_min - margin_u),
        max(0.0, v_min - margin_v),
        min(compensator.width - 1.0, u_max + margin_u),
        min(compensator.height - 1.0, v_max + margin_v)
    ]

    return proj_bbox, c_uv[0].tolist(), float(c_depth[0])

def associate_camera_and_lidar(camera_dets, lidar_clusters, compensator, iou_thresh=0.05, max_dist=45.0):
    """
    Associates 2D camera bounding boxes with projected 3D LiDAR clusters.
    
    Returns:
    - matched: list of dicts with keys (camera_det, lidar_cluster, iou, proj_bbox, depth)
    - unmatched_cam: list of camera_det
    - unmatched_lid: list of lidar_cluster
    """
    if len(camera_dets) == 0:
        return [], [], lidar_clusters
    if len(lidar_clusters) == 0:
        return [], camera_dets, []

    projected_lidar = []
    valid_clusters = []
    for cluster in lidar_clusters:
        bbox_2d, c_uv, depth = project_cluster_to_camera(cluster, compensator)
        if bbox_2d is not None and depth <= max_dist:
            projected_lidar.append({"bbox_2d": bbox_2d, "c_uv": c_uv, "depth": depth})
            valid_clusters.append(cluster)

    if len(valid_clusters) == 0:
        return [], camera_dets, lidar_clusters

    n_cam = len(camera_dets)
    n_lid = len(valid_clusters)

    cost_matrix = np.full((n_cam, n_lid), fill_value=1.0, dtype=np.float64)

    for i, c_det in enumerate(camera_dets):
        c_box = c_det.bbox
        c_center = c_det.centroid_2d
        for j, p_lid in enumerate(projected_lidar):
            l_box = p_lid["bbox_2d"]
            l_center = p_lid["c_uv"]
            iou = compute_2d_iou(c_box, l_box)

            diag = np.sqrt(compensator.width**2 + compensator.height**2)
            dist = np.linalg.norm(np.array(c_center) - np.array(l_center)) / diag

            if iou > 0.0:
                cost = 1.0 - iou
            elif dist < 0.20:
                cost = 0.85 + dist
            else:
                cost = 1.0

            cost_matrix[i, j] = cost

    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    matched = []
    matched_c_idx = set()
    matched_l_idx = set()

    for r, c in zip(row_ind, col_ind):
        cost = cost_matrix[r, c]
        if cost < 0.95:
            matched_c_idx.add(r)
            matched_l_idx.add(c)
            iou = compute_2d_iou(camera_dets[r].bbox, projected_lidar[c]["bbox_2d"])
            matched.append({
                "camera_det": camera_dets[r],
                "lidar_cluster": valid_clusters[c],
                "iou": round(float(iou), 3),
                "proj_bbox": projected_lidar[c]["bbox_2d"],
                "depth": projected_lidar[c]["depth"]
            })

    unmatched_cam = [camera_dets[i] for i in range(n_cam) if i not in matched_c_idx]

    matched_cluster_ids = {m["lidar_cluster"].cluster_id for m in matched}
    unmatched_lid = [cl for cl in lidar_clusters if cl.cluster_id not in matched_cluster_ids]

    return matched, unmatched_cam, unmatched_lid
