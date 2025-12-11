"""
Vision Detector Module
Detects ingredients, cooking actions, and objects in frames using YOLOv8
"""

import logging
from pathlib import Path
from typing import List, Dict

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None

logger = logging.getLogger(__name__)


class VisionDetectionError(Exception):
    """Raised when vision detection fails"""
    pass


class VisionDetector:
    """Detects objects and ingredients in images using YOLOv8"""
    
    def __init__(self, model_name: str = "yolov8n.pt"):
        """
        Initialize VisionDetector
        
        Args:
            model_name: YOLOv8 model name (n=nano, s=small, m=medium, l=large)
                       nano = fastest, good for real-time
                       small = balanced
        """
        if YOLO is None:
            raise ImportError("ultralytics not installed. Run: pip install ultralytics")
        
        self.model_name = model_name
        self.model = None
        self.logger = logger
        
        # Common food-related classes to prioritize
        self.food_keywords = {
            'food', 'vegetable', 'fruit', 'meat', 'chicken', 'beef', 'fish',
            'potato', 'tomato', 'onion', 'garlic', 'pepper', 'salt', 'oil',
            'pan', 'pot', 'knife', 'cutting board', 'stove', 'oven',
            'rice', 'pasta', 'bread', 'cheese', 'egg', 'milk'
        }
    
    def _load_model(self):
        """Load YOLOv8 model on first use"""
        if self.model is None:
            self.logger.info(f"Loading YOLOv8 model: {self.model_name}")
            self.model = YOLO(self.model_name)
            self.logger.info("✓ YOLOv8 model loaded")
    
    def detect_objects(
        self,
        image_path: str,
        confidence_threshold: float = 0.5
    ) -> List[Dict]:
        """
        Detect objects in a single image
        
        Args:
            image_path: Path to image file
            confidence_threshold: Minimum confidence score (0-1)
            
        Returns:
            List of detected objects with:
                - class_name: Object class name
                - confidence: Detection confidence
                - bbox: Bounding box coordinates
        """
        try:
            image_path = Path(image_path)
            if not image_path.exists():
                raise VisionDetectionError(f"Image file not found: {image_path}")
            
            self.logger.info(f"Running detection on: {image_path.name}")
            self._load_model()
            
            # Run YOLOv8 detection
            results = self.model(str(image_path), conf=confidence_threshold, verbose=False)
            
            detections = []
            
            if results and len(results) > 0:
                result = results[0]
                
                # Extract detections
                if result.boxes is not None:
                    for box in result.boxes:
                        class_id = int(box.cls)
                        class_name = self.model.names[class_id]
                        confidence = float(box.conf)
                        
                        # Get bounding box
                        coords = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                        
                        detections.append({
                            "class_name": class_name,
                            "confidence": confidence,
                            "bbox": coords
                        })
            
            self.logger.info(f"  Detected {len(detections)} objects")
            return detections
            
        except Exception as e:
            msg = f"Vision detection failed for {image_path}: {str(e)}"
            self.logger.error(msg)
            raise VisionDetectionError(msg) from e
    
    def detect_in_frames(
        self,
        frame_paths: List[str],
        confidence_threshold: float = 0.5
    ) -> Dict[str, List[str]]:
        """
        Detect objects in multiple frames
        
        Args:
            frame_paths: List of frame file paths
            confidence_threshold: Minimum confidence score
            
        Returns:
            Dict mapping frame names to detected class names
        """
        frame_detections = {}
        all_detections = set()
        
        self.logger.info(f"Running detection on {len(frame_paths)} frames")
        
        for frame_path in frame_paths:
            try:
                detections = self.detect_objects(frame_path, confidence_threshold)
                frame_name = Path(frame_path).name
                
                # Extract just the class names
                class_names = [d["class_name"] for d in detections]
                frame_detections[frame_name] = class_names
                all_detections.update(class_names)
                
            except VisionDetectionError as e:
                self.logger.warning(f"Detection failed for {frame_path}: {e}")
                continue
        
        self.logger.info(f"✓ Total unique detections: {len(all_detections)}")
        self.logger.info(f"  Classes: {', '.join(sorted(all_detections))}")
        
        return frame_detections
    
    def extract_ingredients_from_frames(self, frame_paths: List[str]) -> List[str]:
        """
        Extract likely ingredients from frame detections
        
        Args:
            frame_paths: List of frame file paths
            
        Returns:
            List of detected ingredient names
        """
        detections = self.detect_in_frames(frame_paths)
        
        # Combine all detections
        all_classes = set()
        for classes in detections.values():
            all_classes.update(classes)
        
        # Filter for food-related items
        ingredients = [
            cls for cls in all_classes
            if any(keyword in cls.lower() for keyword in self.food_keywords)
        ]
        
        if not ingredients:
            # If no food keywords match, return all detections
            ingredients = sorted(all_classes)
        
        return sorted(ingredients)


# Singleton detector instance
_detector = None


def get_detector(model_name: str = "yolov8n.pt") -> VisionDetector:
    """Get or create VisionDetector singleton"""
    global _detector
    if _detector is None:
        _detector = VisionDetector(model_name)
    return _detector


async def detect_ingredients(frame_paths: List[str]) -> List[str]:
    """
    Async wrapper for detecting ingredients in frames
    
    Args:
        frame_paths: List of frame file paths
        
    Returns:
        List of detected ingredients
    """
    detector = get_detector()
    return detector.extract_ingredients_from_frames(frame_paths)
