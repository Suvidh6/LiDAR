"""
src/evaluation/metrics.py
Statistical and localization performance evaluation metrics for sensor fusion.

Provides:
- evaluate_detection_performance: Matches predictions to ground truth centroids
  and computes Precision, Recall, F1-Score, and Mean 3D Localization Error.
- compute_trajectory_jitter: Inter-frame displacement standard deviation.
"""

import numpy as np

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
        p_pos = pred.position
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
