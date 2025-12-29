"""Streamlit application for Recipe Analyzer V3"""

import streamlit as st
import asyncio
import sys
import os
from pathlib import Path
import json
from dotenv import load_dotenv

# Setup paths - add backend directory to Python path
current_dir = Path(__file__).parent.resolve()
backend_dir = current_dir.parent

# Load environment variables from .env file
env_path = current_dir / ".env"
if env_path.exists():
    load_dotenv(env_path)
    st.success(f"✅ Loaded environment from {env_path}")
else:
    st.warning(f"⚠️ .env file not found at {env_path}")

# Verify API key is loaded
if not os.getenv("GEMINI_API_KEY"):
    st.error("❌ GEMINI_API_KEY not found in environment variables!")
    st.info("Please create a .env file in the recipe_analyzer_v3 directory with: GEMINI_API_KEY=your_api_key")
    st.stop()

# Ensure backend is in path FIRST (before any imports)
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Now import after path is set
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Import the root agent from the recipe_analyzer_v3 package
from recipe_analyzer_v3.agent import root_agent

# Configure page
st.set_page_config(
    page_title="Recipe Analyzer",
    page_icon="🍳",
    layout="wide"
)

# Add custom CSS for better styling
st.markdown("""
    <style>
    .recipe-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .nutrition-card {
        background-color: #e8f4f8;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .ingredient-item {
        padding: 5px 0;
        border-bottom: 1px solid #e0e0e0;
    }
    .step-item {
        padding: 10px;
        margin: 5px 0;
        background-color: white;
        border-left: 3px solid #4CAF50;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("🍳 Recipe Analyzer")
st.markdown("Extract recipes and nutritional information from YouTube cooking videos")

# Input section
youtube_url = st.text_input(
    "Enter YouTube URL",
    placeholder="https://youtube.com/shorts/...",
    help="Paste the URL of a YouTube cooking video"
)

# Analyze button
if st.button("Analyze Recipe", type="primary"):
    if not youtube_url:
        st.error("Please enter a YouTube URL")
    else:
        with st.spinner("Analyzing video... This may take a few moments."):
            try:
                # Run the agent asynchronously
                async def run_agent(url: str):
                    session_service = InMemorySessionService()
                    runner = Runner(
                        agent=root_agent,
                        app_name='recipe_analyzer_app',
                        session_service=session_service,
                    )

                    # Create session
                    session = await session_service.create_session(
                        app_name='recipe_analyzer_app',
                        user_id='streamlit_user',
                        session_id='streamlit_session'
                    )

                    # Create initial message
                    initial_message = types.Content(
                        role='user',
                        parts=[types.Part(text=url)]
                    )

                    # Run agent and collect response
                    response_content = None
                    async for event in runner.run_async(
                        user_id=session.user_id,
                        session_id=session.id,
                        new_message=initial_message,
                    ):
                        if event.content.role == 'model':
                            response_content = event.content

                    return response_content

                # Execute async function
                result = asyncio.run(run_agent(youtube_url))

                # Extract the recipe data from the result
                if result and result.parts:
                    # The result should be the RecipeCardWithNutrition
                    recipe_text = result.parts[0].text if hasattr(result.parts[0], 'text') else str(result.parts[0])

                    # Try to parse as JSON
                    try:
                        recipe_data = json.loads(recipe_text)
                    except:
                        # If not JSON, try to extract from the response
                        st.warning("Could not parse recipe data directly. Displaying raw response.")
                        st.write(recipe_text)
                        recipe_data = None

                    if recipe_data:
                        # Display recipe card
                        st.success("Recipe analyzed successfully!")

                        # Recipe Header
                        st.markdown("---")
                        st.header(recipe_data.get("title", "Recipe"))

                        # Create two columns for layout
                        col1, col2 = st.columns([2, 1])

                        with col1:
                            # Recipe Details
                            st.subheader("📋 Recipe Details")

                            details_col1, details_col2, details_col3 = st.columns(3)
                            with details_col1:
                                st.metric("Servings", recipe_data.get("servings", "N/A"))
                            with details_col2:
                                prep_time = recipe_data.get("prep_time_minutes")
                                st.metric("Prep Time", f"{prep_time} min" if prep_time else "N/A")
                            with details_col3:
                                cook_time = recipe_data.get("cook_time_minutes")
                                st.metric("Cook Time", f"{cook_time} min" if cook_time else "N/A")

                            # Additional info
                            info_col1, info_col2 = st.columns(2)
                            with info_col1:
                                st.write(f"**Difficulty:** {recipe_data.get('difficulty', 'N/A')}")
                            with info_col2:
                                cuisine = recipe_data.get('cuisine')
                                if cuisine:
                                    st.write(f"**Cuisine:** {cuisine}")

                            # Ingredients
                            st.subheader("🥘 Ingredients")
                            ingredients = recipe_data.get("ingredients", [])
                            for ing in ingredients:
                                quantity = ing.get("quantity", "")
                                unit = ing.get("unit", "")
                                name = ing.get("name", "")
                                notes = ing.get("notes", "")

                                ing_text = f"**{quantity} {unit}** {name}"
                                if notes:
                                    ing_text += f" _{notes}_"
                                st.markdown(f"- {ing_text}")

                            # Instructions
                            st.subheader("👨‍🍳 Instructions")
                            steps = recipe_data.get("steps", [])
                            for step in steps:
                                step_num = step.get("step_number", "")
                                instruction = step.get("instruction", "")
                                duration = step.get("duration", "")

                                duration_text = f" ⏱️ _{duration}_" if duration else ""
                                st.markdown(f"""
                                    <div class="step-item">
                                        <strong>Step {step_num}:</strong> {instruction}{duration_text}
                                    </div>
                                """, unsafe_allow_html=True)

                            # Tips
                            tips = recipe_data.get("tips", [])
                            if tips:
                                st.subheader("💡 Tips")
                                for tip in tips:
                                    st.info(tip)

                            # Tags
                            tags = recipe_data.get("tags", [])
                            if tags:
                                st.subheader("🏷️ Tags")
                                st.write(" • ".join(tags))

                        with col2:
                            # Nutrition Information
                            st.subheader("📊 Nutrition Per Serving")
                            nutrition = recipe_data.get("nutrition", {})

                            if nutrition:
                                # Display nutrition metrics
                                st.markdown('<div class="nutrition-card">', unsafe_allow_html=True)

                                calories = nutrition.get("calories_kcal", 0)
                                st.metric("Calories", f"{calories:.0f} kcal")

                                st.markdown("---")

                                protein = nutrition.get("protein_g", 0)
                                st.metric("Protein", f"{protein:.1f}g")

                                fat = nutrition.get("fat_g", 0)
                                st.metric("Fat", f"{fat:.1f}g")

                                carbs = nutrition.get("carbohydrates_g", 0)
                                st.metric("Carbohydrates", f"{carbs:.1f}g")

                                # Percentage of daily needs
                                percentage = nutrition.get("calories_percentage_of_daily_needs")
                                if percentage:
                                    st.markdown("---")
                                    st.write(f"**{percentage:.1f}%** of daily calorie needs")

                                st.markdown('</div>', unsafe_allow_html=True)
                            else:
                                st.warning("Nutrition information not available")

                            # Source link
                            st.markdown("---")
                            st.subheader("🔗 Source")
                            source_url = recipe_data.get("source_url", youtube_url)
                            st.markdown(f"[View Original Video]({source_url})")

                        # Raw JSON (collapsible)
                        with st.expander("📄 View Raw JSON"):
                            st.json(recipe_data)
                else:
                    st.error("No response received from the agent")

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.exception(e)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        Powered by Google ADK & Gemini 2.5 | Recipe Analyzer V3
    </div>
    """,
    unsafe_allow_html=True
)
