"""
src/evaluation/metrics.py
Standardized, dataset-agnostic perception evaluation framework.

Metrics computed:
1. Precision = TP / (TP + FP)
2. Recall    = TP / (TP + FN)
3. F1 Score  = 2 * Precision * Recall / (Precision + Recall)
4. Localization Error (MAE) = Mean Euclidean distance ||p_pred - p_gt||_2 across true positives.
5. Temporal Jitter = Standard deviation of second-order inter-frame displacement differences.
6. Processing Latency (ms)
7. Frame Rate (FPS)

Provides:
- evaluate_3d_frame: Matches 3D predictions to 3D ground truth via Hungarian matching.
- evaluate_2d_frame: Matches 2D camera detections to 2D ground truth boxes via IoU.
- compute_trajectory_jitter: Standard deviation of second displacement differences.
- compute_aggregate_metrics: Standard classification and localization metrics dictionary.
"""

import math
import numpy as np
from scipy.optimize import linear_sum_assignment

def compute_2d_box_iou(boxA, boxB):
    """Computes 2D Intersection-over-Union between two boxes [x1, y1, x2, y2]."""
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    inter_w = max(0.0, xB - xA)
    inter_h = max(0.0, yB - yA)
    inter_area = inter_w * inter_h

    boxA_area = max(1e-4, (boxA[2] - boxA[0]) * (boxA[3] - boxA[1]))
    boxB_area = max(1e-4, (boxB[2] - boxB[0]) * (boxB[3] - boxB[1]))

    iou = inter_area / float(boxA_area + boxB_area - inter_area)
    return float(np.clip(iou, 0.0, 1.0))

def compute_trajectory_jitter(positions_xyz):
    """
    Computes temporal trajectory jitter, defined as the standard deviation of
    second-order inter-frame positional differences (acceleration jitter):
        j_t = p_t - 2 * p_{t-1} + p_{t-2}
        jitter = std(||j_t||_2)
    Quantifies high-frequency positional fluttering / instability across time.
    Returns 0.0 if trajectory has fewer than 3 frames.
    """
    pts = np.asarray(positions_xyz, dtype=np.float64)
    if len(pts) < 3:
        return 0.0
    # Second-order difference: d2 = diff(diff(pts))
    second_diffs = pts[2:] - 2.0 * pts[1:-1] + pts[:-2]
    second_norms = np.linalg.norm(second_diffs, axis=1)
    return float(np.std(second_norms))

def compute_aggregate_metrics(tp: int, fp: int, fn: int, loc_errs: list, jitter: float = 0.0) -> dict:
    """Calculates standardized precision, recall, f1, MAE, and jitter."""
    precision = tp / max(1, tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / max(1, tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2.0 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    loc_err = float(np.mean(loc_errs)) if len(loc_errs) > 0 else float("nan")

    return {
        "tp": int(tp),
        "fp": int(fp),
        "fn": int(fn),
        "precision": float(round(precision, 4)),
        "recall": float(round(recall, 4)),
        "f1_score": float(round(f1, 4)),
        "localization_error_m": float(round(loc_err, 4)) if not np.isnan(loc_err) else None,
        "jitter_m": float(round(jitter, 4))
    }

def evaluate_3d_frame(predictions, gt_positions, dist_threshold: float = 2.5, conf_threshold: float = 0.25):
    """
    Evaluates 3D object detections against authoritative 3D ground truth targets
    using Hungarian global bipartite matching under a Euclidean distance threshold.
    
    Args:
        predictions: list of predicted objects (must have .position and .confidence attributes)
        gt_positions: list of [x, y, z] ground truth coordinates
        dist_threshold: maximum gating Euclidean distance in meters for a valid match (default: 2.5m)
        conf_threshold: confidence cutoff below which predictions are filtered (default: 0.25)
    
    Returns:
        tp, fp, fn, matched_errs, confs
    """
    # Filter predictions by confidence
    valid_preds = []
    confs = []
    for p in predictions:
        conf = getattr(p, "confidence", 1.0)
        confs.append(float(conf))
        if conf >= conf_threshold:
            valid_preds.append(p)

    n_gt = len(gt_positions)
    n_pred = len(valid_preds)

    if n_gt == 0:
        return 0, n_pred, 0, [], confs
    if n_pred == 0:
        return 0, 0, n_gt, [], confs

    # Build Euclidean distance cost matrix
    cost_matrix = np.zeros((n_pred, n_gt), dtype=np.float64)
    pred_positions = [np.asarray(getattr(p, "position", p), dtype=np.float64) for p in valid_preds]

    for i, p_pos in enumerate(pred_positions):
        for j, gt_pos in enumerate(gt_positions):
            cost_matrix[i, j] = np.linalg.norm(p_pos - np.asarray(gt_pos, dtype=np.float64))

    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    tp = 0
    matched_errs = []
    matched_preds = set()
    matched_gts = set()

    for r, c in zip(row_ind, col_ind):
        dist = cost_matrix[r, c]
        if dist <= dist_threshold:
            tp += 1
            matched_errs.append(dist)
            matched_preds.add(r)
            matched_gts.add(c)

    fp = n_pred - tp
    fn = n_gt - tp

    return tp, fp, fn, matched_errs, confs

def evaluate_2d_frame(predictions_2d, gt_boxes_2d, iou_threshold: float = 0.50, conf_threshold: float = 0.25):
    """
    Evaluates 2D camera detections against authoritative 2D ground truth bounding boxes
    using Hungarian global bipartite matching under an IoU threshold (Pascal VOC / COCO rule).
    
    Args:
        predictions_2d: list of CameraDetection (has .bbox [x1, y1, x2, y2] and .confidence)
        gt_boxes_2d: list of dicts with key 'bbox': [x1, y1, x2, y2] or raw [x1, y1, x2, y2]
        iou_threshold: IoU threshold for valid match (default: 0.50)
        conf_threshold: confidence cutoff (default: 0.25)
    
    Returns:
        tp, fp, fn, matched_ious, confs
    """
    valid_preds = []
    confs = []
    for p in predictions_2d:
        conf = getattr(p, "confidence", 1.0)
        confs.append(float(conf))
        if conf >= conf_threshold:
            valid_preds.append(p)

    gt_boxes = [g["bbox"] if isinstance(g, dict) and "bbox" in g else g for g in gt_boxes_2d]

    n_gt = len(gt_boxes)
    n_pred = len(valid_preds)

    if n_gt == 0:
        return 0, n_pred, 0, [], confs
    if n_pred == 0:
        return 0, 0, n_gt, [], confs

    # Build IoU cost matrix: cost = 1.0 - IoU
    cost_matrix = np.full((n_pred, n_gt), fill_value=1.0, dtype=np.float64)
    for i, pred in enumerate(valid_preds):
        p_box = getattr(pred, "bbox", pred)
        for j, gt_box in enumerate(gt_boxes):
            iou = compute_2d_box_iou(p_box, gt_box)
            cost_matrix[i, j] = 1.0 - iou

    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    tp = 0
    matched_ious = []
    min_cost = 1.0 - iou_threshold

    for r, c in zip(row_ind, col_ind):
        cost = cost_matrix[r, c]
        if cost <= min_cost:
            tp += 1
            matched_ious.append(1.0 - cost)

    fp = n_pred - tp
    fn = n_gt - tp

    return tp, fp, fn, matched_ious, confs

# Backward compatibility alias
def evaluate_single_frame(predictions, gt_targets, match_dist: float = 2.5):
    """Backward-compatible wrapper evaluating single frame detections."""
    tp, fp, fn, loc_errs, _ = evaluate_3d_frame(predictions, gt_targets, dist_threshold=match_dist)
    m = compute_aggregate_metrics(tp, fp, fn, loc_errs)
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": m["precision"],
        "recall": m["recall"],
        "f1_score": m["f1_score"],
        "loc_err_m": m["localization_error_m"] if m["localization_error_m"] is not None else 0.0
    }

def evaluate_detection_performance(predictions, gt_targets, p_dict, match_dist=2.5, is_2d=False, gt_boxes_2d=None):
    """
    Standard evaluation updater for benchmark loops.
    Updates dictionary in-place with true positives, false positives, false negatives,
    localization errors, and confidences.
    """
    if is_2d and gt_boxes_2d is not None:
        tp, fp, fn, ious, confs = evaluate_2d_frame(predictions, gt_boxes_2d, iou_threshold=0.50)
        p_dict["tp"] += tp
        p_dict["fp"] += fp
        p_dict["fn"] += fn
        p_dict["confs"].extend(confs)
        # For 2D monocular baseline, 3D localization error is not applicable (N/A)
    else:
        tp, fp, fn, loc_errs, confs = evaluate_3d_frame(predictions, gt_targets, dist_threshold=match_dist)
        p_dict["tp"] += tp
        p_dict["fp"] += fp
        p_dict["fn"] += fn
        p_dict["loc_errs"].extend(loc_errs)
        p_dict["confs"].extend(confs)
