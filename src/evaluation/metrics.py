"""
src/evaluation/metrics.py
Statistical and localization performance evaluation metrics for sensor fusion.

Provides:
- evaluate_single_frame: Evaluates predictions against ground truth targets for a single frame.
- evaluate_detection_performance: Matches predictions to ground truth centroids and updates aggregate dict.
- compute_trajectory_jitter: Inter-frame displacement standard deviation.
- compute_aggregate_metrics: Computes precision, recall, f1, and mean localization error from counts.
"""

import numpy as np

def compute_aggregate_metrics(tp: int, fp: int, fn: int, loc_errs: list) -> dict:
    """Calculates standard classification and localization metrics."""
    precision = tp / max(1, tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / max(1, tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    loc_err = float(np.mean(loc_errs)) if len(loc_errs) > 0 else 0.0

    return {
        "precision": float(round(precision, 4)),
        "recall": float(round(recall, 4)),
        "f1_score": float(round(f1, 4)),
        "localization_error_m": float(round(loc_err, 4))
    }

def evaluate_single_frame(predictions, gt_targets, match_dist: float = 3.0) -> dict:
    """
    Evaluates detections for a single frame against ground-truth obstacle positions.
    Returns dictionary with TP, FP, FN, precision, recall, F1, and mean localization error.
    """
    n_gt = len(gt_targets)
    n_pred = len(predictions)

    if n_gt == 0 and n_pred == 0:
        return {"tp": 0, "fp": 0, "fn": 0, "precision": 1.0, "recall": 1.0, "f1_score": 1.0, "loc_err_m": 0.0}
    if n_gt == 0:
        return {"tp": 0, "fp": n_pred, "fn": 0, "precision": 0.0, "recall": 1.0, "f1_score": 0.0, "loc_err_m": 0.0}
    if n_pred == 0:
        return {"tp": 0, "fp": 0, "fn": n_gt, "precision": 0.0, "recall": 0.0, "f1_score": 0.0, "loc_err_m": 0.0}

    matched_gt = set()
    loc_errs = []
    tp = 0
    fp = 0

    for pred in predictions:
        p_pos = pred.position if hasattr(pred, "position") else pred
        dists = [np.linalg.norm(p_pos - gt) for gt in gt_targets]
        min_idx = int(np.argmin(dists))
        min_dist = dists[min_idx]

        if min_dist <= match_dist and min_idx not in matched_gt:
            tp += 1
            matched_gt.add(min_idx)
            loc_errs.append(min_dist)
        else:
            fp += 1

    fn = n_gt - len(matched_gt)
    m = compute_aggregate_metrics(tp, fp, fn, loc_errs)
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": m["precision"],
        "recall": m["recall"],
        "f1_score": m["f1_score"],
        "loc_err_m": m["localization_error_m"]
    }

def evaluate_detection_performance(predictions, gt_targets, p_dict, match_dist=3.0):
    """
    Evaluates list of predicted object detections against ground truth target centroids.
    Updates p_dict in place with true positives, false positives, false negatives,
    and localization Euclidean error distances.
    """
    n_gt = len(gt_targets)
    n_pred = len(predictions)

    if n_gt == 0:
        p_dict["fp"] += n_pred
        return
    if n_pred == 0:
        p_dict["fn"] += n_gt
        return

    matched_gt = set()
    for pred in predictions:
        p_pos = pred.position if hasattr(pred, "position") else pred
        if hasattr(pred, "confidence"):
            p_dict["confs"].append(pred.confidence)

        # Nearest GT target
        dists = [np.linalg.norm(p_pos - gt) for gt in gt_targets]
        min_idx = int(np.argmin(dists))
        min_dist = dists[min_idx]

        if min_dist <= match_dist and min_idx not in matched_gt:
            p_dict["tp"] += 1
            matched_gt.add(min_idx)
            p_dict["loc_errs"].append(min_dist)
        else:
            p_dict["fp"] += 1

    p_dict["fn"] += (n_gt - len(matched_gt))

def compute_trajectory_jitter(positions_xy):
    """
    Computes standard displacement jitter between consecutive tracklet 2D coordinates.
    """
    pts = np.asarray(positions_xy, dtype=np.float64)
    if len(pts) < 2:
        return 0.0
    diffs = np.diff(pts, axis=0)
    step_lengths = np.linalg.norm(diffs, axis=1)
    return float(np.mean(step_lengths))
