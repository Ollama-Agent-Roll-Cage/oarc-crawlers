"""
YouTube command-line interface for OARC Crawlers.

Provides commands for downloading videos, playlists, captions, searching, and extracting live chat from YouTube.
"""
import asyncio

import click

from oarc_crawlers.cli.help_texts import (
    YOUTUBE_HELP,
    YOUTUBE_DOWNLOAD_HELP,
    YOUTUBE_PLAYLIST_HELP,
    YOUTUBE_CAPTIONS_HELP,
    YOUTUBE_SEARCH_HELP,
    YOUTUBE_CHAT_HELP,
)
from oarc_crawlers.core.crawlers.yt_crawler import YTCrawler
from oarc_crawlers.decorators import handle_error
from oarc_crawlers.utils.const import SUCCESS
from oarc_crawlers.utils.errors import DownloadError

@click.group(help=YOUTUBE_HELP)
def youtube():
    """Group of YouTube CLI commands for downloading videos, playlists, captions, searching, and extracting live chat."""
    pass

@youtube.command(help=YOUTUBE_DOWNLOAD_HELP)
@click.option('--url', required=True, help='YouTube video URL')
@click.option('--format', default='mp4', help='Video format (mp4, webm, mp3)')
@click.option('--resolution', default='highest', 
              help='Video resolution ("highest", "lowest", or specific like "720p")')
@click.option('--extract-audio/--no-extract-audio', default=False, 
              help='Extract audio only')
@click.option('--output-path', help='Directory to save the video')
@click.option('--filename', help='Custom filename for the downloaded video')
@click.option('--verbose', is_flag=True, help='Show detailed error information')
@handle_error
def download(url, format, resolution, extract_audio, output_path, filename, verbose):
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

    Returns:
        int: SUCCESS if the download is successful.

    Raises:
        DownloadError: If the download fails.
    """
    downloader = YTCrawler()
    result = asyncio.run(downloader.download_video(
        url=url, format=format, resolution=resolution, 
        extract_audio=extract_audio, output_path=output_path,
        filename=filename
    ))
    
    if 'error' in result:
        raise DownloadError(f"Error: {result['error']}")
        
    click.secho(f"✓ Downloaded: {result.get('title')}", fg='green')
    click.echo(f"File: {result.get('file_path')}")
    click.echo(f"Size: {result.get('file_size', 0) / (1024*1024):.2f} MB")
    return SUCCESS

@youtube.command(help=YOUTUBE_PLAYLIST_HELP)
@click.option('--url', required=True, help='YouTube playlist URL')
@click.option('--format', default='mp4', help='Video format (mp4, webm)')
@click.option('--max-videos', default=10, type=int, help='Maximum number of videos to download')
@click.option('--output-path', help='Directory to save the playlist videos')
@click.option('--verbose', is_flag=True, help='Show detailed error information')
@handle_error
def playlist(url, format, max_videos, output_path, verbose):
    """
    Download videos from a YouTube playlist.

    Args:
        url (str): The YouTube playlist URL.
        format (str): Desired video format (e.g., 'mp4', 'webm').
        max_videos (int): Maximum number of videos to download.
        output_path (str, optional): Directory to save the downloaded videos.
        verbose (bool): Show detailed error information if True.

    Returns:
        int: SUCCESS if all downloads are successful.

    Raises:
        DownloadError: If any video fails to download.
    """
    downloader = YTCrawler()
    
    with click.progressbar(length=max_videos, label=f'Downloading playlist (max {max_videos} videos)') as bar:
        def progress_callback(current, total):
            bar.update(1)
            
        result = asyncio.run(downloader.download_playlist(
            playlist_url=url, format=format, max_videos=max_videos, 
            output_path=output_path
        ))
    
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

@youtube.command(help=YOUTUBE_CAPTIONS_HELP)
@click.option('--url', required=True, help='YouTube video URL')
@click.option('--languages', default='en', help='Comma-separated language codes (e.g. "en,es,fr")')
@click.option('--verbose', is_flag=True, help='Show detailed error information')
@handle_error
def captions(url, languages, verbose):
    """
    Extract captions/subtitles from a YouTube video.

    Args:
        url (str): The YouTube video URL.
        languages (str): Comma-separated language codes (e.g., "en,es,fr").
        verbose (bool): Show detailed error information if True.

    Returns:
        int: SUCCESS if captions are successfully extracted.

    Raises:
        DownloadError: If extraction fails or no captions are found.
    """
    downloader = YTCrawler()
    
    # Split the languages string into a list
    lang_list = [lang.strip() for lang in languages.split(',')]
    
    result = asyncio.run(downloader.extract_captions(url=url, languages=lang_list))
    
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

@youtube.command(help=YOUTUBE_SEARCH_HELP)
@click.option('--query', required=True, help='Search query')
@click.option('--limit', default=10, type=int, help='Maximum number of results')
@click.option('--verbose', is_flag=True, help='Show detailed error information')
@handle_error
def search(query, limit, verbose):
    """
    Search for YouTube videos.

    Args:
        query (str): The search query string.
        limit (int): Maximum number of results to return.
        verbose (bool): Show detailed error information if True.

    Returns:
        int: SUCCESS if search is successful.

    Raises:
        DownloadError: If the search fails.
    """
    downloader = YTCrawler()
    
    click.echo(f"Searching YouTube for: {query}")
    result = asyncio.run(downloader.search_videos(query=query, limit=limit))
    
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

@youtube.command(help=YOUTUBE_CHAT_HELP)
@click.option('--video-id', required=True, help='YouTube video ID or URL')
@click.option('--max-messages', default=1000, type=int, help='Maximum number of messages to collect')
@click.option('--duration', type=int, help='Duration to collect messages in seconds')
@click.option('--verbose', is_flag=True, help='Show detailed error information')
@handle_error
def chat(video_id, max_messages, duration, verbose):
    """
    Fetch chat messages from a YouTube live stream or premiere.

    Args:
        video_id (str): The YouTube video ID or URL.
        max_messages (int): Maximum number of chat messages to collect.
        duration (int, optional): Duration in seconds to collect messages.
        verbose (bool): Show detailed error information if True.

    Returns:
        int: SUCCESS if chat messages are successfully fetched and saved.

    Raises:
        DownloadError: If fetching chat messages fails.
    """
    downloader = YTCrawler()
    
    click.echo(f"Fetching chat for video: {video_id}")
    result = asyncio.run(downloader.fetch_stream_chat(
        video_id=video_id, 
        max_messages=max_messages,
        save_to_file=True,
        duration=duration
    ))
    
    if 'error' in result:
        raise DownloadError(f"Error: {result['error']}")
    
    message_count = result.get('message_count', 0)
    click.secho(f"✓ Collected {message_count} chat messages", fg='green')
    
    if 'text_path' in result:
        click.echo(f"Messages saved to: {result['text_path']}")
    
    if 'parquet_path' in result:
        click.echo(f"Data saved to: {result['parquet_path']}")
    
    return SUCCESS