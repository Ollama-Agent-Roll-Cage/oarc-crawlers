"""
YouTube command-line interface for OARC Crawlers.

Provides commands for downloading videos, playlists, captions, searching, and extracting live chat from YouTube.
"""
import click

from oarc_crawlers.cli.help_texts import (
    YOUTUBE_HELP,
    YOUTUBE_DOWNLOAD_HELP,
    YOUTUBE_PLAYLIST_HELP,
    YOUTUBE_CAPTIONS_HELP,
    YOUTUBE_SEARCH_HELP,
    YOUTUBE_CHAT_HELP,
    ARGS_VERBOSE_HELP,
    ARGS_CONFIG_HELP,
    ARGS_VIDEO_URL_HELP,
    ARGS_VIDEO_ID_HELP,
    ARGS_PLAYLIST_URL_HELP,
    ARGS_FORMAT_HELP,
    ARGS_RESOLUTION_HELP,
    ARGS_EXTRACT_AUDIO_HELP,
    ARGS_OUTPUT_PATH_HELP,
    ARGS_FILENAME_HELP,
    ARGS_MAX_VIDEOS_HELP,
    ARGS_LANGUAGES_HELP,
    ARGS_QUERY_HELP,
    ARGS_LIMIT_HELP,
    ARGS_MAX_MESSAGES_HELP,
    ARGS_DURATION_HELP,
)
from oarc_crawlers.config.config import apply_config_file
from oarc_crawlers.core.crawlers.yt_crawler import YTCrawler
from oarc_crawlers.decorators import handle_error, asyncio_run
from oarc_crawlers.utils.const import SUCCESS
from oarc_crawlers.utils.errors import DownloadError
from oarc_crawlers.utils.log import enable_debug_logging
from oarc_crawlers.utils.paths import Paths

@click.group(help=YOUTUBE_HELP)
def yt():
    """Group of YouTube CLI commands for downloading videos, playlists, captions, searching, and extracting live chat."""
    pass

@yt.command(help=YOUTUBE_DOWNLOAD_HELP)
@click.option('--url', required=True, help=ARGS_VIDEO_URL_HELP)
@click.option('--format', default='mp4', help=ARGS_FORMAT_HELP)
@click.option('--resolution', default='highest', help=ARGS_RESOLUTION_HELP)
@click.option('--extract-audio/--no-extract-audio', default=False, help=ARGS_EXTRACT_AUDIO_HELP)
@click.option('--output-path', help=ARGS_OUTPUT_PATH_HELP)
@click.option('--filename', help=ARGS_FILENAME_HELP)
@click.option('--verbose', is_flag=True, help=ARGS_VERBOSE_HELP, callback=enable_debug_logging)
@click.option('--config', help=ARGS_CONFIG_HELP, callback=apply_config_file)
@asyncio_run
@handle_error
async def download(url, format, resolution, extract_audio, output_path, filename, verbose, config):
    """
    Download a YouTube video with specified parameters.

    Args:
        url (str): The YouTube video URL.
        format (str): Desired video format (e.g., 'mp4', 'webm', 'mp3').
        resolution (str): Video resolution ('highest', 'lowest', or specific like '720p').
        extract_audio (bool): Whether to extract audio only.
        output_path (str, optional): Directory to save the downloaded file.
        filename (str, optional): Custom filename for the downloaded video.
        verbose (bool): Show detailed error information if True.
        config (str, optional): Path to configuration file.

    Returns:
        int: SUCCESS if the download is successful.

    Raises:
        DownloadError: If the download fails.
    """
    downloader = YTCrawler()
    result = await downloader.download_video(
        url=url, format=format, resolution=resolution, 
        extract_audio=extract_audio, output_path=output_path,
        filename=filename
    )
    
    if 'error' in result:
        raise DownloadError(f"Error: {result['error']}")
        
    click.secho(f"✓ Downloaded: {result.get('title')}", fg='green')
    click.echo(f"File: {result.get('file_path')}")
    click.echo(f"Size: {result.get('file_size', 0) / (1024*1024):.2f} MB")
    return SUCCESS

@yt.command(help=YOUTUBE_PLAYLIST_HELP)
@click.option('--url', required=True, help=ARGS_PLAYLIST_URL_HELP)
@click.option('--format', default='mp4', help=ARGS_FORMAT_HELP)
@click.option('--max-videos', default=10, type=int, help=ARGS_MAX_VIDEOS_HELP)
@click.option('--output-path', help=ARGS_OUTPUT_PATH_HELP)
@click.option('--verbose', is_flag=True, help=ARGS_VERBOSE_HELP, callback=enable_debug_logging)
@click.option('--config', help=ARGS_CONFIG_HELP, callback=apply_config_file)
@asyncio_run
@handle_error
async def playlist(url, format, max_videos, output_path, verbose, config):
    """
    Download videos from a YouTube playlist.

    Args:
        url (str): The YouTube playlist URL.
        format (str): Desired video format (e.g., 'mp4', 'webm').
        max_videos (int): Maximum number of videos to download.
        output_path (str, optional): Directory to save the downloaded videos.
        verbose (bool): Show detailed error information if True.
        config (str, optional): Path to configuration file.

    Returns:
        int: SUCCESS if all downloads are successful.

    Raises:
        DownloadError: If any video fails to download.
    """
    downloader = YTCrawler()
    
    with click.progressbar(length=max_videos, label=f'Downloading playlist (max {max_videos} videos)') as bar:
        def progress_callback(current, total):
            bar.update(1)
            
        result = await downloader.download_playlist(
            playlist_url=url, format=format, max_videos=max_videos, 
            output_path=output_path
        )
    
    if 'error' in result:
        raise DownloadError(f"Error: {result['error']}")
    
    video_count = len(result.get('videos', []))
    click.secho(f"✓ Downloaded {video_count} videos from playlist: {result.get('title')}", fg='green')
    
    # Show details of each downloaded video
    for i, video in enumerate(result.get('videos', [])):
        if 'error' in video:
            click.secho(f"  {i+1}. Error: {video['error']}", fg='yellow')
        else:
            click.echo(f"  {i+1}. {video.get('title')}")
    
    return SUCCESS

@yt.command(help=YOUTUBE_CAPTIONS_HELP)
@click.option('--url', required=True, help=ARGS_VIDEO_URL_HELP)
@click.option('--languages', default='en', help=ARGS_LANGUAGES_HELP)
@click.option('--verbose', is_flag=True, help=ARGS_VERBOSE_HELP, callback=enable_debug_logging)
@click.option('--config', help=ARGS_CONFIG_HELP, callback=apply_config_file)
@asyncio_run
@handle_error
async def captions(url, languages, verbose, config):
    """
    Extract captions/subtitles from a YouTube video.

    Args:
        url (str): The YouTube video URL.
        languages (str): Comma-separated language codes (e.g., "en,es,fr").
        verbose (bool): Show detailed error information if True.
        config (str, optional): Path to configuration file.

    Returns:
        int: SUCCESS if captions are successfully extracted.

    Raises:
        DownloadError: If extraction fails or no captions are found.
    """
    downloader = YTCrawler()
    
    # Split the languages string into a list
    lang_list = [lang.strip() for lang in languages.split(',')]
    
    result = await downloader.extract_captions(url=url, languages=lang_list)
    
    if 'error' in result:
        raise DownloadError(f"Error: {result['error']}")
    
    caption_langs = list(result.get('captions', {}).keys())
    if not caption_langs:
        click.secho("No captions found for the specified languages", fg='yellow')
        return 0
        
    click.secho(f"✓ Extracted captions for video: {result.get('title')}", fg='green')
    click.echo(f"Found {len(caption_langs)} language(s): {', '.join(caption_langs)}")
    
    for lang, path in result.get('captions', {}).items():
        click.echo(f"  • {lang}: {path}")
    
    return SUCCESS

@yt.command(help=YOUTUBE_SEARCH_HELP)
@click.option('--query', required=True, help=ARGS_QUERY_HELP)
@click.option('--limit', default=10, type=int, help=ARGS_LIMIT_HELP)
@click.option('--verbose', is_flag=True, help=ARGS_VERBOSE_HELP, callback=enable_debug_logging)
@click.option('--config', help=ARGS_CONFIG_HELP, callback=apply_config_file)
@asyncio_run
@handle_error
async def search(query, limit, verbose, config):
    """
    Search for YouTube videos.

    Args:
        query (str): The search query string.
        limit (int): Maximum number of results to return.
        verbose (bool): Show detailed error information if True.
        config (str, optional): Path to configuration file.

    Returns:
        int: SUCCESS if search is successful.

    Raises:
        DownloadError: If the search fails.
    """
    downloader = YTCrawler()
    
    click.echo(f"Searching YouTube for: {query}")
    result = await downloader.search_videos(query=query, limit=limit)
    
    if 'error' in result:
        raise DownloadError(f"Error: {result['error']}")
    
    click.secho(f"✓ Found {result.get('result_count', 0)} videos", fg='green')
    
    # Display search results
    for i, video in enumerate(result.get('results', [])):
        title = video.get('title', 'No title')
        author = video.get('author', 'Unknown')
        length = video.get('length', 0)
        views = video.get('views', 'N/A')
        url = video.get('url', '')
        
        click.echo(f"\n{i+1}. {title}")
        click.echo(f"   Author: {author}")
        click.echo(f"   Duration: {length//60}:{length%60:02d}")
        click.echo(f"   Views: {views}")
        click.echo(f"   URL: {url}")
    
    return SUCCESS

@yt.command(help=YOUTUBE_CHAT_HELP)
@click.option('--video-id', required=True, help=ARGS_VIDEO_ID_HELP)
@click.option('--max-messages', default=1000, type=int, help=ARGS_MAX_MESSAGES_HELP)
@click.option('--duration', type=int, help=ARGS_DURATION_HELP)
@click.option('--verbose', is_flag=True, help=ARGS_VERBOSE_HELP, callback=enable_debug_logging)
@click.option('--config', help=ARGS_CONFIG_HELP, callback=apply_config_file)
@asyncio_run
@handle_error
async def chat(video_id, max_messages, duration, verbose, config):
    """
    Fetch chat messages from a YouTube live stream or premiere.

    Args:
        video_id (str): The YouTube video ID or URL.
        max_messages (int): Maximum number of chat messages to collect.
        duration (int, optional): Duration in seconds to collect messages.
        verbose (bool): Show detailed error information if True.
        config (str, optional): Path to configuration file.

    Returns:
        int: SUCCESS if chat messages are successfully fetched and saved.

    Raises:
        DownloadError: If fetching chat messages fails.
    """
    downloader = YTCrawler()
    
    click.echo(f"Fetching chat for video: {video_id}")
    result = await downloader.fetch_stream_chat(
        video_id=video_id, 
        max_messages=max_messages,
        save_to_file=True,
        duration=duration
    )
    
    if 'error' in result:
        raise DownloadError(f"Error: {result['error']}")
    
    message_count = result.get('message_count', 0)
    click.secho(f"✓ Collected {message_count} chat messages", fg='green')
    
    if 'text_path' in result:
        click.echo(f"Messages saved to: {result['text_path']}")
    
    if 'parquet_path' in result:
        click.echo(f"Data saved to: {result['parquet_path']}")
    
    return SUCCESS