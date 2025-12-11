"""
Celery Tasks for KALO Backend
Handles asynchronous processing of recipe extraction, meal planning, etc.
"""
from app.celery_app import app
from app.ai.recipe_extractor import RecipeExtractionPipeline
import logging
import asyncio

logger = logging.getLogger(__name__)

@app.task(bind=True, name='app.tasks.recipe.extract')
def async_extract_recipe(self, video_url: str):
    """
    Celery task for recipe extraction
    
    Args:
        video_url: URL to TikTok, Instagram, or YouTube video
    
    Returns:
        Recipe data in JSON format
    """
    try:
        logger.info(f"[CELERY] Starting recipe extraction for: {video_url}")
        
        # Run async pipeline in event loop
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            RecipeExtractionPipeline.extract_recipe_from_video(video_url)
        )
        
        if result.get("status") == "success":
            logger.info(f"[CELERY] Recipe extraction successful: {result['recipe'].get('title')}")
            return {
                "status": "success",
                "data": result["recipe"],
            }
        else:
            error = result.get("error", "Unknown error")
            logger.error(f"[CELERY] Recipe extraction failed: {error}")
            return {
                "status": "failed",
                "error": error,
            }
    
    except Exception as e:
        logger.error(f"[CELERY] Task failed with exception: {e}")
        raise self.retry(exc=e, countdown=60, max_retries=3)
