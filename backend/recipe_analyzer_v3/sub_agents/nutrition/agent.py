"""Nutrition Calculator Agent - Calculates nutritional information for recipes"""

import logging
from google.adk.agents import Agent
from ...tools.nutrition_tools import lookup_nutrition_data, calculate_recipe_nutrition
from google.adk.tools import google_search
from ...data.database import user_profile, users_db


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

def get_user_calories(user_name: str) -> int:
    """
    Get user's daily calorie needs from the user database.

    Args:
        user_name: User's full name
    Returns:
        Daily calorie needs in kcal
    """
    # Search for user by name in the database
    for user_id, user_data in users_db.items():
        if user_data["name"].lower() == user_name.lower():
            return user_data["daily_calorie_intake"]

    # Default fallback if user not found
    logger.warning(f"User '{user_name}' not found in database, using default profile")
    return user_profile["daily_calorie_intake"]
    


# Create nutrition calculator agent
nutrition_calculator_agent = Agent(
    name="nutrition_calculator",
    model="gemini-2.5-flash-lite",
    description="Calculates accurate nutritional information for recipes.",
    instruction="""
    You are a nutrition calculator specialized in recipe analysis.

    Input Processing:
    1. Parse the input to extract:
       - Recipe analysis (the main content with ingredients)
       - User Context section containing "User Name" value
    2. Use the User Name to fetch personalized calorie information
    3. If User Name is not found in the input, default to "John Doe"

    Your task is to:
    1. Parse the ingredient list from the raw recipe_analysis
    2. Look up nutritional data for each ingredient using the get_ingredient_nutrition_info tool
    3. Compute per-serving nutritional breakdown using the calculate_nutrition_per_serving tool
    4. Use the User Name from the input to call get_user_calories tool (e.g., get_user_calories("Alice"))
    5. Compare total calories against the user's daily needs
    6. Return a structured nutrition summary, including the user's daily calorie comparison

    Required nutritional values to calculate:
    - Calories (kcal)
    - Protein (g)
    - Fat (g)
    - Carbohydrates (g)
    - Calories percentage of daily needs (calculated from user's daily calorie intake)

    Guidelines:
    - Extract the User Name from the "User Context" section in the input
    - Call get_user_calories with the extracted user name
    - Provide per-serving calculations based on the recipe servings
    - Calculate percentage: (calories_per_serving / user_daily_calories) * 100
    - Round values to one decimal place for readability
    - Include the user's name in your analysis for personalization

    Use the calculate_nutrition_per_serving, get_ingredient_nutrition_info tools and get_user_calories tool as needed.
    Always provide accurate, personalized, per-person nutritional information.
    """,
    tools=[get_ingredient_nutrition_info, calculate_nutrition_per_serving, get_user_calories],
    output_key="nutrition_per_serving"
)
