# YouTube Shorts Recipe Analyzer - Google ADK Multi-Agent System

A multi-agent system built with Google's Agent Development Kit (ADK) and Gemini that analyzes YouTube Shorts cooking videos to extract recipes and calculate nutritional information.

## Features

- 🎥 **Video Analysis**: Analyzes YouTube Shorts cooking videos using Gemini's multimodal capabilities
- 📝 **Recipe Extraction**: Extracts ingredients, steps, and metadata from video content
- 🥗 **Nutrition Calculation**: Calculates calories and macros per serving
- 🤖 **Multi-Agent Architecture**: Uses specialized agents for different tasks
- 📊 **Beautiful Output**: Rich terminal output with tables and formatting
- 💾 **Export Options**: Save recipes as JSON or Markdown

## Architecture

The system uses a hierarchical multi-agent architecture:

```
Orchestrator Agent
├── Video Analyzer Agent (analyzes video with Gemini)
├── Recipe Formatter Agent (structures raw data)
└── Nutrition Calculator Agent (calculates nutrition)
```

## Installation

### Using uv (Recommended)

1. Install uv if you haven't already:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Sync dependencies (from the `backend` directory):

```bash
cd backend
uv sync
```

3. Set up environment variables:

```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Using pip (Alternative)

```bash
cd recipe_analyzer
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

## Usage

### Command Line (with uv)

Analyze a YouTube Shorts video:

```bash
uv run python -m recipe_analyzer.app "https://www.youtube.com/shorts/nsdlYMDpXbU"
```

With custom servings:

```bash
uv run python -m recipe_analyzer.app "https://youtube.com/shorts/abc123" --servings 4
```

Save output to file:

```bash
uv run python -m recipe_analyzer.app "https://youtube.com/shorts/abc123" --output recipe.json
uv run python -m recipe_analyzer.app "https://youtube.com/shorts/abc123" --output recipe.md
```

### Command Line (without uv)

If not using uv, activate your virtual environment first:

```bash
source venv/bin/activate
python -m recipe_analyzer.app "https://youtube.com/shorts/abc123"
```

### As a Module

```python
from recipe_analyzer.app import analyze_recipe

recipe = analyze_recipe(
    youtube_url="https://youtube.com/shorts/abc123",
    servings=2
)
```

## Project Structure

```
recipe_analyzer/
├── agents/              # ADK agents
│   ├── video_analyzer.py
│   ├── recipe_formatter.py
│   ├── nutrition_calculator.py
│   └── orchestrator.py
├── tools/               # Agent tools
│   ├── youtube_tools.py
│   ├── nutrition_tools.py
│   └── ingredient_tools.py
├── models/              # Pydantic schemas
│   └── schemas.py
├── formatters/          # Output formatters
│   ├── recipe_card_formatter.py
│   └── json_formatter.py
├── outputs/             # Downloaded videos and outputs
├── app.py              # Main CLI application
├── requirements.txt     # Python dependencies
└── .env.example        # Environment variables template
```

## Data Models

### RecipeCard

```python
class RecipeCard(BaseModel):
    title: str
    source_url: str
    servings: int
    prep_time_minutes: Optional[int]
    cook_time_minutes: Optional[int]
    difficulty: str  # Easy, Medium, Hard
    cuisine: Optional[str]
    ingredients: list[Ingredient]
    steps: list[RecipeStep]
    nutrition_per_serving: NutritionPerPerson
    tips: list[str]
    tags: list[str]
```

### NutritionPerPerson

```python
class NutritionPerPerson(BaseModel):
    calories_kcal: float
    protein_g: float
    fat_g: float
    carbohydrates_g: float
```

## Environment Variables

Required:
- `GEMINI_API_KEY`: Your Gemini API key

Optional:
- `GOOGLE_CLOUD_PROJECT`: Google Cloud project ID (if using Vertex AI)
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to service account key

## Development

### Running Tests

```bash
pytest tests/
```

### Code Style

```bash
black recipe_analyzer/
ruff check recipe_analyzer/
```

## Error Handling

The system handles:
- Invalid or private YouTube URLs
- Non-cooking content detection
- Missing nutritional data for unusual ingredients
- Gemini API rate limits
- Network errors during video download

## Limitations

- Currently supports YouTube Shorts format
- Nutrition data based on standard nutritional databases
- Requires clear video quality for accurate extraction
- English language videos work best (translation support planned)

## Future Enhancements

- [ ] Support for longer YouTube videos
- [ ] Multi-language support with translation
- [ ] Integration with USDA FoodData Central API
- [ ] Recipe variations and substitutions
- [ ] Dietary restriction filtering
- [ ] Web interface
- [ ] Recipe sharing and social features

## License

MIT License

## Contributing

Contributions welcome! Please read CONTRIBUTING.md for guidelines.

## Acknowledgments

- Built with [Google ADK](https://github.com/google/adk-python)
- Powered by [Gemini](https://deepmind.google/technologies/gemini/)
- Video download via [yt-dlp](https://github.com/yt-dlp/yt-dlp)
