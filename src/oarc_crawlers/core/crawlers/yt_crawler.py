"""
YouTube Crawler Module

The `YTCrawler` class provides robust, high-level tools for downloading, extracting, and archiving YouTube content for research and analytics.

Features:
- Download individual videos or entire playlists in configurable formats and resolutions.
- Extract and persist detailed video metadata and multilingual captions (subtitles).
- Perform YouTube searches and archive search results for reproducible analysis.
- Retrieve and archive live chat messages from streams and premieres.
- Store all content and metadata in efficient Parquet files for scalable, structured analysis.

Dependencies:
- pytube: Video, playlist, and metadata extraction.
- pytchat: Live chat message retrieval.
- moviepy: Audio extraction and conversion (optional, for mp3 support).
- ParquetStorage: Structured data storage in Parquet format.

Designed for: Automated, reproducible YouTube data collection pipelines and research workflows.

Authors: @Borcherdingl, RawsonK
Last updated: 2025-04-18
"""

import os
from datetime import datetime, UTC
from typing import Dict, List, Optional

import pytube
from pytube import YouTube, Playlist, Search
import pytchat

from oarc_log import log
from oarc_decorators import (
    OarcError,
    DataExtractionError,
    NetworkError,
    ResourceNotFoundError,
)

from oarc_crawlers.core.storage.parquet_storage import ParquetStorage
from oarc_crawlers.utils.crawler_utils import CrawlerUtils
from oarc_crawlers.utils.paths import Paths
from oarc_crawlers.utils.const import YOUTUBE_VIDEO_URL_FORMAT


class YTCrawler:
    """
    YTCrawler: Comprehensive YouTube content crawler and archiver.

    Overview:
    Provides high-level, automated tools for downloading, extracting, and archiving YouTube content for research, analytics, and reproducibility.

    Core Features:
    - Download individual videos or entire playlists in configurable formats and resolutions.
    - Extract and persist rich video metadata and multilingual captions (subtitles).
    - Perform YouTube searches and archive search results for reproducible analysis.
    - Retrieve and archive live chat messages from streams and premieres.
    - Store all content and metadata in efficient Parquet files for scalable, structured analysis.

    Usage Scenarios:
    - Automated, reproducible YouTube data collection pipelines.
    - Academic research and large-scale video analytics.
    - Archival and monitoring of YouTube content and interactions.

    All methods are designed for robustness, scalability, and integration into research workflows.
    """

    @classmethod
    async def download_video(cls, url: str, video_format: str = "mp4", 
                           resolution: str = "highest", output_path: Optional[str] = None,
                           filename: Optional[str] = None, extract_audio: bool = False,
                           data_dir: Optional[str] = None) -> Dict:
        """
        Download a YouTube video with configurable options.

        Args:
            url (str): The YouTube video URL.
            video_format (str): Desired file format (e.g., "mp4", "webm", "mp3").
            resolution (str): Video resolution ("highest", "lowest", or specific like "720p").
            output_path (str, optional): Directory to save the downloaded file.
            filename (str, optional): Custom filename for the output file.
            extract_audio (bool): If True, download audio only (optionally convert to mp3).
            data_dir (str, optional): Base directory for data storage and metadata.

        Returns:
            dict: Metadata and file information about the downloaded video.

        Raises:
            ResourceNotFoundError: If the video URL is invalid or unavailable.
            NetworkError: If unable to connect to YouTube.
            CrawlerError: For download or conversion failures.
        """
        # Create default output path if not specified
        if output_path is None:
            output_path = str(Paths.youtube_videos_dir(data_dir))
        
        log.debug(f"Starting download of YouTube video: {url}")
        log.debug(f"Format: {video_format}, Resolution: {resolution}, Extract audio: {extract_audio}")
        
        # Create YouTube object
        try:
            youtube = YouTube(url)
        except pytube.exceptions.RegexMatchError:
            raise ResourceNotFoundError(f"Invalid YouTube URL: {url}")
        except pytube.exceptions.VideoUnavailable:
            raise ResourceNotFoundError(f"The video {url} is unavailable")
        except Exception as e:
            raise NetworkError(f"Error connecting to YouTube: {str(e)}")
        
        video_info = cls._extract_video_info(youtube)
        log.debug(f"Successfully extracted metadata for video: {video_info['title']}")
        
        # Get appropriate stream based on parameters
        if extract_audio:
            stream = youtube.streams.filter(only_audio=True).first()
            if not stream:
                raise ResourceNotFoundError(f"No audio stream available for {url}")
            
            file_path = stream.download(output_path=output_path, filename=filename)
            log.debug(f"Downloaded audio to: {file_path}")
            
            # Convert to mp3 if requested
            if video_format.lower() == "mp3":
                try:
                    from moviepy import AudioFileClip
                except ImportError:
                    log.debug("moviepy not installed, cannot convert to mp3")
                    raise OarcError("moviepy package is required for mp3 conversion")
                
                mp3_path = os.path.splitext(file_path)[0] + ".mp3"
                log.debug(f"Converting audio to mp3: {mp3_path}")
                
                audio_clip = AudioFileClip(file_path)
                audio_clip.write_audiofile(mp3_path)
                audio_clip.close()
                os.remove(file_path)  # Remove the original file
                file_path = mp3_path
                log.debug("Conversion to mp3 complete")
        else:
            # Select the appropriate video stream
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
                raise ResourceNotFoundError(f"No suitable stream found for {url} with format {video_format}")
            
            log.debug(f"Selected stream: {stream.resolution}, {stream.mime_type}")
            
            # Download the video
            file_path = stream.download(output_path=output_path, filename=filename)
            log.debug(f"Downloaded video to: {file_path}")
        
        # Update video info with downloaded file info
        video_info.update({
            'file_path': file_path,
            'file_size': os.path.getsize(file_path),
            'format': os.path.splitext(file_path)[1][1:],
            'download_time': datetime.now(UTC).isoformat()
        })
        
        # Save metadata to Parquet
        metadata_path = str(Paths.youtube_metadata_path(data_dir, youtube.video_id))
        log.debug(f"Saving metadata to: {metadata_path}")
        ParquetStorage.save_to_parquet(video_info, metadata_path)
        
        return video_info

    @classmethod
    def _extract_video_info(cls, youtube: YouTube) -> Dict:
        """
        Extract detailed metadata from a pytube YouTube object.

        Args:
            youtube (YouTube): A pytube YouTube object representing the video.

        Returns:
            dict: Dictionary containing extracted video metadata fields.

        Raises:
            DataExtractionError: If metadata extraction fails.
        """
        log.debug(f"Extracting metadata for video ID: {youtube.video_id}")
        
        video_info = {
            'title': youtube.title,
            'video_id': youtube.video_id,
            'url': YOUTUBE_VIDEO_URL_FORMAT.format(video_id=youtube.video_id),
            'author': youtube.author,
            'channel_url': youtube.channel_url,
            'description': youtube.description,
            'length': youtube.length,
            'publish_date': youtube.publish_date.isoformat() if youtube.publish_date else None,
            'views': youtube.views,
            'rating': youtube.rating,
            'thumbnail_url': youtube.thumbnail_url,
            'keywords': youtube.keywords,
            'timestamp': datetime.now(UTC).isoformat()
        }
        
        log.debug(f"Successfully extracted metadata for: {video_info['title']}")
        return video_info

    @classmethod
    async def download_playlist(cls, playlist_url: str, format: str = "mp4", 
                              max_videos: int = 10, output_path: Optional[str] = None,
                              data_dir: Optional[str] = None) -> Dict:
        """
        Download and archive videos from a YouTube playlist.

        Args:
            playlist_url (str): The URL of the YouTube playlist to download.
            format (str): Desired video format (e.g., "mp4", "webm").
            max_videos (int): Maximum number of videos to download from the playlist.
            output_path (str, optional): Directory to save downloaded videos. Defaults to a standard playlists directory.
            data_dir (str, optional): Base directory for storing data and metadata.

        Returns:
            dict: Metadata and file information about the downloaded playlist and its videos.

        Raises:
            ResourceNotFoundError: If the playlist URL is invalid or contains no videos.
            NetworkError: If unable to connect to YouTube.
            DownloadError: If any video download fails.
        """
        if output_path is None:
            output_path = str(Paths.youtube_playlists_dir(data_dir))
        
        log.debug(f"Starting download of YouTube playlist: {playlist_url}")
        log.debug(f"Format: {format}, Max videos: {max_videos}")
        
        try:
            playlist = Playlist(playlist_url)
            if not playlist.video_urls:
                raise ResourceNotFoundError(f"No videos found in playlist: {playlist_url}")
        except pytube.exceptions.RegexMatchError:
            raise ResourceNotFoundError(f"Invalid YouTube playlist URL: {playlist_url}")
        except Exception as e:
            raise NetworkError(f"Error connecting to YouTube playlist: {str(e)}")
        
        playlist_info = {
            'title': playlist.title,
            'playlist_id': playlist.playlist_id,
            'url': playlist.playlist_url,
            'owner': playlist.owner,
            'total_videos': len(playlist.video_urls),
            'videos_to_download': min(max_videos, len(playlist.video_urls)),
            'videos': []
        }
        
        log.debug(f"Found playlist: {playlist_info['title']} with {playlist_info['total_videos']} videos")
        
        safe_title = Paths.sanitize_filename(playlist.title)
        playlist_dir = os.path.join(output_path, f"{safe_title}_{playlist.playlist_id}")
        os.makedirs(playlist_dir, exist_ok=True)
        log.debug(f"Created playlist directory: {playlist_dir}")
        
        for i, video_url in enumerate(playlist.video_urls):
            if i >= max_videos:
                break
                
            log.debug(f"Downloading video {i+1}/{min(max_videos, len(playlist.video_urls))}: {video_url}")
            try:
                video_info = await cls.download_video(
                    url=video_url, 
                    video_format=format, 
                    output_path=playlist_dir,
                    data_dir=data_dir
                )
                playlist_info['videos'].append(video_info)
                log.debug(f"Successfully downloaded: {video_info.get('title', 'Unknown')}")
            except Exception as e:
                error_info = {'error': str(e), 'url': video_url}
                playlist_info['videos'].append(error_info)
                log.error(f"Failed to download video {i+1}: {str(e)}")
        
        metadata_path = os.path.join(playlist_dir, "playlist_metadata.parquet")
        log.debug(f"Saving playlist metadata to: {metadata_path}")
        ParquetStorage.save_to_parquet(playlist_info, metadata_path)
        
        return playlist_info

    @classmethod
    async def extract_captions(cls, url: str, languages: List[str] = ['en'],
                             data_dir: Optional[str] = None) -> Dict:
        """
        Extract captions (subtitles) from a YouTube video in one or more languages.

        Args:
            url (str): The YouTube video URL.
            languages (list): List of language codes to extract captions for (e.g., ['en', 'es', 'fr']).
            data_dir (str, optional): Base directory for saving captions and metadata.

        Returns:
            dict: Dictionary containing extracted captions and related metadata.

        Raises:
            ResourceNotFoundError: If the video URL is invalid or no captions are available.
            NetworkError: If unable to connect to YouTube.
            DataExtractionError: If caption extraction fails.
        """
        log.debug(f"Extracting captions for video: {url}")
        log.debug(f"Requested languages: {languages}")
        
        try:
            youtube = YouTube(url)
        except pytube.exceptions.RegexMatchError:
            raise ResourceNotFoundError(f"Invalid YouTube URL: {url}")
        except pytube.exceptions.VideoUnavailable:
            raise ResourceNotFoundError(f"The video {url} is unavailable")
        except Exception as e:
            raise NetworkError(f"Error connecting to YouTube: {str(e)}")
        
        video_info = cls._extract_video_info(youtube)
        
        captions_data = {
            'video_id': youtube.video_id,
            'title': youtube.title,
            'url': url,
            'captions': {}
        }
        
        caption_tracks = youtube.captions
        if not caption_tracks.all():
            raise ResourceNotFoundError(f"No captions available for video: {url}")
        
        log.debug(f"Found {len(caption_tracks.all())} caption track(s)")
        
        for lang in languages:
            found = False
            for caption in caption_tracks.all():
                log.debug(f"Checking caption track: {caption.code}")
                if lang in caption.code:
                    caption_content = caption.generate_srt_captions()
                    captions_data['captions'][caption.code] = caption_content
                    found = True
                    log.debug(f"Found captions for language: {caption.code}")
                    break
            
            if not found and lang == 'en' and caption_tracks.all():
                caption = caption_tracks.all()[0]
                captions_data['captions'][caption.code] = caption.generate_srt_captions()
                log.debug(f"Used {caption.code} captions as fallback for English")
        
        captions_dir = Paths.youtube_captions_dir(data_dir)
        log.debug(f"Saving captions to directory: {captions_dir}")
        
        for lang_code, content in captions_data['captions'].items():
            caption_file = captions_dir / f"{youtube.video_id}_{lang_code}.srt"
            with open(caption_file, "w", encoding="utf-8") as f:
                f.write(content)
            captions_data['captions'][lang_code] = str(caption_file)
            log.debug(f"Saved {lang_code} captions to: {caption_file}")
        
        metadata_path = captions_dir / f"{youtube.video_id}_caption_metadata.parquet"
        log.debug(f"Saving caption metadata to: {metadata_path}")
        ParquetStorage.save_to_parquet(captions_data, str(metadata_path))
        
        return captions_data

    @classmethod
    async def search_videos(cls, query: str, limit: int = 10,
                          data_dir: Optional[str] = None) -> Dict:
        """
        Perform a YouTube video search and archive the results.

        Args:
            query (str): The search query string.
            limit (int): Maximum number of video results to return.
            data_dir (str, optional): Base directory for saving search results and metadata.

        Returns:
            dict: Dictionary containing search metadata and a list of found videos.

        Raises:
            NetworkError: If unable to connect to YouTube.
            DataExtractionError: If no results are found or extraction fails.
        """
        log.debug(f"Searching YouTube for: {query} (limit: {limit})")
        
        search_results = Search(query)
        videos = []
        
        for i, video in enumerate(search_results.results):
            if i >= limit:
                break
            
            try:
                video_info = {
                    'title': video.title,
                    'video_id': video.video_id,
                    'url': YOUTUBE_VIDEO_URL_FORMAT.format(video_id=video.video_id),
                    'thumbnail_url': video.thumbnail_url,
                    'author': video.author,
                    'publish_date': video.publish_date.isoformat() if video.publish_date else None,
                    'description': video.description,
                    'length': video.length,
                    'views': video.views
                }
                videos.append(video_info)
                log.debug(f"Added search result: {video.title}")
            except Exception as e:
                log.debug(f"Error extracting info for search result: {str(e)}")
        
        if not videos:
            raise DataExtractionError(f"No videos found for query: {query}")
        
        search_data = {
            'query': query,
            'timestamp': datetime.now(UTC).isoformat(),
            'result_count': len(videos),
            'results': videos
        }
        
        search_dir = Paths.youtube_search_dir(data_dir)
        safe_query = Paths.sanitize_filename(query)
        metadata_path = Paths.timestamped_path(search_dir, safe_query, "parquet")
        log.debug(f"Saving search results to: {metadata_path}")
        ParquetStorage.save_to_parquet(search_data, str(metadata_path))
        
        return search_data

    @classmethod
    async def fetch_stream_chat(cls, video_id: str, max_messages: int = 1000, 
                              save_to_file: bool = True, duration: Optional[int] = None,
                              data_dir: Optional[str] = None) -> Dict:
        """
        Retrieve and archive live chat messages from a YouTube live stream or premiere.

        Args:
            video_id (str): YouTube video ID or full URL.
            max_messages (int): Maximum number of chat messages to collect.
            save_to_file (bool): If True, save collected messages to a text file.
            duration (int, optional): Maximum duration (in seconds) to collect messages; None for unlimited.
            data_dir (str, optional): Base directory for saving chat data and metadata.

        Returns:
            dict: Metadata and details about the collected chat messages.

        Raises:
            ResourceNotFoundError: If the video ID/URL is invalid or chat is not active.
            NetworkError: If unable to connect to YouTube.
            DataExtractionError: If chat extraction fails.
        """
        log.debug(f"Fetching chat for video ID/URL: {video_id}")
        log.debug(f"Settings: max_messages={max_messages}, duration={duration or 'unlimited'}")
        
        # Extract video ID if a URL was provided
        try:
            video_id = CrawlerUtils.extract_youtube_id(video_id)
        except ValueError as e:
            raise ResourceNotFoundError(str(e))
        
        log.debug(f"Using video ID: {video_id}")
        
        try:
            chat = pytchat.create(video_id=video_id)
            
            if not chat.is_alive():
                raise ResourceNotFoundError(f"Chat is not active for video: {video_id}")
                
            log.debug("Chat connection established")
            
        except pytchat.exceptions.ChatParseException as e:
            raise ResourceNotFoundError(f"Failed to parse chat for video {video_id}: {str(e)}")
        except Exception as e:
            raise NetworkError(f"Failed to connect to chat for video {video_id}: {str(e)}")
        
        chat_data = {
            "video_id": video_id,
            "url": YOUTUBE_VIDEO_URL_FORMAT.format(video_id=video_id),
            "timestamp": datetime.now(UTC).isoformat(),
            "messages": [],
            "message_count": 0
        }
        
        start_time = datetime.now()
        timeout = False
        
        log.debug("Starting collection of chat messages")
        while chat.is_alive() and len(chat_data["messages"]) < max_messages and not timeout:
            for c in chat.get().sync_items():
                message = {
                    "datetime": c.datetime,
                    "timestamp": c.timestamp,
                    "author_name": c.author.name,
                    "author_id": c.author.channelId,
                    "message": c.message,
                    "type": c.type,
                    "is_verified": c.author.isVerified,
                    "is_chat_owner": c.author.isChatOwner,
                    "is_chat_sponsor": c.author.isChatSponsor,
                    "is_chat_moderator": c.author.isChatModerator
                }
                
                if hasattr(c.author, 'badges') and c.author.badges:
                    message["badges"] = c.author.badges
                    
                chat_data["messages"].append(message)
                
                if len(chat_data["messages"]) >= max_messages:
                    log.debug(f"Reached maximum message count: {max_messages}")
                    break
                    
            if duration and (datetime.now() - start_time).total_seconds() >= duration:
                log.debug(f"Reached duration limit: {duration} seconds")
                timeout = True
                break
        
        chat_data["message_count"] = len(chat_data["messages"])
        log.debug(f"Collected {chat_data['message_count']} chat messages")
        
        if chat_data["message_count"] > 0:
            chat_dir = Paths.youtube_chats_dir(data_dir)
            
            parquet_path = str(Paths.timestamped_path(chat_dir, video_id, "parquet"))
            log.debug(f"Saving chat data to Parquet: {parquet_path}")
            ParquetStorage.save_to_parquet(chat_data, parquet_path)
            chat_data["parquet_path"] = parquet_path
            
            if save_to_file:
                txt_path = str(Paths.timestamped_path(chat_dir, video_id, "txt"))
                log.debug(f"Saving chat messages to text file: {txt_path}")
                
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(f"Chat messages for {video_id}\n")
                    f.write(f"Collected at: {chat_data['timestamp']}\n")
                    f.write(f"Total messages: {chat_data['message_count']}\n\n")
                    for msg in chat_data["messages"]:
                        author_tags = []
                        if msg["is_verified"]: author_tags.append("✓")
                        if msg["is_chat_owner"]: author_tags.append("👑")
                        if msg["is_chat_sponsor"]: author_tags.append("💰")
                        if msg["is_chat_moderator"]: author_tags.append("🛡️")
                        
                        author_suffix = f" ({', '.join(author_tags)})" if author_tags else ""
                        f.write(f"[{msg['datetime']}] {msg['author_name']}{author_suffix}: {msg['message']}\n")
                
                chat_data["text_path"] = txt_path
        
        return chat_data