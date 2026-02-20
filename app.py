"""
app.py
======
VEGA Exam Stress Detection — Streamlit Testing UI

Tabs:
  📷 Monitor   — Live webcam feed + stress analysis
  🎯 Calibrate — Record your own calm/stressed expressions to personalise
  📊 Logs      — Session history and JSON records

Run:
    streamlit run app.py
"""

from __future__ import annotations

import json
import os
import time
from collections import deque

import cv2
import numpy as np
import streamlit as st

# ── macOS camera fix ─────────────────────────────────────────────────────────
os.environ.setdefault("OPENCV_AVFOUNDATION_SKIP_AUTH", "1")

st.set_page_config(
    page_title  = "VEGA Exam Stress Monitor",
    page_icon   = "🎓",
    layout      = "wide",
    initial_sidebar_state = "expanded",
)

st.markdown("""
<style>
  html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
    background-color: #0f1117;
    color: #e0e0e0;
  }
  .state-badge {
    display: inline-block;
    padding: 8px 24px;
    border-radius: 24px;
    font-size: 1.3rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 8px;
  }
  .state-stressed           { background:#ff4444; color:#fff; }
  .state-confused           { background:#ff9900; color:#fff; }
  .state-focused            { background:#0088ff; color:#fff; }
  .state-calm               { background:#00cc77; color:#fff; }
  .state-look_into_camera   { background:#9955ff; color:#fff; }
  .state-face_not_visible   { background:#555; color:#ccc; }
  .state-working            { background:#1a8a6e; color:#fff; }
  .state-unknown            { background:#333; color:#aaa; }
  [data-testid="stMetric"]  { background:#1a1d26; border-radius:10px; padding:12px 16px; }
  [data-testid="stImage"] img { border-radius: 10px; }
  .cal-badge-recording { background:#ff4444; color:#fff; padding:4px 12px;
                         border-radius:8px; font-weight:700; display:inline-block; }
  .cal-badge-ready     { background:#00cc77; color:#fff; padding:4px 12px;
                         border-radius:8px; font-weight:700; display:inline-block; }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
EMOJI_MAP = {
    "stressed":          "😰",
    "confused":          "🤔",
    "focused":           "🎯",
    "calm":              "😌",
    "working":           "✏️",   # writing at paper
    "look_into_camera":  "👁️",
    "face_not_visible":  "🚫",
    "unknown":           "❓",
}
STATE_COLORS = {
    "stressed":          "#ff4444",
    "confused":          "#ff9900",
    "focused":           "#0088ff",
    "calm":              "#00cc77",
    "working":           "#1a8a6e",
    "look_into_camera":  "#9955ff",
    "face_not_visible":  "#555555",
    "unknown":           "#333333",
}
CAL_FRAMES_NEEDED = 60   # frames per class for calibration


def state_badge(state: str) -> str:
    emoji = EMOJI_MAP.get(state, "❓")
    label = state.replace("_", " ").title()
    return f'<div class="state-badge state-{state}">{emoji} {label}</div>'


def stress_color(score: float) -> str:
    return "#00cc77" if score < 0.4 else "#ff9900" if score < 0.65 else "#ff4444"


# ── Pipeline (cached) ─────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading AI models…")
def get_pipeline():
    from models.download_model import download_model
    try:
        download_model()
    except Exception:
        pass
    from src.pipeline import ExamPipeline
    return ExamPipeline(skip_frames=1, buffer_size=3, log_every=5)


# ── Session state defaults ────────────────────────────────────────────────────
def _init_state():
    defaults = {
        "running":        False,
        "history":        [],
        "cap":            None,
        "cal_label":      None,       # "calm" | "stressed" | None
        "cal_buffer":     deque(maxlen=CAL_FRAMES_NEEDED),
        "cal_status":     {},         # {"calm": n, "stressed": n}
        "cal_message":    "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Settings")
    camera_idx = st.number_input("Camera index", min_value=0, max_value=5, value=0)

    from src.calibrator import Calibrator
    svm_exists = Calibrator.model_exists()
    st.caption(f"Personal SVM: {'✅ Active' if svm_exists else '❌ Not calibrated'}")

    st.divider()
    if not st.session_state.running:
        if st.button("▶ Start Monitoring", width="stretch", type="primary"):
            st.session_state.running = True
            st.session_state.history = []
            cap = cv2.VideoCapture(int(camera_idx))
            if not cap.isOpened():
                cap.release(); time.sleep(0.5)
                cap = cv2.VideoCapture(int(camera_idx))
            if not cap.isOpened():
                st.error("❌ Cannot open camera. Check System Settings → Privacy → Camera.")
                st.session_state.running = False
            else:
                st.session_state.cap = cap
    else:
        if st.button("⏹ Stop Monitoring", width="stretch"):
            st.session_state.running = False
            if st.session_state.cap:
                st.session_state.cap.release()
                st.session_state.cap = None

    st.divider()
    st.subheader("📊 Session Stats")
    stats_ph = st.empty()
    st.divider()
    st.caption("VEGA Hackathon — Exam Stress Detection MVP")


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_monitor, tab_calibrate, tab_logs = st.tabs(
    ["📷 Monitor", "🎯 Calibrate (Fix Bias)", "📊 Logs"]
)


# ═══════════════════════════════════════════════════════════════════════════════
#  TAB 1 — MONITOR
# ═══════════════════════════════════════════════════════════════════════════════
with tab_monitor:
    st.title("🎓 VEGA Exam Stress Monitor")
    if not Calibrator.model_exists():
        st.warning("⚠️ **No personal calibration found.** The base model may show 'focused' "
                   "for most expressions. Go to the **🎯 Calibrate** tab to fix this.")

    col_feed, col_dash = st.columns([3, 2], gap="large")
    with col_feed:
        st.subheader("📷 Live Feed")
        feed_ph      = st.empty()
        crop_ph      = st.empty()   # face crop preview

    with col_dash:
        st.subheader("🧠 Live Analysis")
        state_ph     = st.empty()
        m1, m2, m3   = st.columns(3)
        metric_score  = m1.empty()
        metric_stab   = m2.empty()   # stability score (primary)
        metric_mvt    = m3.empty()   # movement score
        gauge_ph      = st.empty()
        st.subheader("📈 Behavior Signals")
        prob_ph       = st.empty()   # emotion probs
        conf_ph       = st.empty()
        st.caption("💡 Primary: Head stability | Secondary: Emotion model")

    st.divider()
    json_ph = st.empty()

    if not st.session_state.running:
        feed_ph.info("▶ Click **Start Monitoring** in the sidebar.")
        state_ph.markdown(state_badge("unknown"), unsafe_allow_html=True)
        metric_score.metric("Stress Score", "—")
        metric_pose.metric("Head Pose", "—")
        st.stop()

    # ── Live loop ─────────────────────────────────────────────────────
    pipeline   = get_pipeline()
    cap        = st.session_state.cap
    frame_time = 1.0 / 12

    while st.session_state.running and cap and cap.isOpened():
        t0 = time.perf_counter()
        ret, frame = cap.read()
        if not ret:
            st.warning("Empty frame — check your webcam."); break

        record   = pipeline.process_frame(frame)
        st.session_state.history.append(record)
        if len(st.session_state.history) > 300:
            st.session_state.history = st.session_state.history[-300:]

        # ── Annotated feed ────────────────────────────────────────────
        # Draw bbox using face_detector directly
        det_result = pipeline.face_detector.detect(frame)
        annotated  = pipeline.face_detector.draw(frame, det_result)
        feed_ph.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB),
                      channels="RGB", width="stretch")

        # ── Face crop preview ─────────────────────────────────────────
        crop = record.get("face_crop")
        if crop is not None:
            crop_ph.image(crop, caption="🔍 Face crop used for emotion", width=96)
        else:
            crop_ph.caption("No face crop")

        # ── Dashboard ─────────────────────────────────────────────────
        state = record.get("state", "unknown")
        score = record.get("stress_score", 0.0)
        pose  = record.get("head_pose",    "unknown")
        probs = record.get("probabilities", {})

        state_ph.markdown(state_badge(state), unsafe_allow_html=True)
        metric_score.metric("Stress Score", f"{score:.3f}")
        stability = record.get("stability_score", 1.0)
        movement  = record.get("movement_score",  0.0)
        dir_ch    = record.get("direction_changes", 0)
        metric_stab.metric("Head Stability",
                           f"{stability:.2f}",
                           delta="✅ Stable" if record.get("is_stable") else "⚠️ Moving")
        metric_mvt.metric("Movement",
                          f"{movement:.2f}",
                          delta=f"Dir changes: {dir_ch}")

        gauge_ph.markdown(f"""
        <div style="background:#1a1d26;border-radius:8px;padding:8px 12px;margin-top:4px">
          <div style="font-size:0.8rem;color:#888;margin-bottom:4px">Stress Level</div>
          <div style="background:#2a2d36;border-radius:6px;height:16px;overflow:hidden">
            <div style="width:{score*100:.1f}%;height:100%;
                        background:{stress_color(score)};
                        border-radius:6px;transition:width 0.3s ease"></div>
          </div>
        </div>""", unsafe_allow_html=True)

        # Raw probabilities bar chart — most important for debugging
        if probs:
            prob_ph.bar_chart(probs, height=160, color="#0088ff")
            max_class = max(probs, key=probs.get)
            max_conf  = probs[max_class]
            if max_conf < 0.45:
                conf_ph.warning(f"⚠️ Low confidence ({max_conf:.2f}) — showing uncertain")
            else:
                conf_ph.caption(f"Highest: **{max_class}** ({max_conf:.2f})")

        json_ph.code(
            json.dumps({k: v for k, v in record.items() if k != "face_crop"}, indent=2),
            language="json",
        )

        # Sidebar stats
        history = st.session_state.history
        n = len(history)
        stats_ph.markdown(f"""
| Metric | Value |
|---|---|
| Frames | {n} |
| Avg stress | {sum(r.get('stress_score',0) for r in history)/max(n,1):.3f} |
| Stressed frames | {sum(1 for r in history if r.get('state')=='stressed')} |
| Look-away | {sum(1 for r in history if r.get('state')=='look_into_camera')} |
""")

        # Calibration feed: if calibration is active, collect sample
        cal_label = st.session_state.cal_label
        if cal_label and record.get("valid_for_emotion") and probs:
            st.session_state.cal_buffer.append((probs, cal_label))

        elapsed = time.perf_counter() - t0
        sleep_t = frame_time - elapsed
        if sleep_t > 0:
            time.sleep(sleep_t)

    if cap:
        cap.release()
    st.session_state.cap  = None
    st.success("✅ Monitoring stopped.")


# ═══════════════════════════════════════════════════════════════════════════════
#  TAB 2 — CALIBRATE
# ═══════════════════════════════════════════════════════════════════════════════
with tab_calibrate:
    st.title("🎯 Personal Calibration")
    st.markdown("""
**Why calibrate?**  The base FER+ model was trained on posed lab faces and tends
to predict *neutral → focused* for almost everyone.  By recording a few seconds
of your own calm and stressed expressions, we train a tiny personal SVM **on top**
of the base model that learns *your* probability fingerprint.  This takes ~2 minutes
and dramatically improves accuracy.

**How to calibrate:**
1. Start Monitoring (sidebar) so the webcam is active.
2. Sit relaxed → click **Record Calm** → hold for ~5 seconds.
3. Frown / furrow brow / look tense → click **Record Stressed** → hold for ~5 seconds.
4. Click **Train Personal Model** when both classes show ✅.
""")

    st.divider()

    # Status display
    cal_status = st.session_state.cal_status
    calm_n     = cal_status.get("calm", 0)
    stressed_n = cal_status.get("stressed", 0)

    c1, c2, c3 = st.columns(3)
    c1.metric("Calm samples",    f"{calm_n} / {CAL_FRAMES_NEEDED}",
              delta="✅" if calm_n >= CAL_FRAMES_NEEDED else "recording needed")
    c2.metric("Stressed samples", f"{stressed_n} / {CAL_FRAMES_NEEDED}",
              delta="✅" if stressed_n >= CAL_FRAMES_NEEDED else "recording needed")
    c3.metric("Personal SVM", "✅ Active" if Calibrator.model_exists() else "❌ None")

    st.divider()

    col_a, col_b, col_c = st.columns([1, 1, 1])

    def _start_recording(label: str):
        st.session_state.cal_label  = label
        st.session_state.cal_buffer = deque(maxlen=CAL_FRAMES_NEEDED)
        st.session_state.cal_message = f"🔴 Recording **{label}** — hold expression…"

    def _stop_and_collect(label: str):
        buf   = list(st.session_state.cal_buffer)
        count = len(buf)
        if count > 0:
            # Merge into global calibrator data store (session state)
            if "cal_data" not in st.session_state:
                st.session_state.cal_data = []
            # Only keep same-label samples from this recording
            st.session_state.cal_data.extend(buf)
            st.session_state.cal_status[label] = \
                sum(1 for p, l in st.session_state.get("cal_data", []) if l == label)
        st.session_state.cal_label  = None
        st.session_state.cal_buffer = deque(maxlen=CAL_FRAMES_NEEDED)
        st.session_state.cal_message = f"✅ Saved {count} {label} samples."

    with col_a:
        if st.session_state.cal_label == "calm":
            if st.button("⏹ Stop Calm Recording", type="secondary"):
                _stop_and_collect("calm")
                st.rerun()
        else:
            if st.button("😌 Record Calm", type="secondary"):
                _start_recording("calm")
                st.rerun()

    with col_b:
        if st.session_state.cal_label == "stressed":
            if st.button("⏹ Stop Stressed Recording", type="secondary"):
                _stop_and_collect("stressed")
                st.rerun()
        else:
            if st.button("😰 Record Stressed", type="secondary"):
                _start_recording("stressed")
                st.rerun()

    with col_c:
        both_ready = (calm_n >= CAL_FRAMES_NEEDED and stressed_n >= CAL_FRAMES_NEEDED)
        if st.button("🚀 Train Personal Model", type="primary", disabled=not both_ready):
            cal = Calibrator()
            for probs, label in st.session_state.get("cal_data", []):
                cal.add_sample(probs, label)
            ok = cal.fit_and_save()
            if ok:
                # Reload pipeline's calibrator
                pipe = get_pipeline()
                pipe.reload_calibrator()
                st.success("✅ Personal model trained and activated! "
                           "Go to the Monitor tab — results should be much better.")
                st.session_state.cal_data   = []
                st.session_state.cal_status = {}
            else:
                st.error("Training failed — see console for details.")

    st.divider()

    if st.session_state.cal_message:
        st.info(st.session_state.cal_message)

    if st.session_state.cal_label:
        buf_len = len(st.session_state.cal_buffer)
        st.progress(min(1.0, buf_len / CAL_FRAMES_NEEDED),
                    text=f"Recording {st.session_state.cal_label}: "
                         f"{buf_len}/{CAL_FRAMES_NEEDED} frames")

    if Calibrator.model_exists():
        st.divider()
        if st.button("🗑️ Delete Personal Model (reset to base model)"):
            Calibrator.delete_model()
            pipe = get_pipeline()
            pipe.reload_calibrator()
            st.warning("Personal model deleted. Reload the page to see changes.")

    st.divider()
    st.caption("💡 Tip: you only need to calibrate once. The model is saved to "
               "`models/personal_svm.pkl` and loaded automatically on next run.")


# ═══════════════════════════════════════════════════════════════════════════════
#  TAB 3 — LOGS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_logs:
    st.title("📊 Session History")
    history = st.session_state.history
    if not history:
        st.info("No data yet — start monitoring first.")
    else:
        import pandas as pd
        rows = []
        for r in history:
            row = {
                "time":       r.get("timestamp", ""),
                "state":      r.get("state", ""),
                "stress":     r.get("stress_score", 0),
                "head_pose":  r.get("head_pose", ""),
                "valid":      r.get("valid_for_emotion", False),
            }
            row.update(r.get("probabilities", {}))
            rows.append(row)
        df = pd.DataFrame(rows)

        st.subheader("Stress Score Over Time")
        st.line_chart(df["stress"], height=200)

        st.subheader("State Distribution")
        st.bar_chart(df["state"].value_counts(), height=180)

        st.subheader("Raw Data")
        st.dataframe(df, use_container_width=True, height=300)

        # Last JSON record
        st.subheader("Last JSON Record")
        last = {k: v for k, v in history[-1].items() if k != "face_crop"}
        st.code(json.dumps(last, indent=2), language="json")
