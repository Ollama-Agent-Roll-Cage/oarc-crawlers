import asyncio
import os
from pathlib import Path
from src.youtube_script import YouTubeDownloader

async def youtube_examples():
    """Examples for using the YouTube Downloader module."""
    
    # Initialize the downloader
    data_dir = Path("./data")
    downloader = YouTubeDownloader(data_dir=data_dir)
    
    print("=== YouTube Downloader Examples ===")
    
    # Example 1: Download a single video
    print("\n1. Download a single video")
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Replace with actual video URL
    result = await downloader.download_video(
        url=video_url,
        format="mp4",
        resolution="720p",  # Try specific resolution
        extract_audio=False
    )
    print(f"Video downloaded to: {result.get('file_path')}")
    print(f"Video title: {result.get('title')}")
    print(f"Video duration: {result.get('length')} seconds")
    
    # Example 2: Extract audio from a video
    print("\n2. Extract audio from a video")
    audio_result = await downloader.download_video(
        url=video_url,
        format="mp3",  # Will trigger audio extraction
        extract_audio=True
    )
    print(f"Audio extracted to: {audio_result.get('file_path')}")
    
    # Example 3: Extract video captions/subtitles
    print("\n3. Extract video captions")
    captions = await downloader.extract_captions(
        url=video_url,
        languages=['en', 'es']  # Try to get English and Spanish captions
    )
    print(f"Captions found: {list(captions.get('captions', {}).keys())}")
    
    # Example 4: Download videos from a playlist (limited to 3)
    print("\n4. Download videos from a playlist")
    playlist_url = "https://www.youtube.com/playlist?list=PLzH6n4zXuckquVnQ0KlMDxyXxiSO2DXOQ"  # Replace with actual playlist
    playlist_result = await downloader.download_playlist(
        playlist_url=playlist_url,
        max_videos=3,
        format="mp4"
    )
    print(f"Downloaded {len(playlist_result.get('videos', []))} videos from playlist '{playlist_result.get('title')}'")
    
    # Example 5: Search for videos
    print("\n5. Search for videos on YouTube")
    search_results = await downloader.search_videos(
        query="machine learning tutorial",
        limit=5
    )
    print(f"Found {search_results.get('result_count')} videos")
    
    # Display search results
    for i, video in enumerate(search_results.get('results', [])):
        print(f"  {i+1}. {video.get('title')} by {video.get('author')}")

if __name__ == "__main__":
    asyncio.run(youtube_examples())