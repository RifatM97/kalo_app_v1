# Recipe Analyzer V3 - Streamlit Application

A beautiful web interface for analyzing YouTube cooking videos and extracting structured recipe information with nutritional data.

## Features

- **Simple Input**: Just paste a YouTube URL
- **Beautiful UI**: Clean, responsive design with cards and metrics
- **Complete Recipe Cards**: Title, ingredients, instructions, and tips
- **Nutritional Information**: Calories, protein, fat, and carbohydrates per serving
- **Personalized Insights**: Comparison against daily calorie needs
- **Source Tracking**: Direct link to original video
- **JSON Export**: View and download raw JSON data

## Installation

### 1. Install Dependencies

From the `backend` directory:

```bash
pip install -e .
```

This will install all required dependencies including Streamlit.

Alternatively, install Streamlit separately:

```bash
pip install streamlit>=1.28.0
```

### 2. Set Up Environment Variables

Make sure you have a `.env` file in the `recipe_analyzer_v3` directory with your Gemini API key:

```bash
GEMINI_API_KEY=your_api_key_here
```

## Running the Application

### Start the Streamlit App

**Option 1: Using the launch script (Recommended)**

From the `recipe_analyzer_v3` directory:

```bash
./run_app.sh
```

**Option 2: Using uv (if you have uv installed) - THIS WORKS**

From the `recipe_analyzer_v3` directory - **use this one if you are using uv**:

```bash
uv run streamlit run app.py
```

**Option 3: Using streamlit directly**

From the `recipe_analyzer_v3` directory:

```bash
streamlit run app.py
```

**Option 4: From the backend directory**

```bash
cd backend
streamlit run recipe_analyzer_v3/app.py
```

The app will open in your default browser at `http://localhost:8501`

## Usage

### Step-by-Step Guide

1. **Launch the App**: Run the command above to start the Streamlit server

2. **Enter YouTube URL**:
   - Paste any YouTube cooking video URL
   - Supports regular YouTube videos and Shorts
   - Example: `https://youtube.com/shorts/abc123`

3. **Click "Analyze Recipe"**:
   - The agent will process the video
   - This may take 10-20 seconds depending on the video

4. **View Results**:
   - Recipe title and metadata
   - Servings, prep time, cook time
   - Complete ingredient list with quantities
   - Step-by-step cooking instructions
   - Nutritional breakdown per serving
   - Cooking tips and tags

### Example URLs to Try

You can test the app with any YouTube cooking video. Some examples:

- YouTube Shorts with quick recipes
- Full-length cooking tutorials
- Recipe demonstration videos

## UI Components

### Recipe Card (Left Column)

- **Header**: Recipe title
- **Details**: Servings, prep time, cook time, difficulty, cuisine
- **Ingredients**: Full list with quantities and units
- **Instructions**: Numbered steps with optional durations
- **Tips**: Helpful cooking advice
- **Tags**: Recipe categories (vegetarian, quick, etc.)

### Nutrition Panel (Right Column)

- **Calories**: Total kilocalories per serving
- **Macronutrients**:
  - Protein (grams)
  - Fat (grams)
  - Carbohydrates (grams)
- **Daily Percentage**: Comparison to daily needs
- **Source Link**: Direct link to original video

### Additional Features

- **Raw JSON Viewer**: Expandable section showing complete structured data
- **Error Handling**: Clear error messages for invalid inputs
- **Loading States**: Spinner during processing
- **Responsive Design**: Works on desktop and mobile

## Customization

### Modify User Profile

To customize the personalized nutrition comparison, edit the user profile in:

```
recipe_analyzer_v3/data/database.py
```

Update fields like:
- `daily_calorie_intake`: Your target daily calories
- `diet_goal`: "lose weight", "gain weight", or "maintain weight"
- `dietary_restrictions`: List of restrictions

### Styling

The app uses custom CSS defined in `app.py`. You can modify:
- Colors and themes
- Card layouts
- Font sizes
- Spacing and padding

Edit the CSS in the `st.markdown()` section at the top of `app.py`.

### Agent Configuration

To modify how the recipe analysis works, update the agent files in:
- `recipe_analyzer_v3/agent.py`: Main orchestrator
- `recipe_analyzer_v3/sub_agents/`: Individual agent logic

## Troubleshooting

### Common Issues

**1. "Module not found" errors**
```bash
# Reinstall dependencies
pip install -e .
```

**2. "GEMINI_API_KEY not found"**
- Ensure `.env` file exists in `recipe_analyzer_v3/` directory
- Check that the API key is valid

**3. "Agent timeout" errors**
- Try a shorter video
- Check your internet connection
- Ensure Gemini API quota is not exceeded

**4. "Could not parse recipe data"**
- Some videos may not contain clear recipe information
- Try a different video with more structured content
- Check the raw response in the error message

### Performance Tips

- **Shorter videos** process faster (Shorts are ideal)
- **Clear recipes** with visible ingredients work best
- **Good lighting** helps the video analysis
- **Spoken instructions** improve extraction accuracy

## Architecture

The Streamlit app integrates with the Recipe Analyzer V3 multi-agent system:

```
User Input (YouTube URL)
    ↓
Streamlit UI (app.py)
    ↓
InMemoryRunner
    ↓
Sequential Workflow Agent
    ↓
├─ Video Analyzer (analyzes video)
    ↓
├─ Parallel Processing
│  ├─ Recipe Formatter (structures data)
│  └─ Nutrition Calculator (computes nutrition)
    ↓
└─ Combine Outputs (merges results)
    ↓
RecipeCardWithNutrition JSON
    ↓
Streamlit UI (displays results)
```

## Development

### Local Development

1. Make changes to `app.py`
2. Save the file
3. Streamlit will auto-reload in the browser

### Adding Features

To add new features:
1. Modify the UI in `app.py`
2. Update agent logic in `recipe_analyzer_v3/agent.py` or sub-agents
3. Extend data models in `recipe_analyzer_v3/models/schemas.py`

## Production Deployment

### Streamlit Cloud

1. Push your code to GitHub
2. Connect to [Streamlit Cloud](https://streamlit.io/cloud)
3. Add `GEMINI_API_KEY` as a secret
4. Deploy

### Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install -e .

COPY recipe_analyzer_v3 ./recipe_analyzer_v3

EXPOSE 8501

CMD ["streamlit", "run", "recipe_analyzer_v3/app.py"]
```

Build and run:

```bash
docker build -t recipe-analyzer .
docker run -p 8501:8501 -e GEMINI_API_KEY=your_key recipe-analyzer
```

## Support

For issues or questions:
- Check the main README in `recipe_analyzer_v3/README.md`
- Review the agent architecture documentation
- Test with different YouTube videos
- Check Gemini API status and quota

## License

[Your License Here]
