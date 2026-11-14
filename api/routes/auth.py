from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from utils.db import get_user_profile_by_mobile, save_user_profile

router = APIRouter()

class LoginRequest(BaseModel):
    mobile: str

class ProfileCreate(BaseModel):
    name: str
    mobile: str
    age: int
    sex: str
    height: float
    weight: float
    target_weight: float
    activity_level: str
    diet_pref: str
    budget: float
    workout_type: str

@router.post("/login")
def login(req: LoginRequest):
    profile = get_user_profile_by_mobile(req.mobile)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"message": "Login successful", "profile": profile}

@router.post("/register")
def register(profile: ProfileCreate):
    # Calculate BMR, TDEE
    prof_dict = profile.model_dump()
    
    if prof_dict['sex'] == 'Male':
        bmr = 10 * prof_dict['weight'] + 6.25 * prof_dict['height'] - 5 * prof_dict['age'] + 5
    else:
        bmr = 10 * prof_dict['weight'] + 6.25 * prof_dict['height'] - 5 * prof_dict['age'] - 161
    
    activity_multipliers = {
        'Sedentary': 1.2,
        'Lightly active': 1.375,
        'Moderately active': 1.55,
        'Very active': 1.725,
        'Super active': 1.9
    }
    tdee = bmr * activity_multipliers.get(prof_dict['activity_level'], 1.2)
    
    if prof_dict['target_weight'] < prof_dict['weight']: target_calories = tdee - 500
    elif prof_dict['target_weight'] > prof_dict['weight']: target_calories = tdee + 500
    else: target_calories = tdee
    
    macros = {
        'protein': (target_calories * 0.3) / 4,
        'carbs': (target_calories * 0.4) / 4,
        'fats': (target_calories * 0.3) / 9
    }
    prof_dict['tdee'] = tdee
    prof_dict['target_calories'] = target_calories
    prof_dict['macros'] = macros
    
    save_user_profile(prof_dict)
    return {"message": "Profile created successfully", "profile": prof_dict}
