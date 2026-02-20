"""
dataset_mapper.py
=================
Maps raw dataset emotion labels (FER2013, AffectNet) into the 4 exam-relevant
emotion classes used by this system.

Exam classes:
    stressed  — high arousal, negative valence (fear, anger, disgust, sad)
    focused   — low arousal, neutral valence   (neutral)
    confused  — surprise or ambivalent states  (surprise, contempt)
    calm      — positive valence               (happy)

Usage:
------
from train.dataset_mapper import FER2013Mapper, AffectNetMapper

# Map a single label
exam_label = FER2013Mapper.map("angry")   # → "stressed"

# Map a whole Pandas DataFrame
import pandas as pd
df = pd.read_csv("fer2013.csv")
df["exam_emotion"] = df["emotion"].apply(FER2013Mapper.map_int)
df_exam = df.dropna(subset=["exam_emotion"])  # drop unmapped rows

# Convenience method: load FER2013 and return mapped DataFrame
df_mapped = FER2013Mapper.load_and_map("fer2013.csv")
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# EXAM EMOTION LABELS
# ──────────────────────────────────────────────────────────────────────────────
EXAM_EMOTIONS = ["stressed", "focused", "confused", "calm"]
EXAM_LABEL_TO_ID = {e: i for i, e in enumerate(EXAM_EMOTIONS)}


# ══════════════════════════════════════════════════════════════════════════════
# FER2013 Mapper
# ══════════════════════════════════════════════════════════════════════════════

class FER2013Mapper:
    """
    FER2013 has 7 classes (indexed 0–6):
        0: Angry, 1: Disgust, 2: Fear, 3: Happy,
        4: Sad, 5: Surprise, 6: Neutral
    """

    # String label → exam emotion
    STR_MAP: dict[str, str] = {
        "angry":    "stressed",
        "disgust":  "stressed",
        "fear":     "stressed",
        "sad":      "stressed",
        "happy":    "calm",
        "surprise": "confused",
        "neutral":  "focused",
    }

    # Integer index (FER2013) → exam emotion  (None = discard)
    INT_MAP: dict[int, Optional[str]] = {
        0: "stressed",   # Angry
        1: "stressed",   # Disgust
        2: "stressed",   # Fear
        3: "calm",       # Happy
        4: "stressed",   # Sad
        5: "confused",   # Surprise
        6: "focused",    # Neutral
    }

    @classmethod
    def map(cls, label: str) -> Optional[str]:
        return cls.STR_MAP.get(label.lower().strip())

    @classmethod
    def map_int(cls, idx: int) -> Optional[str]:
        return cls.INT_MAP.get(int(idx))

    @classmethod
    def load_and_map(cls, csv_path: str | Path, usage: str = "Training"):
        """
        Load FER2013 CSV and return a DataFrame with columns:
            pixels, exam_emotion, exam_label_id, usage

        Args:
            csv_path : Path to fer2013.csv
            usage    : "Training", "PublicTest", or "PrivateTest"
        """
        try:
            import pandas as pd
        except ImportError:
            raise RuntimeError("pandas is required: pip install pandas")

        df = pd.read_csv(csv_path)
        if usage:
            df = df[df["Usage"] == usage].copy()

        df["exam_emotion"] = df["emotion"].apply(cls.map_int)
        df = df.dropna(subset=["exam_emotion"]).copy()
        df["exam_label_id"] = df["exam_emotion"].map(EXAM_LABEL_TO_ID)

        logger.info(
            "FER2013 [%s]: %d samples after mapping → %s",
            usage,
            len(df),
            df["exam_emotion"].value_counts().to_dict(),
        )
        return df


# ══════════════════════════════════════════════════════════════════════════════
# AffectNet Mapper
# ══════════════════════════════════════════════════════════════════════════════

class AffectNetMapper:
    """
    AffectNet has 8 expression classes (indexed 0–7):
        0: Neutral, 1: Happy, 2: Sad, 3: Surprise,
        4: Fear,    5: Disgust, 6: Anger, 7: Contempt
    """

    INT_MAP: dict[int, Optional[str]] = {
        0: "focused",    # Neutral
        1: "calm",       # Happy
        2: "stressed",   # Sad
        3: "confused",   # Surprise
        4: "stressed",   # Fear
        5: "stressed",   # Disgust
        6: "stressed",   # Anger
        7: "confused",   # Contempt
    }

    STR_MAP: dict[str, str] = {
        "neutral":  "focused",
        "happy":    "calm",
        "sad":      "stressed",
        "surprise": "confused",
        "fear":     "stressed",
        "disgust":  "stressed",
        "anger":    "stressed",
        "contempt": "confused",
    }

    @classmethod
    def map(cls, label: str) -> Optional[str]:
        return cls.STR_MAP.get(label.lower().strip())

    @classmethod
    def map_int(cls, idx: int) -> Optional[str]:
        return cls.INT_MAP.get(int(idx))


# ──────────────────────────────────────────────────────────────────────────────
# Utility: decode FER2013 pixel string → numpy image array
# ──────────────────────────────────────────────────────────────────────────────

def decode_fer_pixels(pixel_str: str, size: int = 48) -> np.ndarray:
    """
    Convert space-separated pixel string (FER2013 format) to (H, W, 3) uint8.
    """
    arr = np.array(pixel_str.split(), dtype=np.uint8).reshape(size, size)
    return np.stack([arr, arr, arr], axis=-1)   # grayscale → RGB


if __name__ == "__main__":
    # Quick self-test of the mapper
    for raw, expected in [
        ("angry", "stressed"), ("happy", "calm"),
        ("neutral", "focused"), ("surprise", "confused"),
    ]:
        result = FER2013Mapper.map(raw)
        status = "✓" if result == expected else "✗"
        print(f"  {status}  FER2013 '{raw}' → '{result}' (expected '{expected}')")

    # AffectNet: 0=Neutral→focused, 3=Surprise→confused, 6=Anger→stressed, 7=Contempt→confused
    for idx, expected in [(0, "focused"), (3, "confused"), (6, "stressed"), (7, "confused")]:
        result = AffectNetMapper.map_int(idx)
        status = "✓" if result == expected else "✗"
        print(f"  {status}  AffectNet idx={idx} → '{result}' (expected '{expected}')")
