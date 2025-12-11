"""
Video Downloader Module
Downloads videos from TikTok, Instagram, YouTube using yt-dlp
"""

import os
import logging
from pathlib import Path
from typing import Optional
import yt_dlp

logger = logging.getLogger(__name__)


class VideoDownloadError(Exception):
    """Raised when video download fails"""
    pass


class VideoDownloader:
    """Downloads videos from social media platforms"""
    
    def __init__(self, output_dir: str = "/tmp/kalo_videos"):
        """
        Initialize VideoDownloader
        
        Args:
            output_dir: Directory to save downloaded videos
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logger
    
    def download(self, url: str, video_name: Optional[str] = None) -> str:
        """
        Download video from URL using yt-dlp
        
        Args:
            url: Video URL (TikTok, Instagram, YouTube)
            video_name: Optional custom video name
            
        Returns:
            Path to downloaded MP4 file
            
        Raises:
            VideoDownloadError: If download fails
        """
        try:
            self.logger.info(f"Starting download from: {url}")
            
            # Configure yt-dlp options
            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'outtmpl': str(self.output_dir / (video_name or '%(title)s.%(ext)s')),
                'quiet': False,
                'no_warnings': False,
                'socket_timeout': 30,
                'retries': 3,
                'fragment_retries': 3,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_path = ydl.prepare_filename(info)
                
            if not Path(video_path).exists():
                raise VideoDownloadError(f"Downloaded file not found: {video_path}")
            
            file_size_mb = Path(video_path).stat().st_size / (1024 * 1024)
            self.logger.info(f"✓ Download complete: {video_path} ({file_size_mb:.2f}MB)")
            
            return video_path
            
        except yt_dlp.utils.DownloadError as e:
            msg = f"yt-dlp download error: {str(e)}"
            self.logger.error(msg)
            raise VideoDownloadError(msg) from e
        except Exception as e:
            msg = f"Unexpected error during download: {str(e)}"
            self.logger.error(msg)
            raise VideoDownloadError(msg) from e
    
    def cleanup(self, video_path: str) -> bool:
        """
        Delete downloaded video to free disk space
        
        Args:
            video_path: Path to video file
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            path = Path(video_path)
            if path.exists():
                path.unlink()
                self.logger.info(f"✓ Cleaned up: {video_path}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to cleanup {video_path}: {e}")
            return False


# Singleton downloader instance
_downloader = None


def get_downloader(output_dir: str = "/tmp/kalo_videos") -> VideoDownloader:
    """Get or create VideoDownloader singleton"""
    global _downloader
    if _downloader is None:
        _downloader = VideoDownloader(output_dir)
    return _downloader


async def download_video(url: str, video_name: Optional[str] = None) -> str:
    """
    Async wrapper for downloading video
    
    Args:
        url: Video URL
        video_name: Optional custom name
        
    Returns:
        Path to downloaded video
    """
    downloader = get_downloader()
    return downloader.download(url, video_name)
