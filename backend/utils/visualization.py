import streamlit as st
import pandas as pd


def kpi_metrics(df):

    total_students = len(df)
    high_risk = (df["risk_score"] >= 3.5).sum()
    avg_score = df["avg_score"].mean()

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Students", total_students)
    col2.metric("High Risk Students", high_risk)
    col3.metric("Average Score", f"{avg_score:.2f}")


import streamlit as st
import streamlit.components.v1 as components


def get_color(score):
    """
    Smooth Green → Yellow → Red gradient
    score range: 0 to 5
    """

    # Normalize score to 0–1
    normalized = score / 5

    # If in green → yellow range
    if normalized <= 0.5:
        # Green (0,200,0) → Yellow (255,200,0)
        r = int(255 * (normalized * 2))
        g = 200
        b = 0
    else:
        # Yellow → Red (200,0,0)
        r = 200
        g = int(200 * (1 - (normalized - 0.5) * 2))
        b = 0

    return f"rgb({r},{g},{b})"

def dropout_heatmap(df):

    df = df.sort_values("student_id")

    cells = ""

    for _, row in df.iterrows():
        color = get_color(row["risk_score"])

        tooltip = (
            f"Name: {row['name']} | "
            f"Avg Score: {round(row['avg_score'],2)} | "
            f"Risk: {round(row['risk_score'],2)}"
        )

        cells += f"""
        <div class="heat-cell" 
             style="background-color:{color};"
             title="{tooltip}">
        </div>
        """

    html_code = f"""
    <html>
    <head>
    <style>
    .heat-grid {{
        display: grid;
        grid-template-columns: repeat(10, 40px);
        gap: 6px;
        width: fit-content;
    }}

    .heat-cell {{
        width: 40px;
        height: 40px;
        border-radius: 6px;
        transition: transform 0.2s ease;
    }}

    .heat-cell:hover {{
        transform: scale(1.15);
        outline: 2px solid #000;
    }}
    </style>
    </head>

    <body>
        <div class="heat-grid">
            {cells}
        </div>
    </body>
    </html>
    """

    components.html(html_code, height=500)