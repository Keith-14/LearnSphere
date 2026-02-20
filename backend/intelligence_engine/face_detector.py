"""
face_detector.py
================
Face detection + HEAD MOVEMENT STABILITY tracking.

Primary behavioral signals for exam stress detection:
    - movement_score  : 0.0 (stone still) → 1.0 (very erratic)
    - is_stable       : True if head has been still for last N frames
    - direction_changes: how many times head reversed direction
                         (high = confused / scanning left-right)
    - stability_score : 1.0 - movement_score (for display)

Design rationale (new use case)
--------------------------------
A student solving an exam paper often looks DOWN at the paper, not the camera.
That is perfectly fine and should be read as CALM/FOCUSED.
The key stress signal is NOT where they're looking but HOW MUCH their head
moves and how erratically they scan around.

    STABLE head (even off-camera)  → calm / focused
    ERRATIC rapid movement         → stressed / confused

We no longer penalise "not frontal" — valid_for_emotion is still correct
for the emotion model crop, but the stress scorer uses movement as primary.
"""

from __future__ import annotations

import math
from collections import deque

import cv2
import numpy as np

# ── Cascade paths ─────────────────────────────────────────────────────────────
_CASCADE_PATH     = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
_EYE_CASCADE_PATH = cv2.data.haarcascades + "haarcascade_eye.xml"

# ── Movement tracking config ──────────────────────────────────────────────────
_CENTROID_HISTORY  = 15    # frames of centroid history
_STABLE_THRESHOLD  = 0.03  # movement_score below this → stable (3% of diagonal)
_ERRATIC_THRESHOLD = 0.18  # movement_score above this → erratic / stressed

# ── Face detection config ─────────────────────────────────────────────────────
_SCALE_FACTOR  = 1.15
_MIN_NEIGHBORS = 4
_MIN_FACE_SIZE = (55, 55)


class FaceDetector:
    """
    OpenCV Haar face detector augmented with:
      • Centroid tracking (rolling history of face centre positions)
      • Movement velocity (avg frame-to-frame displacement, normalised)
      • Direction-reversal counter (rapid left-right scanning = confused)
      • Stability classification
    """

    def __init__(self):
        self._face_cascade = cv2.CascadeClassifier(_CASCADE_PATH)
        self._eye_cascade  = cv2.CascadeClassifier(_EYE_CASCADE_PATH)
        if self._face_cascade.empty():
            raise RuntimeError(f"Haar cascade not found at {_CASCADE_PATH}")

        # Rolling centroid history — (cx_norm, cy_norm) tuples
        self._centroids: deque[tuple[float, float]] = deque(maxlen=_CENTROID_HISTORY)
        # Frames since face last seen (for "was stable" memory)
        self._frames_no_face   = 0
        self._last_movement    = 0.0
        self._last_is_stable   = True

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def detect(self, frame: np.ndarray) -> dict:
        """
        Process a single BGR frame.

        Returns:
            face_detected    : bool
            bbox             : (x,y,w,h) or None
            head_pose        : "frontal" | "down" | "away" | "unknown"
            valid_for_emotion: bool  (frontal face crop available)
            movement_score   : float 0-1  (primary stress signal)
            direction_changes: int   (reversal count in history window)
            is_stable        : bool
            stability_score  : float 0-1  (1 = perfectly still)
            was_stable       : bool  (was stable before face disappeared)
        """
        result = {
            "face_detected":     False,
            "bbox":              None,
            "head_pose":         "unknown",
            "valid_for_emotion": False,
            "landmarks":         None,
            "pitch_deg":         0.0,
            "yaw_deg":           0.0,
            "movement_score":    self._last_movement,
            "direction_changes": 0,
            "is_stable":         self._last_is_stable,
            "stability_score":   1.0 - self._last_movement,
            "was_stable":        self._last_is_stable,
        }

        if frame is None or frame.size == 0:
            return result

        h, w = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        faces = self._face_cascade.detectMultiScale(
            gray,
            scaleFactor  = _SCALE_FACTOR,
            minNeighbors = _MIN_NEIGHBORS,
            minSize      = _MIN_FACE_SIZE,
        )

        if not len(faces):
            self._frames_no_face += 1
            result["was_stable"] = self._last_is_stable
            # Carry forward last movement/stability (head may be at paper)
            result["movement_score"]  = self._last_movement
            result["is_stable"]       = self._last_is_stable
            result["stability_score"] = 1.0 - self._last_movement
            return result

        self._frames_no_face = 0
        fx, fy, fw, fh = max(faces, key=lambda b: b[2] * b[3])
        result["face_detected"] = True
        result["bbox"]          = (fx, fy, fw, fh)

        # Normalised centroid
        cx_n = (fx + fw / 2) / w
        cy_n = (fy + fh / 2) / h
        self._centroids.append((cx_n, cy_n))

        # ── Head pose (simple geometry) ───────────────────────────────
        aspect = fw / max(fh, 1)
        face_top_norm = fy / h
        upper_roi = gray[fy: fy + fh // 2, fx: fx + fw]
        eyes = self._eye_cascade.detectMultiScale(
            upper_roi, scaleFactor=1.1, minNeighbors=3, minSize=(12, 12)
        )
        eyes_ok = len(eyes) >= 1

        if face_top_norm > 0.72 and not eyes_ok:
            head_pose = "down"
        elif aspect < 0.38:
            head_pose = "away"
        else:
            head_pose = "frontal"

        result["head_pose"]         = head_pose
        result["valid_for_emotion"] = (head_pose == "frontal")

        # ── Movement analysis ─────────────────────────────────────────
        mvt, dir_changes, is_stable = self._movement_analysis()
        self._last_movement  = mvt
        self._last_is_stable = is_stable

        result["movement_score"]   = mvt
        result["direction_changes"] = dir_changes
        result["is_stable"]        = is_stable
        result["stability_score"]  = round(1.0 - mvt, 3)
        return result

    def draw(self, frame: np.ndarray, detection: dict) -> np.ndarray:
        vis = frame.copy()
        if not detection.get("face_detected") or detection.get("bbox") is None:
            return vis
        x, y, bw, bh = detection["bbox"]
        is_stable = detection.get("is_stable", True)
        mvt       = detection.get("movement_score", 0.0)
        color     = (0, 220, 80) if is_stable else (0, 100, 255)
        cv2.rectangle(vis, (x, y), (x + bw, y + bh), color, 2)
        label = f"mvt:{mvt:.2f}  {'STABLE' if is_stable else 'ERRATIC'}"
        cv2.putText(vis, label, (x, max(y - 8, 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 1, cv2.LINE_AA)
        return vis

    def close(self): pass
    def __enter__(self): return self
    def __exit__(self, *_): self.close()

    # ------------------------------------------------------------------
    # Private: movement analysis
    # ------------------------------------------------------------------

    def _movement_analysis(self) -> tuple[float, int, bool]:
        """
        Returns: (movement_score 0-1, direction_change_count, is_stable)
        """
        pts = list(self._centroids)
        if len(pts) < 3:
            return 0.0, 0, True

        # Velocity: avg euclidean distance between consecutive normalised centroids
        velocities = []
        for i in range(1, len(pts)):
            dx = pts[i][0] - pts[i - 1][0]
            dy = pts[i][1] - pts[i - 1][1]
            velocities.append(math.sqrt(dx * dx + dy * dy))

        avg_vel = sum(velocities) / len(velocities)

        # Scale: _ERRATIC_THRESHOLD maps to 1.0
        movement_score = min(1.0, avg_vel / _ERRATIC_THRESHOLD)

        # Direction changes (x-axis reversals — left-right scanning)
        dx_signs = []
        for i in range(1, len(pts)):
            dx = pts[i][0] - pts[i - 1][0]
            if abs(dx) > 0.005:        # ignore tiny jitter
                dx_signs.append(1 if dx > 0 else -1)

        dir_changes = sum(
            1 for i in range(1, len(dx_signs))
            if dx_signs[i] != dx_signs[i - 1]
        )

        is_stable = movement_score < _STABLE_THRESHOLD

        return round(movement_score, 3), dir_changes, is_stable
