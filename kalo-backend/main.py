"""
KALO Backend - FastAPI Entry Point
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from datetime import datetime
import platform

from app.db.database import init_db, get_db
from app.api import auth, users, recipes, mealplan, grocery, workouts, runs, posts, challenges, ai

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="KALO API",
    description="Next-gen super health app with AI",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "*.example.com"]
)

# Initialize database
@app.on_event("startup")
async def startup():
    logger.info("Starting KALO API...")
    await init_db()
    logger.info("Database initialized successfully")

@app.on_event("shutdown")
async def shutdown():
    logger.info("Shutting down KALO API...")

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(recipes.router, prefix="/api/recipes", tags=["recipes"])
app.include_router(mealplan.router, prefix="/api/mealplan", tags=["mealplan"])
app.include_router(grocery.router, prefix="/api/grocery", tags=["grocery"])
app.include_router(workouts.router, prefix="/api/workouts", tags=["workouts"])
app.include_router(runs.router, prefix="/api/runs", tags=["runs"])
app.include_router(posts.router, prefix="/api/posts", tags=["posts"])
app.include_router(challenges.router, prefix="/api/challenges", tags=["challenges"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])

# Health check endpoints
@app.get("/health")
async def health():
    """Quick health check for iOS connectivity testing"""
    return {
        "status": "healthy",
        "service": "kalo-api",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "platform": platform.system(),
        "message": "API is running and accepting connections from iOS"
    }

@app.get("/health/verbose")
async def health_verbose(db: AsyncSession = Depends(get_db)):
    """Detailed health check including database connectivity"""
    
    services = {
        "api": "healthy",
        "database": "checking...",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Check database
    try:
        await db.execute(select(1))
        services["database"] = "healthy"
    except Exception as e:
        services["database"] = f"error: {str(e)}"
    
    return {
        "status": "healthy" if services["database"] == "healthy" else "degraded",
        "services": services,
        "platform": platform.system(),
        "endpoints_available": [
            "/api/auth", "/api/users", "/api/recipes", "/api/mealplan",
            "/api/grocery", "/api/workouts", "/api/runs", "/api/posts",
            "/api/challenges", "/api/ai"
        ]
    }

# Root
@app.get("/")
async def root():
    return {
        "name": "KALO API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
