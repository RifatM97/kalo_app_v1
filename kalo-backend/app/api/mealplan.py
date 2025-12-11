"""
Meal Plan API Routes - /api/mealplan
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import Optional

from app.db.database import get_db
from app.models.models import MealPlan, MealPlanDay, User
from app.api.users import get_current_user
from app.ai.meal_planner import MealPlanGenerator

router = APIRouter()

class MealPlanResponse(BaseModel):
    id: str
    start_date: str
    end_date: str
    status: str

class GenerateMealPlanRequest(BaseModel):
    daily_calories: int
    macro_targets: dict
    diet_type: str = "balanced"
    restrictions: Optional[list[str]] = None

@router.get("/", response_model=Optional[MealPlanResponse])
async def get_current_meal_plan(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current active meal plan"""
    result = await db.execute(
        select(MealPlan)
        .where(MealPlan.user_id == user.id)
        .where(MealPlan.status == "active")
    )
    return result.scalar_one_or_none()

@router.post("/generate", response_model=dict)
async def generate_meal_plan(
    req: GenerateMealPlanRequest,
    user: User = Depends(get_current_user),
):
    """Generate AI meal plan"""
    result = await MealPlanGenerator.generate_meal_plan(
        daily_calories=req.daily_calories,
        macro_targets=req.macro_targets,
        diet_type=req.diet_type,
        restrictions=req.restrictions or []
    )
    return result

@router.get("/history")
async def get_meal_plan_history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all meal plans for user"""
    result = await db.execute(
        select(MealPlan).where(MealPlan.user_id == user.id)
    )
    return result.scalars().all()
