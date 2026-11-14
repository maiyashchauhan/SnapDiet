import streamlit as st
import sys, os

st.set_page_config(page_title="Workout Planner | SnapDiet", layout="wide")

try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
except Exception:
    pass

from utils.sidebar import render_sidebar
from utils.ui_theme import render_hero
from utils.ai_engine import generate_workout_plan


render_sidebar()

if st.session_state.get('user_profile') is None:
    st.switch_page("app.py")

profile = st.session_state.user_profile

render_hero("AI Workout Planner 🏋️", "Your personalized 7-day fitness routine based on your goals.")

if st.button("🚀 Generate New Workout Plan", type="primary", use_container_width=True):
    with st.spinner("AI is crafting your perfect routine..."):
        plan = generate_workout_plan(profile)
        st.session_state.workout_plan = plan
        st.rerun()

st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 30px 0;'>", unsafe_allow_html=True)

if 'workout_plan' in st.session_state and st.session_state.workout_plan:
    st.markdown("<h3>Your 7-Day Routine</h3>", unsafe_allow_html=True)
    
    for day_plan in st.session_state.workout_plan:
        st.markdown(f"""
        <div style='background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 20px; margin-bottom: 15px;'>
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;'>
                <h4 style='margin: 0; color: #34d399; font-size: 1.2rem;'>{day_plan.get('day')}</h4>
                <span style='background: rgba(59, 130, 246, 0.2); color: #60a5fa; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;'>
                    {day_plan.get('duration')}
                </span>
            </div>
            <h5 style='color: #e2e8f0; margin-bottom: 10px; font-size: 1.1rem;'>🎯 Focus: {day_plan.get('focus')}</h5>
            <p style='color: #94a3b8; font-size: 1rem; margin: 0; line-height: 1.6;'>
                <strong>Exercises:</strong> {day_plan.get('exercises')}
            </p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("Click the button above to generate your customized AI Workout Plan!")
