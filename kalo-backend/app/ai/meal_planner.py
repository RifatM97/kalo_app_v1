"""
AI Meal Plan Generator
Generates personalized weekly meal plans based on nutrition goals
"""
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class MealPlanGenerator:
    """Generate AI-powered meal plans"""
    
    MEAL_PLAN_PROMPT = """
    Create a healthy weekly meal plan for the following user:
    
    - Daily Calorie Goal: {daily_calories}
    - Protein Target: {protein}g per day
    - Carbs Target: {carbs}g per day
    - Fat Target: {fat}g per day
    - Diet Type: {diet_type}
    - Restrictions: {restrictions}
    
    Please generate a JSON meal plan with 7 days, 4 meals per day:
    {{
        "week": [
            {{
                "day": "Monday",
                "meals": [
                    {{
                        "meal_type": "breakfast",
                        "recipe_name": "Oatmeal with Berries",
                        "estimated_calories": 350,
                        "macros": {{"protein": 15, "carbs": 50, "fat": 8}}
                    }}
                ]
            }}
        ],
        "weekly_summary": {{
            "avg_calories": 2000,
            "avg_protein": 150,
            "avg_carbs": 200,
            "avg_fat": 65
        }},
        "grocery_items": [
            {{"item": "Oats", "quantity": 2, "unit": "kg"}}
        ]
    }}
    
    Return only valid JSON.
    """
    
    @staticmethod
    async def generate_meal_plan(
        daily_calories: int,
        macro_targets: dict,
        diet_type: str = "balanced",
        restrictions: list[str] = None,
    ) -> dict:
        """
        Generate meal plan using GPT
        """
        try:
            import openai
            
            restrictions_str = ", ".join(restrictions) if restrictions else "None"
            
            prompt = MealPlanGenerator.MEAL_PLAN_PROMPT.format(
                daily_calories=daily_calories,
                protein=macro_targets.get("protein", 150),
                carbs=macro_targets.get("carbs", 250),
                fat=macro_targets.get("fat", 70),
                diet_type=diet_type,
                restrictions=restrictions_str,
            )
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional nutritionist creating meal plans."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
            )
            
            meal_plan_json = response.choices[0].message.content
            return {
                "status": "success",
                "meal_plan": json.loads(meal_plan_json)
            }
        except Exception as e:
            logger.error(f"Meal plan generation failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

class GroceryListGenerator:
    """Auto-generate grocery list from meal plan"""
    
    @staticmethod
    def generate_from_meal_plan(meal_plan: dict) -> list[dict]:
        """
        Extract and consolidate grocery items from meal plan
        """
        try:
            grocery_items = []
            
            # Extract from meal plan
            if "grocery_items" in meal_plan:
                grocery_items = meal_plan["grocery_items"]
            
            # Consolidate duplicates
            item_dict = {}
            for item in grocery_items:
                key = item["item"].lower()
                if key in item_dict:
                    # Combine quantities (simplified)
                    item_dict[key]["quantity"] += item["quantity"]
                else:
                    item_dict[key] = item
            
            return list(item_dict.values())
        except Exception as e:
            logger.error(f"Grocery list generation failed: {e}")
            return []
