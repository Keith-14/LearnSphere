# LearnSphere Frontend & VEGA Backend

This repository contains both the Next.js frontend for LearnSphere and the Python backend for the VEGA Exam Stress Detection MVP.

## Next.js Frontend

This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

### Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.
This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

---

## VEGA Exam Stress Detection (Backend)

Real-time facial expression and stress detection during exams using a webcam. Built for the **VEGA Hackathon**.

### 📁 Project Structure

```
VEGA Hachthon/
├── app.py                        # Streamlit testing UI
├── requirements.txt
├── README.md
├── models/
│   └── download_model.py         # Verify & cache emotion model weights
├── src/
│   ├── face_detector.py          # MediaPipe face detection + head pose
│   ├── emotion_model.py          # FER2013 emotion model wrapper
│   ├── stress_scorer.py          # Stress scoring + temporal smoothing
│   ├── logger.py                 # JSONL session logger
│   └── pipeline.py               # Main orchestrator
└── train/
    ├── dataset_mapper.py         # FER2013 / AffectNet → 4 exam emotions
    └── train_emotion.py          # MobileNetV2 transfer learning trainer
```

### ⚡ Quick Setup

#### 1. Prerequisites
- Python 3.9 – 3.11
- macOS / Linux (webcam access required)

#### 2. Create a virtual environment (recommended)
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Verify model weights
```bash
python models/download_model.py
```

### 🚀 Running the App
```bash
streamlit run app.py
```
Open **http://localhost:8501** in your browser.
