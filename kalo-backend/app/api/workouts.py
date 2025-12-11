"""
Workouts API Routes - /api/workouts
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import Optional

from app.db.database import get_db
from app.models.models import Workout, WorkoutPlan, User
from app.api.users import get_current_user
from app.ai.workout_generator import WorkoutPlanGenerator

router = APIRouter()

class ExerciseSchema(BaseModel):
    name: str
    sets: int
    reps: int
    weight: Optional[str] = None

class WorkoutResponse(BaseModel):
    id: str
    type: str
    name: str
    duration: int
    calories_burned: Optional[int]

class CreateWorkoutRequest(BaseModel):
    type: str
    name: str
    duration: int
    exercises: list[ExerciseSchema]
    calories_burned: Optional[int] = None

class GenerateWorkoutPlanRequest(BaseModel):
    goal: str
    level: str
    frequency: int
    equipment: list[str]
    duration_weeks: int = 12

@router.post("/", response_model=WorkoutResponse)
async def log_workout(
    req: CreateWorkoutRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Log completed workout"""
    workout = Workout(
        user_id=user.id,
        type=req.type,
        name=req.name,
        duration=req.duration,
        exercises=[ex.model_dump() for ex in req.exercises],
        calories_burned=req.calories_burned
    )
    db.add(workout)
    await db.commit()
    await db.refresh(workout)
    return workout

@router.get("/", response_model=list[WorkoutResponse])
async def get_workouts(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get workout history"""
    result = await db.execute(
        select(Workout).where(Workout.user_id == user.id)
    )
    return result.scalars().all()

@router.post("/generate", response_model=dict)
async def generate_workout_plan(
    req: GenerateWorkoutPlanRequest,
    user: User = Depends(get_current_user),
):
    """Generate AI workout plan"""
    result = await WorkoutPlanGenerator.generate_workout_plan(
        goal=req.goal,
        level=req.level,
        frequency=req.frequency,
        equipment=req.equipment,
        duration_weeks=req.duration_weeks
    )
    return result
