"""
Users API Routes - /api/users
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import Optional, Dict, List
import jwt

from app.db.database import get_db
from app.models.models import User, UserPreferences
from app.config import settings

router = APIRouter()

# ==================
# Schemas
# ==================

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    avatar_url: Optional[str]
    bio: Optional[str]
    fitness_goals: dict
    dietary_restrictions: list

    class Config:
        from_attributes = True

class UserPreferencesResponse(BaseModel):
    daily_calorie_goal: int
    macro_targets: dict
    units: str

    class Config:
        from_attributes = True

class UpdateProfileRequest(BaseModel):
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    fitness_goals: Optional[Dict] = None
    dietary_restrictions: Optional[List] = None

class UpdatePreferencesRequest(BaseModel):
    daily_calorie_goal: Optional[int] = None
    macro_targets: Optional[Dict] = None
    units: Optional[str] = None

# ==================
# Dependency: Get current user
# ==================

async def get_current_user(
    authorization: str = None,
    db: AsyncSession = Depends(get_db)
) -> User:
    """Extract user from JWT token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    
    token = authorization.split(" ")[1]
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        user_id = payload.get("sub")
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# ==================
# Routes
# ==================

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(user: User = Depends(get_current_user)):
    """Get current user profile"""
    return user

@router.put("/me", response_model=UserResponse)
async def update_profile(
    req: UpdateProfileRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user profile"""
    
    if req.username:
        user.username = req.username
    if req.avatar_url:
        user.avatar_url = req.avatar_url
    if req.bio:
        user.bio = req.bio
    if req.fitness_goals:
        user.fitness_goals = req.fitness_goals
    if req.dietary_restrictions:
        user.dietary_restrictions = req.dietary_restrictions
    
    await db.commit()
    await db.refresh(user)
    
    return user

@router.get("/me/preferences", response_model=UserPreferencesResponse)
async def get_preferences(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user preferences"""
    
    if not user.preferences:
        # Create default preferences
        prefs = UserPreferences(user_id=user.id)
        db.add(prefs)
        await db.commit()
        await db.refresh(prefs)
        return prefs
    
    return user.preferences

@router.put("/me/preferences")
async def update_preferences(
    req: UpdatePreferencesRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user preferences"""
    
    if not user.preferences:
        prefs = UserPreferences(user_id=user.id)
        db.add(prefs)
    else:
        prefs = user.preferences
    
    if req.daily_calorie_goal:
        prefs.daily_calorie_goal = req.daily_calorie_goal
    if req.macro_targets:
        prefs.macro_targets = req.macro_targets
    if req.units:
        prefs.units = req.units
    
    await db.commit()
    await db.refresh(prefs)
    
    return prefs

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get user profile by ID"""
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user
