import streamlit as st
from utils.data_loader import load_all_data
from utils.feature_engineering import generate_features
from utils.prediction import predict_dropout
from utils.visualization import kpi_metrics, dropout_heatmap

st.title("📊 Admin Overview")

students, tests, emotions, engagement = load_all_data()
features_df = generate_features(students, tests, emotions, engagement)

features_df["risk_score"] = predict_dropout(features_df)

kpi_metrics(features_df)

st.divider()
st.subheader("🔥 Dropout Risk Heat Grid")
dropout_heatmap(features_df)