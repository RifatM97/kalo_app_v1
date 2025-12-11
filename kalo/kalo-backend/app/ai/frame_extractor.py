"""
Frame Extractor Module
Extracts frames from video for OCR and vision analysis
"""

import subprocess
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


class FrameExtractionError(Exception):
    """Raised when frame extraction fails"""
    pass


class FrameExtractor:
    """Extracts frames from video files"""
    
    def __init__(self, output_dir: str = "/tmp/kalo_frames"):
        """
        Initialize FrameExtractor
        
        Args:
            output_dir: Directory to save extracted frames
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logger
    
    def _get_video_duration(self, video_path: str) -> float:
        """
        Get video duration in seconds using ffprobe
        
        Args:
            video_path: Path to video file
            
        Returns:
            Duration in seconds
        """
        try:
            cmd = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1:nokey_sep=:",
                str(video_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return float(result.stdout.strip())
        except Exception as e:
            self.logger.warning(f"Could not get video duration: {e}, using default")
            return 0
    
    def extract_frames(
        self,
        video_path: str,
        num_frames: int = 5,
        frame_prefix: str = "frame"
    ) -> List[str]:
        """
        Extract evenly-spaced frames from video
        
        Args:
            video_path: Path to video file
            num_frames: Number of frames to extract (default 5)
            frame_prefix: Prefix for output frame files
            
        Returns:
            List of paths to extracted frame images
            
        Raises:
            FrameExtractionError: If extraction fails
        """
        try:
            video_path = Path(video_path)
            if not video_path.exists():
                raise FrameExtractionError(f"Video file not found: {video_path}")
            
            self.logger.info(f"Extracting {num_frames} frames from: {video_path}")
            
            # Get video duration
            duration = self._get_video_duration(str(video_path))
            self.logger.info(f"Video duration: {duration:.2f}s")
            
            # Calculate frame timestamps
            if duration > 0:
                timestamps = [duration * i / (num_frames - 1) for i in range(num_frames)]
            else:
                # Fallback: extract frames at fixed intervals
                timestamps = [i * 2 for i in range(num_frames)]
            
            frame_paths = []
            
            # Extract each frame
            for idx, timestamp in enumerate(timestamps):
                frame_filename = f"{frame_prefix}_{idx:03d}.jpg"
                frame_path = self.output_dir / frame_filename
                
                cmd = [
                    "ffmpeg",
                    "-i", str(video_path),
                    "-ss", str(timestamp),  # Seek to timestamp
                    "-vframes", "1",  # Extract 1 frame
                    "-q:v", "2",  # Quality (1=best, 31=worst)
                    "-y",  # Overwrite
                    str(frame_path)
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0:
                    self.logger.warning(f"Failed to extract frame {idx}: {result.stderr}")
                    continue
                
                if frame_path.exists():
                    frame_paths.append(str(frame_path))
                    self.logger.info(f"  ✓ Frame {idx} @ {timestamp:.2f}s: {frame_path.name}")
            
            if not frame_paths:
                raise FrameExtractionError("No frames could be extracted")
            
            self.logger.info(f"✓ Extracted {len(frame_paths)} frames")
            return frame_paths
            
        except Exception as e:
            msg = f"Frame extraction failed: {str(e)}"
            self.logger.error(msg)
            raise FrameExtractionError(msg) from e
    
    def cleanup(self, frame_paths: List[str]) -> int:
        """
        Delete extracted frames to free disk space
        
        Args:
            frame_paths: List of frame file paths
            
        Returns:
            Number of files deleted
        """
        deleted = 0
        for frame_path in frame_paths:
            try:
                path = Path(frame_path)
                if path.exists():
                    path.unlink()
                    deleted += 1
            except Exception as e:
                self.logger.error(f"Failed to cleanup {frame_path}: {e}")
        
        if deleted > 0:
            self.logger.info(f"✓ Cleaned up {deleted} frames")
        return deleted


# Singleton extractor instance
_extractor = None


def get_extractor(output_dir: str = "/tmp/kalo_frames") -> FrameExtractor:
    """Get or create FrameExtractor singleton"""
    global _extractor
    if _extractor is None:
        _extractor = FrameExtractor(output_dir)
    return _extractor


async def extract_frames(
    video_path: str,
    num_frames: int = 5,
    frame_prefix: str = "frame"
) -> List[str]:
    """
    Async wrapper for extracting frames
    
    Args:
        video_path: Path to video
        num_frames: Number of frames
        frame_prefix: Output prefix
        
    Returns:
        List of frame paths
    """
    extractor = get_extractor()
    return extractor.extract_frames(video_path, num_frames, frame_prefix)
