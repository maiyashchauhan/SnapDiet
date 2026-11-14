import streamlit as st
import sys, os

st.set_page_config(page_title="Diet Planner | SnapDiet", layout="wide")

try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
except Exception:
    pass

from utils.sidebar import render_sidebar
from utils.ui_theme import render_hero, render_metric_card
from utils.db import get_user_profile, update_user_diet_plan
from utils.ai_engine import generate_custom_diet_plan, generate_meal_plan


render_sidebar()

if st.session_state.get('user_profile') is None:
    st.switch_page("app.py")

profile = st.session_state.user_profile

render_hero("AI Diet & Budget Planner 🥗", "Your personalized, AI-generated meal plans and budget tools.")

tab1, tab2, tab3 = st.tabs(["My Custom Diet Plan", "Budget Meals", "Leftover Magic"])

with tab1:
    st.markdown("<h3 style='color: white; margin-bottom: 5px;'>Your Daily Nutrition Plan</h3>", unsafe_allow_html=True)
    
    if profile.get('is_profile_completed', False):
        st.markdown(f"<p style='color: #94a3b8; margin-bottom: 20px;'>Target: {int(profile.get('target_calories', 2000))} kcal | Preference: {profile.get('diet_pref', 'Mixed')}</p>", unsafe_allow_html=True)
        
        col_g1, col_g2 = st.columns([1, 4])
        with col_g1:
            if st.button("✨ Generate New Plan", use_container_width=True):
                with st.spinner("Our AI Nutritionist is crafting your plan..."):
                    new_plan = generate_custom_diet_plan(profile)
                    if new_plan:
                        update_user_diet_plan(new_plan, user_id=profile.get('id'))
                        profile['diet_plan'] = new_plan
                        st.session_state.user_profile = profile
                        st.success("Plan generated and saved!")
                        st.rerun()
                    else:
                        st.error("Could not generate a plan. Please try again.")
        
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 20px 0;'>", unsafe_allow_html=True)
        
        diet_plan = profile.get('diet_plan')
        if not diet_plan:
            st.info("You don't have a generated diet plan yet. Click the button above to generate one!")
        else:
            for meal in diet_plan:
                st.markdown(f"""
                <div class="snap-card" style="margin-bottom: 15px; border-left: 4px solid #3b82f6;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <h3 style="margin: 0; color: #60a5fa;">{meal.get('meal', 'Meal')}</h3>
                        <div style="background: rgba(255, 87, 34, 0.2); color: #FF5722; padding: 4px 12px; border-radius: 20px; font-weight: bold;">
                            🔥 {meal.get('calories', 0)} kcal
                        </div>
                    </div>
                    <p style="font-size: 1.1rem; color: #f8fafc; font-weight: 500; margin-bottom: 15px;">{meal.get('food', 'Food Name')}</p>
                    <div style="display: flex; gap: 15px;">
                        <div style="color: #94a3b8; font-size: 0.9rem;">🥩 Protein: <strong style="color: #3b82f6;">{meal.get('protein', 0)}g</strong></div>
                        <div style="color: #94a3b8; font-size: 0.9rem;">🍞 Carbs: <strong style="color: #f59e0b;">{meal.get('carbs', 0)}g</strong></div>
                        <div style="color: #94a3b8; font-size: 0.9rem;">🥑 Fats: <strong style="color: #ec4899;">{meal.get('fats', 0)}g</strong></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("We need your body metrics (Weight, Height, Activity) to generate an accurate custom diet plan!")
        if st.button("📝 Complete Profile to Generate Plan", key="diet_complete"):
            st.switch_page("pages/0_profile_setup.py")

with tab2:
    st.markdown("<h3 style='color: white; margin-bottom: 15px;'>Maximize Nutrition within Budget</h3>", unsafe_allow_html=True)
    budget = st.number_input("Enter meal budget (₹)", min_value=10, max_value=1000, value=50)
    if st.button("Suggest Meals", key="budget_btn"):
        with st.spinner("Generating..."):
            plan = generate_meal_plan(budget)
            st.markdown(f"<div class='snap-card'>{plan}</div>", unsafe_allow_html=True)

with tab3:
    st.markdown("<h3 style='color: white; margin-bottom: 15px;'>Leftover Magic</h3>", unsafe_allow_html=True)
    ingredients = st.text_area("What ingredients do you have at home?")
    if st.button("Generate Recipe", key="recipe_btn"):
        with st.spinner("Cooking up ideas..."):
            recipe = generate_meal_plan(budget=0, ingredients=ingredients)
            st.markdown(f"<div class='snap-card'>{recipe}</div>", unsafe_allow_html=True)
