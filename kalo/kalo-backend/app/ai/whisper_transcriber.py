"""
Whisper Transcriber Module
Transcribes audio to text using OpenAI Whisper
"""

import logging
from pathlib import Path
from typing import Optional

try:
    import whisper
except ImportError:
    whisper = None

logger = logging.getLogger(__name__)


class TranscriptionError(Exception):
    """Raised when transcription fails"""
    pass


class WhisperTranscriber:
    """Transcribes audio files using Whisper"""
    
    def __init__(self, model_name: str = "small"):
        """
        Initialize WhisperTranscriber
        
        Args:
            model_name: Whisper model size (tiny, base, small, medium, large)
                       small = good balance of speed/accuracy
        """
        if whisper is None:
            raise ImportError("openai-whisper not installed. Run: pip install openai-whisper")
        
        self.model_name = model_name
        self.model = None
        self.logger = logger
    
    def _load_model(self):
        """Load Whisper model on first use"""
        if self.model is None:
            self.logger.info(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name)
            self.logger.info("✓ Whisper model loaded")
    
    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        temperature: float = 0.0
    ) -> dict:
        """
        Transcribe audio file to text
        
        Args:
            audio_path: Path to audio file
            language: Optional language code (e.g., 'en', 'es', 'fr')
            temperature: Sampling temperature (0 = deterministic, 1 = random)
            
        Returns:
            Dict with:
                - text: Full transcription
                - segments: List of timed segments
                - language: Detected language
        """
        try:
            audio_path = Path(audio_path)
            if not audio_path.exists():
                raise TranscriptionError(f"Audio file not found: {audio_path}")
            
            self.logger.info(f"Transcribing: {audio_path}")
            self._load_model()
            
            # Run Whisper
            result = self.model.transcribe(
                str(audio_path),
                language=language,
                temperature=temperature,
                verbose=False
            )
            
            self.logger.info(f"✓ Transcription complete")
            self.logger.info(f"  Language: {result.get('language', 'unknown')}")
            self.logger.info(f"  Text length: {len(result['text'])} chars")
            
            return {
                "text": result["text"],
                "segments": result.get("segments", []),
                "language": result.get("language", "unknown")
            }
            
        except Exception as e:
            msg = f"Transcription failed: {str(e)}"
            self.logger.error(msg)
            raise TranscriptionError(msg) from e
    
    def transcribe_to_text(self, audio_path: str) -> str:
        """
        Transcribe audio and return just the text
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Transcribed text
        """
        result = self.transcribe(audio_path)
        return result["text"]


# Singleton transcriber instance
_transcriber = None


def get_transcriber(model_name: str = "small") -> WhisperTranscriber:
    """Get or create WhisperTranscriber singleton"""
    global _transcriber
    if _transcriber is None:
        _transcriber = WhisperTranscriber(model_name)
    return _transcriber


async def transcribe_audio(audio_path: str, language: Optional[str] = None) -> str:
    """
    Async wrapper for transcribing audio
    
    Args:
        audio_path: Path to audio file
        language: Optional language code
        
    Returns:
        Transcribed text
    """
    transcriber = get_transcriber()
    return transcriber.transcribe_to_text(audio_path)
