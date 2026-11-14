import streamlit as st
import sys, os

st.set_page_config(page_title="Family Dashboard | SnapDiet", layout="wide")

try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
except Exception:
    pass

from utils.sidebar import render_sidebar
from utils.ui_theme import render_hero, render_metric_card
from utils.db import get_family_members, add_family_member, update_family_member_stats, delete_family_member
from utils.ai_engine import distribute_family_meal


render_sidebar()

if st.session_state.get('user_profile') is None:
    st.switch_page("app.py")

render_hero("Family Dashboard 👨‍👩‍👧‍👦", "Track and manage nutrition for your entire family in one place.")

# Load from DB
st.session_state.family_members = get_family_members()

with st.expander("➕ Add Family Member"):
    with st.form("add_member"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name")
            relation = st.selectbox("Relation", ["Self", "Mother", "Father", "Spouse", "Child", "Sibling", "Other"])
            age = st.number_input("Age", 5, 100, 30)
        with col2:
            sex = st.selectbox("Sex", ["Male", "Female"])
            weight = st.number_input("Weight (kg)", 20, 150, 60)
            activity = st.selectbox("Activity Level", ["Sedentary", "Active"])
        
        if st.form_submit_button("Add Member", use_container_width=True):
            new_member = {
                "name": name, "relation": relation, "age": age, "sex": sex, "weight": weight, "activity": activity,
                "stats": {"calories": 0, "protein": 0, "carbs": 0, "fats": 0}
            }
            add_family_member(new_member)
            st.success(f"Added {name}!")
            st.rerun()

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<h3 style='margin-bottom: 5px;'>Single-Tap Group Logging</h3>", unsafe_allow_html=True)
st.markdown("<p style='color: #94a3b8; margin-bottom: 20px;'>Log a family meal and our AI will distribute the calories and macros based on each member's profile.</p>", unsafe_allow_html=True)

col_g1, col_g2 = st.columns([3, 1])
with col_g1:
    meal_desc = st.text_input("", placeholder="e.g., Cooked Paneer and Roti for 4 people", label_visibility="collapsed")
with col_g2:
    if st.button("🚀 Distribute & Log Meal", use_container_width=True):
        if not st.session_state.family_members:
            st.warning("Add family members first!")
        elif not meal_desc:
            st.warning("Enter a meal description.")
        else:
            with st.spinner("Distributing with AI..."):
                distribution = distribute_family_meal(meal_desc, st.session_state.family_members)
                
                if "error" in distribution and distribution["error"]:
                     st.error("Error distributing meal.")
                else:
                     for person, data in distribution.items():
                         if person == "error": continue
                         
                         # Find member and update stats in DB
                         for member in st.session_state.family_members:
                             if member["name"] == person:
                                 stats = member.get("stats", {"calories": 0, "protein": 0, "carbs": 0, "fats": 0})
                                 safe_int = lambda v: int(''.join(filter(str.isdigit, str(v))) or 0) if v else 0
                                 stats["calories"] += safe_int(data.get('calories', 0))
                                 m = data.get('macros', {})
                                 stats["protein"] += safe_int(m.get('protein', 0))
                                 stats["carbs"] += safe_int(m.get('carbs', 0))
                                 stats["fats"] += safe_int(m.get('fats', 0))
                                 update_family_member_stats(member['id'], stats)
                     
                     st.success("Meal successfully distributed and logged for all members!")
                     st.rerun()

st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 30px 0;'>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Manage Family", "🏆 Social Leaderboard"])

with tab1:
    st.markdown("<h3>Family Member Reports</h3>", unsafe_allow_html=True)
    
    if not st.session_state.family_members:
        st.info("No members added yet. Add members to see their reports here.")
    else:
        for m in st.session_state.family_members:
            stats = m.get("stats", {"calories": 0, "protein": 0, "carbs": 0, "fats": 0})
                
            st.markdown(f"<h3 style='margin-top: 15px;'>{m['name']} <span style='font-size: 1rem; color: #94a3b8; font-weight: normal;'>({m.get('relation', 'N/A')}, {m.get('age')} yrs)</span></h3>", unsafe_allow_html=True)
            
            col1, col2, col3, col4, col5 = st.columns([1,1,1,1, 0.5])
            with col1:
                render_metric_card("Calories", f"{int(stats['calories'])}", "kcal", "#FF5722", "🔥")
            with col2:
                render_metric_card("Protein", f"{int(stats['protein'])}", "g", "#3B82F6", "🥩")
            with col3:
                render_metric_card("Carbs", f"{int(stats['carbs'])}", "g", "#F59E0B", "🍞")
            with col4:
                render_metric_card("Fats", f"{int(stats['fats'])}", "g", "#EC4899", "🥑")
            with col5:
                st.markdown("<br><br>", unsafe_allow_html=True)
                if st.button("🗑️ Delete", key=f"del_{m['id']}", use_container_width=True):
                    delete_family_member(m['id'])
                    st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)

with tab2:
    st.markdown("<h3>Weekly Family Leaderboard</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8;'>Scores are based on logged nutrition and streak consistency.</p>", unsafe_allow_html=True)
    
    if not st.session_state.family_members:
        st.info("Add family members to see the leaderboard!")
    else:
        # Calculate scores
        leaderboard_data = []
        for m in st.session_state.family_members:
            stats = m.get("stats", {"calories": 0, "protein": 0})
            score = (stats.get('calories', 0) * 0.1) + (stats.get('protein', 0) * 2)
            leaderboard_data.append({"name": m['name'], "score": int(score)})
            
        leaderboard_data = sorted(leaderboard_data, key=lambda x: x["score"], reverse=True)
        
        for i, data in enumerate(leaderboard_data):
            if i == 0: medal, color = "🥇", "linear-gradient(90deg, #F59E0B, #fbbf24)"
            elif i == 1: medal, color = "🥈", "linear-gradient(90deg, #94a3b8, #cbd5e1)"
            elif i == 2: medal, color = "🥉", "linear-gradient(90deg, #b45309, #d97706)"
            else: medal, color = f"{i+1}.", "rgba(255,255,255,0.1)"
            
            st.markdown(f"""
            <div style='background: {color if i < 3 else "rgba(255,255,255,0.05)"}; 
                        border-radius: 12px; padding: 15px 20px; margin-bottom: 10px;
                        display: flex; justify-content: space-between; align-items: center;
                        color: {"#000" if i < 3 else "#fff"}; font-weight: bold;'>
                <div style='font-size: 1.2rem;'>
                    <span style='margin-right: 15px; font-size: 1.5rem;'>{medal}</span>
                    {data['name']}
                </div>
                <div style='font-size: 1.2rem;'>
                    {data['score']} pts
                </div>
            </div>
            """, unsafe_allow_html=True)
