"""Recipe Formatter Agent - Formats raw recipe data into structured format"""

import logging
from google.adk.agents import Agent
from typing import List, Dict
from ...models.schemas import RecipeCard
import json

logger = logging.getLogger(__name__)

### To do: Implement number of servings scaling in ingredient parsing


# Create recipe formatter agent
recipe_formatter_agent = Agent(
    name="recipe_formatter",
    model="gemini-2.5-flash-lite",
    description="Formats raw recipe data into structured, clean recipe cards.",
    instruction=f"""
    You are a Recipe Formatter. Your task is to transform raw recipe analysis into a structured JSON object. 
    
    Processing Steps:
    1. Parse ingredients and scale them to the requested number of servings.
    2. Standardize all measurements to culinary units (g, ml, cups, tbsp, etc.).
    3. Determine the difficulty level based on complexity.
    4. Estimate nutritional information per serving.
    
    Respond ONLY with a JSON object conforming to the output_schema. Do not include any text before or after the JSON.
    Match with this exact schema:
    "{json.dumps(RecipeCard.model_json_schema(), indent=2)}"

    Return a comprehensive RecipeCard in JSON with all details.
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