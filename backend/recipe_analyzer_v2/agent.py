"""Orchestrator Agent - Coordinates the multi-agent workflow"""

import logging
from google.adk.agents import Agent
from .sub_agents.video_analyzer.agent import video_analyzer_agent
from .sub_agents.recipe_formatter.agent import recipe_formatter_agent
from .sub_agents.nutrition.agent import nutrition_calculator_agent

logger = logging.getLogger(__name__)


# Create orchestrator agent with sub-agents
orchestrator_agent = Agent(
    name="recipe_orchestrator",
    model="gemini-2.5-flash-lite",
    description="Orchestrates the complete recipe analysis workflow from YouTube URL to formatted recipe card.",
    instruction=f"""
    You are the orchestrator for a YouTube recipe analyzer system.

    Your workflow:
    1. Delegate to video_analyzer to extract recipe information from the input video url.
    2. Delegate the "{recipe_formatter_agent}" to structure the raw recipe_analysis instructions into a clean recipe card

    Coordination guidelines:
    - Ensure the sub-agent receives the correct input from previous steps
    - Handle errors gracefully at each stage
    - Pass the target number of servings through the pipeline
    - Validate that all required information is present before final output

    Always follow the complete workflow in order.
    """,
    sub_agents=[
        video_analyzer_agent,
        recipe_formatter_agent,
    ],
    output_key="recipe_analysis"
)

root_agent = orchestrator_agent

# 2. Use the recipe analysis instructions from "{video_analyzer_agent}" to format a structured recipe card using "{recipe_formatter_agent}".