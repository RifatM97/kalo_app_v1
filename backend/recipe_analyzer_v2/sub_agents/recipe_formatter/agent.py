"""Recipe Formatter Agent - Formats raw recipe data into structured format"""

import logging
from google.adk.agents import Agent
from typing import List, Dict
from ...models.schemas import RecipeCard
import json


logger = logging.getLogger(__name__)


def parse_ingredients_from_text(ingredients_text: str) -> List[Dict]:
    """
    Parse ingredient list from text into structured format.

    Args:
        ingredients_text: Raw text containing ingredients

    Returns:
        List of ingredient dictionaries
    """
    import re

    ingredients = []
    lines = ingredients_text.strip().split('\n')

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        # Remove bullet points, numbers, dashes
        line = re.sub(r'^[-•*\d.)\s]+', '', line)

        # Try to parse quantity, unit, and name
        # Pattern: number unit name
        pattern = r'(\d+(?:\.\d+)?(?:/\d+)?)\s*([a-zA-Z]+)?\s+(.+)'
        match = re.match(pattern, line)

        if match:
            quantity_str = match.group(1)
            # Handle fractions like 1/2
            if '/' in quantity_str:
                parts = quantity_str.split('/')
                quantity = float(parts[0]) / float(parts[1])
            else:
                quantity = float(quantity_str)

            unit = match.group(2) if match.group(2) else "unit"
            rest = match.group(3)

            # Split name and notes on comma
            parts = rest.split(',', 1)
            name = parts[0].strip()
            notes = parts[1].strip() if len(parts) > 1 else None

            ingredients.append({
                "name": name,
                "quantity": quantity,
                "unit": unit,
                "notes": notes
            })
        else:
            # If no quantity found, add as-is
            ingredients.append({
                "name": line,
                "quantity": 0,
                "unit": "to taste",
                "notes": None
            })

    return ingredients


def parse_steps_from_text(steps_text: str) -> List[Dict]:
    """
    Parse cooking steps from text into structured format.

    Args:
        steps_text: Raw text containing cooking steps

    Returns:
        List of step dictionaries
    """
    import re

    steps = []
    lines = steps_text.strip().split('\n')

    step_number = 1
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        # Remove step numbers if present
        line = re.sub(r'^\d+[\.)]\s*', '', line)
        line = re.sub(r'^[-•*]\s*', '', line)

        # Extract duration if present
        duration_match = re.search(r'\((\d+\s*(?:min|mins|minutes|sec|seconds))\)', line, re.IGNORECASE)
        duration = duration_match.group(1) if duration_match else None

        steps.append({
            "step_number": step_number,
            "instruction": line,
            "duration": duration
        })
        step_number += 1

    return steps


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