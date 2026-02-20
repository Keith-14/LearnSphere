import pandas as pd

def load_all_data():
    students = pd.read_csv("data/students_raw.csv")
    tests = pd.read_csv("data/test_logs.csv")
    emotions = pd.read_csv("data/emotion_scores.csv")
    engagement = pd.read_csv("data/engagement_metrics.csv")
    return students, tests, emotions, engagement