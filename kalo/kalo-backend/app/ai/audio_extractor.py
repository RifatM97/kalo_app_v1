"""
Audio Extractor Module
Extracts audio from video using ffmpeg
"""

import subprocess
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class AudioExtractionError(Exception):
    """Raised when audio extraction fails"""
    pass


class AudioExtractor:
    """Extracts audio from video files"""
    
    def __init__(self, output_dir: str = "/tmp/kalo_audio"):
        """
        Initialize AudioExtractor
        
        Args:
            output_dir: Directory to save extracted audio
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logger
    
    def extract_audio(
        self,
        video_path: str,
        audio_name: Optional[str] = None,
        sample_rate: int = 16000
    ) -> str:
        """
        Extract audio from video as WAV file
        
        Args:
            video_path: Path to video file
            audio_name: Optional custom audio name
            sample_rate: Audio sample rate (default 16kHz for Whisper)
            
        Returns:
            Path to extracted WAV file
            
        Raises:
            AudioExtractionError: If extraction fails
        """
        try:
            video_path = Path(video_path)
            if not video_path.exists():
                raise AudioExtractionError(f"Video file not found: {video_path}")
            
            # Generate output filename
            if audio_name:
                audio_filename = f"{audio_name}.wav"
            else:
                audio_filename = f"{video_path.stem}_audio.wav"
            
            audio_path = self.output_dir / audio_filename
            
            self.logger.info(f"Extracting audio from: {video_path}")
            self.logger.info(f"Output: {audio_path} (sample rate: {sample_rate}Hz)")
            
            # FFmpeg command to extract audio
            cmd = [
                "ffmpeg",
                "-i", str(video_path),
                "-vn",  # No video
                "-acodec", "pcm_s16le",  # 16-bit PCM
                "-ar", str(sample_rate),  # Sample rate
                "-ac", "1",  # Mono
                "-y",  # Overwrite output
                str(audio_path)
            ]
            
            # Run ffmpeg
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                error_msg = result.stderr or "Unknown ffmpeg error"
                raise AudioExtractionError(f"FFmpeg error: {error_msg}")
            
            if not audio_path.exists():
                raise AudioExtractionError(f"Audio file was not created: {audio_path}")
            
            file_size_mb = audio_path.stat().st_size / (1024 * 1024)
            self.logger.info(f"✓ Audio extracted: {audio_path} ({file_size_mb:.2f}MB)")
            
            return str(audio_path)
            
        except subprocess.TimeoutExpired:
            raise AudioExtractionError("FFmpeg timeout - video too long or system slow")
        except Exception as e:
            msg = f"Audio extraction failed: {str(e)}"
            self.logger.error(msg)
            raise AudioExtractionError(msg) from e
    
    def cleanup(self, audio_path: str) -> bool:
        """
        Delete extracted audio to free disk space
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            path = Path(audio_path)
            if path.exists():
                path.unlink()
                self.logger.info(f"✓ Cleaned up: {audio_path}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to cleanup {audio_path}: {e}")
            return False


# Singleton extractor instance
_extractor = None


def get_extractor(output_dir: str = "/tmp/kalo_audio") -> AudioExtractor:
    """Get or create AudioExtractor singleton"""
    global _extractor
    if _extractor is None:
        _extractor = AudioExtractor(output_dir)
    return _extractor


async def extract_audio(
    video_path: str,
    audio_name: Optional[str] = None,
    sample_rate: int = 16000
) -> str:
    """
    Async wrapper for extracting audio
    
    Args:
        video_path: Path to video
        audio_name: Optional custom name
        sample_rate: Sample rate for audio
        
    Returns:
        Path to extracted audio
    """
    extractor = get_extractor()
    return extractor.extract_audio(video_path, audio_name, sample_rate)
