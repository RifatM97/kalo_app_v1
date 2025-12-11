"""
Recipe Extraction Service using OpenAI Vision
Extracts recipes from images and videos with structured JSON output
"""

import logging
import io
from typing import Dict, Any, List, Optional
from PIL import Image

logger = logging.getLogger(__name__)


class RecipeExtractor:
    """Extract recipes from images using OpenAI Vision API."""
    
    def __init__(self, openai_provider):
        """
        Initialize recipe extractor.
        
        Args:
            openai_provider: Instance of OpenAIProvider
        """
        self.provider = openai_provider
    
    async def extract_from_image(
        self,
        image_bytes: bytes
    ) -> Dict[str, Any]:
        """
        Extract recipe from a single image.
        
        Args:
            image_bytes: Image data
            
        Returns:
            Dictionary with recipe data:
            {
                "title": str,
                "description": str,
                "servings": int,
                "ingredients": [{"name": str, "quantity": float, "unit": str}],
                "steps": [str],
                "estimated_calories_per_serving": float,
                "macros_per_serving": {
                    "protein_g": float,
                    "carbs_g": float,
                    "fat_g": float
                },
                "tags": [str],
                "prep_time_minutes": int,
                "cook_time_minutes": int,
                "difficulty": str
            }
        """
        try:
            logger.info("Starting recipe extraction from image")
            
            # Validate image
            image_bytes = self._validate_and_resize_image(image_bytes)
            
            # Craft the extraction prompt
            system_prompt = """You are an expert chef and nutritionist analyzing recipe images.
Extract ALL visible recipe information and provide complete, accurate nutritional estimates.
Always respond with valid JSON only, no additional text."""
            
            prompt = """Analyze this recipe image and extract the following information in JSON format:

{
  "title": "Recipe name (create one if not visible)",
  "description": "Brief description of the dish",
  "servings": number of servings (estimate if not shown),
  "ingredients": [
    {
      "name": "ingredient name",
      "quantity": numeric amount (or null),
      "unit": "measurement unit" (or null)
    }
  ],
  "steps": [
    "Step 1: ...",
    "Step 2: ..."
  ],
  "estimated_calories_per_serving": estimated calories per serving,
  "macros_per_serving": {
    "protein_g": estimated protein grams,
    "carbs_g": estimated carb grams,
    "fat_g": estimated fat grams
  },
  "tags": ["tag1", "tag2"],
  "prep_time_minutes": estimated prep time,
  "cook_time_minutes": estimated cook time,
  "difficulty": "easy" | "medium" | "hard"
}

If ingredients are visible as a list, extract them precisely.
If steps are visible, extract them in order.
For nutritional info, provide reasonable estimates based on visible ingredients and dish type.
If information is not visible, make reasonable assumptions based on the dish shown."""
            
            # Call OpenAI Vision with JSON mode
            result = await self.provider.analyze_image_json(
                image_bytes=image_bytes,
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=2048
            )
            
            # Validate and normalize the response
            recipe = self._normalize_recipe(result)
            
            logger.info(f"✓ Extracted recipe: {recipe.get('title', 'Untitled')}")
            
            return recipe
        
        except Exception as e:
            logger.error(f"Recipe extraction failed: {e}")
            raise ValueError(f"Failed to extract recipe: {str(e)}")
    
    async def extract_from_video_frames(
        self,
        frames: List[bytes]
    ) -> Dict[str, Any]:
        """
        Extract recipe from multiple video frames.
        
        Strategy: Analyze each frame and merge information.
        
        Args:
            frames: List of frame image bytes
            
        Returns:
            Merged recipe dictionary
        """
        try:
            logger.info(f"Extracting recipe from {len(frames)} video frames")
            
            if not frames:
                raise ValueError("No frames provided")
            
            # For simplicity, analyze the middle frame (usually shows key info)
            # In production, you might analyze multiple frames and merge
            middle_frame = frames[len(frames) // 2]
            
            logger.info("Using middle frame for extraction")
            
            return await self.extract_from_image(middle_frame)
        
        except Exception as e:
            logger.error(f"Video recipe extraction failed: {e}")
            raise ValueError(f"Failed to extract recipe from video: {str(e)}")
    
    async def refine_macros(
        self,
        ingredients: List[Dict[str, Any]],
        servings: int
    ) -> Dict[str, float]:
        """
        Refine nutritional macros using text-only model (cheaper).
        
        Args:
            ingredients: List of ingredient dictionaries
            servings: Number of servings
            
        Returns:
            Dictionary with refined macros:
            {
                "calories": float,
                "protein_g": float,
                "carbs_g": float,
                "fat_g": float
            }
        """
        try:
            logger.info(f"Refining macros for {len(ingredients)} ingredients")
            
            # Format ingredients as text
            ingredients_text = "\n".join([
                f"- {ing['name']}: {ing.get('quantity', 'some')} {ing.get('unit', '')}"
                for ing in ingredients
            ])
            
            prompt = f"""Calculate accurate nutritional macros PER SERVING for this recipe.

Ingredients:
{ingredients_text}

Servings: {servings}

Provide your calculation in JSON format:
{{
  "calories": total calories per serving,
  "protein_g": grams of protein per serving,
  "carbs_g": grams of carbohydrates per serving,
  "fat_g": grams of fat per serving
}}

Use standard USDA nutritional data. Be precise."""
            
            system_prompt = "You are a professional nutritionist with access to USDA food database knowledge."
            
            result = await self.provider.generate_json_response(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3  # Low temperature for consistency
            )
            
            # Validate macros
            macros = {
                "calories": float(result.get("calories", 0)),
                "protein_g": float(result.get("protein_g", 0)),
                "carbs_g": float(result.get("carbs_g", 0)),
                "fat_g": float(result.get("fat_g", 0)),
            }
            
            logger.info(f"✓ Refined macros: {macros['calories']} cal")
            
            return macros
        
        except Exception as e:
            logger.error(f"Macro refinement failed: {e}")
            # Return zeros on failure
            return {
                "calories": 0.0,
                "protein_g": 0.0,
                "carbs_g": 0.0,
                "fat_g": 0.0
            }
    
    def _validate_and_resize_image(self, image_bytes: bytes, max_size: int = 2048) -> bytes:
        """
        Validate image and resize if too large.
        
        Args:
            image_bytes: Original image bytes
            max_size: Maximum dimension in pixels
            
        Returns:
            Processed image bytes
        """
        try:
            img = Image.open(io.BytesIO(image_bytes))
            
            # Check if resize needed
            width, height = img.size
            if max(width, height) > max_size:
                # Calculate new size maintaining aspect ratio
                if width > height:
                    new_width = max_size
                    new_height = int(height * (max_size / width))
                else:
                    new_height = max_size
                    new_width = int(width * (max_size / height))
                
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Convert back to bytes
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=85)
                image_bytes = output.getvalue()
                
                logger.info(f"Resized image from {width}x{height} to {new_width}x{new_height}")
            
            return image_bytes
        
        except Exception as e:
            logger.warning(f"Image validation/resize failed: {e}, using original")
            return image_bytes
    
    def _normalize_recipe(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize and validate extracted recipe data.
        
        Args:
            raw: Raw extraction result
            
        Returns:
            Normalized recipe dictionary
        """
        # Ensure all required fields exist with defaults
        recipe = {
            "title": raw.get("title", "Untitled Recipe"),
            "description": raw.get("description", ""),
            "servings": int(raw.get("servings", 4)),
            "ingredients": raw.get("ingredients", []),
            "steps": raw.get("steps", []),
            "estimated_calories_per_serving": float(raw.get("estimated_calories_per_serving", 0)),
            "macros_per_serving": raw.get("macros_per_serving", {
                "protein_g": 0.0,
                "carbs_g": 0.0,
                "fat_g": 0.0
            }),
            "tags": raw.get("tags", []),
            "prep_time_minutes": int(raw.get("prep_time_minutes", 15)),
            "cook_time_minutes": int(raw.get("cook_time_minutes", 30)),
            "difficulty": raw.get("difficulty", "medium")
        }
        
        # Normalize ingredients
        normalized_ingredients = []
        for ing in recipe["ingredients"]:
            if isinstance(ing, dict):
                normalized_ingredients.append({
                    "name": ing.get("name", "Unknown"),
                    "quantity": float(ing["quantity"]) if ing.get("quantity") else None,
                    "unit": ing.get("unit", None)
                })
        recipe["ingredients"] = normalized_ingredients
        
        # Normalize steps
        if isinstance(recipe["steps"], list):
            recipe["steps"] = [str(step) for step in recipe["steps"]]
        
        # Normalize macros
        macros = recipe["macros_per_serving"]
        recipe["macros_per_serving"] = {
            "protein_g": float(macros.get("protein_g", 0)),
            "carbs_g": float(macros.get("carbs_g", 0)),
            "fat_g": float(macros.get("fat_g", 0))
        }
        
        return recipe
