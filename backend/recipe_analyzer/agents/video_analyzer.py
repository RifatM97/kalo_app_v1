"""Video Analyzer Agent - Analyzes YouTube cooking videos using Gemini"""

import logging
from google.adk.agents import Agent
from google import genai
from google.genai import types
import os
from pathlib import Path
import time

logger = logging.getLogger(__name__)


def analyze_video_with_gemini(video_url: str) -> dict:
    """
    Analyze a cooking video using Gemini's multimodal capabilities.

    Args:
        video_url: Original YouTube URL

    Returns:
        Dictionary with extracted recipe information
    """
    try:
        # Initialize Gemini client
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        client = genai.Client(api_key=api_key)

        # Upload video file
        # logger.info(f"Uploading video: {video_path}")
        # video_file = client.files.upload(file=video_path)

        # Create prompt for recipe extraction
        prompt = """
        Analyze this cooking video and extract all recipe information. Provide:

        1. Recipe title
        2. List of ALL ingredients mentioned (with approximate quantities if visible/mentioned)
        3. Step-by-step cooking instructions in order
        4. Estimated number of servings
        5. Estimated preparation time (in minutes)
        6. Estimated cooking time (in minutes)
        7. Difficulty level (Easy, Medium, or Hard)
        8. Cuisine type (if identifiable)
        9. Any cooking tips or tricks mentioned
        10. Tags (e.g., vegetarian, vegan, gluten-free, quick, healthy, halal)

        Pay close attention to:
        - Visual cues showing ingredients
        - Any text overlays with measurements
        - Spoken instructions
        - Timing of different steps

        Format your response as a structured analysis.
        """
        # --- ADD THIS WAIT BLOCK ---
        # print(f"\nFile is ready. State: {video_file.state.name}")
        # while video_file.state.name == "PROCESSING":
        #     print('.', end='', flush=True)
        #     time.sleep(15)
        #     video_file = client.files.get(name=video_file.name)

        # if video_file.state.name == "FAILED":
        #     raise ValueError(f"Video processing failed: {video_file.state.name}")
        # ---------------------------
        # print(f"File is ready. State: {video_file.state.name}")

        # Generate content with video
        logger.info("Analyzing video with Gemini...")
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=types.Content(
                parts=[
                    types.Part(
                        file_data=types.FileData(file_uri=video_url),
                        video_metadata=types.VideoMetadata(fps=0.1)
                    ),
                    types.Part(text=prompt)
                        ]
                )

        )

        analysis_text = response.text

        # Parse the response and extract structured data
        # For now, return the raw analysis
        return {
            "video_url": video_url,
            "analysis": analysis_text,
            # "video_file_id": video_file.name if hasattr(video_file, 'name') else None
        }

    except Exception as e:
        logger.error(f"Video analysis failed: {e}")
        raise RuntimeError(f"Failed to analyze video: {str(e)}")


# Create video analyzer agent
video_analyzer_agent = Agent(
    name="video_analyzer",
    model="gemini-2.5-flash-lite",
    description="Analyzes YouTube cooking videos to extract recipe information using multimodal AI.",
    instruction="""
    You are a video analyzer specialized in cooking videos.

    Your task is to:
    1. Take the YouTube Shorts URL as input
    2. Analyze the video content using Gemini's multimodal capabilities using the analyze_video_with_gemini tool
    3. Extract all recipe information including ingredients, steps, timing, and metadata

    When analyzing:
    - Pay attention to both visual and audio cues
    - Extract exact quantities when visible or mentioned
    - Note the sequence of cooking steps
    - Identify cooking techniques and tips
    - Detect dietary restrictions or cuisine types

    Always use the analyze_video_with_gemini tool to process videos.
    Return a comprehensive analysis with all extracted information.
    """,
    tools=[analyze_video_with_gemini],
    output_key="recipe_analysis"
)
