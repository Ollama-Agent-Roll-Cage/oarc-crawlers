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


@click.group()
@click.option('--verbose', is_flag=True, help=ARGS_VERBOSE_HELP, callback=enable_debug_logging)
@click.option('--config', help=ARGS_CONFIG_HELP, callback=apply_config_file)
def yt(verbose, config):
    """Group of YouTube CLI commands for video operations.

    This group provides commands to interact with YouTube content, including:
      • Downloading videos and playlists
      • Extracting captions and subtitles
      • Searching for videos
      • Fetching chat messages from live streams

    Examples:

      Download a video:

        $ oarc-crawlers yt download --url https://www.youtube.com/watch?v=dQw4w9WgXcQ

      Download a playlist:

        $ oarc-crawlers yt playlist --url https://www.youtube.com/playlist?list=PLexample

      Extract captions:

        $ oarc-crawlers yt captions --url https://www.youtube.com/watch?v=dQw4w9WgXcQ
    """
    pass


@yt.command()
@click.option('--url', required=True, help=ARGS_VIDEO_URL_HELP)
@click.option('--video-format', default='mp4', help=ARGS_FORMAT_HELP)
@click.option('--resolution', default='highest', help=ARGS_RESOLUTION_HELP)
@click.option('--extract-audio/--no-extract-audio', default=False, help=ARGS_EXTRACT_AUDIO_HELP)
@click.option('--output-path', help=ARGS_OUTPUT_PATH_HELP)
@click.option('--filename', help=ARGS_FILENAME_HELP)
@asyncio_run
@handle_error
async def download(url, video_format, resolution, extract_audio, output_path, filename):
    """Download a YouTube video with specified parameters.

    Downloads a video from YouTube with customizable format, resolution, and output options.
    Can optionally extract audio only from the video.

    Examples:

        Download a video with default settings:

            $ oarc-crawlers yt download --url https://www.youtube.com/watch?v=dQw4w9WgXcQ

        Download with specific resolution:

            $ oarc-crawlers yt download --url https://www.youtube.com/watch?v=dQw4w9WgXcQ --resolution 720p

        Extract audio only:

            $ oarc-crawlers yt download --url https://www.youtube.com/watch?v=dQw4w9WgXcQ --extract-audio

        Download to specific location with custom filename:

            $ oarc-crawlers yt download --url https://www.youtube.com/watch?v=dQw4w9WgXcQ --output-path /downloads --filename video.mp4
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


@yt.command()
@click.option('--url', required=True, help=ARGS_PLAYLIST_URL_HELP)
@click.option('--format', default='mp4', help=ARGS_FORMAT_HELP)
@click.option('--max-videos', default=10, type=int, help=ARGS_MAX_VIDEOS_HELP)
@click.option('--output-path', help=ARGS_OUTPUT_PATH_HELP)
@asyncio_run
@handle_error
async def playlist(url, format, max_videos, output_path):
    """Download videos from a YouTube playlist.

    Downloads multiple videos from a YouTube playlist up to a specified maximum.
    Shows progress during download and provides a summary of results.

    Examples:

      Download a playlist with default settings (10 videos max):

        $ oarc-crawlers yt playlist --url https://www.youtube.com/playlist?list=PLexample

      Download more videos:

        $ oarc-crawlers yt playlist --url https://www.youtube.com/playlist?list=PLexample --max-videos 20

      Download in specific format:

        $ oarc-crawlers yt playlist --url https://www.youtube.com/playlist?list=PLexample --format webm

      Save to specific directory:

        $ oarc-crawlers yt playlist --url https://www.youtube.com/playlist?list=PLexample --output-path /downloads/playlists
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


@yt.command()
@click.option('--url', required=True, help=ARGS_VIDEO_URL_HELP)
@click.option('--languages', default='en', help=ARGS_LANGUAGES_HELP)
@asyncio_run
@handle_error
async def captions(url, languages):
    """Extract captions/subtitles from a YouTube video for specified languages.

    Extracts available subtitles or closed captions from a YouTube video for the
    specified languages. Supports multiple language extraction by providing a comma-separated list.

    Examples:

      Extract English captions:

        $ oarc-crawlers yt captions --url https://www.youtube.com/watch?v=dQw4w9WgXcQ

      Extract captions in multiple languages:

        $ oarc-crawlers yt captions --url https://www.youtube.com/watch?v=dQw4w9WgXcQ --languages en,es,fr

      Extract with verbose logging:

        $ oarc-crawlers yt captions --url https://www.youtube.com/watch?v=dQw4w9WgXcQ --verbose
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


@yt.command()
@click.option('--query', required=True, help=ARGS_QUERY_HELP)
@click.option('--limit', default=10, type=int, help=ARGS_LIMIT_HELP)
@asyncio_run
@handle_error
async def search(query, limit):
    """Search for YouTube videos based on a query string.

    Performs a search on YouTube and displays the top matching videos up to the
    specified limit. Shows details including title, author, duration, and views.

    Examples:

      Search for videos about Python programming:

        $ oarc-crawlers yt search --query "Python programming"

      Limit search results to 5 videos:

        $ oarc-crawlers yt search --query "machine learning" --limit 5

      Search for exact phrase:

        $ oarc-crawlers yt search --query '"artificial intelligence"'

      Search with verbose logging:

        $ oarc-crawlers yt search --query "data science" --verbose
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


@yt.command()
@click.option('--video-id', required=True, help=ARGS_VIDEO_ID_HELP)
@click.option('--max-messages', default=1000, type=int, help=ARGS_MAX_MESSAGES_HELP)
@click.option('--duration', type=int, help=ARGS_DURATION_HELP)
@asyncio_run
@handle_error
async def chat(video_id, max_messages, duration):
    """Fetch chat messages from a YouTube live stream or premiere.

    Collects chat messages from a YouTube live stream or premiere, with options
    to control the maximum number of messages and duration of collection.

    Examples:

      Collect chat messages from a live stream:

        $ oarc-crawlers yt chat --video-id dQw4w9WgXcQ

      Collect a maximum of 500 messages:

        $ oarc-crawlers yt chat --video-id dQw4w9WgXcQ --max-messages 500

      Collect messages for 5 minutes:

        $ oarc-crawlers yt chat --video-id dQw4w9WgXcQ --duration 300

      Collect with verbose logging:

        $ oarc-crawlers yt chat --video-id dQw4w9WgXcQ --verbose
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