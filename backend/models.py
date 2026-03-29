from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ── Emotion ──────────────────────────────────────────────────────────────────

class EmotionResult(BaseModel):
    emotion_label: str          # Frustrated | Confused | Anxious | Confident | Neutral
    confidence_score: float     # 0.0 – 1.0
    detected_cause: str         # topic_confusion | rank_anxiety | peer_comparison |
                                # repeated_attempts | time_pressure | none


# ── Chat ─────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    domain: str         # "upsc" | "jee" | "cat" | "gate"
    student_id: str
    session_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str
    emotion: EmotionResult
    session_id: str
    emotion_raw: Optional[str] = None   # raw LLM output shown in Streamlit debug view


# ── Student ──────────────────────────────────────────────────────────────────

class StudentCreate(BaseModel):
    name: str
    email: str
    active_domain: str          # "upsc" | "jee" | "cat" | "gate"


class StudentOut(BaseModel):
    student_id: str
    name: str
    email: str
    active_domain: str
    created_at: Optional[str] = None


# ── Test Scores ───────────────────────────────────────────────────────────────

class TestScore(BaseModel):
    test_name: str
    score: int
    max_score: int
    subject: str
    date: Optional[str] = None


# ── Message (stored in Firestore chat_sessions) ───────────────────────────────

class Message(BaseModel):
    role: str               # "user" | "assistant"
    content: str
    timestamp: str
    detected_emotion: Optional[str] = None


# ── Sentiment Log Entry ───────────────────────────────────────────────────────

class SentimentEntry(BaseModel):
    timestamp: str
    emotion_label: str
    confidence: float
    detected_cause: str
    session_id: str
