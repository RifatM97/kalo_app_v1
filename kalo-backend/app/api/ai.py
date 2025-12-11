"""
AI API Routes - /api/ai
Endpoints for AI features: insights, meal generation, workout generation, recipe extraction, etc.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
import uuid
import logging

from app.api.users import get_current_user
from app.ai.meal_planner import MealPlanGenerator
from app.ai.workout_generator import WorkoutPlanGenerator
from app.ai.insights_engine import InsightAnalyzer
from app.ai.recipe_extractor import RecipeExtractionPipeline
from app.services.chatbot import (
    generate_chat_response, 
    get_session_history, 
    ChatSession, 
    get_or_create_session,
    AI_COACH_SYSTEM_PROMPT
)

router = APIRouter()
logger = logging.getLogger(__name__)

# ===== DATA MODELS =====
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    coach_mode: Optional[bool] = False  # Enable AI Coach with personalized context
    context: Optional[dict] = None  # User context: goals, recent workouts, etc.

class ChatResponse(BaseModel):
    message: str
    session_id: str
    provider: str  # "ollama/llama3" or "openai/gpt-4"

# =====
class MealPlanRequest(BaseModel):
    daily_calories: int
    macro_targets: dict
    diet_type: str = "balanced"
    restrictions: Optional[list[str]] = None

class WorkoutPlanRequest(BaseModel):
    goal: str  # strength, weight_loss, endurance
    level: str  # beginner, intermediate, advanced
    frequency: int  # per week
    equipment: list[str]
    duration_weeks: int = 12

class InsightsRequest(BaseModel):
    daily_logs: list[dict]
    workouts: list[dict]

class RecipeExtractionRequest(BaseModel):
    url: str

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

class RecipeExtractionResponse(BaseModel):
    task_id: Optional[str] = None
    status: str
    title: Optional[str] = None
    description: Optional[str] = None
    ingredients: Optional[List[RecipeIngredient]] = None
    steps: Optional[List[RecipeStep]] = None
    cook_time_minutes: Optional[int] = None
    prep_time_minutes: Optional[int] = None
    difficulty: Optional[str] = None
    servings: Optional[int] = None
    macros: Optional[MacroInfo] = None
    error: Optional[str] = None

# ===== TASK STORAGE =====
extraction_tasks = {}

# ===== CHATBOT ENDPOINT =====
@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Chat with Kalo AI assistant.
    
    Supports multi-turn conversations with session tracking.
    Uses configured LLM provider (Ollama/Llama3 by default, OpenAI as fallback).
    
    Request:
        - message: User's question/message
        - session_id: Optional session ID for multi-turn conversations
        - coach_mode: Enable AI Coach with fitness/nutrition expertise
        - context: Optional user context (goals, workouts, activity)
    
    Response:
        - message: AI response
        - session_id: Session ID for future requests
        - provider: Which LLM provider was used
    
    Example:
        ```
        POST /api/ai/chat
        {"message": "How should I train for basketball?", "coach_mode": true}
        
        Response:
        {
            "message": "Focus on explosive lower body work...",
            "session_id": "session_1234567890",
            "provider": "openai/gpt-4o-mini"
        }
        ```
    """
    try:
        logger.info(
            f"[CHAT] New message: {req.message[:50]}... "
            f"(coach_mode={req.coach_mode})"
        )
        
        # Use provided session_id or create new one
        session_id = req.session_id or f"session_{uuid.uuid4().hex[:12]}"
        
        # If coach mode, override system prompt
        if req.coach_mode:
            session = get_or_create_session(session_id)
            session.system_prompt = AI_COACH_SYSTEM_PROMPT
            
            # If context provided, prepend it to the message
            if req.context:
                context_str = "\n\nUSER CONTEXT:\n"
                if "goals" in req.context:
                    context_str += f"Goals: {req.context['goals']}\n"
                if "recent_workouts" in req.context:
                    context_str += f"Recent Activity: {req.context['recent_workouts']}\n"
                if "stats" in req.context:
                    context_str += f"Stats: {req.context['stats']}\n"
                
                # Prepend context to user message
                message_with_context = req.message + context_str
            else:
                message_with_context = req.message
        else:
            message_with_context = req.message
        
        # Generate response using configured LLM provider
        response_text = await generate_chat_response(
            message=message_with_context,
            session_id=session_id,
            temperature=0.3 if req.coach_mode else 0.7,  # Lower temp for coaching
        )
        
        # Determine which provider was used
        from app.services.llm import get_llm_provider
        provider = get_llm_provider()
        provider_name = provider.get_provider_name()
        
        logger.info(
            f"[CHAT] ✓ Response generated ({provider_name}): "
            f"{len(response_text)} chars"
        )
        
        return ChatResponse(
            message=response_text,
            session_id=session_id,
            provider=provider_name,
        )
    
    except Exception as e:
        logger.error(f"[CHAT] Error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Chat error: {str(e)}"
        )

@router.get("/chat/{session_id}/history")
async def get_chat_history(session_id: str):
    """
    Get message history for a chat session.
    
    Returns all messages in the session including user and assistant messages.
    """
    try:
        from app.services.chatbot import get_session_history
        
        history = get_session_history(session_id)
        
        if history is None:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        return {
            "session_id": session_id,
            "messages": history,
            "message_count": len(history),
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[CHAT-HISTORY] Error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving history: {str(e)}"
        )

@router.post("/chat/{session_id}/clear")
async def clear_chat_session(session_id: str):
    """Clear all messages from a chat session"""
    try:
        from app.services.chatbot import clear_session
        
        success = clear_session(session_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        logger.info(f"[CHAT] Cleared session {session_id}")
        
        return {
            "status": "cleared",
            "session_id": session_id,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[CHAT-CLEAR] Error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing session: {str(e)}"
        )

# ===== MEAL PLAN GENERATION =====
@router.post("/mealplan/generate")
async def generate_meal_plan(
    req: MealPlanRequest,
    user = Depends(get_current_user)
):
    """Generate AI meal plan"""
    return await MealPlanGenerator.generate_meal_plan(
        daily_calories=req.daily_calories,
        macro_targets=req.macro_targets,
        diet_type=req.diet_type,
        restrictions=req.restrictions or []
    )

@router.post("/workout/generate")
async def generate_workout_plan(
    req: WorkoutPlanRequest,
    user = Depends(get_current_user)
):
    """Generate AI workout plan"""
    return await WorkoutPlanGenerator.generate_workout_plan(
        goal=req.goal,
        level=req.level,
        frequency=req.frequency,
        equipment=req.equipment,
        duration_weeks=req.duration_weeks
    )

@router.post("/insights/generate")
async def generate_insights(
    req: InsightsRequest,
    user = Depends(get_current_user)
):
    """Generate personalized insights"""
    return await InsightAnalyzer.generate_insights(
        daily_logs=req.daily_logs,
        workouts=req.workouts
    )

@router.get("/insights")
async def get_insights(user = Depends(get_current_user)):
    """Get previously generated insights"""
    return {
        "message": "Fetch from database"
    }

@router.get("/trends")
async def get_trends(user = Depends(get_current_user)):
    """Get trend analysis"""
    return {
        "message": "Analyze patterns"
    }

# ===== RECIPE EXTRACTION =====
@router.post("/extract-recipe", response_model=RecipeExtractionResponse)
async def extract_recipe(req: RecipeExtractionRequest, background_tasks: BackgroundTasks):
    """
    Extract recipe from video URL using AI pipeline
    
    Supports:
    - TikTok videos
    - Instagram Reels
    - YouTube videos
    
    Returns task_id for status polling
    """
    logger.info(f"[EXTRACT-RECIPE] New extraction request - URL: {req.url}")
    
    # Validate URL
    if not req.url.startswith(('http://', 'https://')):
        raise HTTPException(status_code=400, detail="Invalid URL format")
    
    task_id = str(uuid.uuid4())[:12]
    
    # Store task status
    extraction_tasks[task_id] = {
        "status": "processing",
        "url": req.url,
        "result": None,
        "error": None,
    }
    
    # Start extraction in background
    background_tasks.add_task(_extract_recipe_background, req.url, task_id)
    
    logger.info(f"[EXTRACT-RECIPE] Task {task_id} queued")
    
    return RecipeExtractionResponse(
        task_id=task_id,
        status="processing",
        title=None
    )

@router.get("/extract-recipe/{task_id}/status", response_model=RecipeExtractionResponse)
async def get_extraction_status(task_id: str):
    """Get recipe extraction task status"""
    
    logger.info(f"[EXTRACT-RECIPE-STATUS] Status query for task: {task_id}")
    
    if task_id not in extraction_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = extraction_tasks[task_id]
    status = task.get("status")
    
    logger.info(f"[EXTRACT-RECIPE-STATUS] Task {task_id}: {status}")
    
    if status == "processing":
        return RecipeExtractionResponse(
            task_id=task_id,
            status="processing",
            title=None
        )
    
    elif status == "completed":
        result = task.get("result", {})
        recipe = result.get("recipe", {})
        
        return RecipeExtractionResponse(
            task_id=task_id,
            status="completed",
            title=recipe.get("title"),
            description=recipe.get("description"),
            ingredients=[
                RecipeIngredient(
                    name=ing.get("name"),
                    quantity=ing.get("quantity"),
                    unit=ing.get("unit")
                )
                for ing in recipe.get("ingredients", [])
            ],
            steps=[
                RecipeStep(
                    step=step.get("step"),
                    instruction=step.get("instruction")
                )
                for step in recipe.get("steps", [])
            ],
            cook_time_minutes=recipe.get("cook_time_minutes"),
            prep_time_minutes=recipe.get("prep_time_minutes"),
            difficulty=recipe.get("difficulty"),
            servings=recipe.get("servings"),
            macros=MacroInfo(
                calories=recipe.get("macros", {}).get("calories"),
                protein=recipe.get("macros", {}).get("protein"),
                carbs=recipe.get("macros", {}).get("carbs"),
                fat=recipe.get("macros", {}).get("fat"),
            )
        )
    
    elif status == "failed":
        error = task.get("error")
        logger.error(f"[EXTRACT-RECIPE-STATUS] Task {task_id} failed: {error}")
        
        return RecipeExtractionResponse(
            task_id=task_id,
            status="failed",
            error=error
        )
    
    else:
        return RecipeExtractionResponse(
            task_id=task_id,
            status="unknown"
        )

# ===== BACKGROUND TASK =====
async def _extract_recipe_background(video_url: str, task_id: str):
    """Background task for recipe extraction"""
    try:
        logger.info(f"[BACKGROUND] Starting extraction for task {task_id}: {video_url}")
        
        # Run the REAL AI pipeline
        result = await RecipeExtractionPipeline.extract_recipe_from_video(video_url)
        
        if result.get("status") == "success":
            extraction_tasks[task_id]["status"] = "completed"
            extraction_tasks[task_id]["result"] = result
            logger.info(f"[BACKGROUND] Task {task_id} completed successfully")
        else:
            error = result.get("error", "Unknown error")
            extraction_tasks[task_id]["status"] = "failed"
            extraction_tasks[task_id]["error"] = error
            logger.error(f"[BACKGROUND] Task {task_id} failed: {error}")
    
    except Exception as e:
        logger.error(f"[BACKGROUND] Task {task_id} exception: {e}")
        extraction_tasks[task_id]["status"] = "failed"
        extraction_tasks[task_id]["error"] = str(e)

