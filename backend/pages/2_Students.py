import streamlit as st
from utils.data_loader import load_all_data
from utils.feature_engineering import generate_features
from utils.prediction import predict_dropout

st.title("👨‍🎓 Student Analytics")

# Load data
students, tests, emotions, engagement = load_all_data()
features_df = generate_features(students, tests, emotions, engagement)
features_df["risk_score"] = predict_dropout(features_df)

# ---------- SESSION STATE FOR SORTING ----------
if "sort_column" not in st.session_state:
    st.session_state.sort_column = "student_id"

if "sort_order" not in st.session_state:
    st.session_state.sort_order = True  # True = Ascending


def sort_data(column):
    if st.session_state.sort_column == column:
        # Toggle order if same column clicked
        st.session_state.sort_order = not st.session_state.sort_order
    else:
        # New column → default ascending
        st.session_state.sort_column = column
        st.session_state.sort_order = True


# ---------- SORT BUTTON ROW ----------
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.write("**Student ID**")
    if st.button("↕", key="id_sort"):
        sort_data("student_id")

with col2:
    st.write("**Name**")
    if st.button("↕", key="name_sort"):
        sort_data("name")

with col3:
    st.write("**Avg Score**")
    if st.button("↕", key="score_sort"):
        sort_data("avg_score")

with col4:
    st.write("**Stress Level**")
    if st.button("↕", key="stress_sort"):
        sort_data("stress_level")

with col5:
    st.write("**Risk Score**")
    if st.button("↕", key="risk_sort"):
        sort_data("risk_score")


# ---------- APPLY SORT ----------
sorted_df = features_df.sort_values(
    by=st.session_state.sort_column,
    ascending=st.session_state.sort_order
)

st.dataframe(sorted_df, use_container_width=True)