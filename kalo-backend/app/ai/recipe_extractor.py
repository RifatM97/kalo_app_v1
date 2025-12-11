"""
AI Recipe Extraction Pipeline
Handles: Video download → Transcription → OCR → Ingredient detection → Recipe structuring
"""
import asyncio
import json
import os
import subprocess
import tempfile
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)

class VideoDownloader:
    """Download video from TikTok, Instagram, YouTube"""
    
    @staticmethod
    async def download(video_url: str, output_path: str) -> Optional[str]:
        """
        Download video from various sources
        Uses yt-dlp library (pip install yt-dlp)
        """
        try:
            import yt_dlp
            
            logger.info(f"Downloading video from: {video_url}")
            
            ydl_opts = {
                'format': 'best',
                'outtmpl': output_path,
                'quiet': False,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
            
            # Find the downloaded file (check common extensions)
            video_file = None
            for ext in ['mp4', 'mkv', 'webm', 'mov', 'avi', 'flv']:
                candidate = f"{output_path}.{ext}"
                if os.path.exists(candidate):
                    video_file = candidate
                    logger.info(f"Found video file: {video_file}")
                    break
            
            if not video_file and os.path.exists(output_path):
                video_file = output_path
            
            if video_file:
                file_size = os.path.getsize(video_file)
                logger.info(f"✓ Video download successful: {file_size} bytes")
                return video_file
            else:
                logger.error(f"Video file not created after download")
                return None
                
        except Exception as e:
            logger.error(f"Video download failed: {e}")
            return None

class AudioExtractor:
    """Extract audio from video using ffmpeg"""
    
    @staticmethod
    async def extract(video_path: str, output_path: str) -> Optional[str]:
        """Extract audio from video"""
        try:
            import subprocess
            
            logger.info(f"Extracting audio from: {video_path}")
            
            # Check if ffmpeg is available
            try:
                subprocess.run(['which', 'ffmpeg'], capture_output=True, check=True)
            except:
                logger.warning("ffmpeg not found. Audio extraction will be skipped.")
                return None
            
            wav_file = f"{output_path}.wav"
            
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vn',
                '-acodec', 'pcm_s16le',
                '-ar', '16000',
                '-ac', '1',
                '-y',
                wav_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(wav_file):
                file_size = os.path.getsize(wav_file)
                logger.info(f"✓ Audio extraction successful: {file_size} bytes")
                return wav_file
            else:
                logger.error(f"Audio extraction failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Audio extraction error: {e}")
            return None

class FrameExtractor:
    """Extract frames from video"""
    
    @staticmethod
    async def extract(video_path: str, output_dir: str, interval: int = 30) -> List[str]:
        """Extract frames at regular intervals"""
        try:
            import cv2
            
            logger.info(f"Extracting frames from: {video_path}")
            
            os.makedirs(output_dir, exist_ok=True)
            
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logger.error(f"Cannot open video: {video_path}")
                return []
            
            frame_count = 0
            saved_frames = []
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % interval == 0:
                    frame_path = os.path.join(output_dir, f"frame_{frame_count:06d}.jpg")
                    cv2.imwrite(frame_path, frame)
                    saved_frames.append(frame_path)
                
                frame_count += 1
            
            cap.release()
            
            logger.info(f"✓ Extracted {len(saved_frames)} frames from {frame_count} total")
            return saved_frames
            
        except ImportError as e:
            logger.error(f"cv2 import error: {e}")
            return []
        except Exception as e:
            logger.error(f"Frame extraction error: {e}")
            return []

class AudioTranscriber:
    """Transcribe audio from video using OpenAI Whisper"""
    
    @staticmethod
    async def transcribe(audio_path: str, model: str = "base") -> Optional[str]:
        """
        Transcribe audio to text
        Uses OpenAI Whisper (pip install openai-whisper)
        """
        try:
            import whisper
            
            if not os.path.exists(audio_path):
                logger.error(f"Audio file not found: {audio_path}")
                return None
            
            logger.info(f"Loading Whisper model: {model}")
            model_obj = whisper.load_model(model)
            
            logger.info(f"Transcribing audio...")
            result = model_obj.transcribe(audio_path, language="en")
            
            transcript = result.get("text", "")
            logger.info(f"✓ Transcription complete: {len(transcript)} characters")
            
            return transcript if transcript.strip() else None
            
        except ImportError as e:
            logger.error(f"Whisper import error: {e}")
            return None
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return None

class OCRProcessor:
    """Extract text from video frames using PaddleOCR"""
    
    @staticmethod
    async def extract_text(frames: List[str]) -> str:
        """
        Extract text from frames
        Uses PaddleOCR (pip install paddleocr)
        """
        try:
            from paddleocr import PaddleOCR
            
            logger.info(f"Initializing OCR for {len(frames)} frames")
            ocr = PaddleOCR(use_textline_orientation=True, lang='en')
            
            extracted_text = []
            
            # Process every Nth frame to reduce computation
            for i, frame_path in enumerate(frames[::max(1, len(frames)//10)]):  # Process ~10 frames
                try:
                    result = ocr.ocr(frame_path, cls=True)
                    
                    if result:
                        for line in result:
                            if line:
                                for word_info in line:
                                    text = word_info[1][0]
                                    confidence = word_info[1][1]
                                    if confidence > 0.3:  # Filter low confidence
                                        extracted_text.append(text)
                except Exception as e:
                    logger.debug(f"OCR error for frame {i}: {e}")
                    continue
            
            ocr_text = " ".join(extracted_text)
            logger.info(f"✓ OCR extraction complete: {len(ocr_text)} characters")
            
            return ocr_text
            
        except ImportError as e:
            logger.error(f"PaddleOCR import error: {e}")
            logger.warning("Install paddle: pip install paddleocr paddlepaddle")
            return ""
        except Exception as e:
            logger.error(f"OCR extraction error: {e}")
            return ""

class FoodDetector:
    """Detect ingredients from video frames using YOLOv8"""
    
class FoodDetector:
    """Detect ingredients from video frames using YOLOv8"""
    
    @staticmethod
    async def detect_ingredients(frames: List[str]) -> List[str]:
        """
        Detect food items in frames
        Uses YOLOv8 (pip install ultralytics)
        """
        try:
            from ultralytics import YOLO
            
            logger.info(f"Loading YOLOv8 model...")
            model = YOLO("yolov8n.pt")
            
            detected_items = set()
            
            # Process frames for object detection
            for i, frame_path in enumerate(frames[::max(1, len(frames)//5)]):  # ~5 frames
                try:
                    results = model(frame_path, verbose=False, conf=0.3)
                    
                    for r in results:
                        if r.boxes is not None:
                            for idx, c in enumerate(r.boxes.cls):
                                class_name = model.names[int(c)]
                                # Include food-related and common cooking items
                                detected_items.add(class_name)
                
                except Exception as e:
                    logger.debug(f"YOLO error for frame {i}: {e}")
                    continue
            
            detections_list = sorted(list(detected_items))
            logger.info(f"✓ YOLO detection complete: {len(detections_list)} objects")
            
            return detections_list
            
        except ImportError as e:
            logger.error(f"YOLO import error: {e}")
            return []
        except Exception as e:
            logger.error(f"Ingredient detection error: {e}")
            return []

class RecipeStructurer:
    """Use OpenAI Vision to structure recipe from video frames"""
    
    RECIPE_EXTRACTION_PROMPT = """
You are a professional chef and nutrition expert analyzing cooking video frames.

You are seeing {num_frames} frames from a cooking video showing the recipe preparation process.

Additional context from the video:
- Audio transcription: {transcript}
- Text visible in frames (OCR): {ocr_text}

Please analyze these frames carefully and create a structured JSON recipe. 

CRITICAL: If the frames do NOT show cooking or food preparation (e.g., just random objects, intro screens, or unrelated content), return a JSON with empty/null fields and set "title": "Unable to extract recipe - no cooking content detected".

Otherwise, extract the recipe information in this EXACT JSON structure:
{{
    "title": "Specific dish name (be precise)",
    "description": "Brief description of the dish",
    "ingredients": [
        {{"name": "ingredient", "quantity": 1.0, "unit": "cup"}}
    ],
    "steps": [
        {{"step": 1, "instruction": "First instruction"}},
        {{"step": 2, "instruction": "Second instruction"}}
    ],
    "cook_time_minutes": 30,
    "prep_time_minutes": 15,
    "servings": 4,
    "difficulty": "easy",
    "macros": {{
        "calories": 300,
        "protein": 20,
        "carbs": 40,
        "fat": 10
    }}
}}

RULES:
1. Return ONLY valid JSON - no markdown, no code blocks
2. All numbers must be actual numbers, not strings
3. Identify the specific dish shown (e.g., "Grilled Chicken Caesar Salad" not just "Salad")
4. Extract visible ingredients and estimate quantities if not shown
5. Describe actual cooking steps you can see in the frames
6. Provide realistic nutritional estimates based on visible ingredients
7. DO NOT hallucinate - if you can't see cooking, say so
"""
    
    @staticmethod
    async def structure_recipe(
        transcript: str,
        ocr_text: str,
        detected_ingredients: List[str],
        frame_paths: List[str] = None
    ) -> Optional[Dict]:
        """
        Use OpenAI Vision to structure recipe from video frames
        
        This is the FIXED version that actually sends frames as images to GPT-4o Vision
        """
        try:
            import base64
            from openai import OpenAI
            from app.config import settings
            
            api_key = settings.OPENAI_API_KEY
            if not api_key:
                logger.error("OPENAI_API_KEY not set in environment")
                return None
            
            client = OpenAI(api_key=api_key)
            
            # Select frames to analyze (max 8 to control costs)
            selected_frames = []
            if frame_paths:
                # Select evenly distributed frames
                total_frames = len(frame_paths)
                if total_frames <= 8:
                    selected_frames = frame_paths
                else:
                    # Select 8 frames evenly distributed across the video
                    indices = [int(i * total_frames / 8) for i in range(8)]
                    selected_frames = [frame_paths[i] for i in indices]
                
                logger.info(f"Selected {len(selected_frames)} frames from {total_frames} total")
            
            # Build the message content with frames
            content = []
            
            # Add text prompt
            prompt_text = RecipeStructurer.RECIPE_EXTRACTION_PROMPT.format(
                num_frames=len(selected_frames) if selected_frames else 0,
                transcript=transcript[:800] if transcript else "[No audio transcription available]",
                ocr_text=ocr_text[:400] if ocr_text else "[No visible text detected]"
            )
            content.append({"type": "text", "text": prompt_text})
            
            # Add frame images
            for frame_path in selected_frames:
                try:
                    with open(frame_path, "rb") as f:
                        frame_bytes = f.read()
                    frame_b64 = base64.b64encode(frame_bytes).decode('utf-8')
                    content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{frame_b64}",
                            "detail": "low"  # Use "low" to save tokens/cost
                        }
                    })
                except Exception as e:
                    logger.warning(f"Failed to load frame {frame_path}: {e}")
            
            if not content or len(content) == 1:  # Only text, no images
                logger.warning("No frames available, falling back to text-only analysis")
                # If no frames, fall back to text-only (original behavior)
                return await RecipeStructurer._structure_recipe_text_only(
                    transcript, ocr_text, detected_ingredients
                )
            
            logger.info(f"Calling OpenAI Vision API (gpt-4o) with {len(content)-1} frames...")
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert chef analyzing cooking videos. Extract recipes accurately from visual frames. Return only valid JSON."
                    },
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                temperature=0.2,  # Low temperature for less hallucination
                max_tokens=2000,
            )
            
            recipe_json_str = response.choices[0].message.content
            logger.debug(f"Vision API response (first 200 chars): {recipe_json_str[:200]}")
            
            # Clean up markdown if present
            if recipe_json_str.startswith("```"):
                lines = recipe_json_str.split("\n")
                recipe_json_str = "\n".join(lines[1:-1])  # Remove first and last line
                if recipe_json_str.startswith("json"):
                    recipe_json_str = recipe_json_str[4:]
            recipe_json_str = recipe_json_str.strip()
            
            recipe_json = json.loads(recipe_json_str)
            logger.info(f"✓ Recipe structured: {recipe_json.get('title', 'Unknown')}")
            
            # Check if the model detected no cooking content
            title = recipe_json.get('title', '')
            if 'unable to extract' in title.lower() or 'no cooking' in title.lower():
                logger.warning(f"Model could not extract recipe from frames: {title}")
                return None
            
            return recipe_json
            
        except ImportError as e:
            logger.error(f"OpenAI import error: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.error(f"Response was: {recipe_json_str[:500]}")
            return None
        except Exception as e:
            logger.error(f"Recipe structuring failed: {e}")
            return None
    
    @staticmethod
    async def _structure_recipe_text_only(
        transcript: str,
        ocr_text: str,
        detected_ingredients: List[str]
    ) -> Optional[Dict]:
        """
        Fallback: Use text-only model when frames are not available
        """
        try:
            from openai import OpenAI
            from app.config import settings
            
            api_key = settings.OPENAI_API_KEY
            if not api_key:
                return None
            
            client = OpenAI(api_key=api_key)
            
            prompt = f"""Extract recipe information from this video analysis:

Transcription: {transcript[:800] if transcript else 'None'}
OCR Text: {ocr_text[:400] if ocr_text else 'None'}
Detected Objects: {', '.join(detected_ingredients) if detected_ingredients else 'None'}

Return a JSON recipe following this structure:
{{
    "title": "Recipe name",
    "description": "Brief description",
    "ingredients": [{{"name": "ingredient", "quantity": 1, "unit": "cup"}}],
    "steps": [{{"step": 1, "instruction": "instruction"}}],
    "cook_time_minutes": 30,
    "prep_time_minutes": 15,
    "servings": 4,
    "difficulty": "easy",
    "macros": {{"calories": 300, "protein": 20, "carbs": 40, "fat": 10}}
}}

Return ONLY valid JSON."""
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Cheaper text-only model
                messages=[
                    {"role": "system", "content": "Extract recipes from text. Return only JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500,
            )
            
            recipe_json_str = response.choices[0].message.content.strip()
            if recipe_json_str.startswith("```"):
                lines = recipe_json_str.split("\n")
                recipe_json_str = "\n".join(lines[1:-1])
            
            return json.loads(recipe_json_str)
            
        except Exception as e:
            logger.error(f"Text-only structuring failed: {e}")
            return None

class RecipeExtractionPipeline:
    """Orchestrate the entire video-to-recipe extraction process"""
    
    @staticmethod
    async def extract_recipe_from_video(video_url: str, output_dir: str = "/tmp") -> Dict:
        """
        End-to-end pipeline:
        1. Download video
        2. Extract frames
        3. Transcribe audio (if available)
        4. Extract text (OCR)
        5. Detect ingredients (YOLO)
        6. Structure recipe with LLM
        """
        logger.info(f"Starting recipe extraction for: {video_url}")
        
        try:
            temp_dir = tempfile.mkdtemp()
            logger.info(f"Using temp directory: {temp_dir}")
            
            # Step 1: Download
            logger.info("Step 1: Downloading video...")
            video_path = await VideoDownloader.download(video_url, os.path.join(temp_dir, "video"))
            
            if not video_path:
                return {
                    "status": "failed",
                    "error": "Failed to download video",
                }
            
            # Step 2: Extract frames
            logger.info("Step 2: Extracting frames...")
            frames = await FrameExtractor.extract(video_path, os.path.join(temp_dir, "frames"))
            
            if not frames:
                return {
                    "status": "failed",
                    "error": "Failed to extract frames",
                }
            
            # Step 3: Extract audio and transcribe
            transcript = ""
            audio_path = await AudioExtractor.extract(video_path, os.path.join(temp_dir, "audio"))
            if audio_path:
                logger.info("Step 3: Transcribing audio...")
                transcript = await AudioTranscriber.transcribe(audio_path) or ""
                logger.info(f"Transcript length: {len(transcript)} characters")
            else:
                logger.warning("Audio extraction failed, skipping transcription")
            
            # Step 4: OCR
            logger.info("Step 4: Extracting text (OCR)...")
            ocr_text = await OCRProcessor.extract_text(frames)
            logger.info(f"OCR text length: {len(ocr_text)} characters")
            
            # Step 5: Detect ingredients
            logger.info("Step 5: Detecting ingredients...")
            detected_ingredients = await FoodDetector.detect_ingredients(frames)
            logger.info(f"Detected items: {detected_ingredients}")
            
            # Step 6: Structure recipe with Vision (frames + context)
            logger.info("Step 6: Structuring recipe with AI Vision...")
            recipe = await RecipeStructurer.structure_recipe(
                transcript=transcript,
                ocr_text=ocr_text,
                detected_ingredients=detected_ingredients,
                frame_paths=frames  # NOW PASSING ACTUAL FRAMES!
            )
            
            if not recipe:
                logger.warning("Recipe structuring returned None, using fallback")
                recipe = RecipeExtractionPipeline._create_fallback_recipe(
                    transcript, ocr_text, detected_ingredients
                )
            
            logger.info("✓ Recipe extraction complete!")
            return {
                "status": "success",
                "recipe": recipe,
                "transcript": transcript,
                "ocr_text": ocr_text,
                "detected_ingredients": detected_ingredients,
            }
        
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
            }
    
    @staticmethod
    def _create_fallback_recipe(transcript: str, ocr_text: str, detected_ingredients: List[str]) -> Dict:
        """Create a fallback recipe when LLM fails"""
        logger.info("Creating fallback recipe")
        
        title = "Recipe from Video"
        if detected_ingredients:
            title = f"Recipe with {', '.join(detected_ingredients[:2])}"
        
        return {
            "title": title,
            "description": "Recipe extracted from video content",
            "ingredients": [
                {"name": ingredient, "quantity": 1, "unit": ""}
                for ingredient in detected_ingredients[:5]
            ] or [{"name": "Ingredients from video", "quantity": 1, "unit": ""}],
            "steps": [
                {"step": 1, "instruction": "Prepare all ingredients"},
                {"step": 2, "instruction": "Follow the cooking method shown in the video"},
                {"step": 3, "instruction": "Serve and enjoy"}
            ],
            "cook_time_minutes": 30,
            "prep_time_minutes": 15,
            "servings": 4,
            "difficulty": "medium",
            "macros": {
                "calories": 350,
                "protein": 15,
                "carbs": 45,
                "fat": 12
            }
        }

