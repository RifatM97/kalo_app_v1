"""Nutrition data lookup and calculation tools"""

import logging
import httpx
from typing import Optional

logger = logging.getLogger(__name__)


def lookup_nutrition_data(ingredient: str, quantity: float = 100.0, unit: str = "g") -> dict:
    """
    Look up nutritional information for an ingredient.
    Uses Google search and estimation for nutritional data.

    Args:
        ingredient: Name of the ingredient
        quantity: Quantity amount
        unit: Unit of measurement

    Returns:
        Dictionary with calories, protein, fat, carbs per specified quantity
    """
    # Common nutritional database (per 100g)
    # In production, this would use a real API like USDA FoodData Central
    nutrition_db = {
        # Proteins
        "chicken breast": {"calories": 165, "protein": 31, "fat": 3.6, "carbs": 0},
        "beef": {"calories": 250, "protein": 26, "fat": 15, "carbs": 0},
        "salmon": {"calories": 208, "protein": 20, "fat": 13, "carbs": 0},
        "eggs": {"calories": 155, "protein": 13, "fat": 11, "carbs": 1.1},
        "tofu": {"calories": 76, "protein": 8, "fat": 4.8, "carbs": 1.9},

        # Carbs
        "rice": {"calories": 130, "protein": 2.7, "fat": 0.3, "carbs": 28},
        "pasta": {"calories": 131, "protein": 5, "fat": 1.1, "carbs": 25},
        "bread": {"calories": 265, "protein": 9, "fat": 3.2, "carbs": 49},
        "potato": {"calories": 77, "protein": 2, "fat": 0.1, "carbs": 17},
        "quinoa": {"calories": 120, "protein": 4.4, "fat": 1.9, "carbs": 21},

        # Vegetables
        "broccoli": {"calories": 34, "protein": 2.8, "fat": 0.4, "carbs": 7},
        "spinach": {"calories": 23, "protein": 2.9, "fat": 0.4, "carbs": 3.6},
        "tomato": {"calories": 18, "protein": 0.9, "fat": 0.2, "carbs": 3.9},
        "onion": {"calories": 40, "protein": 1.1, "fat": 0.1, "carbs": 9.3},
        "garlic": {"calories": 149, "protein": 6.4, "fat": 0.5, "carbs": 33},

        # Dairy
        "milk": {"calories": 42, "protein": 3.4, "fat": 1, "carbs": 5},
        "cheese": {"calories": 402, "protein": 25, "fat": 33, "carbs": 1.3},
        "yogurt": {"calories": 59, "protein": 10, "fat": 0.4, "carbs": 3.6},
        "cream": {"calories": 340, "protein": 2.1, "fat": 37, "carbs": 2.8},
        "butter": {"calories": 717, "protein": 0.9, "fat": 81, "carbs": 0.1},

        # Fats/Oils
        "olive oil": {"calories": 884, "protein": 0, "fat": 100, "carbs": 0},
        "coconut oil": {"calories": 862, "protein": 0, "fat": 100, "carbs": 0},

        # Nuts/Seeds
        "almonds": {"calories": 579, "protein": 21, "fat": 50, "carbs": 22},
        "walnuts": {"calories": 654, "protein": 15, "fat": 65, "carbs": 14},
    }

    # Normalize ingredient name
    ingredient_lower = ingredient.lower().strip()

    # Find matching ingredient
    nutrition = None
    for key, value in nutrition_db.items():
        if key in ingredient_lower or ingredient_lower in key:
            nutrition = value
            break

    # Default values if not found
    if nutrition is None:
        logger.warning(f"Nutrition data not found for: {ingredient}. Using estimates.")
        nutrition = {"calories": 50, "protein": 2, "fat": 1, "carbs": 10}

    # Scale to quantity (assuming database is per 100g)
    scale_factor = quantity / 100.0

    return {
        "ingredient": ingredient,
        "quantity": quantity,
        "unit": unit,
        "calories_kcal": round(nutrition["calories"] * scale_factor, 1),
        "protein_g": round(nutrition["protein"] * scale_factor, 1),
        "fat_g": round(nutrition["fat"] * scale_factor, 1),
        "carbohydrates_g": round(nutrition["carbs"] * scale_factor, 1),
    }


def calculate_recipe_nutrition(ingredients: list[dict]) -> dict:
    """
    Calculate total nutritional values for a recipe.

    Args:
        ingredients: List of ingredient dicts with name, quantity, unit

    Returns:
        Dictionary with total calories, protein, fat, carbs
    """
    total_calories = 0.0
    total_protein = 0.0
    total_fat = 0.0
    total_carbs = 0.0

    for ingredient in ingredients:
        nutrition = lookup_nutrition_data(
            ingredient["name"],
            ingredient["quantity"],
            ingredient["unit"]
        )

        total_calories += nutrition["calories_kcal"]
        total_protein += nutrition["protein_g"]
        total_fat += nutrition["fat_g"]
        total_carbs += nutrition["carbohydrates_g"]

    return {
        "total_calories_kcal": round(total_calories, 1),
        "total_protein_g": round(total_protein, 1),
        "total_fat_g": round(total_fat, 1),
        "total_carbohydrates_g": round(total_carbs, 1),
    }
