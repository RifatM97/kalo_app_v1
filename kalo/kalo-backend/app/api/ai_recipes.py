"""
AI Recipe Extraction Endpoints
/api/v1/ai/extract-recipe - Recipe extraction from video URLs
"""

import os
import uuid
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime

from app.core.celery_app import celery_app
from app.ai.tasks import extract_recipe_async

router = APIRouter()
logger = logging.getLogger(__name__)

# Response models matching Swift Codable structure exactly
class RecipeIngredient(BaseModel):
    name: str
    quantity: Optional[float] = None
    unit: Optional[str] = None


class RecipeStep(BaseModel):
    step: int
    instruction: str


class MacroInfo(BaseModel):
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None


class RecipeExtractionRequest(BaseModel):
    """Request model for recipe extraction"""
    url: str = Field(..., description="Video URL (TikTok, Instagram, YouTube)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://www.tiktok.com/@username/video/123456"
            }
        }


class RecipeExtractionResponse(BaseModel):
    """Response model - MUST MATCH Swift Codable exactly"""
    id: Optional[int] = None
    task_id: Optional[str] = None  # snake_case to match Swift CodingKeys
    title: Optional[str] = None
    description: Optional[str] = None
    ingredients: Optional[list[RecipeIngredient]] = None
    steps: Optional[list[RecipeStep]] = None
    cook_time_minutes: Optional[int] = None
    prep_time_minutes: Optional[int] = None
    difficulty: Optional[str] = None
    servings: Optional[int] = None
    macros: Optional[MacroInfo] = None
    status: Optional[str] = None
    error: Optional[str] = None
    
    class Config:
        # This ensures snake_case in JSON output
        populate_by_name = True


class TaskStatusResponse(BaseModel):
    """Status response for polling"""
    task_id: str
    status: str  # pending, processing, completed, failed
    progress: str = "Starting..."
    recipe: Optional[RecipeExtractionResponse] = None
    error: Optional[str] = None


@router.post(
    "/ai/extract-recipe",
    response_model=RecipeExtractionResponse,
    status_code=202
)
async def start_recipe_extraction(request: RecipeExtractionRequest):
    """
    Start async recipe extraction from video URL
    
    Returns immediately with task_id for polling.
    
    Args:
        request: RecipeExtractionRequest with video URL
        
    Returns:
        RecipeExtractionResponse with task_id and status="processing"
        
    Example:
        POST /api/v1/ai/extract-recipe
        {
            "url": "https://www.tiktok.com/@chef/video/123"
        }
        
        Response:
        {
            "task_id": "abc-123-def",
            "status": "processing",
            "title": null,
            "ingredients": null,
            ...
        }
    """
    try:
        logger.info(f"🎬 Recipe extraction requested for URL: {request.url}")
        
        # Validate URL
        if not request.url or not isinstance(request.url, str):
            raise HTTPException(
                status_code=400,
                detail="Invalid URL format"
            )
        
        # Check if URL is from supported platform
        supported_domains = ["tiktok.com", "instagram.com", "youtube.com", "youtu.be", "twitter.com", "x.com"]
        if not any(domain in request.url.lower() for domain in supported_domains):
            raise HTTPException(
                status_code=400,
                detail="URL must be from TikTok, Instagram, YouTube, or Twitter"
            )
        
        # Generate task ID
        task_id = str(uuid.uuid4())
        user_id = "anonymous"  # In production, get from auth
        recipe_id = str(uuid.uuid4())
        
        logger.info(f"📋 Generated task_id: {task_id}")
        
        # Queue Celery task
        celery_task = extract_recipe_async.delay(
            video_url=request.url,
            user_id=user_id,
            recipe_id=recipe_id,
            task_id=task_id
        )
        
        logger.info(f"✅ Task queued: {celery_task.id}")
        
        # Return immediate response with task ID
        return RecipeExtractionResponse(
            task_id=task_id,
            status="processing",
            description="Recipe extraction in progress. Poll /ai/extract-recipe/{task_id}/status for updates."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error starting extraction: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start recipe extraction: {str(e)}"
        )


@router.get(
    "/ai/extract-recipe/{task_id}/status",
    response_model=RecipeExtractionResponse
)
async def get_extraction_status(task_id: str = Query(..., description="Celery task ID")):
    """
    Poll extraction status and retrieve recipe when ready
    
    Args:
        task_id: Celery task ID from initial extraction request
        
    Returns:
        RecipeExtractionResponse with current status
        - status="processing" while running
        - status="completed" with full recipe when done
        - status="failed" with error message if failed
        
    Example:
        GET /api/v1/ai/extract-recipe/abc-123-def/status
        
        Response while processing:
        {
            "task_id": "abc-123-def",
            "status": "processing",
            "title": null,
            ...
        }
        
        Response when complete:
        {
            "task_id": "abc-123-def",
            "status": "completed",
            "title": "Chocolate Chip Cookies",
            "ingredients": [...],
            "steps": [...],
            "macros": {...},
            ...
        }
    """
    try:
        logger.info(f"📊 Checking status for task: {task_id}")
        
        # Get task result from Redis
        result = celery_app.AsyncResult(task_id)
        
        logger.info(f"Task state: {result.state}")
        
        # Map Celery states to our status
        if result.state == "PENDING":
            return RecipeExtractionResponse(
                task_id=task_id,
                status="processing",
                description="Task queued, waiting to start..."
            )
        
        elif result.state == "STARTED" or result.state == "PROGRESS":
            return RecipeExtractionResponse(
                task_id=task_id,
                status="processing",
                description="Extracting recipe from video..."
            )
        
        elif result.state == "SUCCESS":
            # Extract recipe data from result
            recipe_data = result.result or {}
            
            # Convert to response model, ensuring snake_case for Swift
            ingredients = [
                RecipeIngredient(**ing)
                for ing in recipe_data.get("ingredients", [])
            ]
            
            steps = [
                RecipeStep(**step)
                for step in recipe_data.get("steps", [])
            ]
            
            macros = None
            macro_data = recipe_data.get("macros")
            if macro_data:
                macros = MacroInfo(
                    calories=macro_data.get("calories_per_serving") or macro_data.get("calories"),
                    protein=macro_data.get("protein_grams") or macro_data.get("protein"),
                    carbs=macro_data.get("carbs_grams") or macro_data.get("carbs"),
                    fat=macro_data.get("fat_grams") or macro_data.get("fat")
                )
            
            response = RecipeExtractionResponse(
                task_id=task_id,
                status="completed",
                title=recipe_data.get("title"),
                description=recipe_data.get("description"),
                ingredients=ingredients if ingredients else None,
                steps=steps if steps else None,
                cook_time_minutes=recipe_data.get("cook_time_minutes") or recipe_data.get("cook_time"),
                prep_time_minutes=recipe_data.get("prep_time_minutes") or recipe_data.get("prep_time"),
                difficulty=recipe_data.get("difficulty"),
                servings=recipe_data.get("serves") or recipe_data.get("servings"),
                macros=macros
            )
            
            logger.info(f"✅ Recipe ready: {response.title}")
            return response
        
        elif result.state == "FAILURE":
            error_msg = str(result.info) if result.info else "Unknown error"
            logger.error(f"❌ Task failed: {error_msg}")
            
            return RecipeExtractionResponse(
                task_id=task_id,
                status="failed",
                error=error_msg
            )
        
        else:
            # RETRY, REVOKED, etc.
            return RecipeExtractionResponse(
                task_id=task_id,
                status="processing",
                description=f"Current state: {result.state}"
            )
    
    except Exception as e:
        logger.error(f"❌ Error getting status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get extraction status: {str(e)}"
        )


@router.post("/ai/extract-recipe/{task_id}/cancel")
async def cancel_extraction(task_id: str):
    """
    Cancel a running recipe extraction task
    
    Args:
        task_id: Celery task ID to cancel
        
    Returns:
        Success message
    """
    try:
        logger.info(f"🛑 Cancelling task: {task_id}")
        
        # Revoke the task
        celery_app.control.revoke(task_id, terminate=True)
        
        logger.info(f"✅ Task cancelled: {task_id}")
        
        return {
            "status": "cancelled",
            "task_id": task_id,
            "message": "Recipe extraction cancelled"
        }
    
    except Exception as e:
        logger.error(f"❌ Error cancelling task: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel extraction: {str(e)}"
        )
