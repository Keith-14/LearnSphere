import streamlit as st

st.set_page_config(
    page_title="LearnSphere Admin Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎓 LearnSphere Admin Dashboard")

st.markdown("""
Welcome to the LearnSphere Admin Dashboard.

Use the sidebar to navigate:
- Home → KPIs & Dropout Risk Grid
- Students → Student Analytics & Filtering
""")