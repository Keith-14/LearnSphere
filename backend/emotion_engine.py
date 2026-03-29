"""
Step 1 of the two-step Groq pipeline: Emotion Detection.

Takes the student's current message + last N conversation turns and asks
the LLM to output a structured JSON emotion object.  No prose — just JSON.

The key design insight: we pass the full conversation window so the LLM can
detect *implicit* emotions (e.g. asking the same question three times in a row
signals Confused even without the word "confused" appearing anywhere).
"""

import json
import os
import re

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_client = Groq(api_key=os.environ["GROQ_API_KEY"])

MODEL = "llama-3.3-70b-versatile"

EMOTION_SYSTEM_PROMPT = """\
You are an emotion detection engine embedded inside an educational AI assistant.

Given:
  1. A list of recent conversation messages between a student and an AI tutor.
  2. The student's latest message.

Your job is to output ONLY a valid JSON object — no prose, no markdown, no explanation.

JSON schema (strict):
{
  "emotion_label": "<one of: Focused/Concentrating | Frustrated/Confused | Stressed/Anxious | calm/Confident | Neutral>",
  "confidence_score": <float between 0.0 and 1.0>,
  "detected_cause": "<one of: topic_confusion | rank_anxiety | peer_comparison | repeated_attempts | time_pressure | or you can invent your own cause based on the conversation, but keep it concise>"
}

Detection rules:
- Infer from CONTEXT, not just keywords. If a student asks the same question 3 times, label Confused even with no explicit sentiment words.
- "I'll never clear this exam" or comparison phrases like "everyone else is better" → Anxious / rank_anxiety.
- Short, crisp, confident phrasing → Confident.
- Multiple "!" or "???" with expressions of giving up → Frustrated.
- Calm academic phrasing → Neutral.
- NEVER make medical or clinical diagnoses. Emotions are learning-context only.
- Output ONLY the JSON object. No text before or after it.
"""


def detect_emotion(current_message: str, history: list[dict]) -> dict:
    """
    Calls Groq to classify the student's emotional state.

    Args:
        current_message: The student's latest chat message.
        history: List of recent messages [{role, content, ...}] from Firebase.

    Returns:
        Dict with keys: emotion_label, confidence_score, detected_cause.
        Falls back to Neutral on any parse error.
    """
    # Build a compact conversation string from history
    conversation_lines = []
    for msg in history:
        role = msg.get("role", "unknown").capitalize()
        content = msg.get("content", "")
        conversation_lines.append(f"{role}: {content}")

    conversation_str = "\n".join(conversation_lines) if conversation_lines else "(no prior messages)"

    user_payload = (
        f"Conversation so far:\n{conversation_str}\n\n"
        f"Student's latest message: {current_message}\n\n"
        f"Classify the emotion. Reply with ONLY the JSON object."
    )

    response = _client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": EMOTION_SYSTEM_PROMPT},
            {"role": "user",   "content": user_payload},
        ],
        temperature=0.1,
        max_tokens=256,
    )

    raw = (response.choices[0].message.content or "").strip()
    finish_reason = response.choices[0].finish_reason
    print(f"\n[emotion_engine] finish_reason={finish_reason}\nraw:\n{raw}\n")

    result = _parse_emotion_json(raw)
    result["_raw"] = raw
    return result


def _strip_code_fences(text: str) -> str:
    """Remove markdown code fences the model sometimes wraps around JSON."""
    # Remove ```json ... ``` or ``` ... ```
    text = re.sub(r'^```(?:json)?\s*', '', text.strip(), flags=re.IGNORECASE)
    text = re.sub(r'\s*```$', '', text.strip())
    return text.strip()


def _parse_emotion_json(raw: str) -> dict:
    """Parse the LLM output, falling back gracefully on malformed JSON."""
    # Pass 1: try direct parse after stripping code fences
    cleaned = _strip_code_fences(raw)
    try:
        data = json.loads(cleaned)
        return _extract(data)
    except (json.JSONDecodeError, ValueError):
        pass

    # Pass 2: greedy scan — captures the full {...} object (non-greedy breaks multi-line JSON)
    match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group())
            return _extract(data)
        except Exception:
            pass

    # Pass 3: try the original raw in case stripping mangled something
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group())
            return _extract(data)
        except Exception:
            pass

    print(f"[emotion_engine] WARNING: could not parse JSON, using Neutral fallback. raw='{raw}'")
    return {"emotion_label": "Neutral", "confidence_score": 0.5, "detected_cause": "none"}


def _extract(data: dict) -> dict:
    return {
        "emotion_label":    data.get("emotion_label", "Neutral"),
        "confidence_score": float(data.get("confidence_score", 0.5)),
        "detected_cause":   data.get("detected_cause", "none"),
    }
