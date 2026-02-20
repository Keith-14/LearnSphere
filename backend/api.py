from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
import os
import base64
import cv2
from intelligence_engine.pipeline import ExamPipeline

app = FastAPI()

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Load Models ──────────────────────────────────────────────────────────
MODEL_PATH = "models/dropout_model.pkl"
SCALER_PATH = "models/scaler.pkl"

try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
except:
    model, scaler = None, None

# Initialize the intelligence engine
try:
    pipeline = ExamPipeline(enable_logging=False)
except Exception as e:
    print(f"Failed to initialize ExamPipeline: {e}")
    pipeline = None

# Global state to store latest analysis for teacher dashboard
active_sessions = {
    "st1": {
        "state": "focused",
        "stress_score": 0.1,
        "is_stable": True,
        "confidence": 0.95
    }
}

# ─── Schemas ──────────────────────────────────────────────────────────────
class StudentData(BaseModel):
    avg_score: float
    stress_level: float
    confidence_level: float
    login_count: float
    avg_session_time: float

class AnalyzeFrameRequest(BaseModel):
    image: str  # base64 encoded string

# ─── Helpers ──────────────────────────────────────────────────────────────
def probability_to_score(prob):
    return round(prob * 5, 2)

# ─── Endpoints ────────────────────────────────────────────────────────────
@app.post("/predict")
def predict(data: StudentData):
    if not model or not scaler:
        return {"error": "Prediction models not loaded"}
    df = pd.DataFrame([data.dict()])
    X_scaled = scaler.transform(df)
    prob = model.predict_proba(X_scaled)[0][1]
    risk_score = probability_to_score(prob)
    return {
        "probability": float(prob),
        "risk_score": risk_score
    }

@app.post("/analyze-frame")
async def analyze_frame(request: AnalyzeFrameRequest):
    if not pipeline:
        raise HTTPException(status_code=500, detail="Intelligence engine not initialized")
    
    try:
        # 1. Decode base64 image
        header, encoded = request.image.split(",", 1) if "," in request.image else ("", request.image)
        nparr = np.frombuffer(base64.b64decode(encoded), np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image data")

        # 2. Process through pipeline
        result = pipeline.process_frame(frame)
        
        # 3. Clean up result for JSON
        clean_result = {
            "state": result.get("state", "unknown"),
            "stress_score": float(result.get("stress_score", 0.0)),
            "head_pose": result.get("head_pose", "unknown"),
            "face_detected": bool(result.get("face_detected", False)),
            "movement_score": float(result.get("movement_score", 0.0)),
            "stability_score": float(result.get("stability_score", 1.0)),
            "is_stable": bool(result.get("is_stable", True)),
            "probabilities": {k: float(v) for k, v in result.get("probabilities", {}).items()}
        }

        # 4. Save to global state for teacher view (Assume "st1" for demo)
        active_sessions["st1"] = {
            "state": clean_result["state"],
            "stress_score": clean_result["stress_score"],
            "is_stable": clean_result["is_stable"],
            "confidence": max(clean_result["probabilities"].values()) if clean_result["probabilities"] else 0.5
        }
        
        return clean_result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/session-status/{student_id}")
async def get_session_status(student_id: str):
    if student_id not in active_sessions:
        return {"error": "Session not found"}
    return active_sessions[student_id]