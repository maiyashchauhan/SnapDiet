from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Any
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from utils.db import get_daily_log, update_daily_log, update_user_diet_plan

router = APIRouter()

class DailyLogUpdate(BaseModel):
    calories: float = 0
    protein: float = 0
    carbs: float = 0
    fats: float = 0
    water: float = 0

@router.get("/daily_log")
def get_log():
    return get_daily_log()

@router.post("/daily_log")
def update_log(log_update: DailyLogUpdate):
    current = get_daily_log()
    current['calories'] += log_update.calories
    current['protein'] += log_update.protein
    current['carbs'] += log_update.carbs
    current['fats'] += log_update.fats
    current['water'] += log_update.water
    update_daily_log(current)
    return {"message": "Log updated", "log": current}
    
@router.post("/update_plan")
def save_plan(plan: List[Any]):
    update_user_diet_plan(plan)
    return {"message": "Diet plan saved"}
