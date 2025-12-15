"""Main application entry point for YouTube Recipe Analyzer"""

import argparse
import asyncio
import logging
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.logging import RichHandler

from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .agents.orchestrator import orchestrator_agent
from .tools.youtube_tools import extract_video_id

# TODO: Uncomment when implementing full recipe card output
# from pathlib import Path
# from .models.schemas import RecipeCard
# from .formatters import format_recipe_card, format_nutrition_table, save_recipe_json, save_recipe_markdown

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger(__name__)
console = Console()


async def analyze_recipe(youtube_url: str, servings: int = 2, output_dir: str = "outputs"):
    """
    Analyze a YouTube Shorts cooking video and extract recipe.

    Args:
        youtube_url: YouTube Shorts URL
        servings: Number of servings to scale recipe for
        output_dir: Directory to save outputs (TODO: implement file saving)

    Returns:
        Agent response with recipe analysis
    """
    # TODO: Use output_dir for saving downloaded videos and results
    try:
        console.print(f"\n[bold cyan]Analyzing YouTube recipe...[/bold cyan]")
        console.print(f"URL: {youtube_url}")
        console.print(f"Target servings: {servings}\n")

        # Create runner with orchestrator agent
        session_service = InMemorySessionService()
        await session_service.create_session(
        app_name="recipe_analyzer", user_id="user", session_id="test_session"
    )
        runner = Runner(
            app_name="recipe_analyzer",
            agent=orchestrator_agent,
            session_service=session_service
        )

        # Create user message with YouTube URL and servings
        # The orchestrator's instruction already knows what to do
        user_message = f"Please analyze this YouTube cooking video and create a recipe card for {servings} people: {youtube_url}"

        # Run agent and collect response
        logger.info("Starting multi-agent orchestration...")

        response_text = ""
        async for event in runner.run_async(
            user_id="user",
            session_id="test_session",
            new_message=types.Content(
                role="user",
                parts=[types.Part(text=user_message)]
            )
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response_text += part.text
                        console.print(f"[dim]{part.text}[/dim]")

        logger.info("Recipe analysis complete!")

        # Note: This is a demonstration. In production, you'd:
        # 1. Configure agents to return structured Pydantic models
        # 2. Use ADK's structured output features
        # 3. Handle the multi-agent workflow more explicitly
        # 4. Parse response_text into RecipeCard

        return response_text

    except Exception as e:
        logger.error(f"Failed to analyze recipe: {e}")
        raise


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Analyze YouTube Shorts cooking videos and extract recipes with nutritional information"
    )

    parser.add_argument(
        "url",
        type=str,
        help="YouTube Shorts URL to analyze"
    )

    parser.add_argument(
        "--servings",
        type=int,
        default=2,
        help="Number of servings to scale recipe for (default: 2)"
    )

    parser.add_argument(
        "--output",
        type=str,
        help="Output file path (saves as JSON if .json, markdown if .md)"
    )

    parser.add_argument(
        "--format",
        type=str,
        choices=["terminal", "markdown", "json"],
        default="terminal",
        help="Output format (default: terminal)"
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default="recipe_analyzer/outputs",
        help="Directory to save outputs (default: outputs)"
    )

    args = parser.parse_args()

    try:
        # Validate URL
        try:
            extract_video_id(args.url)  # Validates the URL format
        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)

        # Analyze recipe (run async function)
        result = asyncio.run(analyze_recipe(
            youtube_url=args.url,
            servings=args.servings,
            output_dir=args.output_dir
        ))

        # Display results
        console.print("\n[bold green]✓ Analysis Complete![/bold green]")
        console.print(f"\n{result}")

        # Note: In production, you would:
        # if isinstance(result, RecipeCard):
        #     # Display recipe card
        #     if args.format == "terminal":
        #         format_recipe_card(result, output_format="terminal")
        #         format_nutrition_table(
        #             result.nutrition_per_serving.model_dump(),
        #             servings=result.servings
        #         )
        #
        #     # Save outputs
        #     if args.output:
        #         output_path = Path(args.output)
        #         if output_path.suffix == '.json':
        #             save_recipe_json(result, output_path)
        #         elif output_path.suffix == '.md':
        #             save_recipe_markdown(result, output_path)
        #         console.print(f"\n[green]Saved to: {output_path}[/green]")
        #     else:
        #         # Auto-save
        #         output_base = Path(args.output_dir) / video_id
        #         save_recipe_json(result, f"{output_base}_recipe.json")
        #         save_recipe_markdown(result, f"{output_base}_recipe.md")
        #         console.print(f"\n[green]Saved to: {output_base}_recipe.{{json,md}}[/green]")

        console.print("\n[bold green]✓ Complete![/bold green]\n")

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        logger.exception("Application error")
        sys.exit(1)


if __name__ == "__main__":
    main()
