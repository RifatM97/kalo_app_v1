"""Nutrition Calculator Agent - Calculates nutritional information for recipes"""

import logging
from google.adk.agents import Agent
from ..tools.nutrition_tools import lookup_nutrition_data, calculate_recipe_nutrition

logger = logging.getLogger(__name__)


def calculate_nutrition_per_serving(ingredients: list[dict], servings: int) -> dict:
    """
    Calculate nutritional information per serving.

    Args:
        ingredients: List of ingredient dicts with name, quantity, unit
        servings: Number of servings

    Returns:
        Dictionary with nutrition per serving
    """
    if servings <= 0:
        raise ValueError("Servings must be greater than 0")

    # Calculate total nutrition
    total_nutrition = calculate_recipe_nutrition(ingredients)

    # Divide by servings
    return {
        "calories_kcal": round(total_nutrition["total_calories_kcal"] / servings, 1),
        "protein_g": round(total_nutrition["total_protein_g"] / servings, 1),
        "fat_g": round(total_nutrition["total_fat_g"] / servings, 1),
        "carbohydrates_g": round(total_nutrition["total_carbohydrates_g"] / servings, 1),
    }


def get_ingredient_nutrition_info(ingredient_name: str, quantity: float = 100.0, unit: str = "g") -> dict:
    """
    Get nutritional information for a single ingredient.

    Args:
        ingredient_name: Name of ingredient
        quantity: Quantity amount
        unit: Unit of measurement

    Returns:
        Nutritional information dictionary
    """
    return lookup_nutrition_data(ingredient_name, quantity, unit)


# Create nutrition calculator agent
nutrition_calculator_agent = Agent(
    name="nutrition_calculator",
    model="gemini-2.5-flash",
    description="Calculates accurate nutritional information for recipes.",
    instruction="""
    You are a nutrition calculator specialized in recipe analysis.

    Your task is to:
    1. Take a list of ingredients with quantities
    2. Look up nutritional data for each ingredient
    3. Calculate total nutritional values
    4. Compute per-serving nutritional breakdown

    Required nutrients to calculate:
    - Calories (kcal)
    - Protein (g)
    - Fat (g)
    - Carbohydrates (g)

    Guidelines:
    - Use standard nutritional databases for accuracy
    - Account for cooking methods that may change nutritional values
    - Provide per-serving calculations based on the recipe servings
    - Round values to one decimal place for readability

    Use the calculate_nutrition_per_serving and get_ingredient_nutrition_info tools.
    Always provide accurate, per-person nutritional information.
    """,
    tools=[calculate_nutrition_per_serving, get_ingredient_nutrition_info]
)
