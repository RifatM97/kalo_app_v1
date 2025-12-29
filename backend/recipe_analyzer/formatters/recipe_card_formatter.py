"""Recipe card and nutrition table formatters for terminal output"""

from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from ..models.schemas import RecipeCard

console = Console()


def format_recipe_card(recipe: RecipeCard, output_format: str = "terminal") -> str:
    """
    Format recipe card for display.

    Args:
        recipe: RecipeCard instance
        output_format: 'terminal' for rich output, 'markdown' for markdown

    Returns:
        Formatted recipe card string
    """
    if output_format == "markdown":
        return _format_recipe_markdown(recipe)
    else:
        return _format_recipe_terminal(recipe)


def _format_recipe_markdown(recipe: RecipeCard) -> str:
    """Format recipe as markdown"""
    md = []
    md.append("=" * 70)
    md.append(f"                    🍳 RECIPE CARD")
    md.append("=" * 70)
    md.append("")
    md.append(f"**Title:** {recipe.title}")
    md.append(f"**Source:** {recipe.source_url}")
    md.append(f"**Servings:** {recipe.servings} people")

    time_info = []
    if recipe.prep_time_minutes:
        time_info.append(f"Prep: {recipe.prep_time_minutes} min")
    if recipe.cook_time_minutes:
        time_info.append(f"Cook: {recipe.cook_time_minutes} min")
    if time_info:
        md.append(f"**Time:** {' | '.join(time_info)}")

    md.append(f"**Difficulty:** {recipe.difficulty}")
    if recipe.cuisine:
        md.append(f"**Cuisine:** {recipe.cuisine}")
    md.append("")

    # Ingredients
    md.append("-" * 70)
    md.append("📝 INGREDIENTS (for {} people)".format(recipe.servings))
    md.append("-" * 70)
    md.append("")
    for ing in recipe.ingredients:
        if ing.notes:
            md.append(f"  • {ing.quantity}{ing.unit} {ing.name}, {ing.notes}")
        else:
            md.append(f"  • {ing.quantity}{ing.unit} {ing.name}")
    md.append("")

    # Instructions
    md.append("-" * 70)
    md.append("👨‍🍳 INSTRUCTIONS")
    md.append("-" * 70)
    md.append("")
    for step in recipe.steps:
        if step.duration:
            md.append(f"  {step.step_number}. {step.instruction} ({step.duration})")
        else:
            md.append(f"  {step.step_number}. {step.instruction}")
    md.append("")

    # Tips
    if recipe.tips:
        md.append("-" * 70)
        md.append("💡 TIPS")
        md.append("-" * 70)
        md.append("")
        for tip in recipe.tips:
            md.append(f"  • {tip}")
        md.append("")

    # Tags
    if recipe.tags:
        md.append(f"**Tags:** {', '.join(recipe.tags)}")
        md.append("")

    md.append("=" * 70)

    return "\n".join(md)


def _format_recipe_terminal(recipe: RecipeCard) -> None:
    """Format and print recipe using rich for terminal"""
    # Header
    header = Text()
    header.append("🍳 RECIPE CARD\n", style="bold yellow")
    header.append(f"{recipe.title}", style="bold cyan")

    # Recipe info table
    info_table = Table(show_header=False, box=None, padding=(0, 1))
    info_table.add_column("Key", style="dim")
    info_table.add_column("Value", style="white")

    info_table.add_row("Source:", recipe.source_url)
    info_table.add_row("Servings:", f"{recipe.servings} people")

    time_parts = []
    if recipe.prep_time_minutes:
        time_parts.append(f"Prep: {recipe.prep_time_minutes} min")
    if recipe.cook_time_minutes:
        time_parts.append(f"Cook: {recipe.cook_time_minutes} min")
    if time_parts:
        info_table.add_row("Time:", " | ".join(time_parts))

    info_table.add_row("Difficulty:", recipe.difficulty)
    if recipe.cuisine:
        info_table.add_row("Cuisine:", recipe.cuisine)

    console.print(Panel(info_table, title=header, border_style="yellow"))

    # Ingredients
    ing_table = Table(title="📝 INGREDIENTS", show_header=True, box=box.ROUNDED)
    ing_table.add_column("Quantity", style="cyan", justify="right")
    ing_table.add_column("Unit", style="green")
    ing_table.add_column("Ingredient", style="white")
    ing_table.add_column("Notes", style="dim")

    for ing in recipe.ingredients:
        ing_table.add_row(
            f"{ing.quantity}",
            ing.unit,
            ing.name,
            ing.notes or ""
        )

    console.print(ing_table)

    # Instructions
    steps_table = Table(title="👨‍🍳 INSTRUCTIONS", show_header=False, box=box.ROUNDED)
    steps_table.add_column("Step", style="bold cyan", width=4)
    steps_table.add_column("Instruction", style="white")

    for step in recipe.steps:
        instruction = step.instruction
        if step.duration:
            instruction += f" [dim]({step.duration})[/dim]"
        steps_table.add_row(f"{step.step_number}.", instruction)

    console.print(steps_table)

    # Tips
    if recipe.tips:
        tips_text = Text()
        tips_text.append("💡 TIPS\n", style="bold yellow")
        for tip in recipe.tips:
            tips_text.append(f"  • {tip}\n", style="white")
        console.print(Panel(tips_text, border_style="yellow"))

    # Tags
    if recipe.tags:
        tags_text = " ".join([f"[{tag}]" for tag in recipe.tags])
        console.print(f"\n[dim]Tags: {tags_text}[/dim]")


def format_nutrition_table(nutrition: dict, servings: int = 1) -> None:
    """
    Format nutrition information as a table.

    Args:
        nutrition: Dictionary with calories_kcal, protein_g, fat_g, carbohydrates_g
        servings: Number of servings
    """
    # Create nutrition table
    table = Table(
        title=f"🥗 NUTRITION (per person, serves {servings})",
        show_header=True,
        box=box.DOUBLE_EDGE
    )

    table.add_column("Nutrient", style="cyan", justify="left")
    table.add_column("Amount", style="green", justify="right")

    table.add_row("Calories", f"{nutrition.get('calories_kcal', 0)} kcal")
    table.add_row("Protein", f"{nutrition.get('protein_g', 0)} g")
    table.add_row("Fat", f"{nutrition.get('fat_g', 0)} g")
    table.add_row("Carbohydrates", f"{nutrition.get('carbohydrates_g', 0)} g")

    console.print("\n")
    console.print(table)
    console.print("=" * 70)
