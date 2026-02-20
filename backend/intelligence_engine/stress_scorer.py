"""
stress_scorer.py
================
Movement-primary hybrid stress scoring for exam behaviour detection.

Signal weights
--------------
  Primary  (65%): Head movement stability
                  → still head (even looking at paper) = calm/focused
                  → erratic rapid scanning = stressed/confused

  Secondary (35%): Emotion model probabilities
                  → used for fine-grained calm vs focused distinction

State logic
-----------
  STABLE   + low emotion stress  → "calm"
  STABLE   + moderate stress     → "focused"  (concentrating)
  ERRATIC  + direction changes   → "confused"  (scanning, doesn't know answer)
  ERRATIC  + high emotion stress → "stressed"
  MOVING   (moderate)            → use emotion to decide

Special cases
-------------
  face_not_visible AND was_stable  → "working"  (looking at paper, solving)
  face_not_visible AND was_erratic → "face_not_visible"  (unknown)
"""

from __future__ import annotations

from collections import deque

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

# EMA alpha (0-1): how much current frame matters vs history
_EMA_ALPHA  = 0.75     # fast but not jittery

# Movement weighting in combined score
_MOVEMENT_WEIGHT = 0.65
_EMOTION_WEIGHT  = 0.35

# Stability thresholds (must match face_detector)
_STABLE_THRESHOLD  = 0.03   # movement_score < this → calm
_ERRATIC_THRESHOLD = 0.18   # movement_score > this → stressed

# Direction change threshold for "confused" (rapid left-right scanning)
_CONFUSED_DIR_CHANGES = 3   # per 15-frame window

# Minimum direction scanning for "confused" override
_DIR_CONFUSED_MOVEMENT = 0.10  # must also be moving at least this much

# Frames before "face not visible" becomes valid (avoids blink glitch)
_NO_FACE_GRACE_FRAMES = 8

# Score floor
_SCORE_FLOOR = 0.02


class StressScorer:
    """
    Hybrid stress scorer: movement-primary, emotion-secondary.
    """

    def __init__(self, buffer_size: int = 4):
        self._probs_buffer: deque[dict[str, float]] = deque(maxlen=buffer_size)
        self._smoothed_score: float = 0.2
        self._last_state: str = "calm"
        self._no_face_count: int = 0
        self._last_was_stable: bool = True

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(
        self,
        probs:             dict[str, float] | None,
        valid_for_emotion: bool,
        face_detected:     bool,
        head_pose:         str,
        movement_score:    float = 0.0,
        direction_changes: int   = 0,
        is_stable:         bool  = True,
        was_stable:        bool  = True,
    ) -> tuple[float, str]:
        """
        Returns (stress_score 0-1, state_label).

        Parameters
        ----------
        movement_score    : 0=still, 1=very erratic (primary signal)
        direction_changes : head left-right reversals in last window
        is_stable         : True if movement_score < STABLE_THRESHOLD
        was_stable        : True if head was stable before face disappeared
        """

        # ── Face not visible ──────────────────────────────────────────
        if not face_detected:
            self._no_face_count += 1
            if self._no_face_count < _NO_FACE_GRACE_FRAMES:
                # Brief disappearance — hold last state
                return self._smoothed_score, self._last_state

            if was_stable or self._last_was_stable:
                # Was stable → student looking at paper, solving problem
                self._smoothed_score = max(_SCORE_FLOOR,
                                           self._smoothed_score * 0.98)
                state = "working"
            else:
                # Was erratic → unknown
                self._smoothed_score = max(_SCORE_FLOOR,
                                           self._smoothed_score * 0.95)
                state = "face_not_visible"
            self._last_state = state
            return self._smoothed_score, state

        self._no_face_count = 0
        self._last_was_stable = is_stable

        # ── Emotion component (secondary) ─────────────────────────────
        if probs and valid_for_emotion:
            self._probs_buffer.append(probs)

        avg_probs = self._buffer_average()
        emotion_stress = self._emotion_component(avg_probs)

        # ── Combined raw stress score ─────────────────────────────────
        raw = (_MOVEMENT_WEIGHT * movement_score
               + _EMOTION_WEIGHT * emotion_stress)
        raw = max(0.0, min(1.0, raw))

        # EMA smoothing
        self._smoothed_score = (
            _EMA_ALPHA * raw + (1 - _EMA_ALPHA) * self._smoothed_score
        )
        self._smoothed_score = max(_SCORE_FLOOR, min(1.0, self._smoothed_score))

        # ── State classification ──────────────────────────────────────
        state = self._classify(
            score             = self._smoothed_score,
            movement_score    = movement_score,
            direction_changes = direction_changes,
            is_stable         = is_stable,
            avg_probs         = avg_probs,
        )
        self._last_state = state
        return round(self._smoothed_score, 3), state

    def reset(self):
        self._probs_buffer.clear()
        self._smoothed_score = 0.2
        self._last_state     = "calm"
        self._no_face_count  = 0
        self._last_was_stable = True

    @property
    def smoothed_score(self) -> float:
        return self._smoothed_score

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _emotion_component(avg_probs: dict[str, float]) -> float:
        """
        Compute 0-1 emotion stress component from buffered avg probs.
        Calm/happy → low.  Stressed/confused → high.
        """
        if not avg_probs:
            return 0.3   # neutral assumption
        s = avg_probs.get("stressed", 0)
        c = avg_probs.get("confused", 0)
        k = avg_probs.get("calm",    0)
        f = avg_probs.get("focused", 0)
        raw = 0.60 * s + 0.30 * c - 0.40 * k - 0.10 * f
        # Normalise from approx [-0.5, 0.6] → [0, 1]
        return max(0.0, min(1.0, (raw + 0.3) / 0.9))

    @staticmethod
    def _classify(
        score:             float,
        movement_score:    float,
        direction_changes: int,
        is_stable:         bool,
        avg_probs:         dict[str, float],
    ) -> str:
        """
        Movement-primary state classification.

        Priority (high→low):
        1.  Very stable head → calm or focused
        2.  Direction-scanning (confused behaviour) → confused
        3.  Erratic movement → stressed
        4.  Moderate movement → fallback to emotion model
        """
        k = avg_probs.get("calm",    0.0)
        s = avg_probs.get("stressed",0.0)
        c = avg_probs.get("confused",0.0)

        # ── STABLE: student is locked in solving ─────────────────────
        if is_stable or movement_score < _STABLE_THRESHOLD * 2:
            # Use emotion to distinguish calm vs deeply focused
            if k >= s:
                return "calm"
            return "focused"

        # ── CONFUSED: rapid left-right scanning ──────────────────────
        if (direction_changes >= _CONFUSED_DIR_CHANGES
                and movement_score >= _DIR_CONFUSED_MOVEMENT):
            return "confused"

        # ── STRESSED: high movement + high stress score ───────────────
        if movement_score >= _ERRATIC_THRESHOLD or score >= 0.55:
            if c >= 0.15:
                return "confused"
            return "stressed"

        # ── MODERATE: let emotion tip the balance ─────────────────────
        if k >= 0.20:
            return "calm"
        if c >= 0.15:
            return "confused"
        if s >= 0.28:
            return "stressed"
        return "focused"

    def _buffer_average(self) -> dict[str, float]:
        if not self._probs_buffer:
            return {}
        keys = self._probs_buffer[0].keys()
        n = len(self._probs_buffer)
        return {k: sum(d.get(k, 0.0) for d in self._probs_buffer) / n
                for k in keys}

    # keep build_record compatibility
    def update_legacy(self, probs, valid_for_emotion, face_detected, head_pose):
        """Backward-compatible wrapper with no movement data."""
        return self.update(probs, valid_for_emotion, face_detected, head_pose)
