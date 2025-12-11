"""
AI Workout Generator
Creates personalized workout plans based on fitness goals
"""
import json
import logging

logger = logging.getLogger(__name__)

class WorkoutPlanGenerator:
    """Generate personalized workout plans"""
    
    WORKOUT_PLAN_PROMPT = """
    Create a personalized {duration_weeks}-week workout plan for the following user:
    
    - Fitness Goal: {goal}
    - Experience Level: {level}
    - Frequency: {frequency} workouts per week
    - Available Equipment: {equipment}
    - Focus Areas: {focus_areas}
    
    Generate a progressive overload workout plan in JSON format:
    {{
        "title": "12-Week Strength Training Program",
        "weeks": [
            {{
                "week": 1,
                "workouts": [
                    {{
                        "day": "Monday",
                        "type": "strength",
                        "exercises": [
                            {{
                                "name": "Barbell Squat",
                                "sets": 4,
                                "reps": 8,
                                "weight": "185 lbs",
                                "rest_seconds": 90,
                                "notes": "Explosive movement"
                            }}
                        ],
                        "total_duration_minutes": 60
                    }}
                ],
                "progression": "Increase weight by 5 lbs on main lifts"
            }}
        ],
        "progression_notes": "Linear progression week by week"
    }}
    
    Return only valid JSON with 4-12 weeks.
    """
    
    @staticmethod
    async def generate_workout_plan(
        goal: str,
        level: str,
        frequency: int,
        equipment: list[str],
        duration_weeks: int = 12,
        focus_areas: list[str] = None,
    ) -> dict:
        """
        Generate workout plan using AI
        goal: strength, weight_loss, endurance, muscle_gain, general_fitness
        level: beginner, intermediate, advanced
        """
        try:
            import openai
            
            equipment_str = ", ".join(equipment) if equipment else "None (bodyweight)"
            focus_str = ", ".join(focus_areas) if focus_areas else "Full body"
            
            prompt = WorkoutPlanGenerator.WORKOUT_PLAN_PROMPT.format(
                goal=goal,
                level=level,
                frequency=frequency,
                equipment=equipment_str,
                duration_weeks=duration_weeks,
                focus_areas=focus_str,
            )
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an elite personal trainer creating structured workout programs."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
            )
            
            workout_plan_json = response.choices[0].message.content
            return {
                "status": "success",
                "workout_plan": json.loads(workout_plan_json)
            }
        except Exception as e:
            logger.error(f"Workout plan generation failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

class WorkoutProgressTracker:
    """Track workout progress and adjust plans"""
    
    @staticmethod
    def detect_plateaus(completed_workouts: list[dict]) -> list[str]:
        """Detect when user has plateaued"""
        suggestions = []
        
        if len(completed_workouts) < 4:
            return suggestions
        
        # Simple plateau detection: if weights haven't increased in 4 weeks
        recent = completed_workouts[-4:]
        weights = []
        
        for wo in recent:
            for exercise in wo.get("exercises", []):
                if "weight" in exercise:
                    try:
                        weight = float(exercise["weight"].split()[0])
                        weights.append(weight)
                    except:
                        pass
        
        if len(weights) >= 4 and weights[-1] == weights[0]:
            suggestions.append("No weight progression detected. Try increasing volume or reps.")
        
        return suggestions
