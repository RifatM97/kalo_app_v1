"""
AI Pipeline Module
Orchestrates the complete video-to-recipe extraction pipeline
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional

from .video_downloader import VideoDownloader
from .audio_extractor import AudioExtractor
from .frame_extractor import FrameExtractor
from .whisper_transcriber import WhisperTranscriber
from .ocr_extractor import OCRExtractor
from .vision_detector import VisionDetector
from .llm_structurer import LLMStructurer

logger = logging.getLogger(__name__)


class PipelineError(Exception):
    """Raised when pipeline fails"""
    pass


class RecipeExtractionPipeline:
    """
    Complete pipeline for extracting recipes from videos
    
    Flow:
    1. Download video from URL
    2. Extract audio
    3. Extract frames
    4. Transcribe audio (Whisper)
    5. Extract text from frames (OCR)
    6. Detect ingredients (Vision)
    7. Structure into recipe (LLM)
    8. Return structured recipe JSON
    """
    
    def __init__(self, cleanup: bool = True, llm_api_key: Optional[str] = None):
        """
        Initialize RecipeExtractionPipeline
        
        Args:
            cleanup: Whether to delete intermediate files after processing
            llm_api_key: API key for LLM (OpenAI, Anthropic, etc.)
        """
        self.cleanup = cleanup
        self.llm_api_key = llm_api_key
        self.logger = logger
        
        # Initialize components
        self.downloader = VideoDownloader()
        self.audio_extractor = AudioExtractor()
        self.frame_extractor = FrameExtractor()
        self.transcriber = WhisperTranscriber(model_name="small")
        self.ocr = OCRExtractor()
        self.vision = VisionDetector()
        self.llm = LLMStructurer(api_key=llm_api_key)
    
    async def run(
        self,
        video_url: str,
        num_frames: int = 5
    ) -> Dict:
        """
        Run complete extraction pipeline
        
        Args:
            video_url: URL to video (TikTok, Instagram, YouTube)
            num_frames: Number of frames to extract for analysis
            
        Returns:
            Structured recipe JSON
        """
        video_path = None
        audio_path = None
        frame_paths = None
        
        try:
            self.logger.info(f"{'='*60}")
            self.logger.info(f"RECIPE EXTRACTION PIPELINE START")
            self.logger.info(f"{'='*60}")
            self.logger.info(f"URL: {video_url}")
            
            # Step 1: Download video
            self.logger.info(f"\n[1/7] Downloading video...")
            video_path = self.downloader.download(video_url)
            self.logger.info(f"✓ Downloaded: {video_path}")
            
            # Step 2: Extract audio
            self.logger.info(f"\n[2/7] Extracting audio...")
            audio_path = self.audio_extractor.extract_audio(video_path)
            self.logger.info(f"✓ Audio extracted: {audio_path}")
            
            # Step 3: Extract frames
            self.logger.info(f"\n[3/7] Extracting frames...")
            frame_paths = self.frame_extractor.extract_frames(video_path, num_frames=num_frames)
            self.logger.info(f"✓ Extracted {len(frame_paths)} frames")
            
            # Step 4: Transcribe audio
            self.logger.info(f"\n[4/7] Transcribing audio with Whisper...")
            transcript = self.transcriber.transcribe_to_text(audio_path)
            self.logger.info(f"✓ Transcribed: {len(transcript)} characters")
            self.logger.info(f"  Preview: {transcript[:100]}...")
            
            # Step 5: Extract OCR text
            self.logger.info(f"\n[5/7] Extracting text with OCR...")
            ocr_text = self.ocr.extract_all_text_from_frames(frame_paths)
            self.logger.info(f"✓ OCR extracted: {len(ocr_text)} characters")
            self.logger.info(f"  Preview: {ocr_text[:100]}...")
            
            # Step 6: Detect ingredients
            self.logger.info(f"\n[6/7] Detecting ingredients with Vision...")
            detected_items = self.vision.extract_ingredients_from_frames(frame_paths)
            self.logger.info(f"✓ Detected {len(detected_items)} items")
            self.logger.info(f"  Items: {', '.join(detected_items[:10])}")
            
            # Step 7: Structure with LLM
            self.logger.info(f"\n[7/7] Structuring recipe with LLM...")
            recipe = self.llm.structure_recipe(
                transcript=transcript,
                ocr_text=ocr_text,
                detected_items=detected_items
            )
            self.logger.info(f"✓ Recipe structured")
            self.logger.info(f"  Title: {recipe.get('title', 'Unknown')}")
            self.logger.info(f"  Ingredients: {len(recipe.get('ingredients', []))}")
            self.logger.info(f"  Steps: {len(recipe.get('steps', []))}")
            
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"EXTRACTION COMPLETE - SUCCESS")
            self.logger.info(f"{'='*60}\n")
            
            return recipe
            
        except Exception as e:
            self.logger.error(f"\n{'='*60}")
            self.logger.error(f"EXTRACTION FAILED: {str(e)}")
            self.logger.error(f"{'='*60}\n")
            raise PipelineError(f"Pipeline failed: {str(e)}") from e
            
        finally:
            # Cleanup intermediate files if requested
            if self.cleanup:
                self.logger.info("Cleaning up intermediate files...")
                
                if video_path:
                    self.downloader.cleanup(video_path)
                
                if audio_path:
                    self.audio_extractor.cleanup(audio_path)
                
                if frame_paths:
                    self.frame_extractor.cleanup(frame_paths)


# Singleton pipeline instance
_pipeline = None


def get_pipeline(cleanup: bool = True, llm_api_key: Optional[str] = None) -> RecipeExtractionPipeline:
    """Get or create RecipeExtractionPipeline singleton"""
    global _pipeline
    if _pipeline is None:
        _pipeline = RecipeExtractionPipeline(cleanup=cleanup, llm_api_key=llm_api_key)
    return _pipeline


async def extract_recipe_from_video(
    video_url: str,
    num_frames: int = 5,
    cleanup: bool = True,
    llm_api_key: Optional[str] = None
) -> Dict:
    """
    Extract recipe from video URL using complete pipeline
    
    Args:
        video_url: URL to video (TikTok, Instagram, YouTube)
        num_frames: Number of frames to analyze
        cleanup: Whether to delete intermediate files
        llm_api_key: LLM API key
        
    Returns:
        Structured recipe JSON
    """
    pipeline = get_pipeline(cleanup=cleanup, llm_api_key=llm_api_key)
    return await pipeline.run(video_url, num_frames)
