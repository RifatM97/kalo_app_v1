"""Tools for ingredient manipulation and scaling"""

from typing import List, Dict


def scale_ingredients(ingredients: List[Dict], original_servings: int, target_servings: int) -> List[Dict]:
    """
    Scale ingredient quantities from original servings to target servings.

    Args:
        ingredients: List of ingredient dicts with name, quantity, unit
        original_servings: Original number of servings
        target_servings: Desired number of servings

    Returns:
        List of scaled ingredients with updated quantities
    """
    if original_servings <= 0:
        raise ValueError("Original servings must be greater than 0")

    if target_servings <= 0:
        raise ValueError("Target servings must be greater than 0")

    scale_factor = target_servings / original_servings

    scaled_ingredients = []
    for ingredient in ingredients:
        scaled = ingredient.copy()
        if "quantity" in scaled and isinstance(scaled["quantity"], (int, float)):
            scaled["quantity"] = round(scaled["quantity"] * scale_factor, 2)
        scaled_ingredients.append(scaled)

    return scaled_ingredients


def parse_ingredient_string(ingredient_str: str) -> Dict:
    """
    Parse a natural language ingredient string into structured data.

    Args:
        ingredient_str: String like "200g spaghetti" or "2 tbsp olive oil"

    Returns:
        Dict with name, quantity, unit, and notes
    """
    import re

    # Pattern: quantity unit name (notes)
    # Examples: "200g pasta", "2 cups flour, sifted", "3 cloves garlic, minced"

    # Try to extract quantity and unit
    pattern = r'^(\d+(?:\.\d+)?)\s*([a-zA-Z]+)?\s+(.+)$'
    match = re.match(pattern, ingredient_str.strip())

    if match:
        quantity = float(match.group(1))
        unit = match.group(2) if match.group(2) else "unit"
        rest = match.group(3)

        # Split on comma to separate name and notes
        parts = rest.split(',', 1)
        name = parts[0].strip()
        notes = parts[1].strip() if len(parts) > 1 else None

        return {
            "name": name,
            "quantity": quantity,
            "unit": unit,
            "notes": notes
        }

    # If no pattern match, return as-is
    return {
        "name": ingredient_str.strip(),
        "quantity": 0,
        "unit": "to taste",
        "notes": None
    }
