import pandas as pd

def generate_features(students, tests, emotions, engagement):
    
    # Aggregate test performance
    test_agg = tests.groupby("student_id").agg({
        "score": "mean"
    }).reset_index().rename(columns={"score": "avg_score"})

    # Aggregate emotion scores
    emotion_agg = emotions.groupby("student_id").agg({
        "stress_level": "mean",
        "confidence_level": "mean"
    }).reset_index()

    # Aggregate engagement
    engagement_agg = engagement.groupby("student_id").agg({
        "login_count": "sum",
        "avg_session_time": "mean"
    }).reset_index()

    # Merge everything
    df = students.merge(test_agg, on="student_id", how="left")
    df = df.merge(emotion_agg, on="student_id", how="left")
    df = df.merge(engagement_agg, on="student_id", how="left")

    df.fillna(0, inplace=True)

    return df