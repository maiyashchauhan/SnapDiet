import streamlit as st
import sys, os
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="90-Day Challenge | SnapDiet", layout="wide")

try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
except Exception:
    pass

from utils.sidebar import render_sidebar


render_sidebar()

if st.session_state.get('user_profile') is None:
    st.switch_page("app.py")
st.title("90-Day Transformation Challenge 🏆")

current_day = 45 # Mock current day
phase = "Foundation (1-30)" if current_day <= 30 else "Acceleration (31-60)" if current_day <= 60 else "Peak (61-90)"

st.markdown(f"### Current Phase: **{phase}** (Day {current_day}/90)")

st.progress(current_day / 90.0)
st.markdown(f"<p style='text-align: right; color: #a0a0a0;'>{current_day} out of 90 days completed</p>", unsafe_allow_html=True)

if "Acceleration" in phase:
    st.info("**Phase Rules:** Time to push harder. Reduce simple carbs by 10% and add 15 mins of brisk walking.")

st.subheader("Weight Progress")

# Mock data
dates = pd.date_range(end=pd.Timestamp.today(), periods=current_day)
weights = [70 - (i*0.05) + (i%2*0.2) for i in range(current_day)] # Decreasing trend
df = pd.DataFrame({"Date": dates, "Weight (kg)": weights})

fig = px.line(df, x="Date", y="Weight (kg)", markers=True, title="Your Transformation Journey")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Unlocked Badges 🎖️")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div style="text-align:center; padding: 20px; background:#2e2e2e; border-radius:10px;">
        <h1>🏃</h1>
        <p>7-Day Streak</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div style="text-align:center; padding: 20px; background:#2e2e2e; border-radius:10px;">
        <h1>🥦</h1>
        <p>Veggie Master</p>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div style="text-align:center; padding: 20px; background:#2e2e2e; border-radius:10px; opacity:0.5;">
        <h1>💪</h1>
        <p>Phase 2 Complete (Locked)</p>
    </div>
    """, unsafe_allow_html=True)
