"""
Runs API Routes - /api/runs (GPS tracking & activity)
Complete implementation with start, update, finish, summary, and heatmap.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import math

from app.db.database import get_db
from app.models.models import Run, RunSession, User
from app.api.users import get_current_user

router = APIRouter()

# =====================
# SCHEMAS / PYDANTIC MODELS
# =====================

class GPSPoint(BaseModel):
    lat: float
    lng: float
    timestamp: Optional[str] = None  # ISO8601

class StartRunRequest(BaseModel):
    """Start a new run session"""
    pass

class StartRunResponse(BaseModel):
    session_id: str
    started_at: str
    message: str

class UpdateRunRequest(BaseModel):
    """Update an active run session with live data"""
    current_distance_m: float
    route_points: Optional[List[GPSPoint]] = None

class UpdateRunResponse(BaseModel):
    session_id: str
    current_distance_m: float
    elapsed_seconds: int
    current_pace_s_per_km: Optional[float]
    message: str

class FinishRunRequest(BaseModel):
    """Complete a run session"""
    final_distance_m: float
    final_duration_s: int
    elevation_gain_m: Optional[float] = None
    calories_burned: Optional[int] = None

class RunResponse(BaseModel):
    id: str
    distance_m: float
    duration_s: int
    avg_pace_s_per_km: float
    calories_burned: Optional[int]
    elevation_gain_m: Optional[float]
    started_at: str
    ended_at: str
    route_points: List[dict]

    class Config:
        from_attributes = True

class RunDetailResponse(BaseModel):
    id: str
    distance_m: float
    duration_s: int
    avg_pace_s_per_km: float
    calories_burned: Optional[int]
    elevation_gain_m: Optional[float]
    started_at: str
    ended_at: str
    route_points: List[dict]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

class RunSummaryResponse(BaseModel):
    total_distance_m: float
    total_time_s: int
    number_of_runs: int
    average_pace_s_per_km: float
    total_calories: int
    per_day_breakdown: List[dict]  # [{date, distance_m, time_s, runs_count}, ...]

class HeatmapDayData(BaseModel):
    date: str  # YYYY-MM-DD
    distance_m: float
    time_s: int
    runs_count: int
    intensity: float  # 0-1 for color intensity

class HeatmapResponse(BaseModel):
    period: str  # month, week, year
    data: List[HeatmapDayData]

# =====================
# HELPER FUNCTIONS
# =====================

def calculate_pace(distance_m: float, duration_s: int) -> float:
    """
    Calculate average pace in seconds per km.
    Returns 0 if distance is 0.
    """
    if distance_m <= 0:
        return 0.0
    distance_km = distance_m / 1000
    return duration_s / distance_km if distance_km > 0 else 0.0

def calculate_calories(weight_kg: float, duration_minutes: float, intensity: str = "moderate") -> int:
    """
    Simple calorie burn estimation using MET (Metabolic Equivalent of Task).
    Running: 9.8 MET (moderate pace ~5 min/km)
    """
    met = 9.8  # Running at moderate pace
    calories = met * weight_kg * (duration_minutes / 60)
    return int(calories)

def get_intensity_color(distance_m: float, max_distance: float) -> float:
    """
    Get intensity (0-1) for heatmap based on distance.
    Used for color gradient in calendar view.
    """
    if max_distance == 0:
        return 0.0
    return min(distance_m / max_distance, 1.0)

# =====================
# ENDPOINTS
# =====================

@router.post("/start", response_model=StartRunResponse)
async def start_run(
    req: StartRunRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Start a new run session.
    
    Returns a session_id to use for updates and finishing.
    """
    session = RunSession(
        user_id=user.id,
        started_at=datetime.utcnow(),
        current_distance_m=0.0,
        current_route_points=[]
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    return StartRunResponse(
        session_id=str(session.id),
        started_at=session.started_at.isoformat(),
        message="Run session started. Use this session_id to update and finish."
    )

@router.post("/{session_id}/update", response_model=UpdateRunResponse)
async def update_run(
    session_id: str,
    req: UpdateRunRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an active run session with live data.
    
    Call this periodically (e.g., every 5-10 seconds) during a run.
    Optionally include GPS route points.
    """
    # Fetch the session
    result = await db.execute(
        select(RunSession).where(
            (RunSession.id == session_id) & (RunSession.user_id == user.id)
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Run session not found")
    
    # Update distance and route
    session.current_distance_m = req.current_distance_m
    if req.route_points:
        session.current_route_points = [p.model_dump() for p in req.route_points]
    
    await db.commit()
    await db.refresh(session)
    
    # Calculate elapsed time and current pace
    elapsed = (datetime.utcnow() - session.started_at).total_seconds()
    current_pace = calculate_pace(req.current_distance_m, int(elapsed))
    
    return UpdateRunResponse(
        session_id=str(session.id),
        current_distance_m=req.current_distance_m,
        elapsed_seconds=int(elapsed),
        current_pace_s_per_km=current_pace if current_pace > 0 else None,
        message="Run session updated"
    )

@router.post("/{session_id}/finish", response_model=RunDetailResponse)
async def finish_run(
    session_id: str,
    req: FinishRunRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Complete a run session and save it to history.
    
    Creates a Run record with final stats.
    """
    # Fetch the session
    result = await db.execute(
        select(RunSession).where(
            (RunSession.id == session_id) & (RunSession.user_id == user.id)
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Run session not found")
    
    # Calculate average pace
    avg_pace = calculate_pace(req.final_distance_m, req.final_duration_s)
    
    # Create Run record
    now = datetime.utcnow()
    run = Run(
        user_id=user.id,
        distance_m=req.final_distance_m,
        duration_s=req.final_duration_s,
        avg_pace_s_per_km=avg_pace,
        calories_burned=req.calories_burned,
        elevation_gain_m=req.elevation_gain_m,
        route_points=session.current_route_points,
        started_at=session.started_at,
        ended_at=now,
        created_at=now,
        updated_at=now
    )
    db.add(run)
    
    # Delete the session
    await db.delete(session)
    
    await db.commit()
    await db.refresh(run)
    
    return RunDetailResponse(
        id=str(run.id),
        distance_m=run.distance_m,
        duration_s=run.duration_s,
        avg_pace_s_per_km=run.avg_pace_s_per_km,
        calories_burned=run.calories_burned,
        elevation_gain_m=run.elevation_gain_m,
        started_at=run.started_at.isoformat(),
        ended_at=run.ended_at.isoformat(),
        route_points=run.route_points,
        created_at=run.created_at.isoformat(),
        updated_at=run.updated_at.isoformat()
    )

@router.get("/", response_model=List[RunResponse])
async def get_runs(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    start_date: Optional[str] = None,  # YYYY-MM-DD
    end_date: Optional[str] = None  # YYYY-MM-DD
):
    """
    Get user's run history.
    
    Query parameters:
    - limit: Max number of runs (default 20, max 100)
    - offset: Pagination offset (default 0)
    - start_date: Filter runs from this date (YYYY-MM-DD)
    - end_date: Filter runs until this date (YYYY-MM-DD)
    
    Returns most recent runs first.
    """
    query = select(Run).where(Run.user_id == user.id)
    
    if start_date:
        query = query.where(Run.started_at >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.where(Run.started_at <= datetime.fromisoformat(end_date))
    
    # Order by most recent first
    query = query.order_by(Run.started_at.desc()).limit(limit).offset(offset)
    
    result = await db.execute(query)
    runs = result.scalars().all()
    
    return [
        RunResponse(
            id=str(r.id),
            distance_m=r.distance_m,
            duration_s=r.duration_s,
            avg_pace_s_per_km=r.avg_pace_s_per_km,
            calories_burned=r.calories_burned,
            elevation_gain_m=r.elevation_gain_m,
            started_at=r.started_at.isoformat(),
            ended_at=r.ended_at.isoformat(),
            route_points=r.route_points
        )
        for r in runs
    ]

@router.get("/{run_id}", response_model=RunDetailResponse)
async def get_run_detail(
    run_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed information for a specific run."""
    result = await db.execute(
        select(Run).where((Run.id == run_id) & (Run.user_id == user.id))
    )
    run = result.scalar_one_or_none()
    
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    return RunDetailResponse(
        id=str(run.id),
        distance_m=run.distance_m,
        duration_s=run.duration_s,
        avg_pace_s_per_km=run.avg_pace_s_per_km,
        calories_burned=run.calories_burned,
        elevation_gain_m=run.elevation_gain_m,
        started_at=run.started_at.isoformat(),
        ended_at=run.ended_at.isoformat(),
        route_points=run.route_points,
        created_at=run.created_at.isoformat(),
        updated_at=run.updated_at.isoformat()
    )

@router.get("/summary/stats", response_model=RunSummaryResponse)
async def get_run_summary(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    period: str = Query("week", regex="^(week|month|year)$")
):
    """
    Get aggregated run statistics for a period.
    
    Query parameters:
    - period: "week", "month", or "year" (default: week)
    
    Returns:
    - Total distance, time, number of runs, average pace
    - Per-day breakdown for charting
    """
    now = datetime.utcnow()
    
    if period == "week":
        start = now - timedelta(days=7)
    elif period == "month":
        start = now - timedelta(days=30)
    else:  # year
        start = now - timedelta(days=365)
    
    # Fetch all runs in period
    result = await db.execute(
        select(Run).where(
            (Run.user_id == user.id) & (Run.started_at >= start)
        ).order_by(Run.started_at)
    )
    runs = result.scalars().all()
    
    if not runs:
        return RunSummaryResponse(
            total_distance_m=0.0,
            total_time_s=0,
            number_of_runs=0,
            average_pace_s_per_km=0.0,
            total_calories=0,
            per_day_breakdown=[]
        )
    
    # Aggregate by day
    day_data = {}
    total_distance = 0.0
    total_time = 0
    total_calories = 0
    
    for run in runs:
        day_key = run.started_at.strftime("%Y-%m-%d")
        
        if day_key not in day_data:
            day_data[day_key] = {
                "date": day_key,
                "distance_m": 0.0,
                "time_s": 0,
                "runs_count": 0
            }
        
        day_data[day_key]["distance_m"] += run.distance_m
        day_data[day_key]["time_s"] += run.duration_s
        day_data[day_key]["runs_count"] += 1
        
        total_distance += run.distance_m
        total_time += run.duration_s
        total_calories += run.calories_burned or 0
    
    # Calculate average pace
    avg_pace = calculate_pace(total_distance, total_time) if total_distance > 0 else 0.0
    
    # Fill in missing days with zeros for visualization
    per_day = list(day_data.values())
    
    return RunSummaryResponse(
        total_distance_m=total_distance,
        total_time_s=total_time,
        number_of_runs=len(runs),
        average_pace_s_per_km=avg_pace,
        total_calories=int(total_calories),
        per_day_breakdown=per_day
    )

@router.get("/heatmap/data", response_model=HeatmapResponse)
async def get_run_heatmap(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    period: str = Query("month", regex="^(week|month|year)$")
):
    """
    Get heatmap data for calendar visualization.
    
    Query parameters:
    - period: "week", "month", or "year" (default: month)
    
    Returns:
    - For each date: distance_m, time_s, runs_count, intensity (0-1)
    - Useful for calendar heatmap and activity intensity visualization
    """
    now = datetime.utcnow()
    
    if period == "week":
        start = now - timedelta(days=7)
    elif period == "month":
        start = now - timedelta(days=30)
    else:  # year
        start = now - timedelta(days=365)
    
    # Fetch all runs in period
    result = await db.execute(
        select(Run).where(
            (Run.user_id == user.id) & (Run.started_at >= start)
        ).order_by(Run.started_at)
    )
    runs = result.scalars().all()
    
    # Aggregate by day
    day_data = {}
    max_distance = 0.0
    
    for run in runs:
        day_key = run.started_at.strftime("%Y-%m-%d")
        
        if day_key not in day_data:
            day_data[day_key] = {
                "distance_m": 0.0,
                "time_s": 0,
                "runs_count": 0
            }
        
        day_data[day_key]["distance_m"] += run.distance_m
        day_data[day_key]["time_s"] += run.duration_s
        day_data[day_key]["runs_count"] += 1
        
        max_distance = max(max_distance, day_data[day_key]["distance_m"])
    
    # Create heatmap data with intensity
    heatmap_data = [
        HeatmapDayData(
            date=date,
            distance_m=data["distance_m"],
            time_s=data["time_s"],
            runs_count=data["runs_count"],
            intensity=get_intensity_color(data["distance_m"], max_distance)
        )
        for date, data in sorted(day_data.items())
    ]
    
    # Fill in missing dates for continuous calendar
    current_date = start.date()
    end_date = now.date()
    all_dates = []
    existing_dates = {d.date for d in heatmap_data}
    
    while current_date <= end_date:
        if current_date not in existing_dates:
            all_dates.append(
                HeatmapDayData(
                    date=current_date.isoformat(),
                    distance_m=0.0,
                    time_s=0,
                    runs_count=0,
                    intensity=0.0
                )
            )
        current_date += timedelta(days=1)
    
    heatmap_data.extend(all_dates)
    heatmap_data.sort(key=lambda x: x.date)
    
    return HeatmapResponse(
        period=period,
        data=heatmap_data
    )

@router.get("/stats/all")
async def get_all_run_stats(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive running statistics for the user.
    
    Returns:
    - Total stats (all time)
    - Weekly stats
    - Personal records (fastest pace, longest distance)
    """
    result = await db.execute(
        select(Run).where(Run.user_id == user.id).order_by(Run.started_at.desc())
    )
    runs = result.scalars().all()
    
    if not runs:
        return {
            "total_distance_m": 0.0,
            "total_time_s": 0,
            "total_runs": 0,
            "average_pace_s_per_km": 0.0,
            "average_distance_m": 0.0,
            "personal_records": {
                "fastest_pace_s_per_km": None,
                "longest_distance_m": None,
                "longest_duration_s": None
            }
        }
    
    total_distance = sum(r.distance_m for r in runs)
    total_time = sum(r.duration_s for r in runs)
    total_runs = len(runs)
    avg_pace = calculate_pace(total_distance, total_time)
    avg_distance = total_distance / total_runs if total_runs > 0 else 0.0
    
    # Personal records
    fastest_pace = min(r.avg_pace_s_per_km for r in runs) if runs else None
    longest_distance = max(r.distance_m for r in runs) if runs else None
    longest_duration = max(r.duration_s for r in runs) if runs else None
    
    return {
        "total_distance_m": round(total_distance, 2),
        "total_time_s": int(total_time),
        "total_runs": total_runs,
        "average_pace_s_per_km": round(avg_pace, 2) if avg_pace > 0 else 0.0,
        "average_distance_m": round(avg_distance, 2),
        "personal_records": {
            "fastest_pace_s_per_km": round(fastest_pace, 2) if fastest_pace else None,
            "longest_distance_m": round(longest_distance, 2) if longest_distance else None,
            "longest_duration_s": int(longest_duration) if longest_duration else None
        }
    }
