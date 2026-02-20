🎓 LearnSphere
Emotion-Aware Adaptive Learning Platform

LearnSphere is a full-stack AI-driven adaptive learning ecosystem designed to intelligently respond to both academic performance and emotional well-being.

Unlike traditional EdTech systems that only measure scores, LearnSphere integrates Computer Vision, LLM-based emotional intelligence, and predictive analytics to detect stress, adapt learning pathways, and proactively prevent student dropout.

🚀 Core Features
🧠 Real-Time Emotion Detection

Live facial emotion analysis using Computer Vision

Detects stress, confusion, engagement levels

Emotion signals logged securely to Firebase
<img width="1385" height="795" alt="image" src="https://github.com/user-attachments/assets/22f7990c-1cac-4387-94f8-dcf411fb3a36" />

<img width="1353" height="781" alt="image" src="https://github.com/user-attachments/assets/5bab4ad7-70a2-48eb-8724-17a3d20eb99f" />


📈 Adaptive Testing Engine

Automatically adjusts question difficulty during mock tests

Reduces complexity when stress is detected

Reinforces confidence-building strategies
<img width="1457" height="761" alt="image" src="https://github.com/user-attachments/assets/f863969e-6352-48ad-ba01-282f73317d79" />


💬 Emotion-Aware AI Chatbot

Powered by Groq LLM

Detects emotional tone in conversations

Switches between:

Academic guidance mode

Emotional intervention mode

Redirects students to wellness activities when needed

🔥 Dropout Risk Prediction

Combines:

Academic performance trends

CV stress frequency

Chatbot sentiment signals

Engagement metrics

Mood polling history

Generates a 0–5 dropout likelihood score

Visualized in GitHub-style heatmap (Green → Yellow → Red)


👩‍🏫 Teacher / Admin Dashboard

Real-time KPI metrics

Live chatbot sentiment monitoring

CV feedback aggregation

Student-level emotional timelines

Manual mood-check trigger system
<img width="1444" height="769" alt="image" src="https://github.com/user-attachments/assets/fd2a4b48-3cdf-4821-80fe-44e249c4f042" />

🔔 Proactive Mood Polling

Duolingo-style emotional check-in popups

Emoji-based sentiment tracking

Builds longitudinal emotional profiles
<img width="1451" height="766" alt="image" src="https://github.com/user-attachments/assets/0fc54261-2b1b-452b-8dc3-ece7f1cc92ae" />

🏗 System Architecture
Frontend (Next.js - Student & Teacher)
        ↓
Firebase (Real-Time Data Layer)
        ↓
AI Services Layer
    - Computer Vision Model
    - Groq LLM Chat Engine
    - Dropout Risk Engine
        ↓
Admin Analytics Dashboard (Streamlit)
🔄 Data Flow Overview
Student Side Writes:

CV emotion signals

Chatbot sentiment logs

Mood poll responses

Test performance metrics

Teacher Side Reads:

Aggregated KPIs

Dropout heatmap

Live sentiment states

Emotional history timelines

All interactions are synchronized through Firebase.

📊 Dropout Heatmap Logic

Each student is mapped to a color-coded grid cell:

🟢 Green → Low risk

🟡 Yellow → Medium risk

🔴 Red → High risk

Risk score calculation factors:

Test score decline

CV-detected stress frequency

Chatbot emotional distress patterns

Reduced engagement

Negative mood trends

🧩 Tech Stack
Frontend

Next.js (TypeScript)

Tailwind CSS

Real-time Firebase listeners

Backend

FastAPI (ML API layer)

Streamlit (Admin dashboard)

Firebase Firestore

AI Components

Computer Vision (Emotion detection)

Groq LLM (Emotion-aware chatbot)

Predictive dropout scoring model

🧪 Integration Checklist

Ensure the following work correctly:

CV script writes CV_Sentiment_Data to Firebase

Mock test logic reads stress level dynamically

Chatbot logs emotional state in database

Dropout risk engine calculates and updates heatmap

Teacher-triggered mood check appears on student interface

Emoji response updates student sentiment profile

📈 Future Enhancements

Batch prediction API for scalability

Real-time WebSocket monitoring

Automated intervention triggers

Weekly risk forecasting

Behavioral clustering engine

AI-powered mentorship recommendations

🎯 Vision

LearnSphere transforms competitive exam preparation from performance-driven to emotionally intelligent learning.

We are building a system where:

AI doesn't just measure scores —
it understands students.
