"""
Challenges API Routes - /api/challenges
Complete implementation with progress calculation and leaderboards.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta

from app.db.database import get_db
from app.models.models import Challenge, ChallengePart, User, Run, ChallengeProof
from app.api.users import get_current_user

router = APIRouter()

# =====================
# SCHEMAS / PYDANTIC MODELS
# =====================

class ChallengeResponse(BaseModel):
    id: str
    title: str
    description: str
    challenge_type: str
    target_value: float
    start_date: str
    end_date: str
    reward_points: int

    class Config:
        from_attributes = True

class LeaderboardEntry(BaseModel):
    user_id: str
    username: str
    current_progress: float
    percentage: float
    position: int
    status: str

class ChallengeDetailResponse(BaseModel):
    id: str
    title: str
    description: str
    challenge_type: str
    target_value: float
    start_date: str
    end_date: str
    reward_points: int
    user_progress: Optional[float]
    user_percentage: Optional[float]
    user_status: Optional[str]
    days_remaining: int
    leaderboard: List[LeaderboardEntry]

    class Config:
        from_attributes = True

class JoinChallengeResponse(BaseModel):
    participation_id: str
    challenge_id: str
    joined_at: str
    message: str

class ProofResponse(BaseModel):
    id: str
    participation_id: str
    proof_type: str
    proof_url: str
    verified: bool
    created_at: str

    class Config:
        from_attributes = True

# =====================
# HELPER FUNCTIONS
# =====================

async def calculate_user_progress(
    db: AsyncSession,
    user_id: str,
    challenge: Challenge
) -> tuple[float, float]:
    """
    Calculate user's progress towards a challenge.
    Returns (current_progress, percentage).
    
    For running challenges, progress is based on Run data.
    For other types, uses ChallengePart.current_progress.
    """
    if challenge.challenge_type == "distance":
        # Sum of distances from runs during challenge period
        result = await db.execute(
            select(func.sum(Run.distance_m)).where(
                (Run.user_id == user_id) &
                (Run.started_at >= challenge.start_date) &
                (Run.started_at <= challenge.end_date)
            )
        )
        total_distance_m = result.scalar() or 0.0
        percentage = min((total_distance_m / challenge.target_value) * 100, 100.0) if challenge.target_value > 0 else 0.0
        return total_distance_m, percentage
    
    elif challenge.challenge_type == "number_of_runs":
        # Count runs during challenge period
        result = await db.execute(
            select(func.count(Run.id)).where(
                (Run.user_id == user_id) &
                (Run.started_at >= challenge.start_date) &
                (Run.started_at <= challenge.end_date)
            )
        )
        run_count = result.scalar() or 0
        percentage = min((run_count / challenge.target_value) * 100, 100.0) if challenge.target_value > 0 else 0.0
        return float(run_count), percentage
    
    else:
        # For other types, use manual progress
        participation_result = await db.execute(
            select(ChallengePart).where(
                (ChallengePart.challenge_id == challenge.id) &
                (ChallengePart.user_id == user_id)
            )
        )
        participation = participation_result.scalar_one_or_none()
        if participation:
            percentage = min((participation.current_progress / challenge.target_value) * 100, 100.0) if challenge.target_value > 0 else 0.0
            return participation.current_progress, percentage
        return 0.0, 0.0

# =====================
# ENDPOINTS
# =====================

@router.get("/", response_model=List[ChallengeResponse])
async def get_active_challenges(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Get all active challenges.
    
    Query parameters:
    - limit: Max challenges to return (default 20)
    - offset: Pagination offset (default 0)
    """
    now = datetime.utcnow()
    result = await db.execute(
        select(Challenge)
        .where(Challenge.end_date >= now)
        .order_by(Challenge.start_date.desc())
        .limit(limit)
        .offset(offset)
    )
    challenges = result.scalars().all()
    
    return [
        ChallengeResponse(
            id=str(c.id),
            title=c.title,
            description=c.description,
            challenge_type=c.challenge_type,
            target_value=c.target_value,
            start_date=c.start_date.isoformat(),
            end_date=c.end_date.isoformat(),
            reward_points=c.reward_points
        )
        for c in challenges
    ]

@router.post("/{challenge_id}/join", response_model=JoinChallengeResponse)
async def join_challenge(
    challenge_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Join a challenge.
    
    User will appear on leaderboard from this moment.
    Progress is calculated from run data during challenge period.
    """
    # Check if challenge exists
    challenge_result = await db.execute(
        select(Challenge).where(Challenge.id == challenge_id)
    )
    challenge = challenge_result.scalar_one_or_none()
    
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    # Check if already joined
    existing_result = await db.execute(
        select(ChallengePart).where(
            (ChallengePart.challenge_id == challenge_id) &
            (ChallengePart.user_id == user.id)
        )
    )
    if existing_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already joined this challenge")
    
    # Create participation
    participation = ChallengePart(
        challenge_id=challenge_id,
        user_id=user.id,
        status="active",
        current_progress=0.0
    )
    db.add(participation)
    await db.commit()
    await db.refresh(participation)
    
    return JoinChallengeResponse(
        participation_id=str(participation.id),
        challenge_id=str(participation.challenge_id),
        joined_at=participation.joined_at.isoformat(),
        message="Successfully joined challenge!"
    )

@router.get("/{challenge_id}", response_model=ChallengeDetailResponse)
async def get_challenge_detail(
    challenge_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get challenge details with user progress and leaderboard.
    
    Returns:
    - Challenge details
    - User's current progress and percentage
    - Top 10 users on leaderboard
    """
    # Get challenge
    challenge_result = await db.execute(
        select(Challenge).where(Challenge.id == challenge_id)
    )
    challenge = challenge_result.scalar_one_or_none()
    
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    # Calculate user progress
    user_progress, user_percentage = await calculate_user_progress(
        db, user.id, challenge
    )
    
    # Get user status
    participation_result = await db.execute(
        select(ChallengePart).where(
            (ChallengePart.challenge_id == challenge_id) &
            (ChallengePart.user_id == user.id)
        )
    )
    user_participation = participation_result.scalar_one_or_none()
    user_status = user_participation.status if user_participation else "not_joined"
    
    # Calculate days remaining
    days_remaining = max(0, (challenge.end_date - datetime.utcnow()).days)
    
    # Get all participations for leaderboard
    leaderboard_result = await db.execute(
        select(ChallengePart)
        .where(ChallengePart.challenge_id == challenge_id)
        .order_by(ChallengePart.current_progress.desc())
        .limit(10)
    )
    participations = leaderboard_result.scalars().all()
    
    # Build leaderboard with updated progress
    leaderboard = []
    for idx, participation in enumerate(participations, 1):
        progress, percentage = await calculate_user_progress(
            db, participation.user_id, challenge
        )
        leaderboard.append(
            LeaderboardEntry(
                user_id=str(participation.user_id),
                username=participation.user.username,
                current_progress=progress,
                percentage=percentage,
                position=idx,
                status=participation.status
            )
        )
    
    return ChallengeDetailResponse(
        id=str(challenge.id),
        title=challenge.title,
        description=challenge.description,
        challenge_type=challenge.challenge_type,
        target_value=challenge.target_value,
        start_date=challenge.start_date.isoformat(),
        end_date=challenge.end_date.isoformat(),
        reward_points=challenge.reward_points,
        user_progress=user_progress,
        user_percentage=user_percentage,
        user_status=user_status,
        days_remaining=days_remaining,
        leaderboard=leaderboard
    )

@router.post("/{challenge_id}/leave")
async def leave_challenge(
    challenge_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Leave a challenge (withdraw participation)."""
    participation_result = await db.execute(
        select(ChallengePart).where(
            (ChallengePart.challenge_id == challenge_id) &
            (ChallengePart.user_id == user.id)
        )
    )
    participation = participation_result.scalar_one_or_none()
    
    if not participation:
        raise HTTPException(status_code=404, detail="Not participating in this challenge")
    
    participation.status = "withdrew"
    await db.commit()
    
    return {"message": "You have withdrawn from the challenge"}

@router.post("/{participation_id}/proof", response_model=ProofResponse)
async def submit_proof(
    participation_id: str,
    proof_url: str,
    proof_type: str = "photo",  # photo, gps, data
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit proof for challenge completion.
    
    proof_type options:
    - "photo": Screenshot/image proof
    - "gps": GPS route data
    - "data": Automated data (from API)
    """
    # Verify participation exists and belongs to user
    participation_result = await db.execute(
        select(ChallengePart).where(ChallengePart.id == participation_id)
    )
    participation = participation_result.scalar_one_or_none()
    
    if not participation or participation.user_id != user.id:
        raise HTTPException(status_code=404, detail="Participation not found")
    
    proof = ChallengeProof(
        participation_id=participation_id,
        proof_url=proof_url,
        proof_type=proof_type,
        verified=False if proof_type == "photo" else True  # Auto-verify GPS/data proofs
    )
    db.add(proof)
    await db.commit()
    await db.refresh(proof)
    
    return ProofResponse(
        id=str(proof.id),
        participation_id=str(proof.participation_id),
        proof_type=proof.proof_type,
        proof_url=proof.proof_url,
        verified=proof.verified,
        created_at=proof.created_at.isoformat()
    )

@router.get("/{challenge_id}/leaderboard")
async def get_challenge_leaderboard(
    challenge_id: str,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get full leaderboard for a challenge.
    
    Shows top N participants ranked by progress.
    """
    # Get challenge
    challenge_result = await db.execute(
        select(Challenge).where(Challenge.id == challenge_id)
    )
    challenge = challenge_result.scalar_one_or_none()
    
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    # Get participations
    leaderboard_result = await db.execute(
        select(ChallengePart)
        .where(ChallengePart.challenge_id == challenge_id)
        .order_by(ChallengePart.current_progress.desc())
        .limit(limit)
    )
    participations = leaderboard_result.scalars().all()
    
    # Build leaderboard with progress
    leaderboard = []
    for idx, participation in enumerate(participations, 1):
        progress, percentage = await calculate_user_progress(
            db, participation.user_id, challenge
        )
        leaderboard.append({
            "position": idx,
            "username": participation.user.username,
            "current_progress": progress,
            "percentage": min(percentage, 100.0),
            "status": participation.status
        })
    
    return {
        "challenge_title": challenge.title,
        "challenge_type": challenge.challenge_type,
        "target_value": challenge.target_value,
        "leaderboard": leaderboard
    }
