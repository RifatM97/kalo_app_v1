"""Orchestrator Agent - Coordinates the multi-agent workflow"""

import logging
from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LlmAgent
from .sub_agents.video_analyzer.agent import video_analyzer_agent
from .sub_agents.recipe_formatter.agent import recipe_formatter_agent
from .sub_agents.nutrition.agent import nutrition_calculator_agent
from .models.schemas import RecipeCardWithNutrition

logger = logging.getLogger(__name__)

# Parallel agent: recipe formatter + nutrition calculator run simultaneously
parallel_processing_agent = ParallelAgent(
    name="recipe_processing_parallel_agent",
    sub_agents=[recipe_formatter_agent, nutrition_calculator_agent],
    description="Processes recipe data in parallel: formatting recipe card and nutrition calculation."
)

# Combiner agent: merges parallel outputs into single structure
combine_parallel = LlmAgent(
    name="combine_outputs",
    model="gemini-2.5-flash-lite",
    instruction="""
    Combine the outputs from the recipe formatter (formatted_recipe_card) and
    nutrition calculator (nutrition_per_serving) into a single RecipeCardWithNutrition object.

    The formatted_recipe_card contains all recipe details (title, ingredients, steps, etc.).
    The nutrition_per_serving contains nutritional information.

    Merge them by taking all fields from formatted_recipe_card and adding the
    nutrition_per_serving data as the "nutrition" field.

    Return a complete RecipeCardWithNutrition JSON object.
    """,
    output_schema=RecipeCardWithNutrition,
)

# Create sequential workflow: video analysis → parallel processing → combine results
overall_workflow = SequentialAgent(
    name="recipe_analysis_workflow",
    sub_agents=[video_analyzer_agent, parallel_processing_agent, combine_parallel]
)

root_agent = overall_workflow