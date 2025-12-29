"""JSON formatter for saving and loading recipe data"""

import json
from pathlib import Path
from typing import Union
from ..models.schemas import RecipeCard


def save_recipe_json(recipe: RecipeCard, output_path: Union[str, Path]) -> None:
    """
    Save recipe to JSON file.

    Args:
        recipe: RecipeCard instance
        output_path: Path to save JSON file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(recipe.model_dump(), f, indent=2, ensure_ascii=False)


def save_recipe_markdown(recipe: RecipeCard, output_path: Union[str, Path]) -> None:
    """
    Save recipe to markdown file.

    Args:
        recipe: RecipeCard instance
        output_path: Path to save markdown file
    """
    from .recipe_card_formatter import format_recipe_card

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    md_content = format_recipe_card(recipe, output_format="markdown")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)


def load_recipe_json(input_path: Union[str, Path]) -> RecipeCard:
    """
    Load recipe from JSON file.

    Args:
        input_path: Path to JSON file

    Returns:
        RecipeCard instance
    """
    input_path = Path(input_path)

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return RecipeCard(**data)
