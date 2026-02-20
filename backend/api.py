from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
import os

app = FastAPI()

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = "models/dropout_model.pkl"
SCALER_PATH = "models/scaler.pkl"

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)


class StudentData(BaseModel):
    avg_score: float
    stress_level: float
    confidence_level: float
    login_count: float
    avg_session_time: float


def probability_to_score(prob):
    return round(prob * 5, 2)


@app.post("/predict")
def predict(data: StudentData):

    df = pd.DataFrame([data.dict()])

    X_scaled = scaler.transform(df)

    prob = model.predict_proba(X_scaled)[0][1]

    risk_score = probability_to_score(prob)

    return {
        "probability": float(prob),
        "risk_score": risk_score
    }