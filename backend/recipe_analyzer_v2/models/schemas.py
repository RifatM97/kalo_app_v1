"""Pydantic data models for recipe analyzer"""

from typing import Optional
from pydantic import BaseModel, Field, HttpUrl


class Ingredient(BaseModel):
    """Recipe ingredient with quantity and unit"""
    name: str = Field(..., description="Ingredient name")
    quantity: float = Field(..., description="Quantity of ingredient")
    unit: str = Field(..., description="Unit of measurement (e.g., g, ml, cups, tbsp)")
    notes: Optional[str] = Field(None, description="Additional notes (e.g., 'finely chopped')")


class RecipeStep(BaseModel):
    """Individual cooking step"""
    step_number: int = Field(..., description="Step sequence number")
    instruction: str = Field(..., description="Detailed instruction for this step")
    duration: Optional[str] = Field(None, description="Estimated duration (e.g., '5 minutes')")


class NutritionPerPerson(BaseModel):
    """Nutritional values for a single serving (1 person)"""
    calories_kcal: float = Field(..., description="Calories in kilocalories")
    protein_g: float = Field(..., description="Protein in grams")
    fat_g: float = Field(..., description="Fat in grams")
    carbohydrates_g: float = Field(..., description="Carbohydrates in grams")


class RecipeCard(BaseModel):
    """Complete recipe card with all details"""
    title: str = Field(..., description="Recipe title")
    source_url: str = Field(..., description="YouTube Shorts URL")
    servings: int = Field(..., description="Number of servings")
    prep_time_minutes: Optional[int] = Field(None, description="Preparation time in minutes")
    cook_time_minutes: Optional[int] = Field(None, description="Cooking time in minutes")
    difficulty: str = Field(..., description="Difficulty level: Easy, Medium, or Hard")
    cuisine: Optional[str] = Field(None, description="Cuisine type (e.g., Italian, Chinese)")
    ingredients: list[Ingredient] = Field(..., description="List of ingredients")
    steps: list[RecipeStep] = Field(..., description="Cooking instructions")
    nutrition_per_serving: NutritionPerPerson = Field(..., description="Nutritional info per person")
    tips: list[str] = Field(default_factory=list, description="Cooking tips and suggestions")
    tags: list[str] = Field(default_factory=list, description="Recipe tags (e.g., vegetarian, quick)")


class VideoAnalysisResult(BaseModel):
    """Result from video analysis agent"""
    video_id: str = Field(..., description="YouTube video ID")
    title: str = Field(..., description="Extracted recipe title")
    ingredients_raw: list[str] = Field(..., description="Raw ingredient list from video")
    steps_raw: list[str] = Field(..., description="Raw steps from video")
    estimated_servings: int = Field(default=1, description="Estimated number of servings")
    prep_time_minutes: Optional[int] = None
    cook_time_minutes: Optional[int] = None
    difficulty: str = Field(default="Medium", description="Estimated difficulty")
    cuisine: Optional[str] = None
    tips: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
