"""
Adaptive response routing.

Maps a detected emotion label → a strategy dict that tells the Groq
response-generation prompt *how* to behave (tone, depth, max_tokens,
and concrete behavioral instruction injected into the system prompt).
"""

from dataclasses import dataclass


@dataclass
class ResponseStrategy:
    tone: str
    max_tokens: int
    behavior_instruction: str   # injected verbatim into Step-2 system prompt


STRATEGIES: dict[str, ResponseStrategy] = {

    "Frustrated/Confused": ResponseStrategy(
        tone="patient-empathetic",
        max_tokens=280,
        behavior_instruction=(
            "The student is frustrated or confused. Open with a one-sentence empathetic acknowledgement "
            "(e.g., 'This part trips up a lot of people — completely understandable.'). "
            "Then use the Socratic method: do NOT give the direct answer immediately. "
            "Break the concept into 2–3 small numbered hints or guiding questions "
            "that lead the student toward the answer on their own. "
            "End with a question like 'Does this help clarify the first part?'"
        ),
    ),

    "Stressed/Anxious": ResponseStrategy(
        tone="calm",
        max_tokens=180,
        behavior_instruction=(
            "The student is stressed or anxious about the exam. "
            "Do NOT continue academic tutoring right now. "
            "Gently acknowledge their feeling without dramatising it. "
            "Suggest ONE small, concrete action: a 5-minute break, a breathing exercise, "
            "or a single easy review question to rebuild confidence. "
            "Do not make clinical or medical claims."
        ),
    ),

    "calm/Confident": ResponseStrategy(
        tone="direct",
        max_tokens=180,
        behavior_instruction=(
            "The student is calm and confident, ready to learn. "
            "Be direct and concise — skip the hand-holding. "
            "After answering, challenge them with one follow-up question or a harder variant "
            "of the same concept to push their understanding further."
        ),
    ),

    "Focused/Concentrating": ResponseStrategy(
        tone="precise",
        max_tokens=240,
        behavior_instruction=(
            "The student is focused and concentrating deeply. "
            "Respect their flow state: give a thorough, well-structured explanation without unnecessary filler. "
            "Use clear steps or numbered points. Do not add motivational fluff — just the content."
        ),
    ),

    "Neutral": ResponseStrategy(
        tone="neutral",
        max_tokens=220,
        behavior_instruction=(
            "Provide a clear, well-structured academic explanation. "
            "Use examples relevant to the exam domain where applicable."
        ),
    ),
}

# Default fallback if an unexpected label arrives
DEFAULT_STRATEGY = STRATEGIES["Neutral"]


def get_strategy(emotion_label: str) -> ResponseStrategy:
    return STRATEGIES.get(emotion_label, DEFAULT_STRATEGY)
