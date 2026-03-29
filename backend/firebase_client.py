"""
Firebase Firestore client.
Lazily initialised on first use — safe to import even before .env is ready.

Firestore hierarchy:
  /domains/{domain}/students/{student_id}
    fields: name, email, active_domain, created_at
    subcollections:
      test_scores/{test_id}
      chat_sessions/{session_id}  → messages[]
      sentiment_log/entries (stored as individual docs)
      cv_sentiment_placeholder/   (reserved for future CV integration)
"""

import os
import uuid
from datetime import datetime, timezone
from typing import Optional

import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

# ── Lazy Firebase singleton ───────────────────────────────────────────────────
# Loads directly from the service-account JSON file sitting in the project root.
# Falls back to env vars if the file isn't found (e.g. in CI/production).

_db = None


def _get_db():
    global _db
    if _db is not None:
        return _db

    if firebase_admin._apps:
        _db = firestore.client()
        return _db

    missing = [k for k in (
        "FIREBASE_PROJECT_ID", "FIREBASE_PRIVATE_KEY_ID",
        "FIREBASE_PRIVATE_KEY", "FIREBASE_CLIENT_EMAIL", "FIREBASE_CLIENT_ID",
    ) if not os.environ.get(k)]
    if missing:
        raise EnvironmentError(
            f"Missing Firebase env vars: {missing}. Copy .env.example → .env and fill them in."
        )

    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": os.environ["FIREBASE_PROJECT_ID"],
        "private_key_id": os.environ["FIREBASE_PRIVATE_KEY_ID"],
        "private_key": os.environ["FIREBASE_PRIVATE_KEY"].replace("\\n", "\n"),
        "client_email": os.environ["FIREBASE_CLIENT_EMAIL"],
        "client_id": os.environ["FIREBASE_CLIENT_ID"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    })
    firebase_admin.initialize_app(cred)
    _db = firestore.client()
    return _db

VALID_DOMAINS = {"upsc", "jee", "cat", "gate"}


# ── Helpers ──────────────────────────────────────────────────────────────────

def _student_ref(domain: str, student_id: str):
    return _get_db().collection("domains").document(domain).collection("students").document(student_id)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Student CRUD ─────────────────────────────────────────────────────────────

def create_student(domain: str, name: str, email: str) -> str:
    """Create a new student document. Returns the generated student_id."""
    student_id = str(uuid.uuid4())[:8]
    ref = _student_ref(domain, student_id)
    ref.set({
        "name": name,
        "email": email,
        "active_domain": domain,
        "created_at": _now_iso(),
    })
    # Seed CV sentiment placeholder for future use
    ref.collection("cv_sentiment_placeholder").document("_meta").set({
        "schema_version": "v0-reserved",
        "description": "Reserved for future CV-based emotion integration during tests",
    })
    return student_id


def get_student(domain: str, student_id: str) -> Optional[dict]:
    """Return student dict or None if not found."""
    doc = _student_ref(domain, student_id).get()
    if not doc.exists:
        return None
    data = doc.to_dict()
    data["student_id"] = student_id
    return data


def list_students(domain: str) -> list[dict]:
    docs = _get_db().collection("domains").document(domain).collection("students").stream()
    result = []
    for doc in docs:
        d = doc.to_dict()
        d["student_id"] = doc.id
        result.append(d)
    return result


# ── Test Scores ───────────────────────────────────────────────────────────────

def add_test_score(domain: str, student_id: str, test_name: str,
                   score: int, max_score: int, subject: str) -> str:
    test_id = str(uuid.uuid4())[:8]
    _student_ref(domain, student_id).collection("test_scores").document(test_id).set({
        "test_name": test_name,
        "score": score,
        "max_score": max_score,
        "subject": subject,
        "date": _now_iso(),
    })
    return test_id


def get_test_scores(domain: str, student_id: str) -> list[dict]:
    docs = _student_ref(domain, student_id).collection("test_scores").stream()
    return [doc.to_dict() for doc in docs]


# ── Chat Session Messages ─────────────────────────────────────────────────────

def append_message(domain: str, student_id: str, session_id: str,
                   role: str, content: str, detected_emotion: Optional[str] = None):
    """Append a single message to a chat session (array union on the messages field)."""
    session_ref = (_student_ref(domain, student_id)
                   .collection("chat_sessions")
                   .document(session_id))

    message = {
        "role": role,
        "content": content,
        "timestamp": _now_iso(),
        "detected_emotion": detected_emotion,
    }

    # Use array_union to atomically append
    session_ref.set(
        {"messages": firestore.ArrayUnion([message]), "started_at": _now_iso()},
        merge=True,
    )


def get_recent_messages(domain: str, student_id: str, session_id: str,
                        n: int = 5) -> list[dict]:
    """Return the last n messages from a chat session."""
    doc = (_student_ref(domain, student_id)
           .collection("chat_sessions")
           .document(session_id)
           .get())
    if not doc.exists:
        return []
    messages = doc.to_dict().get("messages", [])
    return messages[-n:]


# ── Sentiment Log ─────────────────────────────────────────────────────────────

def log_sentiment(domain: str, student_id: str, session_id: str,
                  emotion_label: str, confidence: float, detected_cause: str):
    """Append an emotion observation to the student's sentiment log."""
    entry_id = str(uuid.uuid4())[:8]
    (_student_ref(domain, student_id)
     .collection("sentiment_log")
     .document(entry_id)
     .set({
         "timestamp": _now_iso(),
         "emotion_label": emotion_label,
         "confidence": confidence,
         "detected_cause": detected_cause,
         "session_id": session_id,
     }))


def get_sentiment_history(domain: str, student_id: str, limit: int = 20) -> list[dict]:
    """Return recent sentiment log entries (most recent first)."""
    docs = (
        _student_ref(domain, student_id)
        .collection("sentiment_log")
        .order_by("timestamp", direction=firestore.Query.DESCENDING)
        .limit(limit)
        .stream()
    )
    return [doc.to_dict() for doc in docs]
