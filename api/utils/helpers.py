"""
SnapDiet - Core Calculation & State Management Helpers
Calculates BMR, TDEE, Macros, Nutrition Scores, and handles multi-page session state.
"""

import streamlit as st
import datetime
import os

# Activity level multipliers
ACTIVITY_MULTIPLIERS = {
    "Sedentary (Desk job, little/no exercise)": 1.2,
    "Light (1-2 days light exercise/week)": 1.375,
    "Moderate (3-5 days moderate workout/week)": 1.55,
    "Very Active (6-7 days intense exercise/week)": 1.725,
    "Super Active (Athlete / Physical labor)": 1.9
}

# Goal calorie offsets
GOAL_CALORIE_OFFSETS = {
    "Weight Loss & Fat Reduction (-500 kcal)": -500,
    "Gradual Weight Loss (-300 kcal)": -300,
    "Maintain Healthy Weight & Tone (0 kcal)": 0,
    "Muscle Building & Weight Gain (+350 kcal)": 350,
    "High-Performance Athletic Fuel (+500 kcal)": 500
}

def calculate_bmr(sex: str, weight_kg: float, height_cm: float, age: int) -> float:
    """
    Calculate Basal Metabolic Rate using the clinically validated Mifflin-St Jeor Equation.
    Men: BMR = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    Women: BMR = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
    """
    try:
        weight_kg = float(weight_kg)
        height_cm = float(height_cm)
        age = int(age)
        
        base = (10.0 * weight_kg) + (6.25 * height_cm) - (5.0 * age)
        if sex.lower().startswith("m"):
            return round(base + 5.0, 1)
        else:
            return round(base - 161.0, 1)
    except Exception:
        return 1600.0

def calculate_tdee(bmr: float, activity_level: str) -> float:
    """Calculate Total Daily Energy Expenditure (TDEE)."""
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.375)
    return round(bmr * multiplier, 1)

def calculate_target_macros(tdee: float, goal: str, weight_kg: float) -> dict:
    """
    Compute daily caloric target and balanced Indian macronutrient split (Protein, Carbs, Fats).
    Protein is aligned with ICMR & sports nutrition guidelines (1.4g - 1.8g/kg for active goals).
    """
    offset = GOAL_CALORIE_OFFSETS.get(goal, 0)
    target_calories = max(1200, round(tdee + offset))
    
    if "Muscle" in goal:
        # High Protein: 1.8g/kg
        protein_g = round(min(weight_kg * 1.8, (target_calories * 0.30) / 4))
        fat_cals = target_calories * 0.25
        fat_g = round(fat_cals / 9)
        carb_cals = target_calories - (protein_g * 4) - fat_cals
        carb_g = round(carb_cals / 4)
    elif "Loss" in goal:
        # Calorie deficit with muscle preservation: 1.5g/kg
        protein_g = round(min(weight_kg * 1.6, (target_calories * 0.28) / 4))
        fat_cals = target_calories * 0.25
        fat_g = round(fat_cals / 9)
        carb_cals = target_calories - (protein_g * 4) - fat_cals
        carb_g = round(carb_cals / 4)
    else:
        # Balanced maintenance Indian split
        protein_g = round(min(weight_kg * 1.2, (target_calories * 0.22) / 4))
        fat_cals = target_calories * 0.28
        fat_g = round(fat_cals / 9)
        carb_cals = target_calories - (protein_g * 4) - fat_cals
        carb_g = round(carb_cals / 4)
        
    return {
        "target_calories": target_calories,
        "target_protein": max(45, protein_g),
        "target_carbs": max(80, carb_g),
        "target_fats": max(30, fat_g),
        "water_target_ml": round(weight_kg * 35)  # 35ml per kg bodyweight
    }

def calculate_nutrition_score(daily_logs: dict, targets: dict) -> dict:
    """
    Universal Nutrition Score (0-100) dynamically calculated based on:
    - Calorie adherence: 30 pts
    - Protein target fulfillment: 30 pts
    - Hydration progress: 20 pts
    - Whole food / fresh meal variety: 20 pts
    """
    cal_consumed = daily_logs.get("calories_consumed", 0)
    cal_target = targets.get("target_calories", 2000)
    
    prot_consumed = daily_logs.get("protein_consumed", 0)
    prot_target = targets.get("target_protein", 100)
    
    water_ml = daily_logs.get("water_ml", 0)
    water_target = targets.get("water_target_ml", 3000)
    
    # 1. Calorie adherence (30 pts)
    if cal_target > 0:
        cal_ratio = cal_consumed / cal_target
        if 0.85 <= cal_ratio <= 1.10:
            cal_score = 30
        elif 0.70 <= cal_ratio < 0.85 or 1.10 < cal_ratio <= 1.25:
            cal_score = 22
        elif 0.50 <= cal_ratio < 0.70 or 1.25 < cal_ratio <= 1.45:
            cal_score = 14
        else:
            cal_score = max(5, int(30 * min(cal_ratio, 1.0)))
    else:
        cal_score = 15

    # 2. Protein target (30 pts)
    if prot_target > 0:
        prot_ratio = prot_consumed / prot_target
        prot_score = min(30, int(prot_ratio * 30))
    else:
        prot_score = 15
        
    # 3. Water goal (20 pts)
    if water_target > 0:
        water_ratio = water_ml / water_target
        water_score = min(20, int(water_ratio * 20))
    else:
        water_score = 10
        
    # 4. Variety & whole foods (20 pts)
    meal_count = len(daily_logs.get("logged_meals", []))
    variety_score = min(20, meal_count * 7)

    total_score = min(100, cal_score + prot_score + water_score + variety_score)
    
    if total_score >= 90:
        grade = "A+ (Optimal Nutrition & Balance)"
        verdict = "Excellent! Your Indian thali balance meets ideal ICMR-NIN recommendations."
        badge_color = "#10B981"
    elif total_score >= 75:
        grade = "A (Very Good Balance)"
        verdict = "Great progress! Consider topping up a bit more protein or water."
        badge_color = "#3B82F6"
    elif total_score >= 60:
        grade = "B (Moderate Balance)"
        verdict = "Decent start. Watch out for excess carbs and log your evening hydration."
        badge_color = "#F59E0B"
    else:
        grade = "C (Needs Attention)"
        verdict = "Under-fueled or low logged meals. Scan your meals to boost your score!"
        badge_color = "#EF4444"
        
    return {
        "score": total_score,
        "grade": grade,
        "verdict": verdict,
        "badge_color": badge_color,
        "breakdown": {
            "Calories Adherence": f"{cal_score}/30 pts",
            "Protein Intake": f"{prot_score}/30 pts",
            "Hydration": f"{water_score}/20 pts",
            "Meal Regularity": f"{variety_score}/20 pts"
        }
    }

def get_preset_profiles() -> dict:
    """Pre-configured profiles for quick demo and competition judging testing."""
    return {
        "🎓 College Hosteller (Budget ₹80/Day)": {
            "name": "Rohan Verma",
            "age": 21,
            "sex": "Male",
            "height_cm": 174,
            "weight_kg": 69.0,
            "target_weight_kg": 65.0,
            "activity_level": "Moderate (3-5 days moderate workout/week)",
            "goal": "Weight Loss & Fat Reduction (-500 kcal)",
            "diet_preference": "North Indian Vegetarian",
            "daily_budget_inr": 80,
            "notes": "Hostel student relying on mess food, sattu, eggs, and local fruit."
        },
        "👩‍👧 Family Homemaker & Caregiver": {
            "name": "Priya Sharma",
            "age": 42,
            "sex": "Female",
            "height_cm": 160,
            "weight_kg": 66.0,
            "target_weight_kg": 59.0,
            "activity_level": "Light (1-2 days light exercise/week)",
            "goal": "Weight Loss & Fat Reduction (-500 kcal)",
            "diet_preference": "Pan-Indian / Vegetarian + Egg",
            "daily_budget_inr": 150,
            "notes": "Manages meals for a family of 4. Focus on diabetic care for elders & high protein for kids."
        },
        "🏋️ Working Fitness Professional": {
            "name": "Vikram Sen",
            "age": 28,
            "sex": "Male",
            "height_cm": 180,
            "weight_kg": 78.0,
            "target_weight_kg": 82.0,
            "activity_level": "Very Active (6-7 days intense exercise/week)",
            "goal": "Muscle Building & Weight Gain (+350 kcal)",
            "diet_preference": "High-Protein Indian Non-Veg / Eggetarian",
            "daily_budget_inr": 200,
            "notes": "Focused on lean bulking with soya chunks, chicken, paneer, and sprouted lentils."
        },
        "🌿 South Indian Healthy Living": {
            "name": "Deepa Sundaram",
            "age": 34,
            "sex": "Female",
            "height_cm": 165,
            "weight_kg": 62.0,
            "target_weight_kg": 58.0,
            "activity_level": "Moderate (3-5 days moderate workout/week)",
            "goal": "Maintain Healthy Weight & Tone (0 kcal)",
            "diet_preference": "South Indian Traditional (Millet & Dal focus)",
            "daily_budget_inr": 110,
            "notes": "Prefers ragi mudde, sambar with veggies, curd, and sundal."
        }
    }

def init_session_state():
    """Initialize all required session state keys with robust defaults."""
    
    # 1. API Configuration
    if "gemini_api_key" not in st.session_state or not st.session_state.gemini_api_key:
        api_val = os.getenv("GEMINI_API_KEY", "")
        if not api_val and hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            api_val = st.secrets["GEMINI_API_KEY"]
        st.session_state.gemini_api_key = api_val
    if "GEMINI_API_KEY" not in os.environ or not os.environ["GEMINI_API_KEY"]:
        if st.session_state.gemini_api_key:
            os.environ["GEMINI_API_KEY"] = st.session_state.gemini_api_key
        
    # 2. User Profile
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = {
            "name": "Aarav Sharma",
            "age": 24,
            "sex": "Male",
            "height_cm": 175,
            "weight_kg": 72.0,
            "target_weight_kg": 68.0,
            "activity_level": "Moderate (3-5 days moderate workout/week)",
            "goal": "Weight Loss & Fat Reduction (-500 kcal)",
            "diet_preference": "North Indian Vegetarian",
            "daily_budget_inr": 120,
            "bmr": 1700.0,
            "tdee": 2635.0,
            "target_calories": 2135,
            "target_protein": 115,
            "target_carbs": 240,
            "target_fats": 58,
            "water_target_ml": 2500,
            "is_onboarded": True
        }
        
    # 3. Daily Logs
    if "daily_logs" not in st.session_state:
        st.session_state.daily_logs = {
            "date": str(datetime.date.today()),
            "calories_consumed": 1320,
            "protein_consumed": 68.5,
            "carbs_consumed": 164.0,
            "fats_consumed": 42.0,
            "water_ml": 2000,
            "logged_meals": [
                {
                    "id": "meal_1",
                    "time": "08:30 AM",
                    "type": "Breakfast",
                    "name": "Poha with Roasted Peanuts & Sprouts",
                    "portion": "1 medium plate (200g)",
                    "calories": 340,
                    "protein": 9.8,
                    "carbs": 56.0,
                    "fats": 8.5,
                    "cost_inr": 18,
                    "health_score": 88
                },
                {
                    "id": "meal_2",
                    "time": "01:30 PM",
                    "type": "Lunch",
                    "name": "Dal Tadka with 2 Phulkas & Green Salad",
                    "portion": "1 bowl dal (200g), 2 rotis, cucumber salad",
                    "calories": 420,
                    "protein": 16.5,
                    "carbs": 64.0,
                    "fats": 10.2,
                    "cost_inr": 35,
                    "health_score": 92
                },
                {
                    "id": "meal_3",
                    "time": "05:00 PM",
                    "type": "Snack",
                    "name": "Sprouted Moong & Chana Chaat + Lemon Water",
                    "portion": "1 big bowl (200g)",
                    "calories": 260,
                    "protein": 17.2,
                    "carbs": 44.0,
                    "fats": 2.3,
                    "cost_inr": 20,
                    "health_score": 98
                }
            ]
        }
        
    # 4. Family Members
    if "family_members" not in st.session_state:
        st.session_state.family_members = [
            {
                "id": "fam_self",
                "name": "Aarav (Self)",
                "relation": "Self",
                "age": 24,
                "sex": "Male",
                "weight_kg": 72.0,
                "height_cm": 175,
                "target_calories": 2135,
                "target_protein": 115,
                "water_target_ml": 2500,
                "today_calories": 1320,
                "today_protein": 68.5,
                "today_water_ml": 2000,
                "health_tags": ["Fitness Target", "Active"],
                "alert": None
            },
            {
                "id": "fam_mom",
                "name": "Sunita (Mom)",
                "relation": "Mother",
                "age": 52,
                "sex": "Female",
                "weight_kg": 64.0,
                "height_cm": 158,
                "target_calories": 1550,
                "target_protein": 65,
                "water_target_ml": 2200,
                "today_calories": 850,
                "today_protein": 28.0,
                "today_water_ml": 1250,
                "health_tags": ["Diabetic Friendly", "Low GI"],
                "alert": "⚠️ Low Protein Alert (28g/65g target). Add Paneer/Sattu to dinner."
            },
            {
                "id": "fam_dad",
                "name": "Rajesh (Dad)",
                "relation": "Father",
                "age": 56,
                "sex": "Male",
                "weight_kg": 76.0,
                "height_cm": 172,
                "target_calories": 1800,
                "target_protein": 75,
                "water_target_ml": 2600,
                "today_calories": 1100,
                "today_protein": 52.0,
                "today_water_ml": 1400,
                "health_tags": ["Heart Care", "Low Sodium"],
                "alert": "💧 Hydration Reminder: Only 1.4L consumed today."
            },
            {
                "id": "fam_sis",
                "name": "Ananya (Sister)",
                "relation": "Sister",
                "age": 19,
                "sex": "Female",
                "weight_kg": 54.0,
                "height_cm": 163,
                "target_calories": 1750,
                "target_protein": 70,
                "water_target_ml": 2200,
                "today_calories": 1420,
                "today_protein": 62.0,
                "today_water_ml": 2100,
                "health_tags": ["College Athlete", "High Energy"],
                "alert": None
            }
        ]
        
    # 5. 90-Day Transformation State
    if "transformation_data" not in st.session_state:
        st.session_state.transformation_data = {
            "start_date": str(datetime.date.today() - datetime.timedelta(days=18)),
            "current_day": 18,
            "start_weight": 76.2,
            "current_weight": 72.0,
            "target_weight": 68.0,
            "phase": "Phase 1: Foundation & Gut Reset (Days 1–30)",
            "weight_history": [
                {"day": 1, "date": "Day 1", "weight": 76.2, "nutrition_score": 72},
                {"day": 4, "date": "Day 4", "weight": 75.6, "nutrition_score": 80},
                {"day": 8, "date": "Day 8", "weight": 74.8, "nutrition_score": 85},
                {"day": 12, "date": "Day 12", "weight": 73.9, "nutrition_score": 89},
                {"day": 15, "date": "Day 15", "weight": 73.0, "nutrition_score": 92},
                {"day": 18, "date": "Today (Day 18)", "weight": 72.0, "nutrition_score": 94}
            ],
            "unlocked_badges": [
                {"name": "🔥 7-Day Sugar Cleanse", "desc": "Zero refined sweets for 7 days", "icon": "🌿"},
                {"name": "🥗 Thali Alchemist", "desc": "Mastered 50% fiber/veg plate balance", "icon": "🏆"},
                {"name": "💧 Hydration Hero", "desc": "Hit 3L daily water goal 5 times", "icon": "🌊"},
                {"name": "🇮🇳 NSS Nutrition Champion", "desc": "Completed National Nutrition Week Awareness", "icon": "🏅"}
            ],
            "daily_habits": {
                "salad_first": True,
                "water_3L": False,
                "no_sugary_drinks": True,
                "protein_each_meal": True,
                "walk_8k": False
            }
        }
        
    # 6. Nutribot Chat History
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {
                "role": "assistant",
                "content": (
                    "Namaste! 🙏 I am **Nutri-Bot**, your dedicated Indian AI Nutritionist & Health Coach for **National Nutrition Week 2026**.\n\n"
                    "Whether you need budget-friendly Indian protein hacks (like Sattu & Soya), regional meal balance advice, or diabetic-friendly substitutions, I'm here to help!\n\n"
                    "Try asking me:\n"
                    "- *'How can I get 70g protein in a ₹50 daily vegetarian budget?'*\n"
                    "- *'Is white rice safe for fat loss in Indian meals?'*\n"
                    "- *'What is a balanced South Indian millet thali?'*"
                )
            }
        ]
        
    # 7. Quiz State
    if "quiz_state" not in st.session_state:
        st.session_state.quiz_state = {
            "submitted": False,
            "user_answers": {},
            "score": 0,
            "total": 3
        }
        
    # 8. Streaks & Gamification
    if "streak_days" not in st.session_state:
        st.session_state.streak_days = 12
