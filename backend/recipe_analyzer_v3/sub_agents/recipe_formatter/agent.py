"""Recipe Formatter Agent - Formats raw recipe data into structured format"""

import logging
from google.adk.agents import Agent
from typing import List, Dict
from ...models.schemas import RecipeCard
import json

logger = logging.getLogger(__name__)

# Create recipe formatter agent
recipe_formatter_agent = Agent(
    name="recipe_formatter",
    model="gemini-2.5-flash-lite",
    description="Formats raw recipe data into structured, clean recipe cards.",
    instruction=f"""
    You are a Recipe Formatter. Your task is to transform raw recipe analysis into a structured JSON object.

    Input Processing:
    1. Parse the input to extract:
       - Recipe analysis (the main content)
       - User Context section containing "Target Servings" value
    2. Use the Target Servings value to scale ALL ingredient quantities appropriately
    3. If Target Servings is not found in the input, default to the servings mentioned in the recipe

    Processing Steps:
    1. Parse ingredients and SCALE them to the Target Servings number
    2. Standardize all measurements to culinary units (g, ml, cups, tbsp, etc.)
    3. Determine the difficulty level based on complexity
    4. Set the "servings" field in the output to the Target Servings value

    IMPORTANT Scaling Instructions:
    - If the recipe originally serves X people and Target Servings is Y, multiply all ingredient quantities by (Y/X)
    - Example: Recipe for 4 servings with 200g flour, Target Servings is 2 → use 100g flour
    - Ensure the "servings" field in your output matches the Target Servings value

    Respond ONLY with a JSON object conforming to the output_schema. Do not include any text before or after the JSON.
    Match with this exact schema:
    "{json.dumps(RecipeCard.model_json_schema(), indent=2)}"

    Return a comprehensive RecipeCard in JSON with all details scaled to Target Servings.
    """,
    output_schema=RecipeCard,
    output_key="formatted_recipe_card"
)


# Format example:
#     {
#       "title": "Recipe Title",
#       "source_url": "url",
#       "servings": 2,
#       "ingredients": [{"name": "onion", "quantity": 1, "unit": "whole", "preparation": "diced"}],
#       "steps": [{"step_number": 1, "instruction": "...", "duration_minutes": 5}],
#       "nutrition_per_serving": {"calories": 250},
#       "tips": [],
#       "tags": []
#     }
#     """