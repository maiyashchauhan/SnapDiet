import sys, os
current_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.dirname(current_dir))
sys.path.insert(0, os.path.join(os.path.dirname(current_dir), 'utils'))
sys.path.insert(0, os.path.dirname(os.path.dirname(current_dir)))

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

try:
    from utils.db import get_user_profile_by_mobile, save_user_profile
except ModuleNotFoundError:
    try:
        from db import get_user_profile_by_mobile, save_user_profile
    except ModuleNotFoundError:
        from api.utils.db import get_user_profile_by_mobile, save_user_profile

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
    
    prof_dict['target_calories'] = tdee - 500
    prof_dict['tdee'] = tdee
    
    macros = {
        'protein': (prof_dict['target_calories'] * 0.3) / 4,
        'carbs': (prof_dict['target_calories'] * 0.4) / 4,
        'fats': (prof_dict['target_calories'] * 0.3) / 9
    }
    prof_dict['macros'] = macros
    prof_dict['diet_plan'] = []
    
    user_id = save_user_profile(prof_dict)
    prof_dict['id'] = user_id
    return {"message": "User registered successfully", "profile": prof_dict}
