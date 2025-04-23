"""
Utility functions for all OARC crawler modules.

This module provides common functionality used across different crawler implementations,
including URL handling, ID extraction, and standardized file operations.
"""

import re
from datetime import datetime, UTC
from typing import Dict, Optional

from pytube import YouTube

from oarc_log import log
from oarc_utils.errors import ResourceNotFoundError

from oarc_crawlers.utils.const import (
    YOUTUBE_VIDEO_URL_FORMAT,
    YOUTUBE_WATCH_PATTERN,
    YOUTUBE_SHORT_PATTERN,
    GITHUB_LANGUAGE_EXTENSIONS,
    NLTK_RESOURCES
)

class CrawlerUtils:
    """
    Utility methods for crawler operations across all OARC crawler modules.
    
    This class provides static utility methods for common operations used by
    various crawler implementations, including YouTube, web, and GitHub crawlers.
    """
    
    @staticmethod
    def extract_youtube_id(url_or_id: str) -> str:
        """
        Extract a YouTube video ID from a URL or ID string.
        
        Args:
            url_or_id: A YouTube URL or video ID
            
        Returns:
            The extracted video ID
            
        Raises:
            ValueError: If no valid YouTube ID could be extracted
        """
        if not url_or_id:
            raise ValueError("Empty YouTube URL or ID provided")
            
        # Case 1: Already a simple ID (no slashes or equals)
        if re.match(r'^[A-Za-z0-9_-]{11}$', url_or_id):
            return url_or_id
            
        # Case 2: youtube.com/watch URL
        watch_match = re.search(r'(?:youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_-]{11})', url_or_id)
        if watch_match:
            return watch_match.group(1)
            
        # Case 3: youtu.be short URL
        short_match = re.search(r'youtu\.be/([A-Za-z0-9_-]{11})', url_or_id)
        if short_match:
            return short_match.group(1)
            
        # Case 4: Embedded URL
        embed_match = re.search(r'youtube\.com/embed/([A-Za-z0-9_-]{11})', url_or_id)
        if embed_match:
            return embed_match.group(1)
            
        raise ValueError(f"Could not extract YouTube video ID from {url_or_id}")

    @staticmethod
    def format_timestamp(dt: Optional[datetime] = None) -> str:
        """
        Format a timestamp for consistent use in filenames and logs.
        
        Args:
            dt: Datetime object to format, uses current time if None
            
        Returns:
            Formatted timestamp string (UTC)
        """
        if dt is None:
            dt = datetime.now(UTC)
        return dt.isoformat()

    @staticmethod
    def file_size_format(size_bytes: int) -> str:
        """
        Format a file size in bytes to human-readable format.
        
        Args:
            size_bytes: File size in bytes
            
        Returns:
            Human-readable size string (e.g., "2.5 MB")
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes/(1024*1024):.1f} MB"
        else:
            return f"{size_bytes/(1024*1024*1024):.2f} GB"
            
    @staticmethod
    def extract_video_info(youtube: YouTube) -> Dict:
        """Extract metadata information from a YouTube object.
        
        Args:
            youtube (YouTube): pytube YouTube object
            
        Returns:
            dict: Video metadata
            
        Raises:
            DataExtractionError: If metadata extraction fails
        """
        log.debug(f"Extracting metadata for video ID: {youtube.video_id}")
        
        video_info = {
            'title': youtube.title,
            'video_id': youtube.video_id,
            'url': f"https://www.youtube.com/watch?v={youtube.video_id}",
            'author': youtube.author,
            'channel_url': youtube.channel_url,
            'description': youtube.description,
            'length': youtube.length,
            'publish_date': youtube.publish_date.isoformat() if youtube.publish_date else None,
            'views': youtube.views,
            'rating': youtube.rating,
            'thumbnail_url': youtube.thumbnail_url,
            'keywords': youtube.keywords,
            'timestamp': CrawlerUtils.format_timestamp()
        }
        
        log.debug(f"Successfully extracted metadata for: {video_info['title']}")
        return video_info
    
    @staticmethod
    def select_stream(youtube: YouTube, video_format: str, resolution: str, extract_audio: bool):
        """Select the appropriate stream based on parameters.
        
        Args:
            youtube: YouTube object to get streams from
            video_format: Format string (mp4, webm, etc.)
            resolution: Resolution string (highest, lowest, or specific)
            extract_audio: Whether to extract audio only
            
        Returns:
            The selected stream object
            
        Raises:
            ResourceNotFoundError: If no suitable stream is found
        """
        
        if extract_audio:
            stream = youtube.streams.filter(only_audio=True).first()
            if not stream:
                raise ResourceNotFoundError(f"No audio stream available for {youtube.video_id}")
            return stream
            
        # Handle video streams
        if resolution == "highest":
            if video_format.lower() == "mp4":
                stream = youtube.streams.filter(
                    progressive=True, file_extension=video_format).order_by('resolution').desc().first()
            else:
                stream = youtube.streams.filter(
                    file_extension=video_format).order_by('resolution').desc().first()
        elif resolution == "lowest":
            stream = youtube.streams.filter(
                file_extension=video_format).order_by('resolution').asc().first()
        else:
            # Try to get the specific resolution
            stream = youtube.streams.filter(
                res=resolution, file_extension=video_format).first()
            
            # Fall back to highest if specified resolution not available
            if not stream:
                log.debug(f"Resolution {resolution} not available, using highest available")
                stream = youtube.streams.filter(
                    file_extension=video_format).order_by('resolution').desc().first()
        
        # Check if a stream was found
        if not stream:
            raise ResourceNotFoundError(f"No suitable stream found with format {video_format}")
        
        return stream
    
    @staticmethod
    def format_chat_message_for_file(msg: Dict) -> str:
        """Format a chat message for text file output.
        
        Args:
            msg: Chat message dictionary with metadata
            
        Returns:
            Formatted string representation
        """
        author_tags = []
        if msg["is_verified"]: author_tags.append("✓")
        if msg["is_chat_owner"]: author_tags.append("👑")
        if msg["is_chat_sponsor"]: author_tags.append("💰")
        if msg["is_chat_moderator"]: author_tags.append("🛡️")
        
        author_suffix = f" ({', '.join(author_tags)})" if author_tags else ""
        return f"[{msg['datetime']}] {msg['author_name']}{author_suffix}: {msg['message']}"
    
    @staticmethod
    def sanitize_youtube_url(url: str) -> str:
        """Extract and return the clean YouTube video URL from any YouTube URL format.
        
        Args:
            url (str): Input YouTube URL, can contain extra parameters
            
        Returns:
            str: Clean YouTube video URL with just the video ID
            
        Raises:
            ResourceNotFoundError: If video ID cannot be extracted from URL
        """
        if YOUTUBE_WATCH_PATTERN in url:
            # Handle youtube.com URLs
            try:
                video_id = re.search(r'v=([^&]+)', url).group(1)
                return YOUTUBE_VIDEO_URL_FORMAT.format(video_id=video_id)
            except (AttributeError, IndexError):
                raise ResourceNotFoundError(f"Could not extract video ID from URL: {url}")
        elif YOUTUBE_SHORT_PATTERN in url:
            # Handle youtu.be URLs
            try:
                video_id = url.split(YOUTUBE_SHORT_PATTERN)[1].split("?")[0]
                return YOUTUBE_VIDEO_URL_FORMAT.format(video_id=video_id)
            except IndexError:
                raise ResourceNotFoundError(f"Could not extract video ID from URL: {url}")
        
        # If URL doesn't match any known pattern, raise exception
        if not (YOUTUBE_WATCH_PATTERN in url or YOUTUBE_SHORT_PATTERN in url):
            raise ResourceNotFoundError(f"Could not extract video ID from URL: {url}")
            
        return url
        
    @staticmethod
    def get_language_from_extension(extension: str) -> str:
        """Get programming language name from file extension.
        
        Args:
            extension (str): File extension with leading dot
            
        Returns:
            str: Language name or 'Unknown'
        """
        return GITHUB_LANGUAGE_EXTENSIONS.get(extension.lower(), 'Unknown')

    @staticmethod
    def init_nltk():
        """Initialize NLTK resources."""
        try:
            import nltk
            for resource in NLTK_RESOURCES:
                try:
                    nltk.data.find(resource)
                    log.debug(f"NLTK resource {resource} already available")
                except LookupError:
                    log.debug(f"Downloading NLTK resource: {resource}")
                    resource_name = resource.split('/')[-1]
                    nltk.download(resource_name, quiet=True)
            
            log.debug("NLTK resources initialized successfully")
            return True
        except Exception as e:
            log.warning(f"Failed to initialize NLTK resources: {e}")
            return False