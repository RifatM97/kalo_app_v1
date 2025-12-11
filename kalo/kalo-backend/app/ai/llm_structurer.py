"""
LLM Structurer Module
Structures raw recipe data (transcript, OCR, detections) into JSON using LLM
"""

import json
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class StructuringError(Exception):
    """Raised when recipe structuring fails"""
    pass


class LLMStructurer:
    """Structures recipe data using LLM APIs"""
    
    def __init__(self, api_key: Optional[str] = None, provider: str = "openai"):
        """
        Initialize LLMStructurer
        
        Args:
            api_key: LLM API key (OpenAI, Anthropic, etc.)
            provider: LLM provider (openai, anthropic, local)
        """
        self.api_key = api_key
        self.provider = provider
        self.logger = logger
        
        if provider == "openai":
            try:
                import openai
                if api_key:
                    openai.api_key = api_key
                self.client = openai.OpenAI(api_key=api_key)
            except ImportError:
                raise ImportError("openai not installed. Run: pip install openai")
        elif provider == "anthropic":
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=api_key)
            except ImportError:
                raise ImportError("anthropic not installed. Run: pip install anthropic")
    
    def _create_prompt(
        self,
        transcript: str,
        ocr_text: str,
        detected_items: List[str],
        video_title: str = ""
    ) -> str:
        """
        Create a detailed prompt for the LLM
        
        Args:
            transcript: Audio transcription
            ocr_text: OCR text from frames
            detected_items: Vision-detected objects
            video_title: Video title if available
            
        Returns:
            Structured prompt for LLM
        """
        
        prompt = f"""You are an expert recipe extraction AI. Based on the following data extracted from a cooking video, generate an accurate and detailed recipe in JSON format.

VIDEO DATA:
-----------
Title: {video_title or 'Unknown'}

Audio Transcript (what was spoken):
{transcript[:1000]}  # Limit to first 1000 chars

Text from Video Frames (OCR):
{ocr_text[:1000]}

Detected Objects/Ingredients:
{', '.join(detected_items[:20])}

TASK:
-----
Generate a complete recipe JSON with the following structure:
{{
    "title": "Recipe name",
    "ingredients": [
        {{"name": "ingredient name", "quantity": number, "unit": "grams/ml/cup/tsp/tbsp/whole"}},
        ...
    ],
    "steps": [
        {{"step": 1, "instruction": "detailed instruction"}},
        ...
    ],
    "cook_time_minutes": number,
    "prep_time_minutes": number,
    "serves": number,
    "macros": {{
        "calories_per_serving": number,
        "protein_grams": number,
        "carbs_grams": number,
        "fat_grams": number
    }},
    "difficulty": "easy|medium|hard",
    "tags": ["tag1", "tag2"]
}}

IMPORTANT:
----------
1. Infer quantities from context ("season to taste" = 2 tsp salt)
2. Convert all measurements to standard units
3. Be specific with instructions (e.g., "medium heat" not just "heat")
4. Include prep steps like chopping and boiling
5. Base macros on realistic serving sizes
6. Only include JSON in response, no explanations

RESPOND ONLY WITH VALID JSON:
"""
        return prompt
    
    def structure_recipe(
        self,
        transcript: str,
        ocr_text: str,
        detected_items: List[str],
        video_title: str = ""
    ) -> Dict:
        """
        Structure raw data into a recipe JSON
        
        Args:
            transcript: Audio transcription from Whisper
            ocr_text: Text extracted by OCR
            detected_items: Objects detected by vision
            video_title: Video title if available
            
        Returns:
            Structured recipe dict
        """
        try:
            self.logger.info("Structuring recipe data with LLM")
            
            # Create prompt
            prompt = self._create_prompt(
                transcript,
                ocr_text,
                detected_items,
                video_title
            )
            
            self.logger.info("Calling LLM API...")
            
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a recipe extraction expert. Respond with ONLY valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,  # Lower temperature for consistency
                    max_tokens=2000
                )
                response_text = response.choices[0].message.content
                
            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=2000,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                response_text = response.content[0].text
            else:
                raise StructuringError(f"Unknown provider: {self.provider}")
            
            self.logger.info("✓ LLM response received")
            
            # Parse JSON response
            try:
                recipe = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    recipe = json.loads(json_match.group())
                else:
                    raise StructuringError("Could not parse LLM response as JSON")
            
            # Validate recipe structure
            self._validate_recipe(recipe)
            
            # Transform to match Swift model exactly
            recipe = self._transform_for_swift(recipe)
            
            self.logger.info(f"✓ Recipe structured: {recipe.get('title', 'Unknown')}")
            return recipe
            
        except Exception as e:
            msg = f"Recipe structuring failed: {str(e)}"
            self.logger.error(msg)
            raise StructuringError(msg) from e
    
    def _transform_for_swift(self, recipe: Dict) -> Dict:
        """
        Transform recipe data to match Swift Codable model exactly
        
        Swift expects:
        - task_id (snake_case)
        - cook_time_minutes (snake_case)
        - prep_time_minutes (snake_case)
        - Ingredients with: name, quantity (float), unit (string)
        - Steps with: step (int), instruction (string)
        - Macros with: calories, protein, carbs, fat
        
        Args:
            recipe: Raw recipe dict from LLM
            
        Returns:
            Transformed recipe matching Swift model
        """
        # Transform ingredients
        ingredients = []
        for ing in recipe.get("ingredients", []):
            if isinstance(ing, dict):
                ingredients.append({
                    "name": ing.get("name", ""),
                    "quantity": self._parse_quantity(ing.get("quantity")),
                    "unit": ing.get("unit", "")
                })
        
        # Transform steps
        steps = []
        for i, step in enumerate(recipe.get("steps", []), 1):
            if isinstance(step, dict):
                steps.append({
                    "step": step.get("step", i),
                    "instruction": step.get("instruction", "")
                })
            else:
                steps.append({
                    "step": i,
                    "instruction": str(step)
                })
        
        # Transform macros
        macros = recipe.get("macros", {})
        if macros:
            macros = {
                "calories": self._parse_number(macros.get("calories_per_serving") or macros.get("calories")),
                "protein": self._parse_number(macros.get("protein_grams") or macros.get("protein")),
                "carbs": self._parse_number(macros.get("carbs_grams") or macros.get("carbs")),
                "fat": self._parse_number(macros.get("fat_grams") or macros.get("fat"))
            }
        
        # Return transformed recipe with exact Swift field names
        return {
            "title": recipe.get("title", "Unknown Recipe"),
            "description": recipe.get("description", ""),
            "ingredients": ingredients,
            "steps": steps,
            "cook_time_minutes": int(recipe.get("cook_time_minutes", 0) or 0),
            "prep_time_minutes": int(recipe.get("prep_time_minutes", 0) or 0),
            "difficulty": recipe.get("difficulty", "medium"),
            "serves": int(recipe.get("serves", 1) or 1),
            "macros": macros or {
                "calories": 0,
                "protein": 0,
                "carbs": 0,
                "fat": 0
            },
            "tags": recipe.get("tags", [])
        }
    
    @staticmethod
    def _parse_quantity(value) -> float:
        """Parse quantity to float"""
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        try:
            return float(str(value).split()[0])
        except:
            return None
    
    @staticmethod
    def _parse_number(value) -> float:
        """Parse any number value"""
        if value is None:
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)
        try:
            return float(value)
        except:
            return 0.0
    
    def _validate_recipe(self, recipe: Dict) -> None:
        """
        Validate recipe structure
        
        Args:
            recipe: Recipe dict to validate
            
        Raises:
            StructuringError: If recipe is invalid
        """
        required_fields = ["title", "ingredients", "steps"]
        
        for field in required_fields:
            if field not in recipe:
                raise StructuringError(f"Missing required field: {field}")
        
        if not isinstance(recipe["ingredients"], list):
            raise StructuringError("Ingredients must be a list")
        
        if not isinstance(recipe["steps"], list):
            raise StructuringError("Steps must be a list")
        
        self.logger.info(f"  ✓ Validated: {len(recipe['ingredients'])} ingredients, {len(recipe['steps'])} steps")


# Singleton structurer instance
_structurer = None


def get_structurer(api_key: Optional[str] = None, provider: str = "openai") -> LLMStructurer:
    """Get or create LLMStructurer singleton"""
    global _structurer
    if _structurer is None:
        _structurer = LLMStructurer(api_key, provider)
    return _structurer


async def structure_recipe(
    transcript: str,
    ocr_text: str,
    detected_items: List[str],
    video_title: str = "",
    api_key: Optional[str] = None
) -> Dict:
    """
    Async wrapper for structuring recipe
    
    Args:
        transcript: Audio transcription
        ocr_text: OCR text
        detected_items: Detected items
        video_title: Video title
        api_key: LLM API key
        
    Returns:
        Structured recipe dict matching Swift model
    """
    structurer = get_structurer(api_key)
    return structurer.structure_recipe(transcript, ocr_text, detected_items, video_title)
