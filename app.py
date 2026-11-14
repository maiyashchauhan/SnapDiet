import streamlit as st
st.set_page_config(page_title="SnapDiet | Premium Nutrition", page_icon="🍏", layout="wide")
import sys, os
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
except:
    pass

import streamlit as st
import pandas as pd

# Check for Gemini API key in environment or Streamlit secrets
if "GEMINI_API_KEY" not in os.environ or not os.environ["GEMINI_API_KEY"]:
    try:
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

from utils.sidebar import render_sidebar
from utils.ui_theme import render_hero
from utils.db import init_db, get_user_profile_by_mobile, save_user_profile, get_daily_log, clear_chat_history



# Initialize database
init_db()

# Auto-redirect if already logged in
if 'user_profile' in st.session_state and st.session_state.user_profile is not None:
    if st.session_state.user_profile.get('is_profile_completed', False):
        st.switch_page("pages/1_dashboard.py")
    else:
        st.switch_page("pages/0_profile_setup.py")

render_sidebar()

if 'splash_shown' not in st.session_state:
    st.session_state.splash_shown = True
    st.markdown("""
    <style>
        @keyframes fadeOut {
            0% { opacity: 1; visibility: visible; }
            75% { opacity: 1; visibility: visible; }
            100% { opacity: 0; visibility: hidden; }
        }
        @keyframes scaleUp {
            0% { transform: scale(0.8); opacity: 0; filter: blur(10px); }
            50% { transform: scale(1.05); opacity: 1; filter: blur(0px); }
            100% { transform: scale(1); opacity: 1; filter: blur(0px); }
        }
        .splash-screen {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: #0f172a;
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 999999;
            animation: fadeOut 3.5s forwards cubic-bezier(0.4, 0, 0.2, 1);
            pointer-events: none;
        }
        .splash-text {
            font-size: 5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: scaleUp 1.8s ease-out forwards;
            font-family: 'Plus Jakarta Sans', sans-serif;
            text-align: center;
            letter-spacing: -2px;
        }
    </style>
    <div class="splash-screen">
        <div class="splash-text">SnapDiet</div>
    </div>
    """, unsafe_allow_html=True)

def calculate_bmr_tdee(profile):
    if profile['sex'] == 'Male':
        bmr = 10 * profile['weight'] + 6.25 * profile['height'] - 5 * profile['age'] + 5
    else:
        bmr = 10 * profile['weight'] + 6.25 * profile['height'] - 5 * profile['age'] - 161
    
    activity_multipliers = {
        'Sedentary': 1.2,
        'Lightly active': 1.375,
        'Moderately active': 1.55,
        'Very active': 1.725,
        'Super active': 1.9
    }
    tdee = bmr * activity_multipliers.get(profile['activity_level'], 1.2)
    return bmr, tdee

render_hero("Welcome to SnapDiet 🍏", "Your AI-driven Premium Nutrition Ecosystem")

tab1, tab2 = st.tabs(["Log In", "Sign Up"])

with tab1:
    with st.form("login_form"):
        st.markdown("<h3 style='margin-bottom: 20px;'>Welcome Back</h3>", unsafe_allow_html=True)
        login_mobile = st.text_input("Enter your Mobile Number to Log In")
        submitted_login = st.form_submit_button("Log In", use_container_width=True)
        
        if submitted_login and login_mobile:
            profile = get_user_profile_by_mobile(login_mobile)
            if profile:
                st.session_state.user_profile = profile
                st.session_state.daily_log = get_daily_log()
                clear_chat_history()
                st.session_state.chat_history = []
                st.success(f"Welcome back, {profile['name']}!")
                if profile.get('is_profile_completed', False):
                    st.switch_page("pages/1_dashboard.py")
                else:
                    st.switch_page("pages/0_profile_setup.py")
            else:
                st.error("Profile not found. Please sign up first or check your spelling.")

with tab2:
    with st.form("signup_form"):
        st.markdown("<h3 style='margin-bottom: 20px;'>Create your account</h3>", unsafe_allow_html=True)
        name = st.text_input("Name")
        mobile = st.text_input("Mobile Number")
        
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Sign Up", use_container_width=True)
        
        if submitted and name and mobile:
            # Create a partial profile with safe defaults
            profile = {
                'name': name, 
                'mobile': mobile, 
                'is_profile_completed': False,
                'target_calories': 2000,
                'tdee': 2000,
                'macros': {'protein': 150, 'carbs': 200, 'fats': 65},
                'weight': 70,
                'target_weight': 70,
                'height': 170,
                'age': 25,
                'sex': 'Male',
                'activity_level': 'Lightly active'
            }
            
            # Save to DB and Session State
            saved_profile = save_user_profile(profile)
            st.session_state.user_profile = saved_profile
            st.session_state.daily_log = get_daily_log()
            clear_chat_history()
            st.session_state.chat_history = []
            
            st.success("Account created! Let's set up your profile...")
            st.switch_page("pages/0_profile_setup.py")
