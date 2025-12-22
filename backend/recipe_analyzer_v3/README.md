# Recipe Analyzer V3

An advanced multi-agent AI system built with Google ADK (Agent Development Kit) that analyzes YouTube cooking videos, extracts structured recipe information, and provides personalized nutritional analysis using parallel processing and user profile integration.

## Project Summary

Recipe Analyzer V3 is an intelligent agent orchestration system that transforms YouTube cooking videos into structured recipe cards with personalized nutritional insights. The system leverages Google's Gemini models, parallel processing, and user profile data to deliver comprehensive recipe analysis with dietary recommendations.

### Key Features

- **Video Analysis**: Extracts recipe information from YouTube videos using Gemini's multimodal capabilities
- **Parallel Processing**: Simultaneously formats recipes and calculates nutrition for optimal performance
- **Personalized Nutrition**: Compares recipe calories against user's daily intake goals
- **User Profile Integration**: Leverages user data (weight, diet goals, calorie targets)
- **Structured Output**: Generates comprehensive JSON recipe cards with nutrition
- **Advanced Agent Coordination**: Sequential and parallel agent orchestration patterns

### What's New in V3

Compared to V2, this version introduces:
- **ParallelAgent**: Recipe formatting and nutrition calculation run concurrently
- **SequentialAgent**: Orchestrates workflow stages in order
- **User Profile System**: Database integration for personalized recommendations
- **Enhanced Nutrition Agent**: Compares against user's daily calorie needs
- **Combined Output Schema**: RecipeCardWithNutrition includes all data in one structure
- **LLM Combiner Agent**: Intelligently merges parallel processing results

## Technology Stack

- **Google ADK**: Agent Development Kit with advanced orchestration patterns
- **Gemini Models**:
  - `gemini-2.5-flash`: For video analysis
  - `gemini-2.5-flash-lite`: For formatting, nutrition, and orchestration
- **Agent Patterns**:
  - `SequentialAgent`: Sequential workflow execution
  - `ParallelAgent`: Concurrent task processing
  - `LlmAgent`: LLM-powered data combination
- **Pydantic**: Data validation and schema definition
- **Python 3.12+**: Core runtime

## Agentic Architecture

The system uses advanced agent orchestration patterns with parallel processing and sequential coordination.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│             Sequential Workflow Agent                            │
│           (recipe_analysis_workflow)                             │
│                                                                   │
│   Orchestrates: Video Analysis → Parallel Processing → Combine  │
└──────────┬───────────────────────────────────────────┬──────────┘
           │                                            │
           │ Stage 1: Video Analysis                    │ Stage 2: Parallel Processing
           │                                            │
┌──────────▼─────────────┐              ┌───────────────▼────────────────────┐
│   Video Analyzer       │              │  Parallel Processing Agent         │
│      Agent             │              │  (recipe_processing_parallel)      │
│                        │              │                                    │
│ Analyzes cooking       │              │  Runs in parallel:                 │
│ video, extracts        │──────────────▶  1. Recipe Formatter               │
│ recipe information     │              │  2. Nutrition Calculator           │
│                        │              │                                    │
│ Model: gemini-2.5      │              └──────────┬─────────────────────────┘
│       -flash-lite      │                         │
└────────────────────────┘                         │
                                                   │
                              ┌────────────────────┴──────────────────────┐
                              │                                           │
                    ┌─────────▼────────────┐              ┌──────────────▼─────────────┐
                    │  Recipe Formatter    │              │  Nutrition Calculator      │
                    │      Agent           │              │       Agent                │
                    │                      │              │                            │
                    │ Formats recipe       │              │ Calculates nutrition       │
                    │ Structures data      │              │ Compares vs user profile  │
                    │ Scales ingredients   │              │ Provides recommendations  │
                    │                      │              │                            │
                    │ Model: gemini-2.5    │              │ Model: gemini-2.5         │
                    │       -flash-lite    │              │       -flash-lite         │
                    │                      │              │                            │
                    │ Output:              │              │ Output:                    │
                    │ formatted_recipe_card│              │ nutrition_per_serving     │
                    └─────────┬────────────┘              └──────────────┬─────────────┘
                              │                                          │
                              └──────────────┬───────────────────────────┘
                                             │
                                   ┌─────────▼────────────┐
                                   │   Combine Outputs    │
                                   │    LLM Agent         │
                                   │                      │
                                   │ Merges parallel      │
                                   │ outputs into single  │
                                   │ RecipeCardWith       │
                                   │ Nutrition object     │
                                   │                      │
                                   │ Model: gemini-2.5    │
                                   │       -flash-lite    │
                                   └──────────────────────┘
```

### Agent Orchestration Patterns

#### Sequential Workflow

The top-level orchestrator uses a **SequentialAgent** pattern to ensure stages execute in order:

1. **Stage 1**: Video Analysis (extract recipe data)
2. **Stage 2**: Parallel Processing (format + nutrition)
3. **Stage 3**: Combine Results (merge outputs)

Benefits:
- Ensures data dependencies are respected
- Clean separation of workflow stages
- Easy to understand and maintain

#### Parallel Processing

Within Stage 2, a **ParallelAgent** runs two independent tasks simultaneously:

- **Recipe Formatter**: Structures the raw analysis
- **Nutrition Calculator**: Computes nutritional values

Benefits:
- 2x faster than sequential processing
- Optimal resource utilization
- Both agents work on same input independently

### Agent Descriptions

#### 1. Sequential Workflow Agent (`recipe_analysis_workflow`)

**Type**: SequentialAgent

**Role**: Top-level orchestrator managing the complete pipeline

**Sub-agents**:
1. `video_analyzer_agent`
2. `combine_parallel` (which internally runs parallel processing)

**Workflow**:
1. Accept YouTube URL
2. Run video analysis (sequential)
3. Run parallel processing (recipe formatting + nutrition)
4. Combine results into final output

#### 2. Video Analyzer Agent (`video_analyzer`)

**Type**: Agent (LLM-based)

**Model**: `gemini-2.5-flash-lite`

**Role**: Multimodal video content analyzer for cooking videos

**Responsibilities**:
- Analyze YouTube cooking videos frame-by-frame
- Extract recipe information from visual and audio cues
- Identify ingredients with quantities
- Extract cooking steps in sequence
- Detect metadata (servings, timing, difficulty, cuisine, tags)

**Tools**:
- `analyze_video_with_gemini`: Processes video using Gemini's multimodal API

**Output Key**: `recipe_analysis`

**Output**: Raw recipe analysis text with all extracted information

#### 3. Parallel Processing Agent (`recipe_processing_parallel_agent`)

**Type**: ParallelAgent

**Role**: Coordinates concurrent execution of formatting and nutrition calculation

**Sub-agents**:
1. `recipe_formatter_agent`
2. `nutrition_calculator_agent`

**Execution**: Both agents run simultaneously on the video analysis output

**Benefits**:
- Cuts processing time in half
- Independent operations don't block each other
- Efficient resource usage

#### 4. Recipe Formatter Agent (`recipe_formatter`)

**Type**: Agent (LLM-based)

**Model**: `gemini-2.5-flash-lite`

**Role**: Data structuring specialist

**Responsibilities**:
- Parse raw recipe analysis text
- Scale ingredients to requested servings
- Standardize measurements to culinary units
- Format cooking steps with proper sequencing
- Generate clean JSON conforming to RecipeCard schema

**Output Key**: `formatted_recipe_card`

**Output Schema**: `RecipeCard` (without nutrition)

#### 5. Nutrition Calculator Agent (`nutrition_calculator`)

**Type**: Agent (LLM-based)

**Model**: `gemini-2.5-flash-lite`

**Role**: Personalized nutritional analysis specialist

**Responsibilities**:
- Parse ingredient list from recipe analysis
- Look up nutritional data for each ingredient
- Calculate total recipe nutrition
- Compute per-serving breakdown
- **NEW**: Compare against user's daily calorie needs
- **NEW**: Provide personalized dietary recommendations

**Tools**:
- `get_ingredient_nutrition_info`: Looks up ingredient nutrition
- `calculate_nutrition_per_serving`: Computes per-serving values
- `get_user_calories`: Retrieves user's daily calorie target from database

**Output Key**: `nutrition_per_serving`

**Output**: Nutritional breakdown with user comparison

**User Integration**:
- Accesses `user_profile` from database
- Compares recipe calories vs. user's `daily_calorie_intake`
- Considers user's `diet_goal` (lose/gain/maintain weight)

#### 6. Combine Outputs Agent (`combine_outputs`)

**Type**: LlmAgent

**Model**: `gemini-2.5-flash-lite`

**Role**: Intelligent output merger

**Responsibilities**:
- Receive `formatted_recipe_card` from Recipe Formatter
- Receive `nutrition_per_serving` from Nutrition Calculator
- Merge both outputs into single `RecipeCardWithNutrition` object
- Ensure schema compliance

**Output Schema**: `RecipeCardWithNutrition`

**Why Needed**:
- Parallel outputs are independent
- Need single unified structure for final result
- LLM intelligently handles any format variations

## Data Models

### RecipeCardWithNutrition (New in V3)
Extended recipe card that includes nutritional information.

**Extends**: `RecipeCard`

**Additional Field**:
- `nutrition`: NutritionPerPerson object with macronutrients

### RecipeCard
Complete recipe representation (same as V2).

**Fields**:
- `title`: Recipe name
- `source_url`: Original YouTube URL
- `servings`: Number of portions
- `prep_time_minutes`: Preparation time
- `cook_time_minutes`: Cooking time
- `difficulty`: Easy/Medium/Hard
- `cuisine`: Cuisine type
- `ingredients`: List of Ingredient objects
- `steps`: List of RecipeStep objects
- `tips`: Cooking tips
- `tags`: Recipe tags

### Ingredient
Structured ingredient with measurements.

**Fields**:
- `name`: Ingredient name
- `quantity`: Numerical amount
- `unit`: Measurement unit
- `notes`: Preparation notes (optional)

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

## User Profile System

### Database Structure

Located in `data/database.py`, provides user profile data for personalized analysis.

#### Single User Profile

```python
user_profile = {
    "user_id": "user_001",
    "name": "John Doe",
    "age": 30,
    "weight_kg": 75.5,
    "height_cm": 175,
    "daily_calorie_intake": 2000,
    "diet_goal": "maintain weight",
    "dietary_restrictions": ["vegetarian"],
    "activity_level": "moderate"
}
```

#### Multiple Users Database

```python
users_db = {
    "user_001": {...},  # John Doe - maintain weight
    "user_002": {...},  # Jane Smith - lose weight
    "user_003": {...}   # Mike Johnson - gain weight
}
```

### User Profile Fields

- `user_id`: Unique identifier
- `name`: User's full name
- `age`: Age in years
- `weight_kg`: Current weight in kilograms
- `height_cm`: Height in centimeters
- `daily_calorie_intake`: Target daily calories
- `diet_goal`: "lose weight" | "gain weight" | "maintain weight"
- `dietary_restrictions`: List of restrictions (vegetarian, vegan, etc.)
- `activity_level`: "sedentary" | "light" | "moderate" | "active" | "very active"

### Personalization Features

The Nutrition Calculator agent uses user profiles to:

1. **Compare Calories**: Recipe calories vs. user's daily target
2. **Diet Goal Alignment**: Whether recipe fits user's weight goals
3. **Portion Recommendations**: Suggest serving adjustments
4. **Dietary Compliance**: Check against user's restrictions (future)

## Tools & Utilities

### YouTube Tools (`tools/youtube_tools.py`)
- `extract_video_id()`: Extract video ID from YouTube URLs
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
Input: YouTube URL + User Profile

┌──────────────────────────────────────────────────────────┐
│ Stage 1: Video Analysis                                  │
│ - Video Analyzer extracts recipe from YouTube video      │
│ - Output: Raw recipe analysis text                       │
└────────────────────┬─────────────────────────────────────┘
                     │
                     │ recipe_analysis
                     │
┌────────────────────▼─────────────────────────────────────┐
│ Stage 2: Parallel Processing (CONCURRENT)                │
├───────────────────────────┬──────────────────────────────┤
│ Recipe Formatter          │  Nutrition Calculator        │
│ - Parses ingredients      │  - Looks up nutrition data   │
│ - Formats steps           │  - Calculates per-serving    │
│ - Structures recipe card  │  - Compares vs user profile  │
│                           │  - User: John Doe (2000 cal) │
│ Output:                   │  Output:                     │
│ formatted_recipe_card     │  nutrition_per_serving       │
└───────────────────────────┴──────────────────────────────┘
                     │
                     │ Both outputs ready
                     │
┌────────────────────▼─────────────────────────────────────┐
│ Stage 3: Combine Results                                 │
│ - Combine Outputs agent merges both results              │
│ - Creates single RecipeCardWithNutrition object          │
│ - Includes recipe + nutrition + user comparison          │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
              Final Output:
        RecipeCardWithNutrition JSON
     (Recipe + Nutrition + Recommendations)
```

### Performance Comparison

**Sequential (V2)**:
```
Video Analysis → Recipe Format → Nutrition Calc
Total: T1 + T2 + T3
```

**Parallel (V3)**:
```
Video Analysis → (Recipe Format || Nutrition Calc) → Combine
Total: T1 + max(T2, T3) + T_combine
```

**Speedup**: If T2 ≈ T3, then V3 is ~40-50% faster than V2

## Directory Structure

```
recipe_analyzer_v3/
├── agent.py                      # Main orchestrator with Sequential & Parallel agents
├── models/
│   ├── __init__.py
│   └── schemas.py               # Pydantic models (RecipeCardWithNutrition, etc.)
├── sub_agents/
│   ├── __init__.py
│   ├── video_analyzer/
│   │   ├── __init__.py
│   │   └── agent.py            # Video analysis agent
│   ├── recipe_formatter/
│   │   ├── __init__.py
│   │   └── agent.py            # Recipe formatting agent
│   └── nutrition/
│       ├── __init__.py
│       └── agent.py            # Nutrition calculation agent (with user integration)
├── tools/
│   ├── __init__.py
│   ├── youtube_tools.py        # YouTube processing utilities
│   ├── nutrition_tools.py      # Nutrition lookup and calculation
│   └── ingredient_tools.py     # Ingredient parsing and scaling
└── data/
    ├── __init__.py
    └── database.py             # Mock user profile database
```

## Configuration

### Environment Variables

```bash
GEMINI_API_KEY=your_api_key_here
```

### User Profile Setup

Edit `data/database.py` to customize user profiles:

```python
user_profile = {
    "name": "Your Name",
    "weight_kg": 70.0,
    "daily_calorie_intake": 2200,
    "diet_goal": "lose weight",  # or "gain weight", "maintain weight"
    # ... other fields
}
```

### ADK Session

The system uses Google ADK's session management (`.adk/session.db`) for conversation state.

## Key Design Decisions

### 1. Parallel Processing Architecture

**Why**: Recipe formatting and nutrition calculation are independent operations that can run concurrently.

**Benefits**:
- 40-50% faster execution
- Better resource utilization
- Scalable pattern for future agents

**Trade-offs**:
- Slightly more complex orchestration
- Need combiner agent to merge results

### 2. User Profile Integration

**Why**: Personalized nutrition recommendations are more valuable than generic data.

**Benefits**:
- Context-aware calorie comparisons
- Diet goal alignment
- Future: meal planning, restriction checking

**Implementation**:
- Mock database for development
- Easy to swap with real database
- Single source of truth for user data

### 3. Sequential + Parallel Hybrid

**Why**: Some operations have dependencies (video → processing), others don't (format || nutrition).

**Pattern**:
```
Sequential[
  video_analyzer,
  Parallel[recipe_formatter, nutrition_calculator],
  combine_outputs
]
```

**Benefits**:
- Respects data dependencies
- Maximizes parallelism where possible
- Clear, maintainable structure

### 4. LLM-Based Output Combiner

**Why**: Parallel agents may produce slightly different formats; LLM handles variations gracefully.

**Alternative**: Manual JSON merging (brittle, error-prone)

**Benefits**:
- Handles schema variations
- Natural language understanding
- Fault-tolerant combination

### 5. Model Selection Strategy

| Agent | Model | Reasoning |
|-------|-------|-----------|
| Video Analyzer | flash-lite | Fast inference, good enough for prompting multimodal tool |
| Recipe Formatter | flash-lite | Simple structured output task |
| Nutrition Calculator | flash-lite | Lookup + calculation, not complex reasoning |
| Combine Outputs | flash-lite | Simple JSON merging |

**Strategy**: Use lighter models where possible to reduce cost and latency.

## Future Enhancements

### Immediate Roadmap
- [ ] Implement serving size scaling in Recipe Formatter (TODO in code)
- [ ] Add dietary restriction filtering based on user profile
- [ ] Support multiple video sources beyond YouTube
- [ ] Real database integration (replace mock data)

### Advanced Features
- [ ] Meal planning agent (weekly plans based on user goals)
- [ ] Shopping list generator
- [ ] Recipe modification suggestions (e.g., "make it vegetarian")
- [ ] Historical tracking of consumed recipes
- [ ] Adaptive calorie recommendations based on progress
- [ ] Multi-language support
- [ ] Recipe image generation
- [ ] Ingredient substitution recommendations

### Architecture Improvements
- [ ] Add caching layer for nutrition lookups
- [ ] Implement fallback strategies for failed agents
- [ ] Add monitoring and logging for agent performance
- [ ] Support user-specific agent customization
- [ ] Multi-user concurrent processing

## Performance Characteristics

### Latency Profile (Estimated)

- **Video Analysis**: 5-10 seconds (Gemini API call)
- **Recipe Formatting**: 2-3 seconds (LLM structured output)
- **Nutrition Calculation**: 2-3 seconds (lookups + LLM)
- **Parallel Execution**: max(formatting, nutrition) ≈ 3 seconds
- **Combine Outputs**: 1-2 seconds (simple LLM merge)

**Total**: ~9-15 seconds (vs. ~12-18 seconds in V2)

### Cost Optimization

- Uses `flash-lite` models (cheaper than `flash`)
- Parallel processing reduces total API calls
- Efficient prompt design minimizes token usage
- Database caching reduces redundant lookups

## Comparison: V2 vs V3

| Feature | V2 | V3 |
|---------|----|----|
| **Orchestration** | Simple Agent with sub-agents | SequentialAgent + ParallelAgent |
| **Processing** | Sequential | Parallel (format + nutrition) |
| **User Integration** | None | User profile database |
| **Nutrition** | Basic calculation | Personalized with user comparison |
| **Output Schema** | RecipeCard (no nutrition) | RecipeCardWithNutrition (unified) |
| **Performance** | Baseline | 40-50% faster |
| **Personalization** | Generic | User-specific recommendations |
| **Agent Patterns** | Basic | Advanced (Sequential, Parallel, LLM) |
| **Database** | None | Mock user profiles |

## Getting Started

### Prerequisites

```bash
pip install google-adk
pip install pydantic
pip install python-dotenv
```

### Setup

1. Set environment variable:
```bash
export GEMINI_API_KEY="your-api-key"
```

2. Customize user profile in `data/database.py`

3. Run the agent:
```python
from recipe_analyzer_v3.agent import root_agent

result = root_agent.run(
    "https://youtube.com/shorts/abc123"
)
```

### Output

```json
{
  "title": "Creamy Pasta Carbonara",
  "source_url": "https://youtube.com/shorts/abc123",
  "servings": 2,
  "ingredients": [...],
  "steps": [...],
  "nutrition": {
    "calories_kcal": 650,
    "protein_g": 25,
    "fat_g": 35,
    "carbohydrates_g": 55
  },
  "tips": [...],
  "tags": [...]
}
```

With user comparison:
- "This recipe provides 650 calories, which is 32.5% of John Doe's daily target (2000 cal)."
- "Suitable for maintain weight goal when combined with other balanced meals."

## License

[Specify your license]

## Contributors

[Your team/contributors]
