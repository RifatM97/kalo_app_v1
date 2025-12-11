# AI Pipeline FastAPI Integration Guide

Complete guide for integrating the recipe extraction AI pipeline with FastAPI endpoints.

## Architecture Overview

```
User Request
    ↓
FastAPI Endpoint (/recipes/extract)
    ↓
Celery Task (extract_recipe_async)
    ↓
AI Pipeline Orchestrator
    ├── Video Downloader
    ├── Audio Extractor
    ├── Frame Extractor
    ├── Whisper Transcriber
    ├── OCR Extractor
    ├── Vision Detector
    └── LLM Structurer
    ↓
Save to Database
    ↓
Return Task ID to User
    ↓
(Later) User polls or receives webhook with result
```

## Database Model Updates

Add/update `Recipe` model in `app/models/recipe.py`:

```python
from sqlalchemy import Column, String, Integer, Float, DateTime, Enum, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum

class ExtractionStatus(str, PyEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Recipe(Base):
    __tablename__ = "recipes"
    
    # Primary fields
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Extraction metadata
    source_url = Column(String, nullable=True)  # TikTok/Instagram URL
    video_path = Column(String, nullable=True)  # Local download path
    extraction_status = Column(String, default=ExtractionStatus.PENDING)
    extraction_error = Column(String, nullable=True)  # Error message if failed
    celery_task_id = Column(String, nullable=True)  # Track background task
    
    # Recipe content
    title = Column(String, nullable=True)
    description = Column(String, nullable=True)
    ingredients = Column(JSON, nullable=True)  # List of {name, quantity, unit}
    steps = Column(JSON, nullable=True)  # List of {step, instruction}
    
    # Metadata
    cook_time_minutes = Column(Integer, nullable=True)
    prep_time_minutes = Column(Integer, nullable=True)
    difficulty = Column(String, nullable=True)  # easy, medium, hard
    servings = Column(Integer, default=1)
    
    # Macros
    macros = Column(JSON, nullable=True)  # {calories, protein, carbs, fat}
    calories_per_serving = Column(Float, nullable=True)
    
    # Extraction details (for debugging)
    transcript = Column(String, nullable=True)  # Audio transcription
    ocr_text = Column(String, nullable=True)  # OCR from frames
    detected_items = Column(JSON, nullable=True)  # Vision detection results
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    extraction_completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="recipes")
    grocery_items = relationship("GroceryItem", back_populates="recipe")
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "ingredients": self.ingredients,
            "steps": self.steps,
            "cook_time_minutes": self.cook_time_minutes,
            "macros": self.macros,
            "extraction_status": self.extraction_status,
        }

class GroceryItem(Base):
    __tablename__ = "grocery_items"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    recipe_id = Column(Integer, ForeignKey("recipes.id"))
    
    name = Column(String)
    quantity = Column(Float)
    unit = Column(String)
    
    recipe = relationship("Recipe", back_populates="grocery_items")
```

## FastAPI Endpoints

Create `app/api/recipes/extract.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Recipe, User
from app.auth import get_current_user
from app.ai.ai_pipeline import RecipeExtractionPipeline
from app.ai.tasks import extract_recipe_async

router = APIRouter(prefix="/recipes", tags=["recipes"])

# Pydantic models
class ExtractRecipeRequest(BaseModel):
    source_url: str
    num_frames: int = 5

class ExtractRecipeResponse(BaseModel):
    recipe_id: int
    task_id: str
    status: str
    message: str

class RecipeResponse(BaseModel):
    id: int
    title: Optional[str]
    description: Optional[str]
    ingredients: Optional[list]
    steps: Optional[list]
    cook_time_minutes: Optional[int]
    macros: Optional[dict]
    extraction_status: str
    created_at: datetime

class TaskStatusResponse(BaseModel):
    recipe_id: int
    task_id: str
    status: str
    progress: str
    error: Optional[str]
    recipe: Optional[RecipeResponse]

# Endpoint 1: Start extraction (returns immediately with task ID)
@router.post("/extract", response_model=ExtractRecipeResponse)
async def start_recipe_extraction(
    request: ExtractRecipeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Start async recipe extraction from video URL.
    
    Returns task ID immediately. Use /extract/{task_id}/status to check progress.
    
    Args:
        source_url: TikTok, Instagram, or YouTube URL
        num_frames: Number of frames to extract (3-10, default 5)
    
    Returns:
        recipe_id: Database ID for tracking
        task_id: Celery task ID for status checking
        status: "queued"
        message: Human-readable status
    
    Example:
        POST /recipes/extract
        {
            "source_url": "https://www.tiktok.com/video/1234567890",
            "num_frames": 5
        }
        
        Response:
        {
            "recipe_id": 42,
            "task_id": "abc123def456",
            "status": "queued",
            "message": "Recipe extraction queued. Check status with task ID."
        }
    """
    
    # Validate URL
    valid_domains = ["tiktok.com", "instagram.com", "youtube.com", "youtu.be"]
    if not any(domain in request.source_url for domain in valid_domains):
        raise HTTPException(
            status_code=400,
            detail="URL must be from TikTok, Instagram, or YouTube"
        )
    
    # Validate num_frames
    if not (3 <= request.num_frames <= 10):
        raise HTTPException(
            status_code=400,
            detail="num_frames must be between 3 and 10"
        )
    
    # Create recipe record in database
    recipe = Recipe(
        user_id=current_user.id,
        source_url=request.source_url,
        extraction_status="pending",
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    
    # Submit async task to Celery
    task = extract_recipe_async.delay(
        video_url=request.source_url,
        user_id=current_user.id,
        recipe_id=recipe.id,
        num_frames=request.num_frames,
    )
    
    # Update recipe with task ID
    recipe.celery_task_id = task.id
    recipe.extraction_status = "processing"
    db.commit()
    
    return ExtractRecipeResponse(
        recipe_id=recipe.id,
        task_id=task.id,
        status="processing",
        message=f"Recipe extraction started. Track progress with task ID: {task.id}",
    )

# Endpoint 2: Check extraction status
@router.get("/extract/{task_id}/status", response_model=TaskStatusResponse)
async def check_extraction_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Check status of recipe extraction task.
    
    Args:
        task_id: Celery task ID from extraction start endpoint
    
    Returns:
        status: "pending", "processing", "completed", or "failed"
        progress: Human-readable progress message
        error: Error message if failed
        recipe: Full recipe data if completed
    
    Example:
        GET /recipes/extract/abc123def456/status
        
        Response while processing:
        {
            "recipe_id": 42,
            "task_id": "abc123def456",
            "status": "processing",
            "progress": "[4/7] Detecting ingredients...",
            "error": null,
            "recipe": null
        }
        
        Response when completed:
        {
            "recipe_id": 42,
            "task_id": "abc123def456",
            "status": "completed",
            "progress": "Extraction completed in 2m 15s",
            "error": null,
            "recipe": {
                "id": 42,
                "title": "Thai Green Curry with Chicken",
                "ingredients": [...],
                "steps": [...],
                "macros": {...}
            }
        }
    """
    from celery.result import AsyncResult
    
    # Get task result
    task_result = AsyncResult(task_id)
    
    # Find recipe in database
    recipe = db.query(Recipe).filter(
        Recipe.celery_task_id == task_id,
        Recipe.user_id == current_user.id,
    ).first()
    
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    # Map Celery state to our status
    status_map = {
        "PENDING": "pending",
        "STARTED": "processing",
        "SUCCESS": "completed",
        "FAILURE": "failed",
        "RETRY": "retrying",
    }
    
    current_status = status_map.get(task_result.state, task_result.state.lower())
    
    # Prepare response
    response_data = {
        "recipe_id": recipe.id,
        "task_id": task_id,
        "status": current_status,
        "progress": getattr(task_result, 'info', {}).get('progress', f"Status: {current_status}"),
        "error": None,
        "recipe": None,
    }
    
    # If failed, include error
    if task_result.state == "FAILURE":
        response_data["error"] = str(task_result.info)
    
    # If completed, include recipe
    if task_result.state == "SUCCESS":
        response_data["recipe"] = recipe.to_dict()
    
    return TaskStatusResponse(**response_data)

# Endpoint 3: Get recipe by ID
@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(
    recipe_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get recipe details by ID.
    
    Example:
        GET /recipes/42
        
        Response:
        {
            "id": 42,
            "title": "Thai Green Curry with Chicken",
            "description": "...",
            "ingredients": [...],
            "steps": [...],
            "cook_time_minutes": 25,
            "macros": {...},
            "extraction_status": "completed",
            "created_at": "2024-01-15T10:30:00"
        }
    """
    recipe = db.query(Recipe).filter(
        Recipe.id == recipe_id,
        Recipe.user_id == current_user.id,
    ).first()
    
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    return recipe.to_dict()

# Endpoint 4: List user's recipes
@router.get("/", response_model=list[RecipeResponse])
async def list_recipes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
):
    """
    List user's recipes with pagination and filtering.
    
    Query params:
        skip: Number of recipes to skip (pagination)
        limit: Number of recipes to return (max 100)
        status: Filter by extraction status (pending/processing/completed/failed)
    
    Example:
        GET /recipes/?skip=0&limit=10&status=completed
    """
    query = db.query(Recipe).filter(Recipe.user_id == current_user.id)
    
    if status:
        query = query.filter(Recipe.extraction_status == status)
    
    recipes = query.offset(skip).limit(limit).all()
    
    return [recipe.to_dict() for recipe in recipes]

# Endpoint 5: Delete recipe
@router.delete("/{recipe_id}")
async def delete_recipe(
    recipe_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete recipe and associated data.
    
    Example:
        DELETE /recipes/42
    """
    recipe = db.query(Recipe).filter(
        Recipe.id == recipe_id,
        Recipe.user_id == current_user.id,
    ).first()
    
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    db.delete(recipe)
    db.commit()
    
    return {"message": "Recipe deleted"}

# Include router in main app
# In app/main.py:
# from app.api.recipes.extract import router as recipe_router
# app.include_router(recipe_router)
```

## Updated Celery Tasks

Update `app/ai/tasks.py` to integrate with database:

```python
from celery import shared_task
from celery.utils.log import get_task_logger
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import os
from datetime import datetime, timedelta

from app.models import Recipe, User
from app.database import SessionLocal
from app.ai.ai_pipeline import RecipeExtractionPipeline

logger = get_task_logger(__name__)

@shared_task(
    name="extract_recipe_async",
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 60},
    soft_time_limit=1800,  # 30 minutes
    time_limit=1900,  # 31m 40s hard limit
)
def extract_recipe_async(self, video_url: str, user_id: int, recipe_id: int, num_frames: int = 5):
    """
    Async task: Extract recipe from video URL.
    
    Updates database with:
    - Status (pending → processing → completed/failed)
    - Progress indicators
    - Final recipe data
    - Error messages
    """
    db = SessionLocal()
    
    try:
        # Get recipe from database
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if not recipe:
            raise ValueError(f"Recipe {recipe_id} not found")
        
        # Update to processing
        recipe.extraction_status = "processing"
        db.commit()
        
        logger.info(f"[Recipe {recipe_id}] Starting extraction from {video_url}")
        
        # Initialize pipeline
        pipeline = RecipeExtractionPipeline(
            llm_provider=os.getenv("LLM_PROVIDER", "openai"),
            whisper_model_size=os.getenv("WHISPER_MODEL_SIZE", "small"),
            ocr_confidence=float(os.getenv("OCR_CONFIDENCE_THRESHOLD", 0.5)),
            vision_confidence=float(os.getenv("VISION_CONFIDENCE_THRESHOLD", 0.5)),
        )
        
        # Run extraction
        extracted_recipe = pipeline.run(video_url, num_frames=num_frames)
        
        logger.info(f"[Recipe {recipe_id}] Extraction completed: {extracted_recipe['title']}")
        
        # Save to database
        recipe.title = extracted_recipe.get("title")
        recipe.description = extracted_recipe.get("description")
        recipe.ingredients = extracted_recipe.get("ingredients", [])
        recipe.steps = extracted_recipe.get("steps", [])
        recipe.cook_time_minutes = extracted_recipe.get("cook_time_minutes")
        recipe.prep_time_minutes = extracted_recipe.get("prep_time_minutes")
        recipe.difficulty = extracted_recipe.get("difficulty")
        recipe.servings = extracted_recipe.get("servings", 1)
        recipe.macros = extracted_recipe.get("macros")
        recipe.calories_per_serving = extracted_recipe.get("macros", {}).get("calories")
        
        # Debug data
        recipe.transcript = extracted_recipe.get("transcript")
        recipe.ocr_text = extracted_recipe.get("ocr_text")
        recipe.detected_items = extracted_recipe.get("detected_items")
        
        # Mark as completed
        recipe.extraction_status = "completed"
        recipe.extraction_completed_at = datetime.utcnow()
        recipe.extraction_error = None
        
        db.commit()
        
        logger.info(f"[Recipe {recipe_id}] Successfully saved to database")
        
        return {
            "status": "completed",
            "recipe_id": recipe_id,
            "title": recipe.title,
            "ingredients_count": len(recipe.ingredients or []),
            "steps_count": len(recipe.steps or []),
        }
        
    except Exception as e:
        logger.error(f"[Recipe {recipe_id}] Extraction failed: {str(e)}")
        
        # Update database with error
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if recipe:
            recipe.extraction_status = "failed"
            recipe.extraction_error = str(e)
            db.commit()
        
        # Re-raise for Celery retry
        raise
        
    finally:
        db.close()

# Scheduled task: Cleanup old extraction files
from celery.schedules import crontab

@shared_task(name="cleanup_old_extractions")
def cleanup_old_extractions(days: int = 7):
    """
    Cleanup temporary files older than N days.
    
    Run this daily via Celery Beat:
    
    # In celery_config.py:
    app.conf.beat_schedule = {
        'cleanup-old-extractions': {
            'task': 'cleanup_old_extractions',
            'schedule': crontab(hour=2, minute=0),  # 2 AM daily
            'args': (7,),  # Keep files for 7 days
        },
    }
    """
    import shutil
    from pathlib import Path
    
    temp_dir = os.getenv("TEMP_FILES_DIR", "./temp_media")
    cutoff_time = datetime.utcnow() - timedelta(days=days)
    
    deleted_count = 0
    freed_bytes = 0
    
    if os.path.exists(temp_dir):
        for item in Path(temp_dir).iterdir():
            if item.stat().st_mtime < cutoff_time.timestamp():
                if item.is_file():
                    freed_bytes += item.stat().st_size
                    item.unlink()
                    deleted_count += 1
                elif item.is_dir():
                    freed_bytes += sum(
                        f.stat().st_size for f in item.rglob("*") if f.is_file()
                    )
                    shutil.rmtree(item)
                    deleted_count += 1
    
    logger.info(f"Cleanup: Deleted {deleted_count} items, freed {freed_bytes / 1024 / 1024:.2f} MB")
    
    return {
        "deleted_count": deleted_count,
        "freed_mb": freed_bytes / 1024 / 1024,
    }
```

## Celery Configuration

Create `app/celery_config.py`:

```python
from celery import Celery
from celery.schedules import crontab
import os

# Initialize Celery
app = Celery(
    'kalo',
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
)

# Load configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task settings
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    
    # Result backend
    result_backend_transport_options={
        'master_name': 'mymaster',
        'retry_on_timeout': True,
    },
    result_expires=3600,  # Results expire after 1 hour
    
    # Scheduled tasks (Celery Beat)
    beat_schedule={
        'cleanup-old-extractions': {
            'task': 'app.ai.tasks.cleanup_old_extractions',
            'schedule': crontab(hour=2, minute=0),  # 2 AM daily
            'args': (7,),  # Keep files for 7 days
        },
    },
)

# Load task modules
app.autodiscover_tasks(['app.ai'])

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
```

## Usage Examples

### 1. Extract Recipe from TikTok (Client-Side JavaScript)

```javascript
// Start extraction
async function startExtraction(tikTokUrl) {
    const response = await fetch('/api/recipes/extract', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`,
        },
        body: JSON.stringify({
            source_url: tikTokUrl,
            num_frames: 5,
        }),
    });
    
    const data = await response.json();
    return data.task_id;  // Save this to check progress
}

// Poll for status
async function checkStatus(taskId) {
    const response = await fetch(`/api/recipes/extract/${taskId}/status`, {
        headers: {
            'Authorization': `Bearer ${authToken}`,
        },
    });
    
    return response.json();
}

// Check every 2 seconds until completion
async function waitForCompletion(taskId) {
    while (true) {
        const status = await checkStatus(taskId);
        
        console.log(`Status: ${status.status}`);
        console.log(`Progress: ${status.progress}`);
        
        if (status.status === 'completed') {
            console.log('Recipe ready:', status.recipe);
            return status.recipe;
        }
        
        if (status.status === 'failed') {
            console.error('Extraction failed:', status.error);
            throw new Error(status.error);
        }
        
        // Wait 2 seconds before checking again
        await new Promise(resolve => setTimeout(resolve, 2000));
    }
}

// Usage
const taskId = await startExtraction('https://www.tiktok.com/video/1234567890');
const recipe = await waitForCompletion(taskId);
```

### 2. Extract Recipe (Python Client)

```python
import httpx
import asyncio
from time import sleep

async def extract_recipe(api_url: str, auth_token: str, video_url: str):
    """Extract recipe from video URL."""
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Start extraction
        response = await client.post(
            f"{api_url}/recipes/extract",
            json={
                "source_url": video_url,
                "num_frames": 5,
            },
            headers=headers,
        )
        response.raise_for_status()
        
        data = response.json()
        task_id = data["task_id"]
        recipe_id = data["recipe_id"]
        
        print(f"✓ Extraction started (Task: {task_id})")
        
        # Poll for completion
        while True:
            response = await client.get(
                f"{api_url}/recipes/extract/{task_id}/status",
                headers=headers,
            )
            response.raise_for_status()
            
            status = response.json()
            print(f"Status: {status['status']} - {status['progress']}")
            
            if status["status"] == "completed":
                print(f"✓ Recipe: {status['recipe']['title']}")
                print(f"  Ingredients: {len(status['recipe']['ingredients'])}")
                print(f"  Steps: {len(status['recipe']['steps'])}")
                return status["recipe"]
            
            if status["status"] == "failed":
                raise Exception(f"Extraction failed: {status['error']}")
            
            # Check every 2 seconds
            sleep(2)

# Usage
if __name__ == "__main__":
    recipe = asyncio.run(extract_recipe(
        api_url="http://localhost:8000",
        auth_token="your-auth-token",
        video_url="https://www.tiktok.com/video/1234567890",
    ))
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK`: Request successful
- `201 Created`: Resource created
- `400 Bad Request`: Invalid input (bad URL format, invalid num_frames)
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: User doesn't have access to this recipe
- `404 Not Found`: Recipe or task not found
- `422 Unprocessable Entity`: Invalid request body
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error (check logs)
- `503 Service Unavailable`: Celery worker offline, Redis down

## Performance Optimization

### 1. Parallel Frame Processing

Update pipeline to process frames in parallel:

```python
# In ai_pipeline.py
import asyncio

async def run(self, video_url: str, num_frames: int = 5):
    # ... download, extract audio, extract frames ...
    
    # Run OCR and vision detection in parallel
    ocr_task = asyncio.create_task(
        self.ocr_extractor.extract_all_text_from_frames(frames)
    )
    vision_task = asyncio.create_task(
        self.vision_detector.extract_ingredients_from_frames(frames)
    )
    
    ocr_text = await ocr_task
    detected_items = await vision_task
    
    # Continue with structured recipe...
```

### 2. Implement Rate Limiting

```python
# In FastAPI app
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@router.post("/extract")
@limiter.limit("5/hour")  # Max 5 extractions per hour
async def start_recipe_extraction(request: ExtractRecipeRequest, ...):
    # ... extraction logic ...
```

### 3. Cache Results

```python
# Cache successful extractions
from functools import lru_cache

@lru_cache(maxsize=100)
async def get_recipe_cached(recipe_id: int):
    # Only cache for 1 hour
    return get_recipe(recipe_id)
```

## Monitoring

### 1. Health Check Endpoint

```python
@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Check if all services are running."""
    import redis
    
    try:
        # Check database
        db.execute("SELECT 1")
        
        # Check Redis
        r = redis.Redis.from_url(os.getenv("REDIS_URL"))
        r.ping()
        
        return {
            "status": "healthy",
            "database": "connected",
            "redis": "connected",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }
```

### 2. Metrics

Add Prometheus metrics:

```python
from prometheus_client import Counter, Histogram
import time

extraction_count = Counter(
    'recipe_extractions_total',
    'Total recipe extractions',
    ['status']
)

extraction_duration = Histogram(
    'recipe_extraction_duration_seconds',
    'Recipe extraction duration'
)

@router.post("/extract")
async def start_recipe_extraction(...):
    start_time = time.time()
    try:
        # ... extraction logic ...
        extraction_count.labels(status='success').inc()
    except:
        extraction_count.labels(status='failed').inc()
    finally:
        extraction_duration.observe(time.time() - start_time)
```

## Next Steps

1. ✅ Update database models with extraction fields
2. ✅ Create FastAPI endpoints for extraction
3. ✅ Update Celery tasks to save to database
4. ✅ Implement status polling
5. ⏳ Test with real videos
6. ⏳ Add rate limiting
7. ⏳ Setup monitoring and alerts
8. ⏳ Deploy to production
