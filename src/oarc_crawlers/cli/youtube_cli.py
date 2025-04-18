"""Command-line interface for YouTube crawler."""
import argparse
import asyncio
from pathlib import Path

from ..youtube_script import YouTubeDownloader

async def _download_video(args):
    """Download a YouTube video."""
    downloader = YouTubeDownloader(data_dir=args.output_dir)
    result = await downloader.download_video(
        args.url, 
        format=args.format,
        resolution=args.resolution,
        extract_audio=args.extract_audio
    )
    print(f"Video downloaded: {result['file_path']}")
    return result

async def _download_playlist(args):
    """Download a YouTube playlist."""
    downloader = YouTubeDownloader(data_dir=args.output_dir)
    result = await downloader.download_playlist(
        args.url,
        format=args.format,
        max_videos=args.max_videos
    )
    print(f"Downloaded {len(result['videos'])} videos from playlist '{result['title']}'")
    return result

async def _extract_captions(args):
    """Extract captions from a YouTube video."""
    downloader = YouTubeDownloader(data_dir=args.output_dir)
    result = await downloader.extract_captions(
        args.url,
        languages=args.languages.split(',')
    )
    print(f"Extracted captions for video '{result['title']}'")
    return result

async def _search_videos(args):
    """Search for YouTube videos."""
    downloader = YouTubeDownloader(data_dir=args.output_dir)
    result = await downloader.search_videos(
        args.query,
        limit=args.limit
    )
    print(f"\nFound {result['result_count']} videos for query '{args.query}'\n")
    
    # Format the results nicely
    for i, video in enumerate(result['results'], 1):
        publish_date = video.get('publish_date', 'Unknown date')
        # Truncate title if it's too long
        title = video.get('title', 'No title')
        if len(title) > 70:
            title = title[:67] + "..."
            
        print(f"{i}. {title}")
        print(f"   By: {video.get('author', 'Unknown author')}")
        print(f"   Published: {publish_date}")
        print(f"   URL: {video.get('url')}")
        print()
        
    return result

def main():
    """Main entry point for the YouTube downloader CLI."""
    parser = argparse.ArgumentParser(description="YouTube Downloader")
    parser.add_argument('--output-dir', type=str, default='./data',
                        help="Directory to save downloaded content")
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Download video parser
    video_parser = subparsers.add_parser('download', help='Download a YouTube video')
    video_parser.add_argument('url', help='YouTube video URL')
    video_parser.add_argument('--format', default='mp4', help='Video format (default: mp4)')
    video_parser.add_argument('--resolution', default='highest', help='Video resolution (default: highest)')
    video_parser.add_argument('--extract-audio', action='store_true', help='Extract audio from video')
    
    # Download playlist parser
    playlist_parser = subparsers.add_parser('playlist', help='Download a YouTube playlist')
    playlist_parser.add_argument('url', help='YouTube playlist URL')
    playlist_parser.add_argument('--format', default='mp4', help='Video format (default: mp4)')
    playlist_parser.add_argument('--max-videos', type=int, default=10, help='Maximum videos to download (default: 10)')
    
    # Extract captions parser
    caption_parser = subparsers.add_parser('captions', help='Extract captions from a YouTube video')
    caption_parser.add_argument('url', help='YouTube video URL')
    caption_parser.add_argument('--languages', default='en', help='Comma-separated languages to extract (default: en)')
    
    # Search parser
    search_parser = subparsers.add_parser('search', help='Search for YouTube videos')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--limit', type=int, default=10, help='Maximum search results (default: 10)')
    
    args = parser.parse_args()
    
    if args.command == 'download':
        asyncio.run(_download_video(args))
    elif args.command == 'playlist':
        asyncio.run(_download_playlist(args))
    elif args.command == 'captions':
        asyncio.run(_extract_captions(args))
    elif args.command == 'search':
        asyncio.run(_search_videos(args))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()