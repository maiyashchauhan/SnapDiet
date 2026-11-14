from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from utils.ai_engine import generate_custom_diet_plan, generate_workout_plan, nutribot_chat

router = APIRouter()

class ProfileRequest(BaseModel):
    profile: Dict[str, Any]

class ChatRequest(BaseModel):
    history: List[Dict[str, str]]
    new_message: str

@router.post("/generate_diet_plan")
def get_diet_plan(req: ProfileRequest):
    plan = generate_custom_diet_plan(req.profile)
    return {"plan": plan}

@router.post("/generate_workout_plan")
def get_workout_plan(req: ProfileRequest):
    plan = generate_workout_plan(req.profile)
    return {"plan": plan}

@router.post("/chat")
def chat(req: ChatRequest):
    response_text = ""
    for chunk in nutribot_chat(req.history, req.new_message):
        response_text += chunk
    return {"response": response_text}
