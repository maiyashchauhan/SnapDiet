import streamlit as st
import sys, os
import plotly.graph_objects as go
import pandas as pd
import datetime
from fpdf import FPDF
import base64
import tempfile

st.set_page_config(page_title="Dashboard | SnapDiet", layout="wide")

try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
except Exception:
    pass

from utils.sidebar import render_sidebar
from utils.ui_theme import render_hero, render_metric_card, render_nutrition_score_card, create_macro_donut_chart
from utils.db import get_daily_log, update_daily_log
from utils.ai_engine import analyze_food_text

render_sidebar()

if st.session_state.get('user_profile') is None:
    st.switch_page("app.py")

profile = st.session_state.user_profile

# Ensure we have the latest daily log from the DB
st.session_state.daily_log = get_daily_log()
log = st.session_state.daily_log

# Safely compute BMI and Body Metrics globally so tab2 never crashes
weight = float(profile.get('weight') or 70.0)
height = float(profile.get('height') or 170.0)
target_weight = float(profile.get('target_weight') or 70.0)
bmi = weight / ((height / 100.0) ** 2) if height > 0 else 22.0
bmi_category = "Underweight" if bmi < 18.5 else "Normal" if bmi < 25 else "Overweight" if bmi < 30 else "Obese"
bmi_color = "#3B82F6" if bmi_category == "Normal" else "#F59E0B" if bmi_category == "Overweight" else "#EF4444"

col_d1, col_d2 = st.columns([5, 1])
with col_d1:
    render_hero("Central Health Dashboard 📊", "Your personalized macro overview and weekly progress.")
with col_d2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⚙️ Edit Profile", use_container_width=True):
        st.switch_page("pages/0_profile_setup.py")

tab1, tab2 = st.tabs(["Today's Overview", "Weekly Report"])

with tab1:
    target_cals = profile.get('target_calories') or 2000
    macros = profile.get('macros') or {'protein': 150, 'carbs': 200, 'fats': 65}
    score = min(100, int((log['calories'] / max(1, target_cals)) * 100))
    grade = "A" if score > 80 else "B" if score > 60 else "C"
    
    render_nutrition_score_card({
        "score": score,
        "grade": grade,
        "verdict": "You are on track with your daily goals for National Nutrition Week.",
        "badge_color": "#10b981" if grade == "A" else "#f59e0b"
    })
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("Calories", f"{int(log['calories'])} kcal", f"Goal: {int(target_cals)}", "#FF5722", "🔥")
    with col2:
        render_metric_card("Protein", f"{int(log['protein'])} g", f"Goal: {int(macros.get('protein', 150))}", "#3B82F6", "🥩")
    with col3:
        render_metric_card("Carbs", f"{int(log['carbs'])} g", f"Goal: {int(macros.get('carbs', 200))}", "#F59E0B", "🍞")
    with col4:
        render_metric_card("Fats", f"{int(log['fats'])} g", f"Goal: {int(macros.get('fats', 65))}", "#EC4899", "🥑")

    st.markdown("<br>", unsafe_allow_html=True)
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown("<h3 style='color: white; margin-bottom: 15px;'>Your Macro Breakdown</h3>", unsafe_allow_html=True)
        fig_donut = create_macro_donut_chart(
            log['calories'], target_cals,
            log['protein'], macros.get('protein', 150),
            log['carbs'], macros.get('carbs', 200),
            log['fats'], macros.get('fats', 65)
        )
        st.plotly_chart(fig_donut, use_container_width=True)
        
    with col_p2:
        st.markdown("<h3 style='color: white; margin-bottom: 15px;'>Target Macro Ratio</h3>", unsafe_allow_html=True)
        labels = ['Protein', 'Carbs', 'Fats']
        t_values = [macros.get('protein', 150), macros.get('carbs', 200), macros.get('fats', 65)]
        fig_tgt = go.Figure(data=[go.Pie(labels=labels, values=t_values, hole=.65, marker_colors=['#3B82F6', '#F59E0B', '#EC4899'], textinfo='label+percent')])
        fig_tgt.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"), height=350, margin=dict(t=30, b=10, l=10, r=10))
        st.plotly_chart(fig_tgt, use_container_width=True)

    st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='color: white; margin-bottom: 15px;'>Quick Meal Logger 📝</h3>", unsafe_allow_html=True)
    with st.form("quick_log_form", clear_on_submit=True):
        col_m1, col_m2 = st.columns([4, 1])
        with col_m1:
            meal_desc = st.text_input("What did you eat?", placeholder="e.g., 2 rotis and a bowl of dal in the morning")
        with col_m2:
            st.markdown("<br>", unsafe_allow_html=True)
            submit_meal = st.form_submit_button("Log Meal", use_container_width=True)
            
        if submit_meal and meal_desc:
            with st.spinner("Analyzing with AI..."):
                result = analyze_food_text(meal_desc)
                if "error" in result and result["error"]:
                    st.error("Error analyzing meal.")
                else:
                    safe_int = lambda v: int(''.join(filter(str.isdigit, str(v))) or 0) if v else 0
                    cals = safe_int(result.get('calories', 0))
                    m = result.get('macros', {})
                    prot = safe_int(m.get('protein', 0))
                    carb = safe_int(m.get('carbs', 0))
                    fats = safe_int(m.get('fats', 0))
                    
                    log['calories'] += cals
                    log['protein'] += prot
                    log['carbs'] += carb
                    log['fats'] += fats
                    update_daily_log(log)
                    st.session_state.daily_log = log
                    st.success(f"Added: {result.get('food_name', 'Meal')} ({cals} kcal, {prot}g Protein)")
                    st.rerun()

    st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    
    if profile.get('is_profile_completed', False):
        st.markdown("<h3 style='color: white; margin-bottom: 15px;'>Smart Hydration 💧</h3>", unsafe_allow_html=True)
        target_water = (profile.get('weight') or 70) * 35 # 35ml per kg
        
        col_w1, col_w2 = st.columns([1, 3])
        with col_w1:
            if st.button("🚰 Add 250ml Glass", use_container_width=True):
                log['water'] += 250
                update_daily_log(log)
                st.session_state.daily_log = log
                st.rerun()
        with col_w2:
            st.progress(min(1.0, log['water'] / target_water))
            st.markdown(f"<div style='text-align: right; color: #94a3b8; font-weight: 600; margin-top: 5px;'>{log['water']} ml / {int(target_water)} ml Goal</div>", unsafe_allow_html=True)
            
            # Intelligent timeline text
            if log['water'] == 0:
                st.markdown("<div style='color: #F59E0B; font-size: 0.9rem;'>You haven't drank any water today! Start hydrating.</div>", unsafe_allow_html=True)
            elif log['water'] < target_water * 0.4:
                st.markdown("<div style='color: #F59E0B; font-size: 0.9rem;'>You are falling behind on your water goal. Time for a glass!</div>", unsafe_allow_html=True)
            elif log['water'] >= target_water:
                st.markdown("<div style='color: #10B981; font-size: 0.9rem;'>Hydration goal met! Great job.</div>", unsafe_allow_html=True)

        st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
        
        st.markdown("<h3 style='color: white; margin-bottom: 15px;'>Your Body Metrics</h3>", unsafe_allow_html=True)
        
        bmi = (profile.get('weight') or 70) / (((profile.get('height') or 170) / 100) ** 2)
        bmi_category = "Underweight" if bmi < 18.5 else "Normal" if bmi < 25 else "Overweight" if bmi < 30 else "Obese"
        bmi_color = "#3B82F6" if bmi_category == "Normal" else "#F59E0B" if bmi_category == "Overweight" else "#EF4444"
        
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            render_metric_card("BMI", f"{bmi:.1f}", bmi_category, bmi_color, "⚖️")
        with col_b2:
            render_metric_card("Weight", f"{(profile.get('weight') or 70)} kg", f"Target: {(profile.get('target_weight') or 70)} kg", "#EC4899", "⚖️")
    else:
        st.info("Unlock personalized Smart Hydration and Body Metrics by completing your profile!")
        if st.button("📝 Complete Profile", key="metrics_complete"):
            st.switch_page("pages/0_profile_setup.py")

    st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='color: white; margin-bottom: 15px;'>Gamification & Streaks</h3>", unsafe_allow_html=True)
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        render_metric_card("Current Streak", "5 Days! 🔥", "You're on fire! Keep logging.", "#F59E0B", "🏅")
    with col_g2:
        render_metric_card("Next Milestone", "Nutrition Ninja ⭐", "Log 2 more meals.", "#3B82F6", "🎯")

with tab2:
    st.markdown("<h3 style='color: white; margin-bottom: 15px;'>Your Weekly AI Report</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="alert-card">
        💡 <strong>AI Insight:</strong> You are doing great on protein, but slightly under your calorie goal. Try adding some almonds or walnuts to your snacks for healthy fats and energy!
    </div>
    """, unsafe_allow_html=True)
    
    dates = [(datetime.date.today() - datetime.timedelta(days=i)).strftime("%a") for i in range(6, -1, -1)]
    cal_data = [target_cals * 0.9, target_cals * 1.1, target_cals * 0.8, target_cals * 0.95, target_cals * 1.05, target_cals * 0.9, log['calories']]
    
    df = pd.DataFrame({
        "Day": dates,
        "Calories Consumed": cal_data,
        "Target Calories": [target_cals] * 7
    })
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["Day"], y=df["Calories Consumed"], name="Consumed", marker_color="#3B82F6", opacity=0.8, marker_line_width=0))
    fig.add_trace(go.Scatter(x=df["Day"], y=df["Target Calories"], name="Target", mode="lines", line=dict(color="#10B981", width=3, dash="dash")))
    fig.update_layout(
        title="Weekly Caloric Intake vs Target", 
        xaxis_title="Day", 
        yaxis_title="Calories", 
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)", 
        font=dict(color="white"),
        hovermode="x unified",
        margin=dict(t=50, b=20, l=20, r=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # --- PDF EXPORT ---
    st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 20px 0;'>", unsafe_allow_html=True)
    if st.button("📄 Generate Weekly PDF Report", use_container_width=True, type="primary"):
        with st.spinner("Generating PDF..."):
            pdf = FPDF()
            pdf.add_page()
            
            # Header
            pdf.set_font("Helvetica", style="B", size=24)
            pdf.set_text_color(16, 185, 129) # Emerald
            pdf.cell(200, 15, txt="SnapDiet Weekly Nutrition Report", ln=True, align="C")
            
            # Subtitle
            pdf.set_font("Helvetica", style="I", size=14)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(200, 10, txt=f"Report for: {profile['name']}  |  Date: {datetime.date.today()}", ln=True, align="C")
            pdf.ln(10)
            
            # Metrics
            pdf.set_font("Helvetica", style="B", size=16)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(200, 10, txt="Your Body Metrics", ln=True)
            pdf.set_font("Helvetica", size=12)
            pdf.cell(200, 8, txt=f"- Weight: {weight} kg (Target: {target_weight} kg)", ln=True)
            pdf.cell(200, 8, txt=f"- BMI: {bmi:.1f} ({bmi_category})", ln=True)
            pdf.cell(200, 8, txt=f"- Activity Level: {profile.get('activity_level', 'Moderate')}", ln=True)
            pdf.cell(200, 8, txt=f"- Workout Type: {profile.get('workout_type', 'None')}", ln=True)
            pdf.ln(10)
            
            # Goals
            pdf_target_cals = int(profile.get('target_calories') or 2000)
            pdf_macros = profile.get('macros') or {'protein': 150, 'carbs': 200, 'fats': 65}
            pdf.set_font("Helvetica", style="B", size=16)
            pdf.cell(200, 10, txt="Daily Targets", ln=True)
            pdf.set_font("Helvetica", size=12)
            pdf.cell(200, 8, txt=f"- Calories: {pdf_target_cals} kcal", ln=True)
            pdf.cell(200, 8, txt=f"- Protein: {int(pdf_macros.get('protein', 150))} g", ln=True)
            pdf.cell(200, 8, txt=f"- Carbs: {int(pdf_macros.get('carbs', 200))} g", ln=True)
            pdf.cell(200, 8, txt=f"- Fats: {int(pdf_macros.get('fats', 65))} g", ln=True)
            pdf.ln(10)
            
            # AI Insight
            pdf.set_font("Helvetica", style="B", size=16)
            pdf.set_text_color(59, 130, 246)
            pdf.cell(200, 10, txt="AI Nutritional Insight", ln=True)
            pdf.set_font("Helvetica", style="I", size=12)
            pdf.set_text_color(50, 50, 50)
            pdf.multi_cell(0, 8, txt="You are doing great on protein, but slightly under your calorie goal. Try adding some almonds or walnuts to your snacks for healthy fats and energy!")
            
            # Save and Download
            pdf_path = os.path.join(tempfile.gettempdir(), "snapdiet_report.pdf")
            pdf.output(pdf_path)
            
            with open(pdf_path, "rb") as pdf_file:
                PDFbyte = pdf_file.read()
                
            st.download_button(
                label="📥 Download PDF",
                data=PDFbyte,
                file_name="SnapDiet_Weekly_Report.pdf",
                mime="application/octet-stream",
                use_container_width=True
            )
