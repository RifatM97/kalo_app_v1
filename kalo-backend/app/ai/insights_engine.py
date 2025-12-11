"""
AI Insights Engine
Generates personalized insights and recommendations from user data
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

class InsightAnalyzer:
    """Analyze user data and generate insights"""
    
    INSIGHTS_PROMPT = """
    Based on the following user health data from the last 30 days:
    
    Daily Calorie Average: {avg_calories}
    Protein Average: {avg_protein}g
    Carbs Average: {avg_carbs}g
    Fat Average: {avg_fat}g
    
    Workouts Completed: {workout_count}
    Average Workout Duration: {avg_workout_duration}m
    
    Meal Pattern: {meal_pattern}
    Consistency Score: {consistency}%
    
    Please generate 3-5 personalized insights and actionable recommendations as JSON:
    {{
        "insights": [
            {{
                "title": "Protein Intake Observation",
                "description": "Your average daily protein is below recommended levels",
                "recommendation": "Increase protein by adding lean meats, eggs, or protein powder",
                "impact": "high",
                "type": "nutrition"
            }}
        ],
        "strengths": ["Consistent workout routine", "Good hydration"],
        "areas_for_improvement": ["Late night snacking", "Weekend consistency"]
    }}
    
    Return only valid JSON.
    """
    
    @staticmethod
    async def generate_insights(
        daily_logs: list[dict],
        workouts: list[dict],
    ) -> dict:
        """
        Generate personalized insights from user data
        """
        try:
            import openai
            
            # Calculate averages
            avg_calories = sum(log.get("total_calories", 0) for log in daily_logs) / max(len(daily_logs), 1)
            avg_protein = sum(log.get("total_macros", {}).get("protein", 0) for log in daily_logs) / max(len(daily_logs), 1)
            avg_carbs = sum(log.get("total_macros", {}).get("carbs", 0) for log in daily_logs) / max(len(daily_logs), 1)
            avg_fat = sum(log.get("total_macros", {}).get("fat", 0) for log in daily_logs) / max(len(daily_logs), 1)
            
            avg_workout_duration = sum(wo.get("duration", 0) for wo in workouts) / max(len(workouts), 1)
            
            # Detect patterns
            meal_pattern = "Regular" if len(daily_logs) > 20 else "Inconsistent"
            consistency = (len(daily_logs) / 30 * 100) if daily_logs else 0
            
            prompt = InsightAnalyzer.INSIGHTS_PROMPT.format(
                avg_calories=int(avg_calories),
                avg_protein=int(avg_protein),
                avg_carbs=int(avg_carbs),
                avg_fat=int(avg_fat),
                workout_count=len(workouts),
                avg_workout_duration=int(avg_workout_duration),
                meal_pattern=meal_pattern,
                consistency=int(consistency),
            )
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a health coach analyzing user fitness and nutrition data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )
            
            insights_json = response.choices[0].message.content
            return {
                "status": "success",
                "insights": json.loads(insights_json)
            }
        except Exception as e:
            logger.error(f"Insight generation failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

class PatternDetector:
    """Detect patterns in user behavior"""
    
    @staticmethod
    def detect_eating_patterns(daily_logs: list[dict]) -> dict:
        """Detect eating patterns (e.g., high carbs at night)"""
        patterns = {
            "high_carbs_at_night": False,
            "high_calories_weekend": False,
            "low_protein_days": False,
            "skipping_meals": False,
        }
        
        if len(daily_logs) < 7:
            return patterns
        
        # Simple pattern detection
        for log in daily_logs[-7:]:
            macros = log.get("total_macros", {})
            if macros.get("carbs", 0) > 300 and log.get("date", "").endswith(("18", "19", "20")):
                patterns["high_carbs_at_night"] = True
        
        return patterns
    
    @staticmethod
    def detect_workout_trends(workouts: list[dict]) -> dict:
        """Detect workout patterns"""
        trends = {
            "consistency_good": False,
            "plateau_detected": False,
            "variety_low": False,
        }
        
        if len(workouts) < 4:
            return trends
        
        # Check last 4 weeks
        recent_workouts = workouts[-16:]
        workout_days = len(recent_workouts) / 4
        trends["consistency_good"] = workout_days >= 3  # 3+ workouts per week
        
        return trends
