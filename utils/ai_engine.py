import os
import json
import time
import streamlit as st
from google import genai
from google.genai import types
# --- Optional compatibility patch for AQ Auth Keys ---
try:
    import google.genai._api_client
    if hasattr(google.genai._api_client, 'ApiClient') and hasattr(google.genai._api_client.ApiClient, 'request'):
        original_request = google.genai._api_client.ApiClient.request
        def patched_request(self, http_method: str, path: str, request_dict, http_options=None):
            if hasattr(self, 'api_key') and self.api_key and self.api_key.startswith('AQ.'):
                if '?' in path:
                    path += f'&key={self.api_key}'
                else:
                    path += f'?key={self.api_key}'
                if http_options and 'headers' in http_options and 'x-goog-api-key' in http_options['headers']:
                    del http_options['headers']['x-goog-api-key']
            return original_request(self, http_method, path, request_dict, http_options)
        google.genai._api_client.ApiClient.request = patched_request
except Exception:
    pass
# ----------------------------------------------------

@st.cache_resource
def get_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        try:
            if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
                api_key = st.secrets["GEMINI_API_KEY"]
                os.environ["GEMINI_API_KEY"] = api_key
        except Exception:
            pass
    if api_key:
        return genai.Client(api_key=api_key)
    return None

def analyze_food_image(image_bytes):
    client = get_client()
    if not client:
        return {
            "food_name": "Paneer Tikka (Mock)",
            "portion": "1 plate (250g)",
            "calories": 450,
            "macros": {"protein": 25, "carbs": 10, "fats": 35},
            "health_score": 85,
            "warnings": ["Moderate sodium"],
            "alternatives": ["Tofu Tikka for lower fat"]
        }
    
    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=[
                image_bytes,
                "Analyze this food image. Identify the Indian food, estimate portion size, calories, and macros. For packaged food, provide a health score, warnings, and alternatives. Return strictly as JSON with keys: food_name, portion, calories, macros (dict with protein, carbs, fats), health_score, warnings (list), alternatives (list)."
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e), "food_name": "Unknown", "calories": 0, "macros": {"protein":0, "carbs":0, "fats":0}}

def analyze_food_text(meal_desc):
    client = get_client()
    if not client:
        return {
            "food_name": "Mock " + meal_desc,
            "calories": 300,
            "macros": {"protein": 10, "carbs": 40, "fats": 10}
        }
    
    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=f"Analyze this meal description: '{meal_desc}'. Estimate the calories and macros for an Indian diet. Return strictly as JSON with keys: 'food_name' (string), 'calories' (integer), 'macros' (dict with 'protein', 'carbs', 'fats' as integers without 'g' suffix).",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e), "food_name": "Unknown", "calories": 0, "macros": {"protein":0, "carbs":0, "fats":0}}

def generate_meal_plan(budget, ingredients=None):
    client = get_client()
    if not client:
        if ingredients:
            return f"**Mock Recipe with {ingredients}**\n\n1. Chop all the {ingredients} you have.\n2. Sauté with Indian spices (jeera, haldi, garam masala).\n3. Serve hot with roti or rice. Enjoy your quick leftover meal!"
        return f"**Mock Meal Plan for ₹{budget}**\n- Dal (₹15, 12g Protein)\n- 3 Roti (₹10, 8g Protein)\n- Curd (₹10, 5g Protein)\nTotal: ₹35, 25g Protein."
    
    if ingredients:
        prompt = f"I have these ingredients at home: {ingredients}. Generate a healthy, easy-to-cook Indian recipe using them, keeping the budget low."
    else:
        prompt = f"Create a highly nutritious, cheap local Indian meal plan for a daily budget of ₹{budget}."
        
    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Error generating plan: {e}"

def distribute_family_meal(meal_desc, members):
    client = get_client()
    if not client:
        return {m['name']: {"portion": "1 serving", "calories": 300, "macros": {"protein": 10, "carbs": 40, "fats": 10}} for m in members}
        
    prompt = f"Distribute this meal: '{meal_desc}' among {len(members)} family members. Members: {json.dumps(members)}. Based on their caloric needs, output a JSON with each member's name as key and a dict with 'portion' (string), 'calories' (integer), and 'macros' (dict with protein, carbs, fats as integers without 'g')."
    
    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        return json.loads(response.text)
    except Exception as e:
        return {"error": str(e)}

def nutribot_chat(history, new_message):
    client = get_client()
    if not client:
        yield "I am the mock Nutri-Bot! Your AI assistant is offline because the Gemini API key is missing. Please add it in the sidebar."
        return
        
    contents = [{"role": "user" if msg["role"] == "user" else "model", "parts": [{"text": msg["content"]}]} for msg in history]
    contents.append({"role": "user", "parts": [{"text": new_message}]})
    
    try:
        response_stream = client.models.generate_content_stream(
            model='gemini-3.6-flash',
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction="You are SnapDiet's Nutri-Bot, an expert Indian nutritionist. Be concise, empathetic, and focus on local, budget-friendly Indian diets.",
            )
        )
        for chunk in response_stream:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        yield f"Error: {e}"

def generate_custom_diet_plan(profile):
    client = get_client()
    if not client:
        # Mock structured plan
        return [
            {"meal": "Breakfast", "food": "Poha with peanuts and a glass of milk", "calories": 350, "protein": 12, "carbs": 50, "fats": 10},
            {"meal": "Lunch", "food": "2 Roti, Dal, Sabzi, and Curd", "calories": 600, "protein": 20, "carbs": 80, "fats": 20},
            {"meal": "Snack", "food": "Roasted Makhana and Tea", "calories": 150, "protein": 5, "carbs": 20, "fats": 5},
            {"meal": "Dinner", "food": "Khichdi with Ghee", "calories": 400, "protein": 12, "carbs": 60, "fats": 12}
        ]
        
    workout_prompt = f"The user does this type of workout: {profile.get('workout_type', 'None')}. Adjust the macros and meal timing accordingly (e.g., higher protein for weightlifting, higher carbs for cardio)."
    prompt = f"Create a daily Indian diet plan for a user with these stats: {json.dumps(profile)}. The total calories should be exactly {profile.get('target_calories')} kcal. {workout_prompt} Make this plan entirely unique and distinct from previous plans (Seed: {time.time()}). Return a JSON array of objects. Each object represents a meal with keys: 'meal' (e.g., Breakfast, Lunch, Snack, Dinner), 'food' (name of the dish), 'calories' (int), 'protein' (int in grams), 'carbs' (int in grams), 'fats' (int in grams). Ensure it is purely a JSON array."
    
    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error generating diet plan: {e}")
        return []

def generate_workout_plan(profile):
    client = get_client()
    workout_type = profile.get('workout_type', 'None')
    if not client:
        return [
            {"day": "Monday", "focus": "Full Body Basics", "exercises": "Pushups (3x10), Squats (3x15), Plank (30s)", "duration": "20 mins"},
            {"day": "Tuesday", "focus": "Cardio", "exercises": "Brisk walking or light jogging", "duration": "30 mins"},
            {"day": "Wednesday", "focus": "Core & Flexibility", "exercises": "Crunches (3x15), Stretching", "duration": "15 mins"},
            {"day": "Thursday", "focus": "Active Recovery", "exercises": "Light Yoga or Walking", "duration": "20 mins"},
            {"day": "Friday", "focus": "Lower Body", "exercises": "Lunges (3x12), Glute Bridges (3x15)", "duration": "25 mins"},
            {"day": "Saturday", "focus": "Upper Body", "exercises": "Dumbbell rows or Pullups, Pushups", "duration": "25 mins"},
            {"day": "Sunday", "focus": "Rest", "exercises": "Total Rest", "duration": "0 mins"}
        ]
        
    prompt = f"Create a 7-day workout routine for someone whose preferred workout style is '{workout_type}', age {profile.get('age')}, and weight {profile.get('weight')}kg. Ensure this routine has a fresh, unique variety of exercises different from standard recommendations (Seed: {time.time()}). Return a JSON array of objects. Each object represents a day with keys: 'day' (Monday, Tuesday...), 'focus' (e.g. Upper Body, Cardio), 'exercises' (comma separated list of exercises with sets/reps if applicable), 'duration' (e.g. '30 mins'). Ensure it is purely a JSON array."
    
    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error generating workout plan: {e}")
        return []
