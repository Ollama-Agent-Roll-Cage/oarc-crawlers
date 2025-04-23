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
from urllib.error import HTTPError

import pytube
from pytube import YouTube, Playlist, Search
import pytchat

from oarc_log import log
from oarc_utils.errors import (
    OARCError,
    DataExtractionError,
    NetworkError,
    ResourceNotFoundError,
)

from oarc_crawlers.core.storage.parquet_storage import ParquetStorage
from oarc_crawlers.utils.crawler_utils import CrawlerUtils
from oarc_crawlers.utils.paths import Paths
from oarc_crawlers.utils.const import (
    YOUTUBE_VIDEO_URL_FORMAT,
    YOUTUBE_WATCH_PATTERN,
    YOUTUBE_SHORT_PATTERN,
    YT_FORMAT_MP4, YT_FORMAT_MP3,
    YT_RESOLUTION_HIGHEST, 
    YT_RESOLUTION_LOWEST,
)


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

    def __init__(self, data_dir: Optional[str] = None):
        """Initialize the YouTube Crawler.
        
        Args:
            data_dir (str, optional): Directory to store data. 
                If None, uses the default data directory.
        """
        # Use Config.get_instance().data_dir if no data_dir provided
        from oarc_crawlers.config.config import Config
        self.data_dir = data_dir or str(Config.get_instance().data_dir)
        log.debug(f"Initialized YTCrawler with data directory: {self.data_dir}")

    @staticmethod
    def _sanitize_url(url: str) -> str:
        """Extract and return the clean YouTube video URL from any YouTube URL format.
        
        Args:
            url (str): Input YouTube URL, can contain extra parameters
            
        Returns:
            str: Clean YouTube video URL with just the video ID
            
        Raises:
            ResourceNotFoundError: If video ID cannot be extracted from URL
        """
        return CrawlerUtils.sanitize_youtube_url(url)

    async def download_video(self, url: str, video_format: str = YT_FORMAT_MP4, 
                           resolution: str = YT_RESOLUTION_HIGHEST, output_path: Optional[str] = None,
                           filename: Optional[str] = None, extract_audio: bool = False) -> Dict:
        """
        Download a YouTube video with configurable options.

        Args:
            url (str): The YouTube video URL.
            video_format (str): Desired file format (e.g., "mp4", "webm", "mp3").
            resolution (str): Video resolution ("highest", "lowest", or specific like "720p").
            output_path (str, optional): Directory to save the downloaded file.
            filename (str, optional): Custom filename for the output file.
            extract_audio (bool): If True, download audio only (optionally convert to mp3).

        Returns:
            dict: Metadata and file information about the downloaded video.

        Raises:
            ResourceNotFoundError: If the video URL is invalid or unavailable.
            NetworkError: If unable to connect to YouTube.
            CrawlerError: For download or conversion failures.
        """
        # Create default output path if not specified
        if output_path is None:
            output_path = str(Paths.youtube_videos_dir(self.data_dir))
        
        log.debug(f"Starting download of YouTube video: {url}")
        log.debug(f"Format: {video_format}, Resolution: {resolution}, Extract audio: {extract_audio}")
        
        # Sanitize the URL before proceeding
        clean_url = self._sanitize_url(url)
        
        try:
            youtube = YouTube(clean_url)
        except pytube.exceptions.RegexMatchError:
            raise ResourceNotFoundError(f"Invalid YouTube URL: {url}")
        except pytube.exceptions.VideoUnavailable:
            raise ResourceNotFoundError(f"The video {url} is unavailable")
        except Exception as e:
            if isinstance(e, HTTPError):
                if e.code == 400:
                    log.error(f"Bad request error, trying alternative URL format")
                    # Try alternative URL format
                    try:
                        video_id = url.split("v=")[1].split("&")[0]
                        alt_url = YOUTUBE_VIDEO_URL_FORMAT.format(video_id=video_id)
                        youtube = YouTube(alt_url)
                    except Exception:
                        raise NetworkError(f"Failed to connect to YouTube after retrying: {str(e)}")
                else:
                    raise NetworkError(f"HTTP error {e.code} connecting to YouTube: {str(e)}")
            else:
                raise NetworkError(f"Error connecting to YouTube: {str(e)}")
        
        video_info = CrawlerUtils.extract_video_info(youtube)
        log.debug(f"Successfully extracted metadata for video: {video_info['title']}")
        
        # Get appropriate stream based on parameters
        if extract_audio:
            stream = youtube.streams.filter(only_audio=True).first()
            if not stream:
                raise ResourceNotFoundError(f"No audio stream available for {url}")
            
            file_path = stream.download(output_path=output_path, filename=filename)
            log.debug(f"Downloaded audio to: {file_path}")
            
            # Convert to mp3 if requested
            if video_format.lower() == YT_FORMAT_MP3:
                try:
                    from moviepy import AudioFileClip
                except ImportError:
                    log.debug("moviepy not installed, cannot convert to mp3")
                    raise OARCError("moviepy package is required for mp3 conversion")
                
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
            stream = CrawlerUtils.select_stream(youtube, video_format, resolution, extract_audio)
            
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
        metadata_path = str(Paths.youtube_metadata_path(self.data_dir, youtube.video_id))
        log.debug(f"Saving metadata to: {metadata_path}")
        ParquetStorage.save_to_parquet(video_info, metadata_path)
        
        return video_info

    async def download_playlist(self, playlist_url: str, format: str = YT_FORMAT_MP4, 
                              max_videos: int = 10, output_path: Optional[str] = None) -> Dict:
        """
        Download and archive videos from a YouTube playlist.

        Args:
            playlist_url (str): The URL of the YouTube playlist to download.
            format (str): Desired video format (e.g., "mp4", "webm").
            max_videos (int): Maximum number of videos to download from the playlist.
            output_path (str, optional): Directory to save downloaded videos. 
                Defaults to a standard playlists directory.

        Returns:
            dict: Metadata and file information about the downloaded playlist and its videos.

        Raises:
            ResourceNotFoundError: If the playlist URL is invalid or contains no videos.
            NetworkError: If unable to connect to YouTube.
            DownloadError: If any video download fails.
        """
        if output_path is None:
            output_path = str(Paths.youtube_playlists_dir(self.data_dir))
        
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
        
        playlist_dir = str(Paths.youtube_playlist_dir(output_path, playlist.title, playlist.playlist_id))
        os.makedirs(playlist_dir, exist_ok=True)
        log.debug(f"Created playlist directory: {playlist_dir}")
        
        for i, video_url in enumerate(playlist.video_urls):
            if i >= max_videos:
                break
                
            log.debug(f"Downloading video {i+1}/{min(max_videos, len(playlist.video_urls))}: {video_url}")
            try:
                video_info = await self.download_video(
                    url=video_url, 
                    video_format=format, 
                    output_path=playlist_dir
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

    async def extract_captions(self, url: str, languages: List[str] = ['en']) -> Dict:
        """
        Extract captions (subtitles) from a YouTube video in one or more languages.

        Args:
            url (str): The YouTube video URL.
            languages (list): List of language codes to extract captions for (e.g., ['en', 'es', 'fr']).

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
        
        video_info = CrawlerUtils.extract_video_info(youtube)
        
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
        
        captions_dir = Paths.youtube_captions_dir(self.data_dir)
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

    async def search_videos(self, query: str, limit: int = 10) -> Dict:
        """
        Perform a YouTube video search and archive the results.

        Args:
            query (str): The search query string.
            limit (int): Maximum number of video results to return.

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
        
        search_dir = Paths.youtube_search_dir(self.data_dir)
        safe_query = Paths.sanitize_filename(query)
        metadata_path = Paths.timestamped_path(search_dir, safe_query, "parquet")
        log.debug(f"Saving search results to: {metadata_path}")
        ParquetStorage.save_to_parquet(search_data, str(metadata_path))
        
        return search_data

    async def fetch_stream_chat(self, video_id: str, max_messages: int = 1000, 
                              save_to_file: bool = True, duration: Optional[int] = None) -> Dict:
        """
        Retrieve and archive live chat messages from a YouTube live stream or premiere.

        Args:
            video_id (str): YouTube video ID or full URL.
            max_messages (int): Maximum number of chat messages to collect.
            save_to_file (bool): If True, save collected messages to a text file.
            duration (int, optional): Maximum duration (in seconds) to collect messages; None for unlimited.

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
            chat_dir = Paths.youtube_chats_dir(self.data_dir)
            
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
                        formatted_msg = CrawlerUtils.format_chat_message_for_file(msg)
                        f.write(f"{formatted_msg}\n")
                
                chat_data["text_path"] = txt_path
        
        return chat_data