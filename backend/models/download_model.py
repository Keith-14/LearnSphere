"""
download_model.py
=================
Downloads and caches the emotion-ferplus ONNX model (~9 MB) from ONNX Model Zoo.
Run this once to pre-cache the model before starting the app.

Usage:
    python3 models/download_model.py
"""

import os
import sys
import urllib.request
from pathlib import Path

_MODEL_DIR  = Path(__file__).resolve().parent
_MODEL_PATH = _MODEL_DIR / "emotion-ferplus-8.onnx"

_MODEL_URL = (
    "https://github.com/onnx/models/raw/main/validated/vision/body_analysis/"
    "emotion_ferplus/model/emotion-ferplus-8.onnx"
)


def _reporthook(count, block_size, total_size):
    downloaded = count * block_size
    pct = min(100, int(downloaded * 100 / total_size)) if total_size > 0 else 0
    mb  = downloaded / 1_048_576
    print(f"\r  Downloading … {mb:.1f} MB  ({pct}%)", end="", flush=True)


def download_model():
    if _MODEL_PATH.exists():
        size_mb = _MODEL_PATH.stat().st_size / 1_048_576
        print(f"[OK] Model already cached: {_MODEL_PATH}  ({size_mb:.1f} MB)")
        return

    print(f"Downloading emotion-ferplus ONNX model from ONNX Model Zoo …")
    print(f"  URL: {_MODEL_URL}")
    _MODEL_DIR.mkdir(parents=True, exist_ok=True)
    try:
        urllib.request.urlretrieve(_MODEL_URL, _MODEL_PATH, reporthook=_reporthook)
        print()
        size_mb = _MODEL_PATH.stat().st_size / 1_048_576
        print(f"[OK] Model saved → {_MODEL_PATH}  ({size_mb:.1f} MB)")
    except Exception as e:
        print(f"\n[ERROR] Download failed: {e}")
        sys.exit(1)


def verify_onnxruntime():
    print("Checking onnxruntime …")
    try:
        import onnxruntime as ort
        print(f"[OK] onnxruntime {ort.__version__} found.")
    except ImportError:
        print("[ERROR] onnxruntime not installed. Run: pip install onnxruntime")
        sys.exit(1)


def smoke_test():
    print("Running ONNX model smoke test …")
    import onnxruntime as ort
    import numpy as np
    opts = ort.SessionOptions()
    opts.log_severity_level = 3
    session = ort.InferenceSession(
        str(_MODEL_PATH), opts, providers=["CPUExecutionProvider"]
    )
    input_name  = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name
    dummy = np.random.randn(1, 1, 64, 64).astype(np.float32)
    outputs = session.run([output_name], {input_name: dummy})
    logits  = outputs[0].flatten()
    print(f"[OK] Inference OK — output shape: {logits.shape}, sample: {logits[:3]}")
    print("Model is ready for inference.")


if __name__ == "__main__":
    verify_onnxruntime()
    download_model()
    smoke_test()
