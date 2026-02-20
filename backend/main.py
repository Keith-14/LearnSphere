"""
LearnSphere – Emotion-Aware Adaptive Study Assistant
FastAPI backend.

Run locally:
    uvicorn main:app --reload --port 8000

Endpoints:
    POST /chat                                      → main chat
    GET  /history/{domain}/{student_id}/{session_id}
    GET  /sentiment/{domain}/{student_id}
    POST /student/{domain}                          → create student
    GET  /student/{domain}/{student_id}
    GET  /domains
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import firebase_client as fb
from emotion_engine import detect_emotion
from groq_client import generate_response
from response_router import get_strategy
from models import (
    ChatRequest, ChatResponse, EmotionResult,
    StudentCreate, StudentOut, TestScore,
)

app = FastAPI(
    title="LearnSphere – Emotion-Aware Study Assistant",
    version="1.0.0",
    description="Adaptive AI tutor that detects student emotions and adjusts its response style.",
)

# Allow Streamlit (and later the real frontend) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

VALID_DOMAINS = {"upsc", "jee", "cat", "gate"}


def _validate_domain(domain: str):
    if domain not in VALID_DOMAINS:
        raise HTTPException(status_code=400, detail=f"Invalid domain '{domain}'. Must be one of {VALID_DOMAINS}")


# ── Health ─────────────────────────────────────────────────────────────────────

@app.get("/")
def health():
    return {"status": "ok", "service": "LearnSphere Emotion-Aware Assistant"}


@app.get("/domains")
def list_domains():
    return {"domains": sorted(VALID_DOMAINS)}


# ── Students ───────────────────────────────────────────────────────────────────

@app.post("/student/{domain}", response_model=StudentOut, status_code=201)
def create_student(domain: str, body: StudentCreate):
    _validate_domain(domain)
    student_id = fb.create_student(domain=domain, name=body.name, email=body.email)
    return StudentOut(
        student_id=student_id,
        name=body.name,
        email=body.email,
        active_domain=domain,
    )


@app.get("/student/{domain}/{student_id}", response_model=StudentOut)
def get_student(domain: str, student_id: str):
    _validate_domain(domain)
    data = fb.get_student(domain, student_id)
    if not data:
        raise HTTPException(status_code=404, detail="Student not found")
    return StudentOut(**data)


@app.get("/students/{domain}")
def list_students(domain: str):
    _validate_domain(domain)
    return {"students": fb.list_students(domain)}


# ── Test Scores ────────────────────────────────────────────────────────────────

@app.post("/scores/{domain}/{student_id}", status_code=201)
def add_score(domain: str, student_id: str, body: TestScore):
    _validate_domain(domain)
    if not fb.get_student(domain, student_id):
        raise HTTPException(status_code=404, detail="Student not found")
    test_id = fb.add_test_score(
        domain, student_id,
        body.test_name, body.score, body.max_score, body.subject
    )
    return {"test_id": test_id}


@app.get("/scores/{domain}/{student_id}")
def get_scores(domain: str, student_id: str):
    _validate_domain(domain)
    return {"scores": fb.get_test_scores(domain, student_id)}


# ── Chat ───────────────────────────────────────────────────────────────────────

@app.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest):
    """
    Main chat endpoint.

    Flow:
      1. Validate inputs
      2. Fetch last 5 messages from Firebase (context window)
      3. Step 1 – Groq emotion detection
      4. Step 2 – Groq adaptive response generation
      5. Persist student message + AI reply to Firebase
      6. Log emotion to sentiment_log
      7. Return ChatResponse
    """
    _validate_domain(body.domain)

    # Ensure student exists
    student = fb.get_student(body.domain, body.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found. Create the student first via POST /student/{domain}")

    # 1. Fetch recent conversation context
    history = fb.get_recent_messages(body.domain, body.student_id, body.session_id, n=5)

    # 2. Detect emotion (Groq Step 1)
    emotion_data = detect_emotion(current_message=body.message, history=history)
    emotion_label    = emotion_data["emotion_label"]
    confidence_score = emotion_data["confidence_score"]
    detected_cause   = emotion_data["detected_cause"]
    emotion_raw      = emotion_data.get("_raw", "")

    # 3. Pick adaptive strategy
    strategy = get_strategy(emotion_label)

    # 4. Generate adaptive response (Groq Step 2)
    reply = generate_response(
        domain=body.domain,
        student_message=body.message,
        emotion_label=emotion_label,
        detected_cause=detected_cause,
        strategy=strategy,
        history=history,
    )

    # 5. Persist both turns to Firebase
    fb.append_message(
        body.domain, body.student_id, body.session_id,
        role="user", content=body.message, detected_emotion=emotion_label,
    )
    fb.append_message(
        body.domain, body.student_id, body.session_id,
        role="assistant", content=reply, detected_emotion=None,
    )

    # 6. Log emotion
    fb.log_sentiment(
        body.domain, body.student_id, body.session_id,
        emotion_label=emotion_label,
        confidence=confidence_score,
        detected_cause=detected_cause,
    )

    return ChatResponse(
        reply=reply,
        emotion=EmotionResult(
            emotion_label=emotion_label,
            confidence_score=confidence_score,
            detected_cause=detected_cause,
        ),
        session_id=body.session_id,
        emotion_raw=emotion_raw,
    )


# ── History & Sentiment ────────────────────────────────────────────────────────

@app.get("/history/{domain}/{student_id}/{session_id}")
def get_history(domain: str, student_id: str, session_id: str):
    _validate_domain(domain)
    messages = fb.get_recent_messages(domain, student_id, session_id, n=100)
    return {"session_id": session_id, "messages": messages}


@app.get("/sentiment/{domain}/{student_id}")
def get_sentiment(domain: str, student_id: str, limit: int = 20):
    _validate_domain(domain)
    entries = fb.get_sentiment_history(domain, student_id, limit=limit)
    return {"student_id": student_id, "sentiment_log": entries}
