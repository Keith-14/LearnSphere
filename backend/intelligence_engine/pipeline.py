"""
pipeline.py
===========
Orchestrates the full inference pipeline:

    Webcam → FaceDetector → (conditional) EmotionModel → StressScorer → Logger

The main entry-point for the Streamlit UI is `process_frame(frame)` which
returns a fully populated output dict.

For standalone CLI usage, call `run_webcam()`.
"""

from __future__ import annotations

import logging
import time
from typing import Optional

import cv2
import numpy as np

from .face_detector  import FaceDetector
from .emotion_model  import EmotionModel, EXAM_EMOTIONS
from .stress_scorer  import StressScorer
from .logger         import SessionLogger, build_record
from .calibrator     import Calibrator

logger = logging.getLogger(__name__)

# Default neutral probabilities (used when emotion inference is skipped)
_NEUTRAL_PROBS: dict[str, float] = {e: 1.0 / len(EXAM_EMOTIONS) for e in EXAM_EMOTIONS}


class ExamPipeline:
    """
    End-to-end inference pipeline for the exam stress detection system.

    Parameters
    ----------
    skip_frames       : Run emotion inference every N frames (default 2).
                        Face detection still runs every frame.
    buffer_size       : Rolling window for stress scorer (default 10).
    log_every         : Write to disk every N frames (default 5).
    enable_logging    : Whether to log to disk (disable for unit tests).
    """

    def __init__(
        self,
        skip_frames:    int  = 2,
        buffer_size:    int  = 10,
        log_every:      int  = 5,
        enable_logging: bool = True,
    ):
        logger.info("Initialising ExamPipeline …")
        self.face_detector  = FaceDetector()
        self.emotion_model  = EmotionModel()
        self.stress_scorer  = StressScorer(buffer_size=buffer_size)
        self.session_logger = SessionLogger(log_every=log_every) if enable_logging else None
        self.calibrator     = Calibrator.load()   # loads personal SVM if exists

        self._skip_frames   = skip_frames
        self._frame_count   = 0
        self._last_probs    = _NEUTRAL_PROBS.copy()
        self._last_record: Optional[dict] = None
        self._last_bbox     = None

        logger.info("ExamPipeline ready. Personal SVM: %s",
                    "LOADED" if Calibrator.model_exists() else "none")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process_frame(self, frame: np.ndarray) -> dict:
        """
        Process a single BGR frame and return the full output record.
        record now includes 'face_crop' (np.ndarray | None) for UI preview.
        """
        self._frame_count += 1

        # ── 1. Face detection (every frame) ──────────────────────────
        detection  = self.face_detector.detect(frame)
        face_det   = detection["face_detected"]
        bbox       = detection["bbox"]
        head_pose  = detection["head_pose"]
        valid      = detection["valid_for_emotion"]
        self._last_bbox = bbox

        # ── 2. Extract face crop for UI preview ───────────────────────
        face_crop = self._extract_crop(frame, bbox)

        # ── 3. Emotion inference (every skip_frames, only if valid) ───
        if valid and self._frame_count % self._skip_frames == 0:
            probs = self.emotion_model.predict_from_frame(frame, bbox)
            self._last_probs = probs
        else:
            probs = self._last_probs

        # ── 4. Stress scoring (movement-primary) ─────────────────────
        stress_score, state = self.stress_scorer.update(
            probs             = probs if valid else None,
            valid_for_emotion = valid,
            face_detected     = face_det,
            head_pose         = head_pose,
            movement_score    = detection.get("movement_score", 0.0),
            direction_changes = detection.get("direction_changes", 0),
            is_stable         = detection.get("is_stable", True),
            was_stable        = detection.get("was_stable", True),
        )

        # ── 5. Personal SVM override (if calibrated) ──────────────────
        if valid and Calibrator.model_exists():
            personal_state = self.calibrator.predict(probs)
            if personal_state is not None:
                state = personal_state   # override base model

        # ── 6. Build output record ────────────────────────────────────
        record = build_record(
            state             = state,
            stress_score      = stress_score,
            probabilities     = probs,
            face_detected     = face_det,
            head_pose         = head_pose,
            valid_for_emotion = valid,
        )
        record["face_crop"]         = face_crop
        record["movement_score"]    = detection.get("movement_score", 0.0)
        record["stability_score"]   = detection.get("stability_score", 1.0)
        record["direction_changes"] = detection.get("direction_changes", 0)
        record["is_stable"]         = detection.get("is_stable", True)
        self._last_record = record

        # ── 7. Log ────────────────────────────────────────────────────
        if self.session_logger:
            self.session_logger.log({k: v for k, v in record.items()
                                     if k != "face_crop"})   # don't log image bytes

        return record

    def reload_calibrator(self):
        """Hot-reload personal SVM after the user has just calibrated."""
        self.calibrator = Calibrator.load()

    @staticmethod
    def _extract_crop(frame: np.ndarray, bbox) -> np.ndarray | None:
        """Return 96×96 RGB face crop, or None if no bbox."""
        if bbox is None or frame is None:
            return None
        x, y, w, h = bbox
        pad = int(0.12 * max(w, h))
        fh, fw = frame.shape[:2]
        crop = frame[max(0, y - pad): min(fh, y + h + pad),
                     max(0, x - pad): min(fw, x + w + pad)]
        if crop.size == 0:
            return None
        crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
        return cv2.resize(crop_rgb, (96, 96))

    def draw_overlay(self, frame: np.ndarray, record: dict) -> np.ndarray:
        """
        Draw the bounding box, state label, and stress bar on the frame.
        Returns annotated frame copy (does not mutate input).
        """
        vis = self.face_detector.draw(
            frame,
            {
                "face_detected":    record.get("face_detected", False),
                "bbox":             self._face_detector_bbox(),
                "head_pose":        record.get("head_pose", "unknown"),
                "valid_for_emotion": record.get("valid_for_emotion", False),
                "pitch_deg":        0.0,
                "yaw_deg":          0.0,
            },
        )

        # State label
        state = record.get("state", "unknown")
        score = record.get("stress_score", 0.0)
        label = f"State: {state}  |  Stress: {score:.2f}"
        _draw_text_with_bg(vis, label, (10, 30))

        # Stress score bar
        h, w = vis.shape[:2]
        bar_y, bar_h = h - 20, 10
        cv2.rectangle(vis, (10, bar_y), (w - 10, bar_y + bar_h), (50, 50, 50), -1)
        bar_w = int((w - 20) * score)
        bar_color = _score_color(score)
        cv2.rectangle(vis, (10, bar_y), (10 + bar_w, bar_y + bar_h), bar_color, -1)

        return vis

    def _face_detector_bbox(self):
        """Return the last detected bbox from the face detector (via last record)."""
        # Bounding box is stored in the detection dict not in record,
        # we skip re-drawing it here since face_detector.draw() is called
        # with a cached detection in process_frame.
        return None

    @property
    def last_record(self) -> Optional[dict]:
        return self._last_record

    def close(self):
        self.face_detector.close()
        if self.session_logger:
            self.session_logger.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    # ------------------------------------------------------------------
    # CLI entry-point
    # ------------------------------------------------------------------

    def run_webcam(self, camera_index: int = 0, target_fps: int = 10):
        """
        Standalone webcam loop.  Press 'q' to quit.
        """
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open camera index {camera_index}")

        frame_time = 1.0 / target_fps
        logger.info("Webcam started. Press 'q' to quit.")

        try:
            while True:
                t0 = time.perf_counter()
                ret, frame = cap.read()
                if not ret:
                    logger.warning("Empty frame received from webcam.")
                    continue

                record = self.process_frame(frame)
                annotated = self.draw_overlay(frame, record)

                cv2.imshow("VEGA Exam Monitor", annotated)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

                elapsed = time.perf_counter() - t0
                sleep_time = frame_time - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)
        finally:
            cap.release()
            cv2.destroyAllWindows()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _draw_text_with_bg(img: np.ndarray, text: str, origin: tuple[int, int]):
    font       = cv2.FONT_HERSHEY_SIMPLEX
    scale, thk = 0.65, 1
    (tw, th), _ = cv2.getTextSize(text, font, scale, thk)
    x, y = origin
    cv2.rectangle(img, (x - 2, y - th - 4), (x + tw + 2, y + 4), (20, 20, 20), -1)
    cv2.putText(img, text, (x, y), font, scale, (230, 230, 230), thk, cv2.LINE_AA)


def _score_color(score: float) -> tuple[int, int, int]:
    """Green → Yellow → Red based on stress score."""
    r = int(min(255, score * 2 * 255))
    g = int(min(255, (1 - score) * 2 * 255))
    return (0, g, r)   # BGR
