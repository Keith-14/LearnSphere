"""
calibrator.py
=============
Personal calibration mode for the exam stress detector.

How it works
------------
1.  User clicks "Record Calm" → we store ~60 frames of emotion probability
    vectors while they sit naturally at their desk.
2.  User clicks "Record Stressed" → they frown/make a stressed face for ~60 frames.
3.  We fit a simple SVM (sklearn, <1 ms inference) on those two distribu-
    tions and save it as models/personal_svm.pkl.
4.  In pipeline.py, if a personal model exists, its prediction overrides
    the base emotion model's state decision.

Why this works
--------------
The FER+ ONNX model has systematic bias (it was trained on posed lab faces),
so the raw probabilities are warped for any individual.  The SVM learns
**your personal probability fingerprint** for each state from only ~60 frames
of data.  It doesn't need retraining on the emotion model at all.

Usage (Streamlit)
-----------------
See app.py for the UI.  Programmatic usage:

    cal = Calibrator()
    cal.add_sample(probs_dict, label="calm")     # label "calm" or "stressed"
    cal.add_sample(probs_dict, label="stressed")
    success = cal.fit_and_save()                 # returns True on success

    cal2 = Calibrator.load()                     # load saved model
    state = cal2.predict(probs_dict)             # "stressed" | "calm" | None
"""

from __future__ import annotations

import logging
import pickle
from pathlib import Path
from typing import Literal

import numpy as np

logger = logging.getLogger(__name__)

_MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "personal_svm.pkl"
_EMOTION_KEYS = ["stressed", "focused", "confused", "calm"]
_MIN_SAMPLES_PER_CLASS = 15   # minimum frames before we can fit


def _probs_to_vec(probs: dict[str, float]) -> np.ndarray:
    """Convert probs dict to a fixed-order feature vector."""
    return np.array([probs.get(k, 0.0) for k in _EMOTION_KEYS], dtype=np.float32)


class Calibrator:
    """
    Collects per-user emotion probability samples and trains a personal
    binary SVM (calm vs stressed) or 4-class SVM.
    """

    def __init__(self):
        self._samples: list[np.ndarray] = []
        self._labels:  list[str]        = []
        self._clf = None   # sklearn SVC

    # ------------------------------------------------------------------
    # Data collection
    # ------------------------------------------------------------------

    def add_sample(
        self,
        probs: dict[str, float],
        label: Literal["calm", "stressed", "focused", "confused"],
    ) -> None:
        """Store one frame's emotion vector with its ground-truth label."""
        self._samples.append(_probs_to_vec(probs))
        self._labels.append(label)

    def sample_count(self, label: str | None = None) -> int:
        if label is None:
            return len(self._labels)
        return sum(1 for l in self._labels if l == label)

    def clear(self) -> None:
        self._samples.clear()
        self._labels.clear()
        self._clf = None

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def ready_to_fit(self) -> tuple[bool, str]:
        """Return (ok, reason_string)."""
        for label in ("calm", "stressed"):
            n = self.sample_count(label)
            if n < _MIN_SAMPLES_PER_CLASS:
                return False, f"Need {_MIN_SAMPLES_PER_CLASS} '{label}' samples, have {n}"
        return True, "ok"

    def fit_and_save(self) -> bool:
        """
        Fit SVM on collected samples, save to disk.
        Returns True on success.
        """
        ok, reason = self.ready_to_fit()
        if not ok:
            logger.warning("Cannot fit: %s", reason)
            return False

        try:
            from sklearn.svm import SVC           # type: ignore
            from sklearn.preprocessing import StandardScaler  # type: ignore

            X = np.vstack(self._samples)
            y = np.array(self._labels)

            scaler = StandardScaler()
            X_s = scaler.fit_transform(X)

            clf = SVC(kernel="rbf", probability=True, C=5.0, gamma="scale")
            clf.fit(X_s, y)

            payload = {"clf": clf, "scaler": scaler, "classes": clf.classes_.tolist()}
            _MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(_MODEL_PATH, "wb") as f:
                pickle.dump(payload, f)

            self._clf = payload
            logger.info("Personal SVM saved → %s", _MODEL_PATH)
            return True

        except Exception as exc:
            logger.error("SVM training failed: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    def predict(self, probs: dict[str, float]) -> str | None:
        """
        Predict using the personal SVM.
        Returns a state string or None if no model loaded.
        """
        if self._clf is None:
            return None
        try:
            vec    = _probs_to_vec(probs).reshape(1, -1)
            vec_s  = self._clf["scaler"].transform(vec)
            proba  = self._clf["clf"].predict_proba(vec_s)[0]
            classes = self._clf["classes"]
            best_idx = int(np.argmax(proba))
            best_conf = float(proba[best_idx])
            if best_conf < 0.45:   # uncertain — don't force a class
                return None
            return classes[best_idx]
        except Exception as exc:
            logger.debug("Personal SVM predict failed: %s", exc)
            return None

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    @classmethod
    def load(cls) -> "Calibrator":
        """Load saved personal model from disk."""
        cal = cls()
        if _MODEL_PATH.exists():
            try:
                with open(_MODEL_PATH, "rb") as f:
                    cal._clf = pickle.load(f)
                logger.info("Personal SVM loaded from %s", _MODEL_PATH)
            except Exception as exc:
                logger.warning("Failed to load personal SVM: %s", exc)
        return cal

    @staticmethod
    def model_exists() -> bool:
        return _MODEL_PATH.exists()

    @staticmethod
    def delete_model() -> None:
        if _MODEL_PATH.exists():
            _MODEL_PATH.unlink()
