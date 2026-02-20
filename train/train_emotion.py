"""
train_emotion.py
================
Transfer learning script: fine-tunes MobileNetV2 on FER2013 mapped to
4 exam emotion classes (stressed, focused, confused, calm).

Quick-start:
    python train/train_emotion.py \\
        --dataset path/to/fer2013.csv \\
        --epochs 20 \\
        --output models/exam_emotion_model.h5

Requirements:
    pip install tensorflow pandas scikit-learn

Dataset:
    Download FER2013 from:  https://www.kaggle.com/datasets/msambare/fer2013
    The CSV has columns: emotion (int), pixels (space-sep), Usage (str)

Architecture:
    MobileNetV2 (ImageNet pre-trained, frozen)
    → GlobalAveragePooling2D
    → Dense(256, relu) + Dropout(0.4)
    → Dense(4, softmax)

Images are upscaled from 48×48 grayscale → 96×96 RGB (3-channel repeat)
for MobileNetV2 compatibility.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import numpy as np

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)

# Add project root to path so we can import train.*
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from train.dataset_mapper import FER2013Mapper, decode_fer_pixels, EXAM_EMOTIONS

IMG_SIZE  = 96      # MobileNetV2 min input
N_CLASSES = 4


# ──────────────────────────────────────────────────────────────────────────────
# Data loading
# ──────────────────────────────────────────────────────────────────────────────

def load_fer2013(csv_path: str):
    """Return (X_train, y_train, X_val, y_val) as float32 numpy arrays."""
    logger.info("Loading and mapping FER2013 from %s …", csv_path)
    df_train = FER2013Mapper.load_and_map(csv_path, usage="Training")
    df_val   = FER2013Mapper.load_and_map(csv_path, usage="PublicTest")

    def build_xy(df):
        X, y = [], []
        for _, row in df.iterrows():
            img = decode_fer_pixels(row["pixels"])  # (48, 48, 3) uint8
            # Upscale to IMG_SIZE × IMG_SIZE
            import cv2
            img = cv2.resize(img, (IMG_SIZE, IMG_SIZE), interpolation=cv2.INTER_LINEAR)
            X.append(img)
            y.append(int(row["exam_label_id"]))
        return np.array(X, dtype=np.float32) / 255.0, np.array(y, dtype=np.int32)

    X_train, y_train = build_xy(df_train)
    X_val,   y_val   = build_xy(df_val)
    logger.info("Train: %d  Val: %d", len(X_train), len(X_val))
    return X_train, y_train, X_val, y_val


# ──────────────────────────────────────────────────────────────────────────────
# Model definition
# ──────────────────────────────────────────────────────────────────────────────

def build_model(fine_tune_from: int = 100) -> "tf.keras.Model":  # type: ignore[name-defined]
    import tensorflow as tf
    from tensorflow.keras import layers, models

    base = tf.keras.applications.MobileNetV2(
        input_shape=(IMG_SIZE, IMG_SIZE, 3),
        include_top=False,
        weights="imagenet",
    )
    # Phase 1: freeze base
    base.trainable = False

    inputs = tf.keras.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
    x = tf.keras.applications.mobilenet_v2.preprocess_input(inputs)
    x = base(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(256, activation="relu")(x)
    x = layers.Dropout(0.4)(x)
    outputs = layers.Dense(N_CLASSES, activation="softmax")(x)

    model = models.Model(inputs, outputs)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model, base


# ──────────────────────────────────────────────────────────────────────────────
# Training
# ──────────────────────────────────────────────────────────────────────────────

def train(
    dataset: str,
    epochs: int,
    batch_size: int,
    output: str,
    fine_tune_layers: int = 30,
):
    import tensorflow as tf

    X_train, y_train, X_val, y_val = load_fer2013(dataset)

    model, base = build_model()
    model.summary(print_fn=logger.info)

    # ── Phase 1: train dense head ────────────────────────────────────
    logger.info("Phase 1: training dense head (%d epochs) …", epochs // 2)
    callbacks = [
        tf.keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True),
        tf.keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=3),
    ]
    model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=epochs // 2,
        batch_size=batch_size,
        callbacks=callbacks,
    )

    # ── Phase 2: fine-tune top N layers of MobileNetV2 ───────────────
    logger.info("Phase 2: fine-tuning top %d layers of MobileNetV2 …", fine_tune_layers)
    base.trainable = True
    for layer in base.layers[:-fine_tune_layers]:
        layer.trainable = False

    model.compile(
        optimizer=tf.keras.optimizers.Adam(1e-5),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=epochs - epochs // 2,
        batch_size=batch_size,
        callbacks=callbacks,
    )

    # ── Save ──────────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    model.save(output)
    logger.info("Model saved → %s", output)

    # Save label mapping
    import json
    mapping_path = output.replace(".h5", "_label_map.json")
    with open(mapping_path, "w") as f:
        json.dump({"labels": EXAM_EMOTIONS}, f, indent=2)
    logger.info("Label map  → %s", mapping_path)


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fine-tune MobileNetV2 on FER2013 → 4 exam emotion classes"
    )
    parser.add_argument("--dataset",    required=True, help="Path to fer2013.csv")
    parser.add_argument("--epochs",     type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--output",     default="models/exam_emotion_model.h5")
    parser.add_argument(
        "--fine-tune-layers",
        type=int, default=30,
        help="Number of top MobileNetV2 layers to unfreeze in phase 2",
    )
    args = parser.parse_args()

    train(
        dataset          = args.dataset,
        epochs           = args.epochs,
        batch_size       = args.batch_size,
        output           = args.output,
        fine_tune_layers = args.fine_tune_layers,
    )
