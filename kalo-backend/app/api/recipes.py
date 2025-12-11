"""
Recipes API Routes - /api/recipes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import Optional
import uuid

from app.db.database import get_db
from app.models.models import Recipe, RecipeExtraction, User
from app.api.users import get_current_user

router = APIRouter()

# ==================
# Schemas
# ==================

class IngredientSchema(BaseModel):
    name: str
    quantity: float
    unit: str
    calories: Optional[int] = None
    macros: Optional[dict] = None

class RecipeResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    ingredients: list
    instructions: Optional[str]
    calories: Optional[int]
    macros: dict
    prep_time: Optional[int]
    cook_time: Optional[int]
    servings: int
    image_url: Optional[str]
    source: str
    created_at: str

    class Config:
        from_attributes = True

class CreateRecipeRequest(BaseModel):
    title: str
    description: Optional[str] = None
    ingredients: list[IngredientSchema]
    instructions: Optional[str] = None
    prep_time: Optional[int] = None
    cook_time: Optional[int] = None
    servings: int = 1
    image_url: Optional[str] = None

class RecipeExtractionResponse(BaseModel):
    id: str
    video_url: str
    status: str
    transcript: Optional[str]
    extracted_recipe: Optional[dict]
    created_at: str

    class Config:
        from_attributes = True

# ==================
# Routes
# ==================

@router.post("/", response_model=RecipeResponse)
async def create_recipe(
    req: CreateRecipeRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new recipe"""
    
    # Calculate totals
    total_calories = sum(ing.calories or 0 for ing in req.ingredients)
    macros = {
        "protein": sum(ing.macros.get("protein", 0) if ing.macros else 0 for ing in req.ingredients),
        "carbs": sum(ing.macros.get("carbs", 0) if ing.macros else 0 for ing in req.ingredients),
        "fat": sum(ing.macros.get("fat", 0) if ing.macros else 0 for ing in req.ingredients),
    }
    
    recipe = Recipe(
        id=uuid.uuid4(),
        user_id=user.id,
        title=req.title,
        description=req.description,
        ingredients=[ing.model_dump() for ing in req.ingredients],
        instructions=req.instructions,
        calories=total_calories,
        macros=macros,
        prep_time=req.prep_time,
        cook_time=req.cook_time,
        servings=req.servings,
        image_url=req.image_url,
        source="user",
    )
    
    db.add(recipe)
    await db.commit()
    await db.refresh(recipe)
    
    return recipe

@router.get("/", response_model=list[RecipeResponse])
async def list_recipes(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0),
    limit: int = Query(10),
):
    """List user's recipes with pagination"""
    
    result = await db.execute(
        select(Recipe)
        .where(Recipe.user_id == user.id)
        .offset(skip)
        .limit(limit)
    )
    
    recipes = result.scalars().all()
    return recipes

@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(recipe_id: str, db: AsyncSession = Depends(get_db)):
    """Get recipe by ID"""
    
    result = await db.execute(select(Recipe).where(Recipe.id == recipe_id))
    recipe = result.scalar_one_or_none()
    
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    
    return recipe

@router.put("/{recipe_id}", response_model=RecipeResponse)
async def update_recipe(
    recipe_id: str,
    req: CreateRecipeRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update recipe"""
    
    result = await db.execute(select(Recipe).where(Recipe.id == recipe_id))
    recipe = result.scalar_one_or_none()
    
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    
    if recipe.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    recipe.title = req.title
    recipe.description = req.description
    recipe.ingredients = [ing.model_dump() for ing in req.ingredients]
    recipe.prep_time = req.prep_time
    recipe.cook_time = req.cook_time
    recipe.servings = req.servings
    
    await db.commit()
    await db.refresh(recipe)
    
    return recipe

@router.delete("/{recipe_id}")
async def delete_recipe(
    recipe_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete recipe"""
    
    result = await db.execute(select(Recipe).where(Recipe.id == recipe_id))
    recipe = result.scalar_one_or_none()
    
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    
    if recipe.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    await db.delete(recipe)
    await db.commit()
    
    return {"message": "Recipe deleted"}

@router.get("/search/query", response_model=list[RecipeResponse])
async def search_recipes(
    q: str = Query(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Search recipes by title"""
    
    result = await db.execute(
        select(Recipe)
        .where(Recipe.user_id == user.id)
        .where(Recipe.title.ilike(f"%{q}%"))
    )
    
    recipes = result.scalars().all()
    return recipes


# ==================
# AI RECIPE EXTRACTION
# ==================

from fastapi import File, UploadFile
import logging
from app.services.llm.factory import get_llm_provider
from app.services.recipe_extractor import RecipeExtractor

logger = logging.getLogger(__name__)


class RecipeExtractionResponse(BaseModel):
    """Response from recipe extraction"""
    title: str
    description: str
    servings: int
    ingredients: list[dict]
    steps: list[str]
    estimated_calories_per_serving: float
    macros_per_serving: dict
    tags: list[str]
    prep_time_minutes: int
    cook_time_minutes: int
    difficulty: str


@router.post("/extract-from-image", response_model=RecipeExtractionResponse)
async def extract_recipe_from_image(
    file: UploadFile = File(...),
    # user: User = Depends(get_current_user),  # Uncomment for auth
    db: AsyncSession = Depends(get_db)
):
    """
    Extract recipe from uploaded image using OpenAI Vision.
    
    Upload a photo of a recipe (from cookbook, screenshot, etc.)
    and get structured recipe data with ingredients, steps, and nutrition.
    
    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/recipes/extract-from-image" \\
             -F "file=@recipe_photo.jpg"
        ```
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an image (JPEG, PNG, etc.)"
            )
        
        logger.info(f"Extracting recipe from image: {file.filename}")
        
        # Read image bytes
        image_bytes = await file.read()
        
        if len(image_bytes) == 0:
            raise HTTPException(
                status_code=400,
                detail="Empty image file"
            )
        
        # Get OpenAI provider
        try:
            provider = get_llm_provider(provider="openai")
        except Exception as e:
            logger.error(f"OpenAI not configured: {e}")
            raise HTTPException(
                status_code=503,
                detail="AI service not configured. Please set OPENAI_API_KEY."
            )
        
        # Extract recipe
        extractor = RecipeExtractor(provider)
        recipe_data = await extractor.extract_from_image(image_bytes)
        
        logger.info(f"✓ Extracted: {recipe_data['title']}")
        
        # Optionally save to database
        # recipe = Recipe(
        #     id=str(uuid.uuid4()),
        #     user_id=user.id,
        #     title=recipe_data["title"],
        #     ... map fields ...
        # )
        # db.add(recipe)
        # await db.commit()
        
        return RecipeExtractionResponse(**recipe_data)
    
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Extraction error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Recipe extraction failed: {str(e)}"
        )


@router.post("/extract-from-video", response_model=RecipeExtractionResponse)
async def extract_recipe_from_video(
    file: UploadFile = File(...),
    # user: User = Depends(get_current_user),  # Uncomment for auth
    db: AsyncSession = Depends(get_db)
):
    """
    Extract recipe from uploaded video using OpenAI Vision.
    
    Upload a recipe video and get structured recipe data.
    System extracts key frames and analyzes them with AI.
    
    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/recipes/extract-from-video" \\
             -F "file=@recipe_video.mp4"
        ```
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('video/'):
            raise HTTPException(
                status_code=400,
                detail="File must be a video (MP4, MOV, etc.)"
            )
        
        logger.info(f"Extracting recipe from video: {file.filename}")
        
        # Read video bytes
        video_bytes = await file.read()
        
        if len(video_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty video file")
        
        # Get OpenAI provider
        try:
            provider = get_llm_provider(provider="openai")
        except Exception as e:
            logger.error(f"OpenAI not configured: {e}")
            raise HTTPException(
                status_code=503,
                detail="AI service not configured. Please set OPENAI_API_KEY."
            )
        
        # Extract frames from video
        frames = await extract_video_frames(video_bytes, max_frames=5)
        
        if not frames:
            raise HTTPException(
                status_code=400,
                detail="Could not extract frames from video"
            )
        
        logger.info(f"Extracted {len(frames)} frames from video")
        
        # Extract recipe from frames
        extractor = RecipeExtractor(provider)
        recipe_data = await extractor.extract_from_video_frames(frames)
        
        logger.info(f"✓ Extracted: {recipe_data['title']}")
        
        return RecipeExtractionResponse(**recipe_data)
    
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Extraction error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Video extraction failed: {str(e)}"
        )


async def extract_video_frames(
    video_bytes: bytes,
    max_frames: int = 5
) -> list[bytes]:
    """
    Extract key frames from video.
    
    Uses OpenCV to extract frames at regular intervals.
    
    Args:
        video_bytes: Video file bytes
        max_frames: Maximum number of frames to extract
        
    Returns:
        List of frame image bytes (JPEG)
    """
    import tempfile
    import cv2
    import numpy as np
    from pathlib import Path
    
    try:
        # Save video to temp file
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            tmp.write(video_bytes)
            tmp_path = tmp.name
        
        # Open video with OpenCV
        cap = cv2.VideoCapture(tmp_path)
        
        if not cap.isOpened():
            raise ValueError("Could not open video file")
        
        # Get video properties
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        if total_frames < 1:
            raise ValueError("Video has no frames")
        
        # Calculate frame intervals
        frame_interval = max(1, total_frames // max_frames)
        
        frames = []
        frame_idx = 0
        
        while frame_idx < total_frames and len(frames) < max_frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            
            if ret:
                # Convert frame to JPEG bytes
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                frame_bytes = buffer.tobytes()
                frames.append(frame_bytes)
            
            frame_idx += frame_interval
        
        cap.release()
        
        # Clean up temp file
        Path(tmp_path).unlink(missing_ok=True)
        
        logger.info(f"Extracted {len(frames)} frames from video")
        
        return frames
    
    except Exception as e:
        logger.error(f"Frame extraction failed: {e}")
        return []
