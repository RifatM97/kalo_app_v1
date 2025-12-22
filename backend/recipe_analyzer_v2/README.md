# Recipe Analyzer V2

A multi-agent AI system built with Google ADK (Agent Development Kit) that analyzes YouTube cooking videos and extracts structured recipe information using Gemini's multimodal capabilities.

## Project Summary

Recipe Analyzer V2 is an intelligent agent system that transforms YouTube cooking videos (particularly Shorts) into structured, machine-readable recipe cards with complete nutritional information. The system leverages Google's Gemini models for video understanding, natural language processing, and structured data extraction.

### Key Features

- **Video Analysis**: Extracts recipe information from YouTube cooking videos using multimodal AI
- **Intelligent Parsing**: Converts unstructured recipe content into standardized format
- **Nutritional Calculation**: Computes per-serving nutritional breakdown
- **Structured Output**: Generates JSON recipe cards with ingredients, steps, timing, and metadata
- **Multi-Agent Coordination**: Orchestrates specialized agents for different tasks

## Technology Stack

- **Google ADK**: Agent Development Kit for building multi-agent systems
- **Gemini Models**:
  - `gemini-2.5-flash`: For video analysis and nutrition calculation
  - `gemini-2.5-flash-lite`: For orchestration and formatting
- **Pydantic**: Data validation and schema definition
- **yt-dlp**: YouTube video downloading (optional)
- **Python 3.12+**: Core runtime

## Agentic Architecture

The system follows a hierarchical multi-agent architecture with specialized agents coordinated by an orchestrator.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                  Orchestrator Agent                     │
│              (recipe_orchestrator)                      │
│                                                          │
│  Coordinates workflow and manages sub-agents            │
│  Model: gemini-2.5-flash-lite                          │
└────────────┬─────────────────────────────┬──────────────┘
             │                             │
             │                             │
    ┌────────▼───────────┐      ┌─────────▼──────────┐
    │  Video Analyzer    │      │  Recipe Formatter   │
    │     Agent          │      │      Agent          │
    │                    │      │                     │
    │ Analyzes video     │      │ Formats raw data    │
    │ Extracts recipe    │      │ Structures output   │
    │ info from video    │      │ Calculates          │
    │                    │      │ nutrition           │
    │ Model: gemini-2.5  │      │ Model: gemini-2.5   │
    │      -flash        │      │      -flash-lite    │
    └────────┬───────────┘      └─────────────────────┘
             │
             │
    ┌────────▼───────────┐
    │   analyze_video    │
    │   _with_gemini     │
    │                    │
    │ Tool: Processes    │
    │ video with Gemini  │
    │ multimodal API     │
    └────────────────────┘
```

### Agent Descriptions

#### 1. Orchestrator Agent (`recipe_orchestrator`)

**Role**: Master coordinator that manages the complete recipe analysis workflow

**Model**: `gemini-2.5-flash-lite`

**Responsibilities**:
- Receives YouTube URL as input
- Delegates video analysis to Video Analyzer agent
- Passes analysis results to Recipe Formatter agent
- Ensures data flows correctly between agents
- Handles errors at each stage
- Returns final structured recipe card

**Workflow**:
1. Accept YouTube URL input
2. Delegate to `video_analyzer` for content extraction
3. Delegate to `recipe_formatter` for structuring
4. Return formatted recipe card

#### 2. Video Analyzer Agent (`video_analyzer`)

**Role**: Multimodal video content analyzer specialized in cooking videos

**Model**: `gemini-2.5-flash`

**Responsibilities**:
- Analyze YouTube cooking videos frame-by-frame
- Extract recipe information from visual and audio cues
- Identify ingredients with quantities
- Extract cooking steps in sequence
- Detect metadata (servings, timing, difficulty, cuisine, tags)
- Process text overlays and spoken instructions

**Tools Available**:
- `analyze_video_with_gemini`: Processes video using Gemini's multimodal API

**Output**: Raw recipe analysis including:
- Recipe title
- Ingredients list (with quantities if visible)
- Step-by-step instructions
- Estimated servings, prep time, cook time
- Difficulty level
- Cuisine type
- Cooking tips
- Tags (vegetarian, vegan, quick, etc.)

#### 3. Recipe Formatter Agent (`recipe_formatter`)

**Role**: Data structuring specialist that transforms raw analysis into standardized format

**Model**: `gemini-2.5-flash-lite`

**Responsibilities**:
- Parse and structure raw recipe analysis
- Scale ingredients to requested servings
- Standardize measurements to culinary units
- Format cooking steps with proper sequencing
- Calculate nutritional information per serving
- Generate clean JSON output conforming to RecipeCard schema

**Output Schema**: `RecipeCard` (Pydantic model)

**Tools Available**:
- `parse_ingredients_from_text`: Converts text to structured ingredients
- `parse_steps_from_text`: Converts text to structured steps

#### 4. Nutrition Calculator Agent (`nutrition_calculator`)

**Role**: Nutritional analysis specialist (standalone, not currently integrated in main workflow)

**Model**: `gemini-2.5-flash`

**Responsibilities**:
- Look up nutritional data for ingredients
- Calculate total recipe nutrition
- Compute per-serving breakdown
- Provide accurate macronutrient information

**Tools Available**:
- `calculate_nutrition_per_serving`: Computes nutrition per serving
- `get_ingredient_nutrition_info`: Looks up individual ingredient nutrition

**Nutrients Calculated**:
- Calories (kcal)
- Protein (g)
- Fat (g)
- Carbohydrates (g)

## Data Models

### RecipeCard
Complete recipe representation with all metadata, ingredients, steps, and nutrition.

**Fields**:
- `title`: Recipe name
- `source_url`: Original YouTube URL
- `servings`: Number of portions
- `prep_time_minutes`: Preparation time
- `cook_time_minutes`: Cooking time
- `difficulty`: Easy/Medium/Hard
- `cuisine`: Cuisine type (Italian, Chinese, etc.)
- `ingredients`: List of Ingredient objects
- `steps`: List of RecipeStep objects
- `nutrition_per_serving`: NutritionPerPerson object
- `tips`: Cooking tips
- `tags`: Recipe tags

### Ingredient
Structured ingredient with measurements.

**Fields**:
- `name`: Ingredient name
- `quantity`: Numerical amount
- `unit`: Measurement unit (g, ml, cups, tbsp, etc.)
- `notes`: Preparation notes (e.g., "finely chopped")

### RecipeStep
Individual cooking instruction.

**Fields**:
- `step_number`: Sequence number
- `instruction`: Detailed instruction text
- `duration`: Estimated time (optional)

### NutritionPerPerson
Per-serving nutritional information.

**Fields**:
- `calories_kcal`: Energy in kilocalories
- `protein_g`: Protein in grams
- `fat_g`: Fat in grams
- `carbohydrates_g`: Carbohydrates in grams

## Tools & Utilities

### YouTube Tools (`tools/youtube_tools.py`)
- `extract_video_id()`: Extract video ID from various YouTube URL formats
- `download_youtube_video()`: Download video using yt-dlp (optional)

### Nutrition Tools (`tools/nutrition_tools.py`)
- `lookup_nutrition_data()`: Get nutritional info for ingredients
- `calculate_recipe_nutrition()`: Compute total recipe nutrition
- Built-in nutritional database with common ingredients

### Ingredient Tools (`tools/ingredient_tools.py`)
- `scale_ingredients()`: Scale quantities based on servings
- `parse_ingredient_string()`: Parse natural language ingredient strings

## Workflow Example

```
Input: "https://youtube.com/shorts/abc123"

┌──────────────────────────────────────────────┐
│ 1. Orchestrator receives YouTube URL         │
└────────────────┬─────────────────────────────┘
                 │
┌────────────────▼─────────────────────────────┐
│ 2. Video Analyzer processes video            │
│    - Analyzes frames and audio               │
│    - Extracts: "Pasta Carbonara"             │
│    - Ingredients: eggs, pasta, bacon...      │
│    - Steps: boil pasta, cook bacon...        │
└────────────────┬─────────────────────────────┘
                 │
┌────────────────▼─────────────────────────────┐
│ 3. Recipe Formatter structures data          │
│    - Parses ingredients into objects         │
│    - Formats steps with numbers              │
│    - Calculates nutrition                    │
│    - Generates JSON RecipeCard               │
└────────────────┬─────────────────────────────┘
                 │
┌────────────────▼─────────────────────────────┐
│ 4. Orchestrator returns final result         │
│    Output: Complete RecipeCard JSON          │
└──────────────────────────────────────────────┘
```

## Directory Structure

```
recipe_analyzer_v2/
├── agent.py                    # Orchestrator agent definition
├── models/
│   ├── __init__.py
│   └── schemas.py             # Pydantic data models
├── sub_agents/
│   ├── __init__.py
│   ├── video_analyzer/
│   │   ├── __init__.py
│   │   └── agent.py          # Video analysis agent
│   ├── recipe_formatter/
│   │   ├── __init__.py
│   │   └── agent.py          # Recipe formatting agent
│   └── nutrition/
│       ├── __init__.py
│       └── agent.py          # Nutrition calculation agent
└── tools/
    ├── __init__.py
    ├── youtube_tools.py      # YouTube processing utilities
    ├── nutrition_tools.py    # Nutrition lookup and calculation
    └── ingredient_tools.py   # Ingredient parsing and scaling
```

## Configuration

### Environment Variables

```bash
GEMINI_API_KEY=your_api_key_here
```

### ADK Session

The system uses Google ADK's session management (`.adk/session.db`) to maintain conversation state and agent coordination.

## Key Design Decisions

1. **Agent Specialization**: Each agent has a focused responsibility, improving reliability and maintainability
2. **Gemini Model Selection**:
   - Use full `flash` model for complex tasks (video analysis, nutrition)
   - Use `flash-lite` for simpler tasks (orchestration, formatting)
3. **Structured Output**: Pydantic schemas ensure type safety and validation
4. **Tool-Based Architecture**: Agents use tools for specific operations, enabling reusability
5. **Hierarchical Coordination**: Orchestrator pattern simplifies workflow management

## Future Enhancements

- Integrate Nutrition Calculator into main workflow
- Support multiple video sources beyond YouTube
- Add recipe image generation
- Implement recipe similarity search
- Support multiple languages
- Add user feedback loop for accuracy improvement
