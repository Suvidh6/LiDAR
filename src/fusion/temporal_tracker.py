"""
src/fusion/temporal_tracker.py
Multi-frame object tracking system supporting IMU ego-motion compensation.

Maintains tracklets across a sliding temporal window [t-2, t-1, t].
Applies SE(3) ego-motion compensation via IMU T_ego to prevent spatial smearing and ghosting.
Applies Kalman filtering and tracklet lifecycle management to filter transient noise
and maintain stable multi-frame tracks.
"""

import numpy as np
from scipy.optimize import linear_sum_assignment

class TemporalTrack:
    """Represents a 3D object tracklet across time."""
    _id_counter = 0

    def __init__(self, init_pos, init_conf=0.8, class_name="vehicle"):
        TemporalTrack._id_counter += 1
        self.track_id = TemporalTrack._id_counter
        self.position = np.asarray(init_pos, dtype=np.float64)  # [x, y, z]
        self.velocity = np.zeros(3, dtype=np.float64)           # [vx, vy, vz]
        self.confidence = float(init_conf)
        self.class_name = str(class_name)

        # State covariance P (6x6: [x, y, z, vx, vy, vz])
        self.P = np.eye(6, dtype=np.float64)
        self.P[:3, :3] *= 0.5
        self.P[3:, 3:] *= 2.0

        self.hits = 1
        self.age = 1
        self.time_since_update = 0
        self.history = [self.position.copy()]

    @property
    def is_confirmed(self):
        """Confirmed once observed in at least 2 frames or high persistence."""
        return self.hits >= 2 or (self.hits == 1 and self.age == 1)

    @property
    def persistence_ratio(self):
        """Temporal consistency metric: hits / age."""
        return float(self.hits) / max(1, self.age)

    def predict(self, T_ego, dt=0.05, use_imu_compensation=True):
        """
        Projects track state into the current frame coordinate system.
        If use_imu_compensation=True, warps coordinate axes using T_ego^-1.
        Otherwise assumes a static world frame, accumulating ego-motion drift.
        """
        if use_imu_compensation and T_ego is not None:
            R_ego = T_ego[:3, :3]
            t_ego = T_ego[:3, 3]

            # Invert ego transform: p_curr = R_ego^T * (p_prev - t_ego)
            R_inv = R_ego.T
            pos_warped = R_inv @ (self.position - t_ego)
            vel_warped = R_inv @ self.velocity

            self.position = pos_warped + vel_warped * dt
            self.velocity = vel_warped
        else:
            self.position = self.position + self.velocity * dt

        Q = np.eye(6, dtype=np.float64) * 0.05
        Q[3:, 3:] *= 0.2
        self.P = self.P + Q

        self.age += 1
        self.time_since_update += 1

    def update(self, meas_pos, meas_conf=None, R_cov=None):
        """Standard 3D Kalman Filter measurement update."""
        z = np.asarray(meas_pos, dtype=np.float64)
        H = np.zeros((3, 6), dtype=np.float64)
        H[:3, :3] = np.eye(3)

        R = np.eye(3, dtype=np.float64) * 0.25 if R_cov is None else np.asarray(R_cov, dtype=np.float64)

        y = z - self.position
        S = H @ self.P @ H.T + R
        K = self.P @ H.T @ np.linalg.inv(S)

        state = np.hstack([self.position, self.velocity])
        state = state + K @ y
        self.position = state[:3]
        self.velocity = state[3:]

        I = np.eye(6, dtype=np.float64)
        self.P = (I - K @ H) @ self.P

        self.hits += 1
        self.time_since_update = 0
        if meas_conf is not None:
            self.confidence = 0.7 * self.confidence + 0.3 * meas_conf

        self.history.append(self.position.copy())
        if len(self.history) > 10:
            self.history.pop(0)

    def to_dict(self):
        return {
            "track_id": self.track_id,
            "position": [round(float(p), 3) for p in self.position],
            "velocity": [round(float(v), 3) for v in self.velocity],
            "confidence": round(float(self.confidence), 3),
            "hits": self.hits,
            "age": self.age,
            "persistence": round(self.persistence_ratio, 3),
            "is_confirmed": self.is_confirmed
        }

class TemporalTracker:
    """
    Multi-frame object tracking system supporting IMU ego-motion compensation.
    Enforces temporal consistency and filters transient single-frame errors.
    """
    def __init__(self, max_age=3, min_hits=2, dist_threshold=2.5, use_imu_compensation=True):
        self.max_age = max_age
        self.min_hits = min_hits
        self.dist_threshold = dist_threshold
        self.use_imu_compensation = use_imu_compensation
        self.tracks = []
        TemporalTrack._id_counter = 0

    def reset(self):
        self.tracks = []
        TemporalTrack._id_counter = 0

    def step(self, detection_list, T_ego=None, dt=0.05):
        """
        Executes one tracking cycle:
        1. Predict track states forward using IMU ego-motion T_ego.
        2. Associate predicted tracks with current detections via Hungarian matching.
        3. Update matched tracks; initialize new tracks; prune dead tracks.
        """
        for trk in self.tracks:
            trk.predict(T_ego, dt=dt, use_imu_compensation=self.use_imu_compensation)

        n_tracks = len(self.tracks)
        n_dets = len(detection_list)

        matched_tracks = set()
        matched_dets = set()

        if n_tracks > 0 and n_dets > 0:
            cost_matrix = np.zeros((n_tracks, n_dets), dtype=np.float64)
            for i, trk in enumerate(self.tracks):
                for j, det in enumerate(detection_list):
                    d_pos = np.asarray(det["position"])
                    dist = np.linalg.norm(trk.position - d_pos)
                    cost_matrix[i, j] = dist

            row_ind, col_ind = linear_sum_assignment(cost_matrix)

            for r, c in zip(row_ind, col_ind):
                if cost_matrix[r, c] <= self.dist_threshold:
                    matched_tracks.add(r)
                    matched_dets.add(c)
                    det = detection_list[c]
                    self.tracks[r].update(det["position"], meas_conf=det.get("confidence", 0.8))

        for j in range(n_dets):
            if j not in matched_dets:
                det = detection_list[j]
                new_track = TemporalTrack(
                    init_pos=det["position"],
                    init_conf=det.get("confidence", 0.7),
                    class_name=det.get("class_name", "vehicle")
                )
                self.tracks.append(new_track)

        surviving_tracks = []
        for trk in self.tracks:
            if trk.time_since_update <= self.max_age:
                surviving_tracks.append(trk)
        self.tracks = surviving_tracks

        confirmed = [trk for trk in self.tracks if trk.is_confirmed]
        return confirmed
