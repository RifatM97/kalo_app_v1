"""Orchestrator Agent - Coordinates the multi-agent workflow"""

import logging
from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LlmAgent
from .sub_agents.video_analyzer.agent import video_analyzer_agent
from .sub_agents.recipe_formatter.agent import recipe_formatter_agent
from .sub_agents.nutrition.agent import nutrition_calculator_agent
from .models.schemas import RecipeCardWithNutrition

logger = logging.getLogger(__name__)

# parallel agent : recipee formatter_agent , nutrition_calculator_agent
parallel_processing_agent = ParallelAgent(
    name="recipe_processing_parallel_agent",
    sub_agents=[recipe_formatter_agent, nutrition_calculator_agent],
    description="Processes recipe data in parallel: formatting recipe card and nutrition calculation."
)

combine_parallel = LlmAgent(
    name="combine_ouputs",
    model="gemini-2.5-flash-lite",
    instruction="Combines outputs from recipe formatter formatted_recipe_card and nutrition calculator nutrition_per_serving into a single structured output.",
    output_schema=RecipeCardWithNutrition,
    ## add output schema if needed : RecipeCard
    )

# Create sequential agent with sub-agents
overall_workflow = SequentialAgent(
    name="recipe_analysis_workflow",
    sub_agents=[video_analyzer_agent, combine_parallel]
    )

root_agent = overall_workflow