"""
Health Check Endpoints
Basic health and status endpoints
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Check API health"""
    return {
        "status": "healthy",
        "service": "kalo-backend",
        "version": "1.0.0"
    }


@router.get("/status")
async def status():
    """Get API status"""
    return {
        "status": "operational",
        "message": "Kalo Backend API is running"
    }
