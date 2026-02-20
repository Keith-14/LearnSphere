import os
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from utils.data_loader import load_all_data
from utils.feature_engineering import generate_features


MODEL_PATH = "models/dropout_model.pkl"
SCALER_PATH = "models/scaler.pkl"


def train_dropout_model():

    students, tests, emotions, engagement = load_all_data()
    labels = pd.read_csv("data/dropout_labels.csv")

    df = generate_features(students, tests, emotions, engagement)
    df = df.merge(labels, on="student_id")

    feature_cols = [
        "avg_score",
        "stress_level",
        "confidence_level",
        "login_count",
        "avg_session_time"
    ]

    X = df[feature_cols]
    y = df["dropout_label"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=6,
        random_state=42
    )

    model.fit(X_train, y_train)

    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)


def ensure_model_exists():
    """
    Background check.
    If model doesn't exist, train automatically.
    """
    if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
        train_dropout_model()