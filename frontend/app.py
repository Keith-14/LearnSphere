"""
LearnSphere – Streamlit Testing Interface

Layout:
  Left column  → Chat window (student view)
  Right column → Admin debug view (emotion JSON + sentiment history chart)

Usage:
  streamlit run frontend/app.py

The Streamlit app calls the FastAPI backend at BACKEND_URL.
Make sure the FastAPI server is running first:
  uvicorn backend.main:app --reload --port 8000
"""

import json
import uuid
import requests
import streamlit as st
import pandas as pd

# ── Config ──────────────────────────────────────────────────────────────────

BACKEND_URL = "http://localhost:8000"
DOMAINS = ["upsc", "jee", "cat", "gate"]

EMOTION_EMOJI = {
    "Frustrated/Confused":    "🤔",
    "Stressed/Anxious":       "😰",
    "calm/Confident":         "😎",
    "Focused/Concentrating":  "🎯",
    "Neutral":                "😐",
}

EMOTION_COLOR = {
    "Frustrated/Confused":    "#FFA500",
    "Stressed/Anxious":       "#AA44FF",
    "calm/Confident":         "#00CC66",
    "Focused/Concentrating":  "#2196F3",
    "Neutral":                "#888888",
}

# ── Page Setup ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="LearnSphere – Emotion-Aware Tutor",
    page_icon="📚",
    layout="wide",
)

st.title("📚 LearnSphere – Emotion-Aware Adaptive Study Assistant")
st.caption("Internal testing interface · FastAPI backend · Groq LLM")

# ── Session State ─────────────────────────────────────────────────────────────

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []      # list of {role, content, emotion}
if "last_emotion" not in st.session_state:
    st.session_state.last_emotion = None
if "last_emotion_raw" not in st.session_state:
    st.session_state.last_emotion_raw = ""

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("Student Setup")
    selected_domain = st.selectbox("Exam Domain", DOMAINS)

    st.subheader("Create New Student")
    new_name  = st.text_input("Name")
    new_email = st.text_input("Email")
    if st.button("Create Student"):
        if new_name and new_email:
            resp = requests.post(
                f"{BACKEND_URL}/student/{selected_domain}",
                json={"name": new_name, "email": new_email, "active_domain": selected_domain},
            )
            if resp.status_code == 201:
                data = resp.json()
                st.success(f"Created! Student ID: **{data['student_id']}**")
                st.session_state["last_created_id"] = data["student_id"]
            else:
                st.error(resp.text)
        else:
            st.warning("Fill in name and email.")

    st.divider()
    st.subheader("Load Existing Student")
    student_id_input = st.text_input(
        "Student ID",
        value=st.session_state.get("last_created_id", ""),
    )

    if st.button("New Session"):
        st.session_state.session_id = str(uuid.uuid4())[:8]
        st.session_state.chat_messages = []
        st.session_state.last_emotion = None
        st.session_state.last_emotion_raw = ""
        st.rerun()

    st.caption(f"Session ID: `{st.session_state.session_id}`")

# ── Main layout ───────────────────────────────────────────────────────────────

col_chat, col_debug = st.columns([3, 2])

# ── LEFT: Chat Window ─────────────────────────────────────────────────────────

with col_chat:
    st.subheader("💬 Chat")

    chat_container = st.container(height=520)
    with chat_container:
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    user_input = st.chat_input("Ask your study question…")

    if user_input:
        if not student_id_input:
            st.error("Enter a Student ID in the sidebar first.")
            st.stop()

        # Call /chat endpoint
        with st.spinner("Thinking…"):
            try:
                resp = requests.post(
                    f"{BACKEND_URL}/chat",
                    json={
                        "domain":     selected_domain,
                        "student_id": student_id_input,
                        "session_id": st.session_state.session_id,
                        "message":    user_input,
                    },
                    timeout=30,
                )
            except requests.exceptions.ConnectionError:
                st.error("Cannot reach backend. Make sure FastAPI is running on port 8000.")
                st.stop()

        if resp.status_code == 200:
            data = resp.json()
            emotion = data["emotion"]

            st.session_state.chat_messages.append({
                "role":    "user",
                "content": user_input,
                "emotion": emotion["emotion_label"],
            })
            st.session_state.chat_messages.append({
                "role":    "assistant",
                "content": data["reply"],
                "emotion": None,
            })
            st.session_state.last_emotion = emotion
            st.session_state.last_emotion_raw = data.get("emotion_raw", "")

            st.rerun()
        else:
            st.error(f"Backend error {resp.status_code}: {resp.text}")

# ── RIGHT: Admin Debug View ───────────────────────────────────────────────────

with col_debug:
    st.subheader("🔍 Admin Debug View")

    # ── Emotion JSON card ──────────────────────────────────────────────────────
    st.markdown("**Latest Emotion Detection (Step 1)**")
    if st.session_state.last_emotion:
        e = st.session_state.last_emotion
        label = e["emotion_label"]
        color = EMOTION_COLOR.get(label, "#888888")
        emoji = EMOTION_EMOJI.get(label, "")

        st.markdown(
            f"<div style='background:{color}22;border-left:4px solid {color};"
            f"padding:10px;border-radius:6px;'>"
            f"<b>{emoji} {label}</b><br>"
            f"Confidence: <b>{e['confidence_score']:.0%}</b><br>"
            f"Cause: <b>{e['detected_cause']}</b>"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.markdown("Parsed result:")
        st.code(json.dumps(e, indent=2), language="json")

        raw = st.session_state.get("last_emotion_raw", "")
        if raw:
            st.markdown("Raw model output (what the LLM actually said):")
            st.code(raw, language="text")
    else:
        st.info("Send a message to see emotion detection output.")

    st.divider()

    # ── Sentiment History Chart ────────────────────────────────────────────────
    st.markdown("**Sentiment History (from Firebase)**")
    if student_id_input:
        if st.button("Refresh Sentiment History"):
            resp = requests.get(
                f"{BACKEND_URL}/sentiment/{selected_domain}/{student_id_input}?limit=20"
            )
            if resp.status_code == 200:
                entries = resp.json().get("sentiment_log", [])
                if entries:
                    df = pd.DataFrame(entries)
                    df["timestamp"] = pd.to_datetime(df["timestamp"])
                    df = df.sort_values("timestamp")

                    # Map labels to numbers for sparkline
                    label_map = {
                        "calm/Confident":        4,
                        "Focused/Concentrating": 3,
                        "Neutral":               2,
                        "Frustrated/Confused":   1,
                        "Stressed/Anxious":      0,
                    }
                    df["emotion_num"] = df["emotion_label"].map(label_map).fillna(2)

                    st.line_chart(df.set_index("timestamp")["emotion_num"],
                                  use_container_width=True)
                    st.caption("4=Confident · 3=Focused · 2=Neutral · 1=Frustrated/Confused · 0=Stressed/Anxious")

                    st.dataframe(
                        df[["timestamp", "emotion_label", "confidence", "detected_cause"]]
                        .tail(10)
                        .reset_index(drop=True),
                        use_container_width=True,
                    )
                else:
                    st.info("No sentiment history yet.")
            else:
                st.error(resp.text)
    else:
        st.caption("Enter a Student ID to load sentiment history.")

    st.divider()

    # ── Quick API Tester ───────────────────────────────────────────────────────
    st.markdown("**Quick API Status**")
    if st.button("Ping Backend"):
        try:
            r = requests.get(f"{BACKEND_URL}/", timeout=5)
            st.success(f"Backend OK: {r.json()}")
        except Exception as exc:
            st.error(f"Backend unreachable: {exc}")
