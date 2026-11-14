import streamlit as st
import sys, os
from PIL import Image

st.set_page_config(page_title="AI Scanner | SnapDiet", layout="wide")

try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
except Exception:
    pass

from utils.sidebar import render_sidebar
from utils.ui_theme import render_hero, render_metric_card
from utils.db import get_daily_log, update_daily_log
from utils.ai_engine import analyze_food_image

render_sidebar()

if st.session_state.get('user_profile') is None:
    st.switch_page("app.py")

# Ensure we have the latest daily log from the DB
st.session_state.daily_log = get_daily_log()

render_hero("AI Meal & Packaged Food Scanner 📸", "Upload or snap a picture of your food to instantly get macros and calories.")

st.markdown("""
<div class="snap-card" style="margin-bottom: 25px;">
    <h3 style="margin-top: 0;">Input Method</h3>
""", unsafe_allow_html=True)

upload_option = st.radio("", ["Camera", "Upload Image"], horizontal=True, label_visibility="collapsed")

img_file = None
if upload_option == "Camera":
    img_file = st.camera_input("Take a picture")
else:
    img_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

st.markdown("</div>", unsafe_allow_html=True)

safe_int = lambda v: int(''.join(filter(str.isdigit, str(v))) or 0) if v else 0

if img_file is not None:
    try:
        st.image(img_file, caption="Selected Image", use_container_width=True)
        img_file.seek(0)
        image = Image.open(img_file).convert("RGB")
    except Exception as e:
        st.error(f"Could not load image. Please try another one. Error: {e}")
        st.stop()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🚀 Analyze Food with Gemini AI", use_container_width=True):
        with st.spinner("Analyzing with Gemini..."):
            result = analyze_food_image(image)
            st.session_state.scanner_result = result

# Render the scan result outside the analyze button so logging works cleanly
if 'scanner_result' in st.session_state and st.session_state.scanner_result:
    result = st.session_state.scanner_result
    
    if "error" in result and result.get('error'):
        st.error(f"Error: {result['error']}")
    else:
        st.markdown(f"<h2 style='text-align: center; color: #34d399; margin: 30px 0 20px 0;'>Detected: {result.get('food_name', 'Unknown')}</h2>", unsafe_allow_html=True)
        
        cals = safe_int(result.get('calories', 0))
        macros = result.get('macros', {})
        prot = safe_int(macros.get('protein', 0))
        carb = safe_int(macros.get('carbs', 0))
        fats = safe_int(macros.get('fats', 0))
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            render_metric_card("Calories", f"{cals}", "kcal", "#FF5722", "🔥")
        with col2:
            render_metric_card("Protein", f"{prot}", "g", "#3B82F6", "🥩")
        with col3:
            render_metric_card("Carbs", f"{carb}", "g", "#F59E0B", "🍞")
        with col4:
            render_metric_card("Fats", f"{fats}", "g", "#EC4899", "🥑")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_i1, col_i2 = st.columns(2)
        with col_i1:
            if 'health_score' in result:
                try:
                    score = safe_int(result['health_score'])
                    color = "#10b981" if score > 75 else "#f59e0b" if score > 40 else "#ef4444"
                    st.markdown(f"""
                    <div class="snap-card" style="border-top: 3px solid {color}; height: 100%;">
                        <h4 style="color: #94a3b8; text-transform: uppercase; font-size: 0.9rem;">Health Score</h4>
                        <div style="font-size: 2.5rem; font-weight: 800; color: {color};">{score}<span style="font-size: 1.2rem; color: #94a3b8;">/100</span></div>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception:
                    pass
        
        with col_i2:
            if 'warnings' in result and result['warnings']:
                warnings_text = ', '.join(str(w) for w in result['warnings'])
                st.markdown(f"""
                <div class="snap-card" style="border-top: 3px solid #ef4444; height: 100%;">
                    <h4 style="color: #94a3b8; text-transform: uppercase; font-size: 0.9rem;">Warnings ⚠️</h4>
                    <p style="color: #fca5a5; font-size: 1rem;">{warnings_text}</p>
                </div>
                """, unsafe_allow_html=True)
        
        if 'alternatives' in result and result['alternatives']:
            alts_text = ', '.join(str(a) for a in result['alternatives'])
            st.markdown(f"""
            <div class="snap-card" style="border-top: 3px solid #3b82f6; margin-top: 20px;">
                <h4 style="color: #94a3b8; text-transform: uppercase; font-size: 0.9rem;">Healthier Alternatives 💡</h4>
                <p style="color: #bfdbfe; font-size: 1rem;">{alts_text}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_btn1, col_btn2 = st.columns([2, 1])
        with col_btn1:
            if st.button("✅ Log to Daily Progress", key="log_btn", use_container_width=True, type="primary"):
                log = st.session_state.daily_log
                log['calories'] += cals
                log['protein'] += prot
                log['carbs'] += carb
                log['fats'] += fats
                update_daily_log(log)
                st.session_state.daily_log = log
                st.session_state.scanner_result = None
                st.success("Successfully logged to today's goals! Check your Dashboard.")
                st.rerun()
        with col_btn2:
            if st.button("🔄 Clear Result", key="clear_scan_btn", use_container_width=True):
                st.session_state.scanner_result = None
                st.rerun()
