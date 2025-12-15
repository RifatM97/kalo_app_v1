"""Orchestrator Agent - Coordinates the multi-agent workflow"""

import logging
from google.adk.agents import Agent
from .video_analyzer import video_analyzer_agent
from .recipe_formatter import recipe_formatter_agent
from .nutrition_calculator import nutrition_calculator_agent
from ..tools.youtube_tools import download_youtube_video, extract_video_id

logger = logging.getLogger(__name__)


# def download_and_prepare_video(youtube_url: str) -> dict:
#     """
#     Download YouTube video and prepare for analysis.

#     Args:
#         youtube_url: YouTube Shorts or video URL

#     Returns:
#         Dictionary with video information and file path
#     """
#     try:
#         video_id = extract_video_id(youtube_url)
#         video_info = download_youtube_video(youtube_url, output_dir="recipe_analyzer/outputs")

#         logger.info(f"Downloaded video: {video_id}")
#         return video_info

#     except Exception as e:
#         logger.error(f"Failed to download video: {e}")
#         raise


# Create orchestrator agent with sub-agents
orchestrator_agent = Agent(
    name="recipe_orchestrator",
    model="gemini-2.5-flash",
    description="Orchestrates the complete recipe analysis workflow from YouTube URL to formatted recipe card.",
    instruction="""
    You are the orchestrator for a YouTube recipe analyzer system.

    Your workflow:
    1. Delegate to video_analyzer to extract recipe information from the input video url
    2. Delegate to recipe_formatter to structure the raw data into a clean recipe card
    3. Delegate to nutrition_calculator to compute nutritional information per serving
    4. Combine all results into a final recipe card with nutrition data

    Coordination guidelines:
    - Ensure each agent receives the correct input from previous steps
    - Handle errors gracefully at each stage
    - Pass the target number of servings through the pipeline
    - Validate that all required information is present before final output

    Always follow the complete workflow in order.
    Return a comprehensive RecipeCard with all details and nutrition information.
    """,
    sub_agents=[
        video_analyzer_agent,
        recipe_formatter_agent,
        nutrition_calculator_agent
    ]
)
