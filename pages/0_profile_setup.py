import streamlit as st
import sys, os

try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
except Exception:
    pass

from utils.sidebar import render_sidebar
from utils.ui_theme import render_hero
from utils.db import save_user_profile

st.set_page_config(page_title="Profile & Settings | SnapDiet", page_icon="👤", layout="wide")

if 'user_profile' not in st.session_state or not st.session_state.user_profile:
    st.switch_page("app.py")

profile = st.session_state.user_profile
is_completed = bool(profile.get('is_profile_completed', False))

render_sidebar()

def calculate_bmr_tdee(prof):
    weight = float(prof.get('weight', 70))
    height = float(prof.get('height', 170))
    age = int(prof.get('age', 25))
    sex = prof.get('sex', 'Male')
    activity = prof.get('activity_level', 'Lightly active')

    if sex == 'Male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    activity_multipliers = {
        'Sedentary': 1.2,
        'Lightly active': 1.375,
        'Moderately active': 1.55,
        'Very active': 1.725,
        'Super active': 1.9
    }
    tdee = bmr * activity_multipliers.get(activity, 1.2)
    return bmr, tdee

# Top Header with quick link to Dashboard if profile is already complete
col_h1, col_h2 = st.columns([4, 1])
with col_h1:
    if is_completed:
        render_hero("My Profile & Settings 👤", "View and edit your personal information, dietary preferences, and fitness goals.")
    else:
        render_hero("Complete Your Profile 📝", "We need a few details to tailor your custom nutrition and fitness ecosystem.")
with col_h2:
    if is_completed:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📊 Go to Dashboard", use_container_width=True):
            st.switch_page("pages/1_dashboard.py")

# Safely extract existing values
sex_options = ["Male", "Female", "Other"]
current_sex = profile.get('sex', 'Male')
sex_index = sex_options.index(current_sex) if current_sex in sex_options else 0

activity_options = ["Sedentary", "Lightly active", "Moderately active", "Very active", "Super active"]
current_act = profile.get('activity_level', 'Lightly active')
act_index = activity_options.index(current_act) if current_act in activity_options else 1

diet_options = ["North Indian", "South Indian", "East Indian", "West Indian", "Mixed"]
current_diet = profile.get('diet_pref', 'North Indian')
diet_index = diet_options.index(current_diet) if current_diet in diet_options else 0

workout_options = ["None", "Cardio / Running", "Weightlifting / Gym", "Yoga / Pilates", "HIIT / Crossfit"]
current_workout = profile.get('workout_type', 'Cardio / Running')
workout_index = workout_options.index(current_workout) if current_workout in workout_options else 1

with st.form("editable_profile_form"):
    st.markdown("<h3 style='margin-bottom: 15px;'>Account Details</h3>", unsafe_allow_html=True)
    c_acc1, c_acc2 = st.columns(2)
    with c_acc1:
        name = st.text_input("Full Name", value=str(profile.get('name', '')))
    with c_acc2:
        mobile = st.text_input("Mobile Number", value=str(profile.get('mobile', '')))

    st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 20px 0;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-bottom: 15px;'>Physical & Lifestyle Metrics</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", min_value=10, max_value=120, value=int(profile.get('age', 25)))
        sex = st.selectbox("Sex", sex_options, index=sex_index)
        
        height_unit = st.radio("Height Unit", ["cm", "feet/inches"], horizontal=True)
        current_h_cm = float(profile.get('height', 170.0))
        if height_unit == "cm":
            height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=current_h_cm)
        else:
            default_feet = max(2, min(8, int(current_h_cm / 30.48)))
            rem_inches = max(0, min(11, round((current_h_cm % 30.48) / 2.54)))
            h_col1, h_col2 = st.columns(2)
            with h_col1:
                feet = st.number_input("Feet", min_value=2, max_value=8, value=default_feet)
            with h_col2:
                inches = st.number_input("Inches", min_value=0, max_value=11, value=rem_inches)
            height = (feet * 30.48) + (inches * 2.54)
            
    with col2:
        weight = st.number_input("Current Weight (kg)", min_value=30.0, max_value=200.0, value=float(profile.get('weight', 70.0)))
        target_weight = st.number_input("Target Weight (kg)", min_value=30.0, max_value=200.0, value=float(profile.get('target_weight', 65.0)))
        activity_level = st.selectbox("Activity Level", activity_options, index=act_index)
        diet_pref = st.selectbox("Regional Diet Preference", diet_options, index=diet_index)
        budget = st.number_input("Daily Food Budget (₹)", min_value=50, max_value=2000, value=int(profile.get('budget', 200)))
        workout_type = st.selectbox("Preferred Workout Type", workout_options, index=workout_index)
    
    st.markdown("<br>", unsafe_allow_html=True)
    submit_label = "💾 Save & Update Profile" if is_completed else "🚀 Complete Setup & Go to Dashboard"
    submitted = st.form_submit_button(submit_label, use_container_width=True, type="primary")
    
    if submitted:
        updated_data = profile.copy()
        updated_data.update({
            'name': name.strip() or profile.get('name', 'User'),
            'mobile': mobile.strip() or profile.get('mobile', ''),
            'age': age,
            'sex': sex,
            'height': height,
            'weight': weight,
            'target_weight': target_weight,
            'activity_level': activity_level,
            'diet_pref': diet_pref,
            'budget': budget,
            'workout_type': workout_type,
            'is_profile_completed': True
        })
        
        bmr, tdee = calculate_bmr_tdee(updated_data)
        if target_weight < weight:
            target_calories = tdee - 500
        elif target_weight > weight:
            target_calories = tdee + 500
        else:
            target_calories = tdee
        
        macros = {
            'protein': round((target_calories * 0.3) / 4),
            'carbs': round((target_calories * 0.4) / 4),
            'fats': round((target_calories * 0.3) / 9)
        }
        
        updated_data['tdee'] = round(tdee)
        updated_data['target_calories'] = round(target_calories)
        updated_data['macros'] = macros
        
        # Save to DB and update Session State
        saved = save_user_profile(updated_data)
        st.session_state.user_profile = saved
        
        if is_completed:
            st.success("✅ Profile updated successfully! All targets and metrics have been recalculated.")
            st.rerun()
        else:
            st.success("🎉 Profile setup complete! Taking you to your dashboard...")
            st.switch_page("pages/1_dashboard.py")
