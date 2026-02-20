"""
Step 2 of the two-step Groq pipeline: Adaptive Response Generation.

Takes:
  - student message
  - detected emotion (from emotion_engine.py Step 1)
  - recent conversation history (for context continuity)
  - exam domain (upsc / jee / cat / gate)
  - response strategy (from response_router.py)

Builds a dynamic system prompt and calls the Groq LLM to produce a
tone-and-depth adjusted academic response.
"""

import os

from groq import Groq
from dotenv import load_dotenv

from response_router import ResponseStrategy

load_dotenv()

_client = Groq(api_key=os.environ["GROQ_API_KEY"])

MODEL = "llama-3.3-70b-versatile"

DOMAIN_CONTEXT = {
    "upsc": "UPSC Civil Services (Prelims + Mains + Interview)",
    "jee":  "JEE Main & Advanced (Physics, Chemistry, Mathematics)",
    "cat":  "CAT (Quantitative Aptitude, VARC, DILR)",
    "gate": "GATE (Engineering/CS core subjects)",
}


def build_system_prompt(domain: str, emotion_label: str, detected_cause: str,
                        strategy: ResponseStrategy) -> str:
    domain_desc = DOMAIN_CONTEXT.get(domain, domain.upper())
    return f"""\
You are an expert AI study assistant specialising in {domain_desc} exam preparation.

=== Student Emotional State ===
Detected emotion : {emotion_label}
Detected cause   : {detected_cause}

=== How You Must Respond ===
{strategy.behavior_instruction}

=== General Rules ===
- Keep your response under {strategy.max_tokens} words (roughly).
- Use clear, accessible language appropriate for a competitive exam student.
- Never make medical or psychological diagnoses.
- Never say "I am an AI" or deflect questions — just help.
- If the student's question is off-topic from the exam domain, gently redirect.
"""


def generate_response(
    domain: str,
    student_message: str,
    emotion_label: str,
    detected_cause: str,
    strategy: ResponseStrategy,
    history: list[dict],
) -> str:
    """
    Generates an adaptive academic response.

    Args:
        domain: Exam domain key ("upsc", "jee", "cat", "gate").
        student_message: The student's current message.
        emotion_label: Label from emotion_engine (e.g. "Confused").
        detected_cause: Cause from emotion_engine (e.g. "topic_confusion").
        strategy: ResponseStrategy from response_router.
        history: Recent messages for context (list of {role, content}).

    Returns:
        The assistant's reply as a plain string.
    """
    system_prompt = build_system_prompt(domain, emotion_label, detected_cause, strategy)

    # Build message list: history (trimmed to last 6) + current user message
    messages = [{"role": "system", "content": system_prompt}]
    for msg in history[-6:]:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": student_message})

    response = _client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=strategy.max_tokens,
    )

    return response.choices[0].message.content.strip()
