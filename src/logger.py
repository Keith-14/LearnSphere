"""
logger.py
=========
Logs per-frame inference results to a JSONL file and keeps an in-memory
ring buffer for the Streamlit UI to read.

Log format (one JSON object per line):
{
  "timestamp": "2026-02-20T11:43:52",
  "state": "stressed | focused | confused | calm | looking_down | face_not_visible",
  "stress_score": 0.0-1.0,
  "probabilities": {"stressed": 0.0, "focused": 0.0, "confused": 0.0, "calm": 0.0},
  "face_detected": true/false,
  "head_pose": "frontal | down | away | unknown",
  "valid_for_emotion": true/false
}
"""

from __future__ import annotations

import json
import logging
import os
from collections import deque
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

_LOG_DIR = Path("logs")
_LOG_DIR.mkdir(exist_ok=True)


class SessionLogger:
    """
    Writes inference records every `log_every` frames and maintains a
    deque of the most recent `memory_size` records for the UI.
    """

    def __init__(
        self,
        log_every: int = 5,
        memory_size: int = 50,
        log_dir: str | Path = _LOG_DIR,
    ):
        self._log_every  = log_every
        self._frame_counter = 0
        self._memory: deque[dict] = deque(maxlen=memory_size)

        # Create session log file
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        self._log_path = log_dir / f"session_{ts}.jsonl"
        self._file = open(self._log_path, "a", encoding="utf-8")
        logger.info("Session log → %s", self._log_path)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def log(self, record: dict) -> bool:
        """
        Log a record.  Writes to disk every `log_every` calls.

        Args:
            record: dict matching the JSON output schema.

        Returns:
            True if the record was written to disk this call.
        """
        self._frame_counter += 1

        # Always add to in-memory buffer
        self._memory.append(record)

        # Write to disk on schedule
        if self._frame_counter % self._log_every == 0:
            try:
                self._file.write(json.dumps(record, ensure_ascii=False) + "\n")
                self._file.flush()
                return True
            except OSError as e:
                logger.error("Failed to write log record: %s", e)
        return False

    @property
    def last_record(self) -> dict | None:
        """Most recent logged record (or None if none yet)."""
        return self._memory[-1] if self._memory else None

    @property
    def recent_records(self) -> list[dict]:
        """All records in the in-memory buffer."""
        return list(self._memory)

    @property
    def log_path(self) -> Path:
        return self._log_path

    def close(self):
        try:
            self._file.close()
        except OSError:
            pass

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


# ---------------------------------------------------------------------------
# Utility: build a canonical record dict from pipeline outputs
# ---------------------------------------------------------------------------

def build_record(
    state: str,
    stress_score: float,
    probabilities: dict[str, float],
    face_detected: bool,
    head_pose: str,
    valid_for_emotion: bool,
) -> dict:
    """Construct the standard output record with a fresh timestamp."""
    return {
        "timestamp":        datetime.now().isoformat(timespec="seconds"),
        "state":            state,
        "stress_score":     round(float(stress_score), 4),
        "probabilities":    {k: round(float(v), 4) for k, v in probabilities.items()},
        "face_detected":    bool(face_detected),
        "head_pose":        head_pose,
        "valid_for_emotion": bool(valid_for_emotion),
    }
