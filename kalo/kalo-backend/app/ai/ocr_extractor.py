"""
OCR Extractor Module
Extracts text from images using PaddleOCR
"""

import logging
from pathlib import Path
from typing import List, Dict

try:
    from paddleocr import PaddleOCR
except ImportError:
    PaddleOCR = None

logger = logging.getLogger(__name__)


class OCRError(Exception):
    """Raised when OCR fails"""
    pass


class OCRExtractor:
    """Extracts text from images using PaddleOCR"""
    
    def __init__(self, language: str = "en"):
        """
        Initialize OCRExtractor
        
        Args:
            language: Language code (en, zh, es, fr, etc.)
        """
        if PaddleOCR is None:
            raise ImportError("paddleocr not installed. Run: pip install paddleocr")
        
        self.language = language
        self.ocr = None
        self.logger = logger
    
    def _load_ocr(self):
        """Load PaddleOCR model on first use"""
        if self.ocr is None:
            self.logger.info(f"Loading PaddleOCR model for {self.language}")
            self.ocr = PaddleOCR(use_angle_cls=True, lang=self.language)
            self.logger.info("✓ PaddleOCR model loaded")
    
    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from a single image
        
        Args:
            image_path: Path to image file
            
        Returns:
            Extracted text
        """
        try:
            image_path = Path(image_path)
            if not image_path.exists():
                raise OCRError(f"Image file not found: {image_path}")
            
            self.logger.info(f"Running OCR on: {image_path.name}")
            self._load_ocr()
            
            # Run OCR
            result = self.ocr.ocr(str(image_path), cls=True)
            
            # Extract text from results
            texts = []
            if result:
                for line in result:
                    for word_info in line:
                        text = word_info[1]  # OCR text
                        confidence = word_info[2]  # Confidence score
                        
                        # Only include high-confidence text (>0.5)
                        if confidence > 0.5:
                            texts.append(text)
            
            extracted_text = " ".join(texts)
            self.logger.info(f"  Extracted {len(texts)} text elements")
            
            return extracted_text
            
        except Exception as e:
            msg = f"OCR extraction failed for {image_path}: {str(e)}"
            self.logger.error(msg)
            raise OCRError(msg) from e
    
    def extract_text_from_frames(self, frame_paths: List[str]) -> Dict[str, str]:
        """
        Extract text from multiple frames
        
        Args:
            frame_paths: List of image/frame file paths
            
        Returns:
            Dict mapping frame filename to extracted text
        """
        results = {}
        
        self.logger.info(f"Running OCR on {len(frame_paths)} frames")
        
        for frame_path in frame_paths:
            try:
                text = self.extract_text_from_image(frame_path)
                frame_name = Path(frame_path).name
                results[frame_name] = text
            except OCRError as e:
                self.logger.warning(f"Failed to process {frame_path}: {e}")
                continue
        
        # Combine all extracted text
        combined_text = " ".join(results.values())
        self.logger.info(f"✓ Combined OCR text: {len(combined_text)} characters")
        
        return results
    
    def extract_all_text_from_frames(self, frame_paths: List[str]) -> str:
        """
        Extract text from frames and combine into single string
        
        Args:
            frame_paths: List of frame file paths
            
        Returns:
            Combined OCR text from all frames
        """
        results = self.extract_text_from_frames(frame_paths)
        return " ".join(results.values())


# Singleton extractor instance
_extractor = None


def get_extractor(language: str = "en") -> OCRExtractor:
    """Get or create OCRExtractor singleton"""
    global _extractor
    if _extractor is None:
        _extractor = OCRExtractor(language)
    return _extractor


async def extract_text_from_frames(frame_paths: List[str], language: str = "en") -> str:
    """
    Async wrapper for extracting text from frames
    
    Args:
        frame_paths: List of frame file paths
        language: Language code
        
    Returns:
        Combined OCR text
    """
    extractor = get_extractor(language)
    return extractor.extract_all_text_from_frames(frame_paths)
