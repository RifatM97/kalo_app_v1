#!/usr/bin/env python3
"""
COMPREHENSIVE DEBUG SCRIPT FOR AI RECIPE EXTRACTION PIPELINE
Tests each module independently and prints raw outputs
"""

import os
import sys
import asyncio
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict
import tempfile

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create temp directory for outputs
TEMP_DIR = tempfile.mkdtemp()
print(f"\n{'='*80}")
print(f"DEBUG OUTPUT DIRECTORY: {TEMP_DIR}")
print(f"{'='*80}\n")

# ============================================================================
# PHASE 1: VIDEO DOWNLOADER
# ============================================================================
class VideoDownloaderDebug:
    """Download video from TikTok, Instagram, YouTube"""
    
    @staticmethod
    async def download(video_url: str, output_path: str) -> Optional[str]:
        """Download video from various sources"""
        print(f"\n{'='*80}")
        print("PHASE 1: VIDEO DOWNLOADER")
        print(f"{'='*80}")
        print(f"URL: {video_url}")
        print(f"Output: {output_path}")
        
        try:
            import yt_dlp
            print("✓ yt_dlp imported successfully")
            
            ydl_opts = {
                'format': 'best',
                'outtmpl': output_path,
                'quiet': False,
                'no_warnings': False,
            }
            
            print(f"Starting download...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
            
            # Find the downloaded file (check common extensions)
            video_file = None
            for ext in ['mp4', 'mkv', 'webm', 'mov', 'avi']:
                candidate = f"{output_path}.{ext}"
                if os.path.exists(candidate):
                    video_file = candidate
                    break
            
            # If not found with extension, check if file exists as-is
            if not video_file and os.path.exists(output_path):
                video_file = output_path
            
            if video_file:
                file_size = os.path.getsize(video_file)
                print(f"\n✓ Download successful!")
                print(f"  Final file path: {video_file}")
                print(f"  File size: {file_size} bytes ({file_size / (1024*1024):.2f} MB)")
                return video_file
            else:
                # List files in directory for debugging
                try:
                    dir_path = os.path.dirname(output_path)
                    if os.path.exists(dir_path):
                        files = os.listdir(dir_path)
                        print(f"\n✗ Expected video file not found")
                        print(f"  Files in directory: {files}")
                except:
                    pass
                return None
                
        except ImportError as e:
            print(f"\n✗ Import error: {e}")
            print("  Fix: pip install yt-dlp")
            return None
        except Exception as e:
            print(f"\n✗ Download error: {e}")
            return None

# ============================================================================
# PHASE 2: AUDIO EXTRACTOR
# ============================================================================
class AudioExtractorDebug:
    """Extract audio from video using ffmpeg"""
    
    @staticmethod
    async def extract(video_path: str, output_path: str) -> Optional[str]:
        """Extract audio from video"""
        print(f"\n{'='*80}")
        print("PHASE 2: AUDIO EXTRACTOR")
        print(f"{'='*80}")
        print(f"Video path: {video_path}")
        print(f"Output: {output_path}")
        
        try:
            import subprocess
            
            # Check if ffmpeg is installed
            result = subprocess.run(['which', 'ffmpeg'], capture_output=True, text=True)
            if result.returncode != 0:
                print("\n✗ ffmpeg not found in PATH")
                print("  Fix: brew install ffmpeg (macOS)")
                return None
            
            ffmpeg_path = result.stdout.strip()
            print(f"✓ ffmpeg found: {ffmpeg_path}")
            
            wav_file = f"{output_path}.wav"
            
            print(f"Extracting audio...")
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
                print(f"\n✓ Audio extraction successful!")
                print(f"  WAV path: {wav_file}")
                print(f"  File size: {file_size} bytes ({file_size / (1024*1024):.2f} MB)")
                return wav_file
            else:
                print(f"\n✗ Audio extraction failed")
                print(f"  stderr: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"\n✗ Audio extraction error: {e}")
            return None

# ============================================================================
# PHASE 3: FRAME EXTRACTOR
# ============================================================================
class FrameExtractorDebug:
    """Extract frames from video"""
    
    @staticmethod
    async def extract(video_path: str, output_dir: str, interval: int = 30) -> List[str]:
        """Extract frames at regular intervals"""
        print(f"\n{'='*80}")
        print("PHASE 3: FRAME EXTRACTOR")
        print(f"{'='*80}")
        print(f"Video path: {video_path}")
        print(f"Output directory: {output_dir}")
        print(f"Frame interval: every {interval} frames")
        
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            import cv2
            print("✓ cv2 imported successfully")
            
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print(f"\n✗ Cannot open video: {video_path}")
                return []
            
            frame_count = 0
            saved_frames = []
            
            print("Extracting frames...")
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
            
            print(f"\n✓ Frame extraction successful!")
            print(f"  Total frames in video: {frame_count}")
            print(f"  Saved frames: {len(saved_frames)}")
            
            if saved_frames:
                print(f"\n  Frame paths:")
                for i, frame_path in enumerate(saved_frames[:5]):  # Show first 5
                    exists = os.path.exists(frame_path)
                    size = os.path.getsize(frame_path) if exists else 0
                    print(f"    [{i+1}] {frame_path} (exists: {exists}, size: {size} bytes)")
                
                if len(saved_frames) > 5:
                    print(f"    ... and {len(saved_frames) - 5} more frames")
            
            return saved_frames
            
        except ImportError as e:
            print(f"\n✗ Import error: {e}")
            print("  Fix: pip install opencv-python")
            return []
        except Exception as e:
            print(f"\n✗ Frame extraction error: {e}")
            return []

# ============================================================================
# PHASE 4: WHISPER TRANSCRIBER
# ============================================================================
class WhisperTranscriberDebug:
    """Transcribe audio using OpenAI Whisper"""
    
    @staticmethod
    async def transcribe(audio_path: str, model: str = "base") -> Optional[str]:
        """Transcribe audio to text"""
        print(f"\n{'='*80}")
        print("PHASE 4: WHISPER TRANSCRIBER")
        print(f"{'='*80}")
        print(f"Audio path: {audio_path}")
        print(f"Model: {model}")
        
        try:
            import whisper
            print("✓ whisper imported successfully")
            
            print(f"Loading Whisper model '{model}'...")
            model_obj = whisper.load_model(model)
            print(f"✓ Model loaded successfully")
            
            print(f"Transcribing audio...")
            result = model_obj.transcribe(audio_path, language="en")
            
            transcript = result.get("text", "")
            
            print(f"\n✓ Transcription successful!")
            print(f"  Transcript length: {len(transcript)} characters")
            print(f"  First 300 characters:")
            print(f"  {transcript[:300]}")
            
            if len(transcript) < 50:
                print(f"\n  ⚠ WARNING: Transcript is very short!")
            
            return transcript
            
        except ImportError as e:
            print(f"\n✗ Import error: {e}")
            print("  Fix: pip install openai-whisper")
            return None
        except Exception as e:
            print(f"\n✗ Transcription error: {e}")
            return None

# ============================================================================
# PHASE 5: OCR EXTRACTOR
# ============================================================================
class OCRExtractorDebug:
    """Extract text from frames using PaddleOCR"""
    
    @staticmethod
    async def extract(frames: List[str]) -> str:
        """Extract text from frames"""
        print(f"\n{'='*80}")
        print("PHASE 5: OCR EXTRACTOR")
        print(f"{'='*80}")
        print(f"Processing {len(frames)} frames")
        
        try:
            from paddleocr import PaddleOCR
            print("✓ PaddleOCR imported successfully")
            
            print("Initializing OCR...")
            ocr = PaddleOCR(use_textline_orientation=True, lang='en')
            print("✓ OCR initialized")
            
            all_text = []
            frame_texts = {}
            
            for i, frame_path in enumerate(frames[:5]):  # Process first 5 frames
                print(f"\nProcessing frame {i+1}/{min(5, len(frames))}: {os.path.basename(frame_path)}")
                
                try:
                    result = ocr.ocr(frame_path)
                    frame_text = []
                    
                    if result:
                        for line in result:
                            if line:
                                for word_info in line:
                                    text = word_info[1][0]
                                    confidence = word_info[1][1]
                                    frame_text.append(text)
                                    all_text.append(text)
                    
                    frame_texts[frame_path] = " ".join(frame_text)
                    print(f"  Text found: {len(frame_text)} words")
                    if frame_text:
                        print(f"  Sample: {' '.join(frame_text[:10])}")
                
                except Exception as e:
                    print(f"  Error processing frame: {e}")
                    frame_texts[frame_path] = ""
            
            ocr_text = " ".join(all_text)
            
            print(f"\n✓ OCR extraction successful!")
            print(f"  Total text extracted: {len(ocr_text)} characters")
            print(f"  Total words: {len(all_text)}")
            
            if ocr_text.strip():
                print(f"\n  Extracted text samples:")
                for frame_path, text in list(frame_texts.items())[:3]:
                    if text:
                        print(f"    {os.path.basename(frame_path)}: {text[:100]}")
            else:
                print(f"\n  ⚠ WARNING: No OCR text extracted!")
            
            return ocr_text
            
        except ImportError as e:
            print(f"\n✗ Import error: {e}")
            print("  Fix: pip install paddleocr")
            return ""
        except Exception as e:
            print(f"\n✗ OCR extraction error: {e}")
            return ""

# ============================================================================
# PHASE 6: YOLO VISION DETECTOR
# ============================================================================
class YOLODetectorDebug:
    """Detect ingredients using YOLOv8"""
    
    @staticmethod
    async def detect(frames: List[str]) -> List[str]:
        """Detect objects in frames"""
        print(f"\n{'='*80}")
        print("PHASE 6: YOLO VISION DETECTOR")
        print(f"{'='*80}")
        print(f"Processing {len(frames)} frames")
        
        try:
            from ultralytics import YOLO
            print("✓ YOLO imported successfully")
            
            print("Loading YOLOv8 model...")
            model = YOLO("yolov8n.pt")
            print("✓ YOLOv8 model loaded")
            
            all_detections = set()
            
            for i, frame_path in enumerate(frames[:5]):
                print(f"\nDetecting in frame {i+1}/{min(5, len(frames))}: {os.path.basename(frame_path)}")
                
                try:
                    results = model(frame_path, verbose=False)
                    frame_detections = []
                    
                    for r in results:
                        if r.boxes is not None:
                            for idx, c in enumerate(r.boxes.cls):
                                class_name = model.names[int(c)]
                                confidence = r.boxes.conf[idx].item()
                                frame_detections.append((class_name, confidence))
                                all_detections.add(class_name)
                    
                    print(f"  Detections: {len(frame_detections)} objects")
                    if frame_detections:
                        for class_name, conf in frame_detections[:5]:
                            print(f"    - {class_name} (confidence: {conf:.2%})")
                
                except Exception as e:
                    print(f"  Error detecting in frame: {e}")
            
            detections_list = sorted(list(all_detections))
            
            print(f"\n✓ YOLO detection successful!")
            print(f"  Total unique objects detected: {len(detections_list)}")
            print(f"\n  All detections:")
            for obj in detections_list:
                print(f"    - {obj}")
            
            if not detections_list:
                print(f"\n  ⚠ WARNING: No objects detected!")
            
            return detections_list
            
        except ImportError as e:
            print(f"\n✗ Import error: {e}")
            print("  Fix: pip install ultralytics")
            return []
        except Exception as e:
            print(f"\n✗ YOLO detection error: {e}")
            return []

# ============================================================================
# PHASE 7: LLM STRUCTURER
# ============================================================================
class LLMStructurerDebug:
    """Structure data using LLM"""
    
    RECIPE_EXTRACTION_PROMPT = """
You are a professional chef and nutrition expert. Your task is to extract and structure recipe information from video content analysis.

Based on the following information extracted from a video:

TRANSCRIPTION (from video audio):
{transcript}

OCR TEXT (text visible in video frames):
{ocr_text}

DETECTED OBJECTS (from computer vision):
{detected_ingredients}

Please analyze this information and structure it into a valid JSON recipe. Return ONLY valid JSON, no markdown, no code blocks.

The JSON must follow this EXACT structure:
{{
    "title": "Recipe title",
    "description": "Brief description of the recipe",
    "ingredients": [
        {{"name": "ingredient name", "quantity": 1, "unit": "cup"}}
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

CRITICAL RULES:
1. Return ONLY valid JSON - no extra text
2. If certain fields cannot be determined from the video, use reasonable estimates
3. Make sure all numbers are actual numbers, not strings
4. The response must be parseable as JSON
"""
    
    @staticmethod
    async def structure(
        transcript: str,
        ocr_text: str,
        detected_ingredients: List[str]
    ) -> Optional[Dict]:
        """Structure data into recipe JSON"""
        print(f"\n{'='*80}")
        print("PHASE 7: LLM STRUCTURER")
        print(f"{'='*80}")
        
        print(f"Input data:")
        print(f"  - Transcript length: {len(transcript)} characters")
        print(f"  - OCR text length: {len(ocr_text)} characters")
        print(f"  - Detected objects: {len(detected_ingredients)}")
        
        try:
            import openai
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print(f"\n✗ OPENAI_API_KEY not set in environment")
                print("  Fix: export OPENAI_API_KEY=your-key")
                return None
            
            openai.api_key = api_key
            print("✓ OpenAI API key configured")
            
            prompt = LLMStructurerDebug.RECIPE_EXTRACTION_PROMPT.format(
                transcript=transcript[:1000] if transcript else "[No transcription]",
                ocr_text=ocr_text[:1000] if ocr_text else "[No OCR text]",
                detected_ingredients=", ".join(detected_ingredients) if detected_ingredients else "[No objects detected]"
            )
            
            print(f"\n{'='*60}")
            print("COMBINED PROMPT BEING SENT TO LLM:")
            print(f"{'='*60}")
            print(prompt)
            print(f"{'='*60}\n")
            
            print("Calling OpenAI API (gpt-3.5-turbo)...")
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional chef who extracts recipes from videos. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000,
            )
            
            recipe_json_str = response.choices[0].message.content
            
            print(f"\n{'='*60}")
            print("RAW RESPONSE FROM LLM:")
            print(f"{'='*60}")
            print(recipe_json_str)
            print(f"{'='*60}\n")
            
            # Parse JSON
            recipe_json = json.loads(recipe_json_str)
            
            print(f"✓ LLM structuring successful!")
            print(f"  Recipe title: {recipe_json.get('title', 'N/A')}")
            print(f"  Ingredients: {len(recipe_json.get('ingredients', []))} items")
            print(f"  Steps: {len(recipe_json.get('steps', []))} steps")
            print(f"  Calories: {recipe_json.get('macros', {}).get('calories', 'N/A')}")
            
            print(f"\nFinal JSON:")
            print(json.dumps(recipe_json, indent=2))
            
            return recipe_json
            
        except ImportError as e:
            print(f"\n✗ Import error: {e}")
            print("  Fix: pip install openai")
            return None
        except json.JSONDecodeError as e:
            print(f"\n✗ JSON parsing error: {e}")
            print(f"  LLM returned non-JSON response")
            return None
        except Exception as e:
            print(f"\n✗ LLM error: {e}")
            return None

# ============================================================================
# MAIN DEBUG ORCHESTRATOR
# ============================================================================
async def run_debug_pipeline(video_url: str):
    """Run complete debug pipeline"""
    
    print(f"\n{'='*80}")
    print("KALO AI RECIPE EXTRACTION - COMPLETE DEBUG")
    print(f"{'='*80}")
    print(f"Video URL: {video_url}")
    print(f"Temp directory: {TEMP_DIR}")
    print(f"{'='*80}\n")
    
    results = {}
    
    # Step 1: Download video
    print("\n[STEP 1/7] DOWNLOADING VIDEO...")
    video_path = await VideoDownloaderDebug.download(
        video_url,
        os.path.join(TEMP_DIR, "video")
    )
    results['video_path'] = video_path
    
    if not video_path:
        print("\n✗ Pipeline halted: Video download failed")
        return results
    
    # Step 2: Extract audio
    print("\n[STEP 2/7] EXTRACTING AUDIO...")
    audio_path = await AudioExtractorDebug.extract(
        video_path,
        os.path.join(TEMP_DIR, "audio")
    )
    results['audio_path'] = audio_path
    
    if not audio_path:
        print("\n⚠ Continuing without audio (Whisper will skip)")
    
    # Step 3: Extract frames
    print("\n[STEP 3/7] EXTRACTING FRAMES...")
    frames = await FrameExtractorDebug.extract(
        video_path,
        os.path.join(TEMP_DIR, "frames")
    )
    results['frames'] = frames
    
    if not frames:
        print("\n✗ Pipeline halted: No frames extracted")
        return results
    
    # Step 4: Transcribe
    print("\n[STEP 4/7] TRANSCRIBING AUDIO...")
    transcript = ""
    if audio_path:
        transcript = await WhisperTranscriberDebug.transcribe(audio_path) or ""
    else:
        print("  Skipping Whisper (no audio extracted)")
    results['transcript'] = transcript
    
    # Step 5: OCR
    print("\n[STEP 5/7] EXTRACTING TEXT VIA OCR...")
    ocr_text = await OCRExtractorDebug.extract(frames)
    results['ocr_text'] = ocr_text
    
    # Step 6: YOLO
    print("\n[STEP 6/7] DETECTING OBJECTS WITH YOLO...")
    detections = await YOLODetectorDebug.detect(frames)
    results['detections'] = detections
    
    # Step 7: LLM
    print("\n[STEP 7/7] STRUCTURING RECIPE WITH LLM...")
    recipe = await LLMStructurerDebug.structure(
        transcript or "[No transcript]",
        ocr_text or "[No OCR]",
        detections
    )
    results['recipe'] = recipe
    
    # Summary
    print(f"\n{'='*80}")
    print("DEBUG SUMMARY")
    print(f"{'='*80}")
    print(f"✓ Video downloaded: {bool(video_path)}")
    print(f"✓ Audio extracted: {bool(audio_path)}")
    print(f"✓ Frames extracted: {len(frames)} frames")
    print(f"✓ Transcript obtained: {len(transcript)} characters")
    print(f"✓ OCR text obtained: {len(ocr_text)} characters")
    print(f"✓ Objects detected: {len(detections)} objects")
    print(f"✓ Recipe structured: {bool(recipe)}")
    print(f"{'='*80}\n")
    
    return results

# ============================================================================
# ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    # Example TikTok URL - CHANGE THIS TO YOUR TEST URL
    TEST_URL = "https://www.tiktok.com/@yourprofile/video/1234567890"
    
    # Check if URL provided as argument
    if len(sys.argv) > 1:
        TEST_URL = sys.argv[1]
    
    print(f"\nUsage: python debug_pipeline.py <video_url>")
    print(f"Current URL: {TEST_URL}\n")
    
    # Run debug
    try:
        results = asyncio.run(run_debug_pipeline(TEST_URL))
        print("\nDebug complete. Check outputs above.")
    except KeyboardInterrupt:
        print("\n\nDebug interrupted by user")
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
