# Multi-Input Agent Configuration Guide

This document explains how the Recipe Analyzer V3 agents have been configured to accept and route multiple inputs (YouTube URL, servings, and user name) to the appropriate sub-agents.

## Overview

The system now supports three inputs:
1. **YouTube URL**: The cooking video to analyze
2. **Target Servings**: Number of servings to scale the recipe to (passed to recipe_formatter)
3. **User Name**: The user's name for personalized nutrition (passed to nutrition_calculator)

## Architecture Flow

```
User Input (JSON)
{
  "video_url": "https://youtube.com/...",
  "user_context": {
    "target_servings": 2,
    "user_name": "John Doe"
  }
}
    ↓
┌─────────────────────────────────────────────────────────────┐
│ 1. Video Analyzer Agent                                     │
│    - Parses JSON input                                      │
│    - Extracts video_url and analyzes video                  │
│    - PASSES THROUGH user_context in output                  │
│                                                              │
│    Output: Recipe Analysis + User Context                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Parallel Processing Agent                                │
│    (Both agents run simultaneously on same input)           │
│                                                              │
│  ┌──────────────────────────┬─────────────────────────────┐ │
│  │ Recipe Formatter         │ Nutrition Calculator        │ │
│  │                          │                             │ │
│  │ - Extracts Target        │ - Extracts User Name        │ │
│  │   Servings from input    │   from input                │ │
│  │ - Scales ingredients     │ - Looks up user's daily     │ │
│  │   to target servings     │   calorie needs             │ │
│  │ - Sets servings field    │ - Calculates personalized   │ │
│  │                          │   nutrition percentage      │ │
│  │                          │                             │ │
│  │ Output: RecipeCard       │ Output: NutritionPerPerson  │ │
│  └──────────────────────────┴─────────────────────────────┘ │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Combine Outputs Agent                                    │
│    - Merges RecipeCard + NutritionPerPerson                 │
│    - Returns RecipeCardWithNutrition                        │
└─────────────────────────────────────────────────────────────┘
```

## Changes Made

### 1. Video Analyzer Agent (`sub_agents/video_analyzer/agent.py`)

**What Changed:**
- Updated instruction to parse JSON input
- Extracts `video_url` from input
- Passes through `user_context` (target_servings and user_name) in output

**Key Instruction:**
```python
instruction="""
    ...
    1. Parse the input JSON to extract:
       - "video_url": The YouTube URL to analyze
       - "user_context": Contains "target_servings" and "user_name"
    ...
    4. IMPORTANT: Include the user_context in your output so downstream agents can access it

    Output format:
    "Recipe Analysis: [your analysis here]

    User Context:
    - Target Servings: [number]
    - User Name: [name]"
    """
```

**Why:** The video analyzer acts as a pass-through for context, ensuring downstream parallel agents receive both the recipe analysis AND the user inputs.

### 2. Recipe Formatter Agent (`sub_agents/recipe_formatter/agent.py`)

**What Changed:**
- Updated instruction to extract `Target Servings` from input
- Implements ingredient scaling based on target servings
- Sets the `servings` field in output to match target servings

**Key Instruction:**
```python
instruction="""
    Input Processing:
    1. Parse the input to extract:
       - Recipe analysis (the main content)
       - User Context section containing "Target Servings" value
    2. Use the Target Servings value to scale ALL ingredient quantities appropriately

    IMPORTANT Scaling Instructions:
    - If the recipe originally serves X people and Target Servings is Y, multiply all ingredient quantities by (Y/X)
    - Example: Recipe for 4 servings with 200g flour, Target Servings is 2 → use 100g flour
    - Ensure the "servings" field in your output matches the Target Servings value
    """
```

**Why:** This allows users to request any number of servings, and the recipe will automatically scale all ingredients proportionally.

**Old Behavior:**
- Had a TODO comment for servings scaling
- Used a mock function returning hardcoded value of 2

**New Behavior:**
- Dynamically scales ingredients based on user input
- Properly sets servings field in output

### 3. Nutrition Calculator Agent (`sub_agents/nutrition/agent.py`)

**What Changed:**
- Updated instruction to extract `User Name` from input
- Calls `get_user_calories` tool with the extracted user name
- Provides personalized nutrition comparison

**Key Instruction:**
```python
instruction="""
    Input Processing:
    1. Parse the input to extract:
       - Recipe analysis (the main content with ingredients)
       - User Context section containing "User Name" value
    2. Use the User Name to fetch personalized calorie information

    Guidelines:
    - Extract the User Name from the "User Context" section in the input
    - Call get_user_calories with the extracted user name
    - Calculate percentage: (calories_per_serving / user_daily_calories) * 100
    - Include the user's name in your analysis for personalization
    """
```

**Updated Tool:**
```python
def get_user_calories(user_name: str) -> int:
    """Get user's daily calorie needs from the user database."""
    # Search for user by name in the database
    for user_id, user_data in users_db.items():
        if user_data["name"].lower() == user_name.lower():
            return user_data["daily_calorie_intake"]

    # Default fallback if user not found
    return user_profile["daily_calorie_intake"]
```

**Why:** Enables personalized nutrition recommendations based on the specific user's daily calorie needs and diet goals.

**Old Behavior:**
- Hardcoded to "John Doe"
- Always used the same user profile

**New Behavior:**
- Looks up user by name in database
- Supports multiple users (John Doe, Jane Smith, Mike Johnson)
- Falls back gracefully if user not found

### 4. Orchestrator Agent (`agent.py`)

**What Changed:**
- Fixed the sequential workflow to include parallel processing agent
- Improved combine outputs instruction

**Old Workflow:**
```python
overall_workflow = SequentialAgent(
    name="recipe_analysis_workflow",
    sub_agents=[video_analyzer_agent, combine_parallel]  # Missing parallel step!
)
```

**New Workflow:**
```python
overall_workflow = SequentialAgent(
    name="recipe_analysis_workflow",
    sub_agents=[video_analyzer_agent, parallel_processing_agent, combine_parallel]
)
```

**Why:** The parallel processing step was defined but not used in the workflow. This fix ensures recipe formatting and nutrition calculation run in parallel as intended.

### 5. Streamlit App (`app.py`)

**What Changed:**
- Added input widgets for `user_name` and `target_servings`
- Constructs JSON input with all three parameters
- Passes all inputs to the agent

**Input Collection:**
```python
# Add Input Widgets
col1, col2 = st.columns(2)
with col1:
    user_name = st.text_input("User Name", value="John Doe")
with col2:
    servings = st.number_input("Target Servings", min_value=1, value=2)

youtube_url = st.text_input("Enter YouTube URL", ...)
```

**Structured Input:**
```python
input_data = {
    "video_url": url,
    "user_context": {
        "target_servings": target_servings,
        "user_name": user
    }
}

initial_message = types.Content(
    role='user',
    parts=[types.Part(text=json.dumps(input_data))]
)
```

## How Data Flows Between Agents

### Sequential Agent Behavior
In ADK, a `SequentialAgent` passes the output of each agent to the next agent as input. This creates a chain:

```
Input → Agent1 → Output1 → Agent2 → Output2 → Agent3 → Final Output
```

### Parallel Agent Behavior
A `ParallelAgent` runs all sub-agents simultaneously on the **same input**. Each agent processes independently:

```
                  ┌→ Agent A → Output A ┐
Input (shared) ───┤                      ├→ Combined Outputs
                  └→ Agent B → Output B ┘
```

### Our Implementation

1. **Video Analyzer** receives JSON input and outputs: `Recipe Analysis + User Context`

2. **Parallel Processing** receives the video analyzer output:
   - **Recipe Formatter** reads the output, finds "Target Servings: 2", scales ingredients
   - **Nutrition Calculator** reads the output, finds "User Name: John Doe", looks up calories

3. **Combine Outputs** merges the two parallel outputs into one `RecipeCardWithNutrition` object

## User Database

Located in `data/database.py`:

```python
users_db = {
    "user_001": {
        "name": "John Doe",
        "daily_calorie_intake": 2000,
        "diet_goal": "maintain weight",
        ...
    },
    "user_002": {
        "name": "Jane Smith",
        "daily_calorie_intake": 1800,
        "diet_goal": "lose weight",
        ...
    },
    "user_003": {
        "name": "Mike Johnson",
        "daily_calorie_intake": 2500,
        "diet_goal": "gain weight",
        ...
    }
}
```

**To Add New Users:**
Simply add a new entry to `users_db` with the user's name and profile.

## Testing the Multi-Input System

### Example 1: Default User (John Doe, 2 Servings)

**Input:**
```json
{
  "video_url": "https://youtube.com/shorts/abc123",
  "user_context": {
    "target_servings": 2,
    "user_name": "John Doe"
  }
}
```

**Expected Behavior:**
- Recipe scaled to 2 servings
- Nutrition compared against John Doe's 2000 cal/day target
- Shows "X% of John Doe's daily needs"

### Example 2: Different User (Jane Smith, 4 Servings)

**Input:**
```json
{
  "video_url": "https://youtube.com/shorts/xyz789",
  "user_context": {
    "target_servings": 4,
    "user_name": "Jane Smith"
  }
}
```

**Expected Behavior:**
- Recipe scaled to 4 servings (ingredients doubled from original 2)
- Nutrition compared against Jane Smith's 1800 cal/day target
- Shows different percentage than John Doe

### Example 3: Large Servings (Mike Johnson, 6 Servings)

**Input:**
```json
{
  "video_url": "https://youtube.com/shorts/def456",
  "user_context": {
    "target_servings": 6,
    "user_name": "Mike Johnson"
  }
}
```

**Expected Behavior:**
- Recipe scaled to 6 servings (ingredients tripled)
- Nutrition compared against Mike Johnson's 2500 cal/day target
- Lower percentage due to higher daily calorie needs

## Key Design Decisions

### Why Pass Context Through Video Analyzer?

**Alternative 1:** Store context in agent state
- **Cons:** Requires state management, harder to debug, not guaranteed to persist

**Alternative 2:** Pass context separately to each agent
- **Cons:** ADK doesn't support selective input routing natively

**Our Choice:** Include context in video analyzer output
- **Pros:**
  - Simple and reliable
  - Works with ADK's sequential/parallel patterns
  - Easy to debug (context visible in output)
  - No state management needed

### Why Use Text-Based Context Passing?

We format the context as text in the output:
```
User Context:
- Target Servings: 2
- User Name: John Doe
```

**Why not JSON?**
- LLMs are excellent at parsing natural language
- More robust to slight variations
- Easier for humans to read in logs
- Works well with ADK's content passing

## Troubleshooting

### Issue: Ingredients Not Scaling

**Check:**
1. Video analyzer output includes "Target Servings: X"
2. Recipe formatter instruction includes scaling logic
3. Original recipe servings are detected correctly

**Debug:**
Add logging in recipe formatter to see extracted target servings value.

### Issue: Wrong User's Calories Used

**Check:**
1. Video analyzer output includes "User Name: XYZ"
2. User name matches entry in `users_db` (case-insensitive)
3. `get_user_calories` function is called with correct name

**Debug:**
Add logging in `get_user_calories` to see which user is looked up.

### Issue: Context Not Passed Through

**Check:**
1. JSON input is properly formatted
2. Video analyzer instruction includes pass-through logic
3. Parallel agents can access video analyzer output

**Debug:**
Log the video analyzer output to verify context is included.

## Future Enhancements

### Potential Improvements

1. **Structured Context Passing**
   - Use Pydantic models for type-safe context
   - Validate inputs before processing

2. **More User Preferences**
   - Dietary restrictions filtering
   - Preferred measurement units (metric/imperial)
   - Spice level preferences

3. **Advanced Scaling**
   - Non-linear scaling for spices and seasonings
   - Adjust cooking times based on batch size

4. **Real Database Integration**
   - Replace mock `users_db` with actual database
   - Support user authentication
   - Store user preferences persistently

## Summary

The multi-input system works by:
1. **Streamlit app** collects 3 inputs and creates structured JSON
2. **Video analyzer** parses JSON, analyzes video, passes context through
3. **Parallel agents** extract their specific inputs from the context:
   - Recipe formatter → uses target_servings
   - Nutrition calculator → uses user_name
4. **Combine agent** merges parallel outputs into final result

This design leverages ADK's sequential and parallel patterns while maintaining clean separation of concerns and enabling personalized, scaled recipe analysis.
