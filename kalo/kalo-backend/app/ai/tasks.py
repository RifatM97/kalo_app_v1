"""
Celery Background Tasks
Async task processing for long-running AI operations
"""

import asyncio
import logging
import os
from typing import Dict, Optional
from celery import shared_task, Task
from celery.exceptions import SoftTimeLimitExceeded
from datetime import datetime

logger = logging.getLogger(__name__)


class CallbackTask(Task):
    """Task with callbacks for success/failure"""
    def on_success(self, retval, task_id, args, kwargs):
        logger.info(f"✅ Task {task_id} completed successfully")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"❌ Task {task_id} failed: {exc}")


@shared_task(
    base=CallbackTask,
    bind=True,
    max_retries=3,
    soft_time_limit=1800,  # 30 minutes
    time_limit=1900,  # 31m 40s hard limit
    name="extract_recipe_async"
)
def extract_recipe_async(
    self,
    video_url: str,
    user_id: str,
    recipe_id: str,
    task_id: Optional[str] = None
) -> Dict:
    """
    Extract recipe from video asynchronously using AI pipeline
    
    Complete flow:
    1. Download video from URL (yt-dlp)
    2. Extract audio (ffmpeg)
    3. Extract frames (ffmpeg)
    4. Transcribe audio (Whisper)
    5. Extract text from frames (PaddleOCR)
    6. Detect ingredients (YOLOv8)
    7. Structure recipe (LLM)
    
    Args:
        video_url: URL to video (TikTok, Instagram, YouTube)
        user_id: User ID who requested extraction
        recipe_id: Recipe ID for tracking
        task_id: Celery task ID (optional)
        
    Returns:
        Structured recipe data matching Swift model exactly
        
    Raises:
        Exception: On extraction failure (retried with exponential backoff)
    """
    task_id = task_id or self.request.id
    
    try:
        from app.ai.ai_pipeline import extract_recipe_from_video
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🎬 RECIPE EXTRACTION TASK STARTED")
        logger.info(f"{'='*60}")
        logger.info(f"Task ID: {task_id}")
        logger.info(f"User ID: {user_id}")
        logger.info(f"Recipe ID: {recipe_id}")
        logger.info(f"Video URL: {video_url}")
        logger.info(f"Timestamp: {datetime.utcnow().isoformat()}")
        
        # Update task progress
        self.update_state(state="PROGRESS", meta={"progress": 0, "status": "Downloading video..."})
        
        # Get OpenAI API key from environment
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            logger.warning("⚠️  OPENAI_API_KEY not set - LLM structuring will use fallback")
        
        # Run extraction pipeline
        logger.info(f"\n[1/7] Initializing async event loop...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            logger.info(f"[2/7] Running AI extraction pipeline...")
            recipe_data = loop.run_until_complete(
                extract_recipe_from_video(
                    video_url=video_url,
                    num_frames=5,
                    cleanup=True,
                    llm_api_key=openai_api_key
                )
            )
        finally:
            loop.close()
        
        logger.info(f"\n✅ EXTRACTION PIPELINE COMPLETE")
        logger.info(f"Recipe Title: {recipe_data.get('title', 'Unknown')}")
        logger.info(f"Ingredients: {len(recipe_data.get('ingredients', []))}")
        logger.info(f"Steps: {len(recipe_data.get('steps', []))}")
        
        # Ensure response matches Swift model exactly
        response_data = {
            "id": None,  # Will be set by Swift if needed
            "task_id": task_id,
            "title": recipe_data.get("title", "Unknown Recipe"),
            "description": recipe_data.get("description", ""),
            "ingredients": recipe_data.get("ingredients", []),
            "steps": recipe_data.get("steps", []),
            "cook_time_minutes": recipe_data.get("cook_time_minutes", 0),
            "prep_time_minutes": recipe_data.get("prep_time_minutes", 0),
            "difficulty": recipe_data.get("difficulty", "medium"),
            "servings": recipe_data.get("serves", 1),
            "macros": recipe_data.get("macros", {
                "calories": 0,
                "protein": 0,
                "carbs": 0,
                "fat": 0
            }),
            "status": "completed"
        }
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ TASK COMPLETED SUCCESSFULLY")
        logger.info(f"{'='*60}\n")
        
        return response_data
    
    except SoftTimeLimitExceeded:
        logger.warning(f"⏱️  SOFT TIME LIMIT EXCEEDED for recipe_id={recipe_id}")
        logger.info(f"Retrying with exponential backoff (attempt {self.request.retries + 1}/3)")
        
        raise self.retry(
            countdown=60 * (2 ** self.request.retries),
            exc=Exception("Task timeout - retrying")
        )
    
    except Exception as e:
        logger.error(f"\n❌ EXTRACTION FAILED")
        logger.error(f"Recipe ID: {recipe_id}")
        logger.error(f"Error: {str(e)}", exc_info=True)
        
        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            countdown = 60 * (2 ** self.request.retries)
            logger.info(f"⚙️  Retrying in {countdown}s (attempt {self.request.retries + 1}/{self.max_retries})")
            
            raise self.retry(
                exc=e,
                countdown=countdown
            )
        else:
            logger.error(f"❌ MAX RETRIES EXCEEDED for recipe_id={recipe_id}")
            
            # Return failure response
            return {
                "id": None,
                "task_id": task_id,
                "status": "failed",
                "error": f"Recipe extraction failed after {self.max_retries} retries: {str(e)}",
                "title": None,
                "ingredients": None,
                "steps": None
            }


@shared_task(bind=True, max_retries=3)
def generate_meal_plan_async(self, user_id: str, days: int = 7, calories: int = 2000) -> Dict:
    """
    Generate AI meal plan asynchronously
    
    Args:
        user_id: User ID
        days: Number of days to plan
        calories: Target daily calories
        
    Returns:
        Meal plan data
    """
    try:
        from app.ai.meal_planner import MealPlanGenerator
        
        logger.info(f"Generating meal plan for user_id={user_id}")
        
        generator = MealPlanGenerator()
        meal_plan = generator.generate(
            user_id=user_id,
            days=days,
            target_calories=calories
        )
        
        logger.info(f"✓ Meal plan generated for user_id={user_id}")
        
        return {
            "status": "success",
            "user_id": user_id,
            "days": days,
            "meals_generated": len(meal_plan.get("meals", []))
        }
        
    except Exception as e:
        logger.error(f"Meal plan generation failed: {e}")
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def generate_workout_plan_async(
    self,
    user_id: str,
    experience: str = "intermediate",
    goal: str = "muscle_gain",
    weeks: int = 12
) -> Dict:
    """
    Generate AI workout plan asynchronously
    
    Args:
        user_id: User ID
        experience: Experience level (beginner, intermediate, advanced)
        goal: Fitness goal (muscle_gain, fat_loss, endurance)
        weeks: Plan duration in weeks
        
    Returns:
        Workout plan data
    """
    try:
        from app.ai.workout_generator import WorkoutPlanGenerator
        
        logger.info(f"Generating workout plan for user_id={user_id}")
        
        generator = WorkoutPlanGenerator()
        workout_plan = generator.generate(
            user_id=user_id,
            experience=experience,
            goal=goal,
            weeks=weeks
        )
        
        logger.info(f"✓ Workout plan generated for user_id={user_id}")
        
        return {
            "status": "success",
            "user_id": user_id,
            "weeks": weeks,
            "workouts_generated": len(workout_plan.get("weeks", []))
        }
        
    except Exception as e:
        logger.error(f"Workout plan generation failed: {e}")
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=2)
def verify_challenge_proof_async(
    self,
    user_id: str,
    challenge_id: str,
    proof_type: str,
    proof_url: str
) -> Dict:
    """
    Verify challenge proof asynchronously (image/GPS/data)
    
    Args:
        user_id: User ID
        challenge_id: Challenge ID
        proof_type: Type of proof (photo, gps, data)
        proof_url: URL to proof file
        
    Returns:
        Verification result
    """
    try:
        from app.ai.proof_verifier import verify_proof
        
        logger.info(f"Verifying proof for user_id={user_id}, challenge_id={challenge_id}")
        
        verification = verify_proof(
            proof_type=proof_type,
            proof_url=proof_url
        )
        
        logger.info(f"✓ Proof verified for user_id={user_id}")
        
        return {
            "status": "success",
            "user_id": user_id,
            "challenge_id": challenge_id,
            "verified": verification.get("valid", False),
            "confidence": verification.get("confidence", 0)
        }
        
    except Exception as e:
        logger.error(f"Proof verification failed: {e}")
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True)
def generate_insights_async(self, user_id: str) -> Dict:
    """
    Generate personalized insights asynchronously
    
    Args:
        user_id: User ID
        
    Returns:
        Insights data
    """
    try:
        from app.ai.insights_engine import InsightGenerator
        
        logger.info(f"Generating insights for user_id={user_id}")
        
        generator = InsightGenerator()
        insights = generator.generate(user_id=user_id)
        
        logger.info(f"✓ Insights generated for user_id={user_id}")
        
        return {
            "status": "success",
            "user_id": user_id,
            "insights_count": len(insights.get("insights", []))
        }
        
    except Exception as e:
        logger.error(f"Insight generation failed: {e}")
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True)
def cleanup_old_extractions(self, days: int = 7) -> Dict:
    """
    Cleanup old extracted files from disk
    
    Args:
        days: Delete files older than this many days
        
    Returns:
        Cleanup statistics
    """
    try:
        import os
        from pathlib import Path
        from datetime import datetime, timedelta
        
        logger.info(f"Cleaning up files older than {days} days")
        
        dirs_to_clean = [
            "/tmp/kalo_videos",
            "/tmp/kalo_audio",
            "/tmp/kalo_frames"
        ]
        
        cutoff_time = datetime.now() - timedelta(days=days)
        total_deleted = 0
        total_size = 0
        
        for directory in dirs_to_clean:
            if not os.path.exists(directory):
                continue
            
            for root, dirs, files in os.walk(directory):
                for file in files:
                    filepath = Path(root) / file
                    mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
                    
                    if mtime < cutoff_time:
                        try:
                            size = filepath.stat().st_size
                            filepath.unlink()
                            total_deleted += 1
                            total_size += size
                        except Exception as e:
                            logger.warning(f"Failed to delete {filepath}: {e}")
        
        logger.info(f"✓ Cleanup complete: {total_deleted} files, {total_size / (1024*1024):.2f}MB freed")
        
        return {
            "status": "success",
            "files_deleted": total_deleted,
            "space_freed_mb": total_size / (1024 * 1024)
        }
        
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        raise self.retry(exc=e, countdown=300)
