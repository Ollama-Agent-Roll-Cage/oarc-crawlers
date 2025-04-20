"""YouTube CLI command module for OARC Crawlers.

Provides commands for downloading YouTube videos and playlists, extracting captions,
searching for videos, and fetching live chat messages from streams or premieres.
"""

import click

from oarc_log import enable_debug_logging
from oarc_utils.decorators import asyncio_run, handle_error
from oarc_utils.errors import OARCError

from oarc_crawlers.config.config import apply_config_file
from oarc_crawlers.core.crawlers.yt_crawler import YTCrawler
from oarc_crawlers.utils.const import SUCCESS, ERROR
from oarc_crawlers.cli.help_texts import (
    YOUTUBE_GROUP_HELP,
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


@click.group(help=YOUTUBE_GROUP_HELP)
@click.option('--verbose', is_flag=True, help=ARGS_VERBOSE_HELP, callback=enable_debug_logging)
@click.option('--config', help=ARGS_CONFIG_HELP, callback=apply_config_file)
def yt(verbose, config):
    """Group of YouTube CLI commands for downloading videos, extracting captions, searching, and fetching chat."""
    pass


@yt.command(help=YOUTUBE_DOWNLOAD_HELP)
@click.option('--url', required=True, help=ARGS_VIDEO_URL_HELP)
@click.option('--video-format', default='mp4', help=ARGS_FORMAT_HELP)
@click.option('--resolution', default='highest', help=ARGS_RESOLUTION_HELP)
@click.option('--extract-audio/--no-extract-audio', default=False, help=ARGS_EXTRACT_AUDIO_HELP)
@click.option('--output-path', help=ARGS_OUTPUT_PATH_HELP)
@click.option('--filename', help=ARGS_FILENAME_HELP)
@asyncio_run
@handle_error
async def download(url, video_format, resolution, extract_audio, output_path, filename):
    """
    Download a YouTube video with specified parameters.
    Args:
        url (str): The URL of the YouTube video to download.
        video_format (str): The desired format of the downloaded file (e.g., 'mp4', 'mp3').
        resolution (str): The desired video resolution (e.g., '720p', '1080p'). Ignored if extracting audio.
        extract_audio (bool): Whether to extract audio only from the video.
        output_path (str): The directory where the downloaded file will be saved.
        filename (str): The name to use for the saved file.
    Raises:
        DownloadError: If an error occurs during the download process.
    Returns:
        int: SUCCESS constant indicating the operation completed successfully.
    """
    crawler = YTCrawler()
    result = await crawler.download_video(
        url=url, video_format=video_format, resolution=resolution, 
        extract_audio=extract_audio, output_path=output_path,
        filename=filename
    )
    
    if 'error' in result:
        raise OARCError(f"Error: {result['error']}")
        
    click.secho(f"✓ Downloaded: {result.get('title')}", fg='green')
    click.echo(f"File: {result.get('file_path')}")
    click.echo(f"Size: {result.get('file_size', 0) / (1024*1024):.2f} MB")
    return SUCCESS


@yt.command(help=YOUTUBE_PLAYLIST_HELP)
@click.option('--url', required=True, help=ARGS_PLAYLIST_URL_HELP)
@click.option('--format', default='mp4', help=ARGS_FORMAT_HELP)
@click.option('--max-videos', default=10, type=int, help=ARGS_MAX_VIDEOS_HELP)
@click.option('--output-path', help=ARGS_OUTPUT_PATH_HELP)
@asyncio_run
@handle_error
async def playlist(url, format, max_videos, output_path):
    """
    Download videos from a YouTube playlist.
    Args:
        url (str): The URL of the YouTube playlist to download.
        format (str): The desired video format (e.g., 'mp4', 'webm').
        max_videos (int): The maximum number of videos to download from the playlist.
        output_path (str): The directory path where downloaded videos will be saved.
    Raises:
        DownloadError: If an error occurs during the download process.
    Returns:
        int: SUCCESS constant indicating successful completion.
    Side Effects:
        - Displays a progress bar and status messages in the CLI.
        - Prints details of each downloaded video, including errors if any.
    """
    crawler = YTCrawler()
    
    with click.progressbar(length=max_videos, label=f'Downloading playlist (max {max_videos} videos)') as bar:
        def progress_callback(current, total):
            bar.update(1)
            
        result = await crawler.download_playlist(
            playlist_url=url, format=format, max_videos=max_videos, 
            output_path=output_path
        )
    
    if ERROR in result:
        raise OARCError(f"Error: {result['error']}")
    
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
@asyncio_run
@handle_error
async def captions(url, languages):
    """
    Extract captions/subtitles from a YouTube video for specified languages.
    Args:
        url (str): The URL of the YouTube video to extract captions from.
        languages (str): Comma-separated list of language codes (e.g., 'en,es,fr') for which to extract captions.
    Raises:
        CrawlError: If an error occurs during caption extraction.
    Returns:
        int: SUCCESS (typically 0) if captions are extracted successfully, otherwise 0 if no captions are found.
    """
    crawler = YTCrawler()
    
    # Split the languages string into a list
    lang_list = [lang.strip() for lang in languages.split(',')]
    
    result = await crawler.extract_captions(url=url, languages=lang_list)
    
    if ERROR in result:
        raise OARCError(f"Error: {result['error']}")
    
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
@asyncio_run
@handle_error
async def search(query, limit):
    """
    Search for YouTube videos based on a query string.
    Args:
        query (str): The search query to use for finding YouTube videos.
        limit (int): The maximum number of videos to retrieve.
    Returns:
        int: SUCCESS constant indicating the operation completed successfully.
    Raises:
        CrawlError: If an error occurs during the search process.
    Side Effects:
        Prints search progress and results to the console using click.
    """
    crawler = YTCrawler()
    
    click.echo(f"Searching YouTube for: {query}")
    result = await crawler.search_videos(query=query, limit=limit)
    
    if ERROR in result:
        raise OARCError(f"Error: {result['error']}")
    
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
@asyncio_run
@handle_error
async def chat(video_id, max_messages, duration):
    """
    Fetch chat messages from a YouTube live stream or premiere.
    Args:
        video_id (str): The YouTube video ID to fetch chat messages from.
        max_messages (int): The maximum number of chat messages to retrieve.
        duration (int): The duration (in seconds) to fetch chat messages for.
    Returns:
        int: SUCCESS constant indicating successful completion.
    Raises:
        CrawlError: If an error occurs during chat message retrieval.
    Side Effects:
        - Saves chat messages to a text file and/or Parquet file if specified.
        - Outputs status and file paths to the console.
    """
    crawler = YTCrawler()
    
    click.echo(f"Fetching chat for video: {video_id}")
    result = await crawler.fetch_stream_chat(
        video_id=video_id, 
        max_messages=max_messages,
        save_to_file=True,
        duration=duration
    )
    
    if ERROR in result:
        raise OARCError(f"Error: {result['error']}")
    
    msg_count = result.get('message_count', 0)
    click.secho(f"✓ Collected {msg_count} chat messages", fg='green')
    
    if 'text_path' in result:
        click.echo(f"Messages saved to: {result['text_path']}")
    
    if 'parquet_path' in result:
        click.echo(f"Data saved to: {result['parquet_path']}")
    
    return SUCCESS