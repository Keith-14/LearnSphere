"""
emotion_model.py
================
Emotion recognition using the ONNX emotion-ferplus model.
NO TensorFlow dependency — runs via onnxruntime (pure C++ backend).

Model:  emotion-ferplus-8.onnx  (ONNX Model Zoo, MIT license)
Input:  (1, 1, 64, 64)  float32  — grayscale face, normalised to [-1, 1]
Output: (1, 8)          float32  — raw logits → softmax

Label order (FER+):
    0: neutral, 1: happiness, 2: surprise, 3: sadness,
    4: anger,   5: disgust,   6: fear,     7: contempt

Exam emotion mapping:
    stressed  ← anger + disgust + fear + sadness
    focused   ← neutral
    confused  ← surprise + contempt
    calm      ← happiness
"""

from __future__ import annotations

import logging
import os
import urllib.request
from pathlib import Path

import cv2
import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Model config
# ---------------------------------------------------------------------------
_MODEL_DIR  = Path(__file__).resolve().parent.parent / "models"
_MODEL_PATH = _MODEL_DIR / "emotion-ferplus-8.onnx"

_MODEL_URL = (
    "https://github.com/onnx/models/raw/main/validated/vision/body_analysis/"
    "emotion_ferplus/model/emotion-ferplus-8.onnx"
)

# FER+ output label order
_FERPLUS_LABELS = [
    "neutral", "happiness", "surprise", "sadness",
    "anger",   "disgust",   "fear",     "contempt",
]

# FER+ label → exam emotion
_FER_TO_EXAM: dict[str, str] = {
    "neutral":   "focused",
    "happiness": "calm",
    "surprise":  "confused",
    "sadness":   "stressed",
    "anger":     "stressed",
    "disgust":   "stressed",
    "fear":      "stressed",
    "contempt":  "confused",
}

EXAM_EMOTIONS = ["stressed", "focused", "confused", "calm"]

# Input image size expected by the model
_INPUT_SIZE = 64


class EmotionModel:
    """
    Lightweight ONNX-based emotion classifier.
    Uses onnxruntime — zero TensorFlow dependency.
    """

    def __init__(self):
        self._session = None
        self._input_name  = None
        self._output_name = None
        self._load_model()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def predict(self, face_crop: np.ndarray) -> dict[str, float]:
        """
        Run emotion inference on a BGR face crop.

        Returns:
            dict {stressed, focused, confused, calm} with values summing to 1.
            Returns uniform distribution on error / empty crop.
        """
        if face_crop is None or face_crop.size == 0 or self._session is None:
            return self._uniform()

        try:
            inp = self._preprocess(face_crop)
            outputs = self._session.run(
                [self._output_name],
                {self._input_name: inp},
            )
            logits = np.array(outputs[0]).flatten()

            # ── Temperature scaling: lower T → sharper, more decisive ──
            # T < 1 amplifies differences between logits so the model
            # doesn't collapse everything into "neutral / focused".
            TEMPERATURE = 0.5   # lower = sharper predictions
            logits = logits / TEMPERATURE

            # Softmax
            exp_logits  = np.exp(logits - logits.max())
            probs_raw   = exp_logits / exp_logits.sum()
            return self._map_to_exam(probs_raw)

        except Exception as exc:
            logger.debug("Emotion inference failed: %s", exc)
            return self._uniform()

    def predict_from_frame(
        self,
        frame: np.ndarray,
        bbox: tuple[int, int, int, int] | None,
    ) -> dict[str, float]:
        """Crop face from full BGR frame using bbox (x, y, w, h) then predict."""
        if bbox is None or frame is None:
            return self._uniform()
        x, y, w, h = bbox
        pad = int(0.10 * max(w, h))
        fh, fw = frame.shape[:2]
        crop = frame[max(0, y - pad): min(fh, y + h + pad),
                     max(0, x - pad): min(fw, x + w + pad)]
        return self.predict(crop)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load_model(self):
        """Download model if needed, then load into onnxruntime session."""
        _MODEL_DIR.mkdir(parents=True, exist_ok=True)

        if not _MODEL_PATH.exists():
            logger.info("Downloading emotion-ferplus ONNX model …")
            print(f"[EmotionModel] Downloading model from ONNX Model Zoo …")
            try:
                urllib.request.urlretrieve(_MODEL_URL, _MODEL_PATH)
                print(f"[EmotionModel] Model saved → {_MODEL_PATH}")
            except Exception as exc:
                logger.error("Model download failed: %s", exc)
                print(f"[EmotionModel] WARNING: Download failed ({exc}). "
                      "Emotion inference will return uniform scores.")
                return

        try:
            import onnxruntime as ort  # type: ignore
            sess_options = ort.SessionOptions()
            sess_options.log_severity_level = 3   # silence ort logs
            self._session = ort.InferenceSession(
                str(_MODEL_PATH),
                sess_options,
                providers=["CPUExecutionProvider"],
            )
            self._input_name  = self._session.get_inputs()[0].name
            self._output_name = self._session.get_outputs()[0].name
            logger.info(
                "ONNX emotion model loaded (input=%s, output=%s).",
                self._input_name, self._output_name,
            )
        except ImportError:
            raise RuntimeError(
                "onnxruntime is not installed. "
                "Run: pip install onnxruntime"
            )
        except Exception as exc:
            logger.error("Failed to load ONNX session: %s", exc)
            self._session = None

    @staticmethod
    def _preprocess(bgr_face: np.ndarray) -> np.ndarray:
        """
        Convert BGR face crop → model input tensor.
        Shape: (1, 1, 64, 64)  float32  normalised to [-1, 1].
        """
        gray = cv2.cvtColor(bgr_face, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (_INPUT_SIZE, _INPUT_SIZE),
                             interpolation=cv2.INTER_LINEAR)
        # Normalise to [-1, 1]
        tensor = resized.astype(np.float32) / 128.0 - 1.0
        # Shape: (1, 1, H, W)
        return tensor[np.newaxis, np.newaxis, :, :]

    @staticmethod
    def _map_to_exam(raw_probs: np.ndarray) -> dict[str, float]:
        """Aggregate FER+ raw probabilities into 4 exam buckets.

        De-biasing: neutral is the most commonly predicted class in FER+
        (the model defaults to it when uncertain).  We scale it down so the
        'focused' bucket doesn't overwhelm everything else.
        """
        # Neutral de-emphasis factor — dramatically reduce neutral's weight
        # so other emotions get a much larger relative share.
        # FER+ is heavily biased toward 'neutral' on resting faces;
        # suppressing it makes real expressions register clearly.
        NEUTRAL_SCALE = 0.15   # was 0.45 — much more aggressive suppression

        exam_scores: dict[str, float] = {e: 0.0 for e in EXAM_EMOTIONS}
        for idx, label in enumerate(_FERPLUS_LABELS):
            exam_label = _FER_TO_EXAM.get(label)
            if exam_label and idx < len(raw_probs):
                p = float(raw_probs[idx])
                if label == "neutral":
                    p *= NEUTRAL_SCALE   # de-emphasise the default class
                exam_scores[exam_label] += p
        total = sum(exam_scores.values())
        if total > 0:
            return {k: v / total for k, v in exam_scores.items()}
        return EmotionModel._uniform_dict()

    @staticmethod
    def _uniform() -> dict[str, float]:
        return EmotionModel._uniform_dict()

    @staticmethod
    def _uniform_dict() -> dict[str, float]:
        p = 1.0 / len(EXAM_EMOTIONS)
        return {e: p for e in EXAM_EMOTIONS}
