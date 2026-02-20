import pandas as pd
import numpy as np

np.random.seed(42)

N = 100

student_ids = np.arange(1, N+1)

# ---------- Students ----------
courses = ["GATE", "UPSC", "JEE", "CAT"]
students = pd.DataFrame({
    "student_id": student_ids,
    "name": [f"Student_{i}" for i in student_ids],
    "age": np.random.randint(18, 24, N),
    "course": np.random.choice(courses, N)
})

# ---------- Test Logs ----------
avg_scores = np.clip(np.random.normal(70, 15, N), 30, 100)

test_logs = pd.DataFrame({
    "student_id": student_ids,
    "score": avg_scores.round(2)
})

# ---------- Emotion Scores ----------
stress = np.clip(np.random.normal(3, 1.2, N), 1, 5)
confidence = np.clip(np.random.normal(3, 1.2, N), 1, 5)

emotion_scores = pd.DataFrame({
    "student_id": student_ids,
    "stress_level": stress.round(2),
    "confidence_level": confidence.round(2)
})

# ---------- Engagement ----------
login_count = np.clip(np.random.normal(25, 12, N), 2, 60)
session_time = np.clip(np.random.normal(35, 15, N), 5, 90)

engagement = pd.DataFrame({
    "student_id": student_ids,
    "login_count": login_count.round(0),
    "avg_session_time": session_time.round(2)
})

# ---------- Dropout Logic (Probabilistic + Noise) ----------

# Normalize for probability logic
score_norm = (100 - avg_scores) / 100
stress_norm = stress / 5
engagement_norm = 1 - (login_count / 60)
confidence_norm = (5 - confidence) / 5

dropout_prob = (
    0.35 * score_norm +
    0.30 * stress_norm +
    0.25 * engagement_norm +
    0.10 * confidence_norm
)

# Add noise
dropout_prob += np.random.normal(0, 0.05, N)

dropout_prob = np.clip(dropout_prob, 0, 1)

dropout_labels = (dropout_prob > 0.5).astype(int)

labels = pd.DataFrame({
    "student_id": student_ids,
    "dropout_label": dropout_labels
})

# ---------- Save Files ----------
students.to_csv("data/students_raw.csv", index=False)
test_logs.to_csv("data/test_logs.csv", index=False)
emotion_scores.to_csv("data/emotion_scores.csv", index=False)
engagement.to_csv("data/engagement_metrics.csv", index=False)
labels.to_csv("data/dropout_labels.csv", index=False)

print("Realistic synthetic dataset generated successfully.")