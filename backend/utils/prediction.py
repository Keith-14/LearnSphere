import os
import joblib
import numpy as np
from utils.train_model import train_dropout_model

MODEL_PATH = "models/dropout_model.pkl"
SCALER_PATH = "models/scaler.pkl"


def load_model():

    if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
        train_dropout_model()

    try:
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
    except Exception:
        train_dropout_model()
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)

    return model, scaler


def probability_to_score(prob):
    """
    Convert probability (0–1)
    into smooth score (0–5)
    """
    return round(prob * 5, 2)


def predict_dropout(df):

    model, scaler = load_model()

    feature_cols = [
        "avg_score",
        "stress_level",
        "confidence_level",
        "login_count",
        "avg_session_time"
    ]

    X = df[feature_cols]
    X_scaled = scaler.transform(X)

    probabilities = model.predict_proba(X_scaled)[:, 1]

    severity_scores = [probability_to_score(p) for p in probabilities]

    return severity_scores