"""YouTube video download and processing tools"""

import re
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def extract_video_id(url: str) -> str:
    """
    Extract YouTube video ID from various YouTube URL formats.

    Args:
        url: YouTube URL (shorts, watch, or youtu.be format)

    Returns:
        Video ID string

    Raises:
        ValueError: If URL format is invalid
    """
    patterns = [
        r'(?:youtube\.com\/shorts\/)([a-zA-Z0-9_-]{11})',
        r'(?:youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})',
        r'(?:youtu\.be\/)([a-zA-Z0-9_-]{11})',
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    raise ValueError(f"Invalid YouTube URL format: {url}")


def download_youtube_video(url: str, output_dir: str = "outputs") -> dict:
    """
    Download YouTube video and extract metadata using yt-dlp.

    Args:
        url: YouTube video URL
        output_dir: Directory to save downloaded video

    Returns:
        Dictionary with video_id, file_path, title, description, duration

    Raises:
        RuntimeError: If download fails
    """
    try:
        import yt_dlp
    except ImportError:
        raise ImportError("yt-dlp is required. Install with: pip install yt-dlp")

    try:
        video_id = extract_video_id(url)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': str(output_path / f'{video_id}.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            return {
                "video_id": video_id,
                "file_path": str(output_path / f"{video_id}.mp4"),
                "title": info.get('title', 'Unknown'),
                "description": info.get('description', ''),
                "duration": info.get('duration', 0),
                "uploader": info.get('uploader', 'Unknown'),
            }

    except Exception as e:
        logger.error(f"Failed to download video: {e}")
        raise RuntimeError(f"Video download failed: {str(e)}")
