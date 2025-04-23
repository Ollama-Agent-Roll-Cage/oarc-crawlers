# OARC-Crawlers API Reference

This document provides detailed API reference for all components in the OARC-Crawlers system.

*Note: The `core`, `utils`, and `config` modules may contain additional APIs not yet documented here.*

## Table of Contents
- [1. Parquet Storage API](#1-parquet-storage-api)
    - [`save_to_parquet(data: Union[Dict, List[Dict], pd.DataFrame], file_path: str) -> bool`](#save_to_parquetdata-file_path)
    - [`load_from_parquet(file_path: str) -> Optional[pd.DataFrame]`](#load_from_parquetfile_path)
    - [`append_to_parquet(data: Union[Dict, List[Dict], pd.DataFrame], file_path: str) -> bool`](#append_to_parquetdata-file_path)
- [2. YouTube Downloader API](#2-youtube-downloader-api)
    - [`__init__(data_dir: Optional[str]=None)`](#__init__data_dirnone)
    - [`async download_video(...)`](#download_videourl-formatmp4-resolutionhighest-output_pathnone-filenamenone-extract_audiofalse)
    - [`async download_playlist(...)`](#download_playlistplaylist_url-formatmp4-max_videos10-output_pathnone)
    - [`async extract_captions(...)`](#extract_captionsurl-languagesen)
    - [`async search_videos(...)`](#search_videosquery-limit10)
- [3. GitHub Crawler API](#3-github-crawler-api)
    - [`__init__(data_dir: Optional[str]=None, token: Optional[str]=None)`](#__init__data_dirnone-tokennone)
    - [`@staticmethod extract_repo_info_from_url(url: str) -> Tuple[str, str, str]`](#extract_repo_info_from_urlurl)
    - [`async clone_repo(repo_url: str, temp_dir: Optional[str]=None) -> Path`](#clone_reporepo_url-temp_dirnone)
    - [`async process_repo_to_dataframe(...)`](#process_repo_to_datareframerepo_path-max_file_size_kb500)
    - [`async clone_and_store_repo(repo_url: str, branch: Optional[str]=None) -> Dict`](#clone_and_store_reporepo_url-branchnone)
    - [`async get_repo_summary(repo_url: str) -> str`](#get_repo_summaryrepo_url)
    - [`async find_similar_code(...)`](#find_similar_coderepo_info-code_snippet-top_n5)
    - [`async query_repo_content(...)`](#query_repo_contentrepo_url-query)
- [4. DuckDuckGo Searcher API](#4-duckduckgo-searcher-api)
    - [`__init__(data_dir: Optional[str]=None)`](#__init__data_dirnone-2)
    - [`async text_search(...)`](#text_searchsearch_query-max_results5)
    - [`async image_search(...)`](#image_searchsearch_query-max_results10)
    - [`async news_search(...)`](#news_searchsearch_query-max_results20)
- [5. BeautifulSoup Web Crawler API](#5-beautifulsoup-web-crawler-api)
    - [`__init__(data_dir: Optional[str]=None)`](#__init__data_dirnone-3)
    - [`async fetch_url_content(url: str) -> Optional[str]`](#fetch_url_contenturl)
    - [`@staticmethod extract_text_from_html(html: str) -> str`](#extract_text_from_htmlhtml)
    - [`@staticmethod extract_pypi_content(...)`](#extract_pypi_contenthtml-package_name)
    - [`@staticmethod extract_documentation_content(...)`](#extract_documentation_contenthtml-url)
    - [`@staticmethod format_pypi_info(package_data: Dict) -> str`](#format_pypi_infopackage_data)
    - [`@staticmethod format_documentation(doc_data: Dict) -> str`](#format_documentationdoc_data)
    - [`async crawl_documentation_site(url: str) -> str`](#crawl_documentation_siteurl)
- [6. ArXiv Crawler API](#6-arxiv-crawler-api)
    - [`__init__(data_dir: Optional[str]=None)`](#__init__data_dirnone-4)
    - [`@staticmethod extract_arxiv_id(arxiv_input: str) -> str`](#extract_arxiv_idarxiv_input)
    - [`async fetch_paper_info(arxiv_id: str) -> Dict`](#fetch_paper_infoarxiv_id)
    - [`async download_source(arxiv_id: str) -> Dict`](#download_sourcearxiv_id)
    - [`async fetch_paper_with_latex(arxiv_id: str) -> Dict`](#fetch_paper_with_latexxarxiv_id)
    - [`@staticmethod async format_paper_for_learning(paper_info: Dict) -> str`](#format_paper_for_learningpaper_info)
    - [`async batch_fetch_papers(...)`](#batch_fetch_papersarxiv_ids-extract_keywordsfalse-extract_referencesfalse)
    - [`async search(query: str, limit: int=5) -> Dict`](#searchquery-limit5)
    - [`async extract_references(...)`](#extract_referencesarxiv_id_or_source_info)
    - [`async extract_keywords(...)`](#extract_keywordsarxiv_id_or_paper_info-max_keywords10)
    - [`async fetch_category_papers(...)`](#fetch_category_paperscategory-max_results100-sort_bysubmitteddate)
    - [`async extract_math_equations(...)`](#extract_math_equationsarxiv_id_or_source_info)
    - [`async generate_citation_network(...)`](#generate_citation_networkseed_papers-max_depth1)
- [7. Model Context Protocol (MCP) Integration](#7-model-context-protocol-mcp-integration)
    - [Server Configuration](#server-configuration)
    - [Installation](#installation)
    - [Available Tools](#available-tools)
    - [Error Handling](#error-handling)
    - [VS Code Integration](#vs-code-integration)
    - [Programmatic Usage](#programmatic-usage)
    - [MCP Server API](#mcp-server-api)

## 1. Parquet Storage API

*Assumed Location: `oarc_crawlers.utils.parquet_storage` (or similar)*

### `save_to_parquet(data: Union[Dict, List[Dict], pd.DataFrame], file_path: str) -> bool`
Saves data to a Parquet file.

**Parameters:**
- `data`: Dictionary, list of dictionaries, or Pandas DataFrame to save.
- `file_path`: Path where the Parquet file will be saved.

**Returns:**
- `bool`: True if the save operation was successful, False otherwise.

**Error Handling:**
- Raises `TypeError` if the input `data` format is not supported (not Dict, List[Dict], or DataFrame).
- Raises `IOError` or `PermissionError` if the directory cannot be created or the file cannot be written.

**Example:**
```python
# Assuming ParquetStorage is imported
data = {'name': 'Model XYZ', 'accuracy': 0.95, 'parameters': 10000000}
try:
    success = ParquetStorage.save_to_parquet(data, 'model_metrics.parquet')
    if success:
        print("Data saved successfully.")
except (TypeError, IOError, PermissionError) as e:
    print(f"Error saving data: {e}")
```

**Implementation Notes:**
- Automatically converts dictionaries and lists of dictionaries into Pandas DataFrames before saving.
- Ensures parent directories for `file_path` exist, creating them if necessary.
- Utilizes the `pyarrow` library as the backend for efficient Parquet serialization.

### `load_from_parquet(file_path: str) -> Optional[pd.DataFrame]`
Loads data from a Parquet file into a Pandas DataFrame.

**Parameters:**
- `file_path`: Path to the Parquet file to load.

**Returns:**
- `Optional[pd.DataFrame]`: A Pandas DataFrame containing the loaded data, or `None` if the file doesn't exist, is corrupted, or cannot be read.

**Error Handling:**
- Returns `None` and logs an error if the file specified by `file_path` does not exist or cannot be read (e.g., due to permissions or corruption). It avoids raising exceptions directly to allow for graceful handling in calling code.

**Example:**
```python
# Assuming ParquetStorage is imported
df = ParquetStorage.load_from_parquet('model_metrics.parquet')
if df is not None:
    print(f"Loaded {len(df)} records.")
    print(f"Model name: {df['name'].iloc[0]}, Accuracy: {df['accuracy'].iloc[0]}")
else:
    print("Failed to load data from Parquet file.")
```

### `append_to_parquet(data: Union[Dict, List[Dict], pd.DataFrame], file_path: str) -> bool`
Appends data to an existing Parquet file. If the file does not exist, it creates a new one.

**Parameters:**
- `data`: Dictionary, list of dictionaries, or Pandas DataFrame to append.
- `file_path`: Path to the Parquet file.

**Returns:**
- `bool`: True if the append operation was successful, False otherwise.

**Error Handling:**
- Raises `TypeError` if the input `data` format is not supported.
- Creates a new file if `file_path` does not exist, behaving like `save_to_parquet`.
- Raises `IOError` or `PermissionError` if the file cannot be read or written.

**Example:**
```python
# Assuming ParquetStorage is imported
new_data = {'name': 'Model ABC', 'accuracy': 0.97, 'parameters': 15000000}
try:
    success = ParquetStorage.append_to_parquet(new_data, 'model_metrics.parquet')
    if success:
        print("Data appended successfully.")
except (TypeError, IOError, PermissionError) as e:
    print(f"Error appending data: {e}")

```

**Implementation Notes:**
- Reads the existing Parquet file (if it exists).
- Converts the input `data` to a DataFrame.
- Concatenates the existing DataFrame with the new DataFrame.
- Writes the combined DataFrame back to the Parquet file, overwriting the original.
- Handles potential schema mismatches between the existing data and the new data by aligning columns; missing columns in either DataFrame will be filled with null values.

## 2. YouTube Downloader API

*Assumed Location: `oarc_crawlers.yt_crawler`*

### `__init__(data_dir: Optional[str]=None)`
Initializes the YouTube Downloader instance.

**Parameters:**
- `data_dir` (`Optional[str]`, default=`None`): The base directory where downloaded videos, metadata, and captions should be stored. If `None`, a default location might be used (e.g., within the user's data directory).

**Example:**
```python
# Assuming YouTubeDownloader is imported
downloader = YouTubeDownloader(data_dir='./youtube_output')
```

### `async download_video(url: str, format: str="mp4", resolution: str="highest", output_path: Optional[str]=None, filename: Optional[str]=None, extract_audio: bool=False) -> Dict`
Downloads a single YouTube video based on the provided URL and options.

**Parameters:**
- `url` (`str`): The URL of the YouTube video to download.
- `format` (`str`, default=`"mp4"`): The desired video container format (e.g., "mp4", "webm"). If `extract_audio` is True, this might influence the audio format (e.g., "mp3", "m4a").
- `resolution` (`str`, default=`"highest"`): The desired video resolution. Can be specific (e.g., "1080p", "720p") or relative ("highest", "lowest").
- `output_path` (`Optional[str]`, default=`None`): A specific directory to save this video. If `None`, it defaults to a subdirectory within the `data_dir` provided during initialization.
- `filename` (`Optional[str]`, default=`None`): A custom filename (without extension) for the downloaded file. If `None`, a filename is generated based on the video title or ID.
- `extract_audio` (`bool`, default=`False`): If True, only the audio track will be downloaded and saved (potentially in a format like mp3 or m4a).

**Returns:**
- `Dict`: A dictionary containing information about the download operation, including:
    - `file_path` (`str`): The full path to the downloaded file (video or audio).
    - `metadata` (`Dict`): Extracted metadata about the video (title, author, duration, etc.).
    - `status` (`str`): "success" or "failed".
    - `error` (`Optional[str]`): An error message if the download failed.

**Error Handling:**
- Raises `ConnectionError` if the YouTube URL is invalid or unreachable.
- Raises `ValueError` if the requested `format` or `resolution` is unavailable for the video.
- Returns a dictionary with `status: "failed"` and an `error` message for download failures (e.g., network issues during download, filesystem errors).

**Example:**
```python
# Assuming downloader is an initialized YouTubeDownloader instance
async def download_hd_video():
    result = await downloader.download_video(
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        resolution="1080p",
        output_path="./videos",
        filename="my_video"
    )
    if result['status'] == 'failed':
        print(f"Download failed: {result['error']}")
    else:
        print(f"Downloaded to: {result['file_path']}")
        # Metadata is also saved to a corresponding Parquet file
    return result
```

**Implementation Notes:**
- Uses the `pytube` library (or a similar alternative) for interacting with YouTube.
- Automatically creates the `output_path` directory if it doesn't exist.
- Saves extracted video metadata (title, author, duration, views, etc.) to a separate Parquet file alongside the downloaded video/audio file, using `ParquetStorage`.

### `async download_playlist(playlist_url: str, format: str="mp4", max_videos: int=10, output_path: Optional[str]=None) -> Dict`
Downloads multiple videos from a YouTube playlist.

**Parameters:**
- `playlist_url` (`str`): The URL of the YouTube playlist.
- `format` (`str`, default=`"mp4"`): The desired video format for all videos in the playlist.
- `max_videos` (`int`, default=`10`): The maximum number of videos to download from the playlist. Downloads typically start from the beginning of the playlist.
- `output_path` (`Optional[str]`, default=`None`): A specific directory to save the playlist videos. If `None`, defaults to a subdirectory within `data_dir`, often named after the playlist title or ID.

**Returns:**
- `Dict`: A summary dictionary of the playlist download operation, including:
    - `playlist_title` (`str`): The title of the playlist.
    - `total_videos_in_playlist` (`int`): Total number of videos available in the playlist.
    - `requested_videos` (`int`): Number of videos requested (`max_videos`).
    - `success_count` (`int`): Number of videos successfully downloaded.
    - `failed_count` (`int`): Number of videos that failed to download.
    - `results` (`List[Dict]`): A list containing the result dictionaries for each individual video download attempt (similar to the return value of `download_video`).
    - `metadata_path` (`str`): Path to the Parquet file containing playlist metadata.

**Error Handling:**
- Raises `ConnectionError` if the `playlist_url` is invalid or unreachable.
- Individual video download errors are handled within the loop: failed videos are skipped, and the process continues with the next video.
- Detailed errors for each failed video are included in the `results` list within the returned dictionary.

**Example:**
```python
# Assuming downloader is an initialized YouTubeDownloader instance
async def download_playlist_example():
    result = await downloader.download_playlist(
        playlist_url="https://www.youtube.com/playlist?list=PLQVvvaa0QuDdttJXlLtAJxJetJcqmqlQq",
        max_videos=5,
        output_path="./python_tutorials"
    )
    print(f"Playlist: {result['playlist_title']}")
    print(f"Successfully downloaded {result['success_count']} of {result['requested_videos']} requested videos.")
    if result['failed_count'] > 0:
        print(f"Failed to download {result['failed_count']} videos.")
        # Optionally iterate through result['results'] for details on failures
    return result
```

**Implementation Notes:**
- Uses `pytube.Playlist` (or similar) to fetch playlist information and video URLs.
- Processes videos sequentially or with limited concurrency to avoid potential rate limiting by YouTube.
- Creates a dedicated subdirectory for the playlist within the specified `output_path` or default `data_dir`.
- Saves overall playlist metadata (title, author, total video count) and individual video metadata to Parquet files using `ParquetStorage`.

### `async extract_captions(url: str, languages: List[str]=['en']) -> Dict`
Extracts available captions (subtitles) for a given YouTube video.

**Parameters:**
- `url` (`str`): The URL of the YouTube video.
- `languages` (`List[str]`, default=`['en']`): A list of preferred language codes (e.g., 'en', 'es', 'fr', 'de') for captions. The function will attempt to fetch captions for these languages if available.

**Returns:**
- `Dict`: A dictionary containing the extracted captions and metadata:
    - `video_url` (`str`): The input video URL.
    - `available_languages` (`List[str]`): List of all language codes for which captions are available.
    - `captions` (`Dict[str, str]`): A dictionary where keys are the language codes of the successfully extracted captions (from the requested `languages` list) and values are the caption text content.
    - `srt_files` (`Dict[str, str]`): A dictionary mapping language codes to the file paths where the corresponding SRT caption files were saved.
    - `parquet_path` (`str`): Path to the Parquet file where caption data is stored.

**Error Handling:**
- Returns a dictionary with an empty `captions` dict if the video has no captions or if none of the requested `languages` are available.
- Silently skips requested languages for which caption tracks are not found.
- Handles errors during the fetching process gracefully.

**Example:**
```python
# Assuming downloader is an initialized YouTubeDownloader instance
async def get_multilingual_captions():
    result = await downloader.extract_captions(
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        languages=['en', 'es', 'fr', 'de']
    )
    if not result['captions']:
        print(f"No captions found for requested languages. Available: {result['available_languages']}")
    else:
        print(f"Found captions in languages: {list(result['captions'].keys())}")
        # Access English captions: result['captions'].get('en')
        # SRT file path: result['srt_files'].get('en')
    return result
```

**Implementation Notes:**
- Uses `pytube`'s caption capabilities.
- Saves extracted captions in both raw SRT format (to a file) and as processed text content.
- Stores the caption data (language, text, potentially timestamps) in a Parquet file using `ParquetStorage` for easier analysis.
- The text format typically concatenates caption lines, possibly removing timestamps.

### `async search_videos(query: str, limit: int=10) -> Dict`
Performs a search on YouTube using the provided query string.

**Parameters:**
- `query` (`str`): The search term or phrase.
- `limit` (`int`, default=`10`): The maximum number of search results to retrieve.

**Returns:**
- `Dict`: A dictionary containing the search results:
    - `query` (`str`): The original search query.
    - `results` (`List[Dict]`): A list of dictionaries, each representing a video found. Each video dictionary includes keys like `title`, `url`, `channel`, `views`, `duration`, `publish_date`, `description`.
    - `status` (`str`): "success" or "failed".
    - `error` (`Optional[str]`): An error message if the search failed.
    - `parquet_path` (`str`): Path to the Parquet file where search results are stored.

**Error Handling:**
- Returns a dictionary with `status: "failed"` and an `error` message if the search API call fails (e.g., network error, API quota exceeded).
- Handles potential errors from the underlying search library gracefully.

**Example:**
```python
# Assuming downloader is an initialized YouTubeDownloader instance
async def search_educational_videos():
    results_data = await downloader.search_videos(
        query="python asynchronous programming tutorial",
        limit=15
    )
    if results_data['status'] == 'failed':
        print(f"Search failed: {results_data['error']}")
    else:
        print(f"Found {len(results_data['results'])} videos for query: '{results_data['query']}'")
        for video in results_data['results']:
            print(f"- {video['title']} by {video['channel']} ({video['views']} views)")
        # Results are also saved to results_data['parquet_path']
    return results_data
```

**Implementation Notes:**
- May use the official YouTube Data API (requires API key setup and manages quotas) or libraries like `youtube-search-python` that might scrape results (potentially less reliable or subject to breaking changes).
- Filters results to exclude irrelevant content like channels or playlists if only videos are desired.
- Extracts key metadata for each video result.
- Stores the structured search results in a Parquet file using `ParquetStorage`.

## 3. GitHub Crawler API

### `__init__(data_dir: Optional[str]=None, token: Optional[str]=None)`
Initializes the GitHub Crawler.

**Parameters:**
- `data_dir`: Directory to store data (optional)
- `token`: GitHub API token (optional, for higher rate limits)

**Example:**
```python
crawler = GHCrawler(data_dir='./github_data')
```

### `@staticmethod extract_repo_info_from_url(url: str) -> Tuple[str, str, str]`
Extracts repository owner, name, and branch from GitHub URL.

**Parameters:**
- `url`: GitHub repository URL

**Returns:**
- `tuple`: Repository owner, name, and branch

**Error Handling:**
- Raises `ValueError` if URL format is invalid
- Returns default branch as "main" if not specified in URL

**Example:**
```python
owner, repo_name, branch = GHCrawler.extract_repo_info_from_url(
    "https://github.com/pytorch/pytorch/tree/master"
)
print(f"Owner: {owner}, Repo: {repo_name}, Branch: {branch}")
```

### `async clone_repo(repo_url: str, temp_dir: Optional[str]=None) -> Path`
Clones a GitHub repository.

**Parameters:**
- `repo_url`: GitHub repository URL
- `temp_dir`: Temporary directory path (optional)

**Returns:**
- `Path`: Path to the cloned repository

**Error Handling:**
- Raises `GitCommandError` if cloning fails
- Raises `PermissionError` if temp directory cannot be created

**Example:**
```python
async def clone_example():
    repo_path = await crawler.clone_repo(
        repo_url="https://github.com/pytorch/pytorch",
        temp_dir="./temp_repos"
    )
    print(f"Repository cloned to {repo_path}")
    return repo_path
```

**Implementation Notes:**
- Uses GitPython for repository operations
- Creates a temporary directory if none specified
- Cleans up temporary files automatically after processing

### `async process_repo_to_dataframe(repo_path: str, max_file_size_kb: int=500) -> pd.DataFrame`
Processes repository files and converts to DataFrame.

**Parameters:**
- `repo_path`: Path to cloned repository
- `max_file_size_kb`: Maximum file size in KB to process

**Returns:**
- `DataFrame`: DataFrame containing file information

**Error Handling:**
- Skips binary files larger than max_file_size_kb
- Skips files that cannot be read or decoded
- Logs errors for problem files instead of failing

**Example:**
```python
async def process_repo_example():
    repo_path = await crawler.clone_repo("https://github.com/pytorch/pytorch")
    df = await crawler.process_repo_to_dataframe(
        repo_path=repo_path,
        max_file_size_kb=1000
    )
    # Analyze file types in the repository
    print(df['language'].value_counts())
    return df
```

**Implementation Notes:**
- Detects file type and language automatically
- Extracts metadata like file size, line count, and path
- Skips `.git` directories during processing

### `async clone_and_store_repo(repo_url: str, branch: Optional[str]=None) -> Dict`
Clones a GitHub repository (using Git if available, else API) and stores its data in Parquet format.

**Parameters:**
- `repo_url`: GitHub repository URL
- `branch`: Branch to use (optional)

**Returns:**
- `Dict`: Metadata including `"data_path"` (Parquet file), `"owner"`, `"repo"`, `"branch"`, `"num_files"`, `"size_kb"`, `"method"` ("git" or "api"), etc.

**Error Handling:**
- Raises exceptions for network, authentication, or data extraction errors.

**Example:**
```python
async def store_repo_example():
    result = await crawler.clone_and_store_repo("https://github.com/pytorch/pytorch")
    print(f"Repository data stored at {result['data_path']}")
```

### `async get_repo_summary(repo_url: str) -> str`
Gets a summary of the repository (Markdown).

**Parameters:**
- `repo_url`: GitHub repository URL

**Returns:**
- `str`: Repository summary formatted as markdown

**Error Handling:**
- Returns error message if repository cannot be processed

**Example:**
```python
async def summary_example():
    summary = await crawler.get_repo_summary("https://github.com/pytorch/pytorch")
    print(summary)
```

### `async find_similar_code(repo_info: Union[str, Tuple[str, str]], code_snippet: str, top_n: int=5) -> List[Dict]`
Finds similar code in the repository.

**Parameters:**
- `repo_info`: Repository URL or (owner, repo) tuple
- `code_snippet`: Code snippet to find similar code for
- `top_n`: Maximum number of results to return

**Returns:**
- `List[Dict]`: Each dict contains `"file_path"`, `"language"`, `"similarity"`, `"content"`, `"line_start"`

**Error Handling:**
- Returns empty list if no similar code found

**Example:**
```python
async def find_similar_code_example():
    code = "def calculate_mean(values):\n    return sum(values) / len(values)"
    similar = await crawler.find_similar_code(
        repo_info="https://github.com/pytorch/pytorch",
        code_snippet=code,
        top_n=3
    )
    for match in similar:
        print(match)
```

### `async query_repo_content(repo_url: str, query: str) -> str`
Queries repository content using natural language.

**Parameters:**
- `repo_url`: GitHub repository URL
- `query`: Natural language query about the repository

**Returns:**
- `str`: Query result formatted as markdown

**Error Handling:**
- Returns explanation if query cannot be processed
- Handles repository access errors

**Example:**
```python
async def query_repo_example():
    result = await crawler.query_repo_content(
        repo_url="https://github.com/pytorch/pytorch",
        query="Find all files related to tensor operations"
    )
    print(result)
    return result
```

**Implementation Notes:**
- Performs semantic search on repository content
- Understands natural language queries
- Returns relevant file snippets and explanations
- Formats response as organized markdown document

## 4. DuckDuckGo Searcher API

### `__init__(data_dir: Optional[str]=None)`
Initializes the DuckDuckGo Searcher.

**Parameters:**
- `data_dir`: Directory to store data (optional)

**Example:**
```python
searcher = DDGCrawler(data_dir='./search_data')
```

### `async text_search(search_query: str, max_results: int=5) -> str`
Performs a text search using DuckDuckGo.

**Parameters:**
- `search_query`: Query to search for
- `max_results`: Maximum number of results to return

**Returns:**
- `str`: Markdown-formatted search results

**Error Handling:**
- Raises `NetworkError` or `DataExtractionError` on failure (should be caught by user)
- Returns markdown string with "No results found." if no results

**Example:**
```python
async def text_search_example():
    try:
        results = await searcher.text_search(
            search_query="python asynchronous programming",
            max_results=10
        )
        print(results)
    except Exception as e:
        print(f"Error: {e}")
```

**Implementation Notes:**
- Results are also saved to Parquet files in the configured data directory.

### `async image_search(search_query: str, max_results: int=10) -> str`
Performs an image search using DuckDuckGo.

**Parameters:**
- `search_query`: Query to search for images
- `max_results`: Maximum number of results to return

**Returns:**
- `str`: Markdown-formatted image search results

**Error Handling:**
- Raises `NetworkError` or `DataExtractionError` on failure

**Example:**
```python
async def image_search_example():
    try:
        results = await searcher.image_search(
            search_query="neural network visualization",
            max_results=15
        )
        print(results)
    except Exception as e:
        print(f"Error: {e}")
```

### `async news_search(search_query: str, max_results: int=20) -> str`
Performs a news search using DuckDuckGo.

**Parameters:**
- `search_query`: Query to search for news
- `max_results`: Maximum number of results to return

**Returns:**
- `str`: Markdown-formatted news search results

**Error Handling:**
- Raises `NetworkError` or `DataExtractionError` on failure

**Example:**
```python
async def news_search_example():
    try:
        results = await searcher.news_search(
            search_query="artificial intelligence breakthroughs",
            max_results=12
        )
        print(results)
    except Exception as e:
        print(f"Error: {e}")
```

**Implementation Notes:**
- All search methods save results to Parquet files for later analysis.
- All methods return markdown-formatted strings for direct printing.

## 5. BeautifulSoup Web Crawler API

### `__init__(data_dir: Optional[str]=None)`
Initializes the Web Crawler.

**Parameters:**
- `data_dir`: Directory to store data (optional)

**Example:**
```python
crawler = BSWebCrawler(data_dir='./web_data')
```

### `async fetch_url_content(url: str) -> Optional[str]`
Fetches content from a URL.

**Parameters:**
- `url`: The URL to fetch content from

**Returns:**
- `str`: HTML content of the page or None if failed

**Error Handling:**
- Returns None if URL is invalid or unreachable
- Handles connection timeouts and HTTP errors
- Logs detailed error information

**Example:**
```python
async def fetch_example():
    html = await crawler.fetch_url_content(
        "https://www.python.org/about/"
    )
    if html:
        print(f"Successfully fetched content ({len(html)} bytes)")
    else:
        print("Failed to fetch content")
    return html
```

**Implementation Notes:**
- Uses aiohttp for asynchronous requests
- Sets appropriate user-agent to avoid being blocked
- Handles redirects automatically
- Applies timeout for unresponsive servers

### `@staticmethod extract_text_from_html(html: str) -> str`
Extracts main text content from HTML using BeautifulSoup.

**Parameters:**
- `html`: HTML content

**Returns:**
- `str`: Extracted text content

**Error Handling:**
- Returns empty string if parsing fails
- Handles malformed HTML gracefully

**Example:**
```python
async def extract_text_example():
    html = await BSWebCrawler.fetch_url_content("https://www.python.org/about/")
    text = BSWebCrawler.extract_text_from_html(html)
    print(f"Extracted {len(text)} characters of text")
    return text
```

**Implementation Notes:**
- Removes script, style, and header elements
- Preserves paragraph structure
- Handles different character encodings
- Cleans up whitespace and formatting

### `@staticmethod extract_pypi_content(html: str, package_name: str) -> Optional[Dict]`
Specifically extracts PyPI package documentation from HTML.

**Parameters:**
- `html`: HTML content from PyPI page
- `package_name`: Name of the package

**Returns:**
- `dict`: Structured package data or None if failed

**Error Handling:**
- Returns None if page structure doesn't match expectations
- Handles missing fields gracefully

**Example:**
```python
async def extract_pypi_example():
    html = await BSWebCrawler.fetch_url_content("https://pypi.org/project/requests/")
    package_data = BSWebCrawler.extract_pypi_content(html, "requests")
    if package_data:
        print(f"Package version: {package_data['version']}")
        print(f"Release date: {package_data['release_date']}")
    return package_data
```

**Implementation Notes:**
- Extracts version, description, author, license
- Parses installation instructions
- Collects dependency information
- Identifies documentation links

### `@staticmethod extract_documentation_content(html: str, url: str) -> Dict`
Extracts content from documentation websites.

**Parameters:**
- `html`: HTML content from the documentation site
- `url`: URL of the documentation page

**Returns:**
- `dict`: Structured documentation data

**Error Handling:**
- Returns partial data if some sections can't be parsed
- Adapts to different documentation site formats

**Example:**
```python
async def extract_docs_example():
    html = await BSWebCrawler.fetch_url_content("https://docs.python.org/3/library/asyncio.html")
    doc_data = BSWebCrawler.extract_documentation_content(html, "https://docs.python.org/3/library/asyncio.html")
    print(f"Title: {doc_data['title']}")
    print(f"Found {len(doc_data['sections'])} sections")
    print(f"Found {len(doc_data['code_snippets'])} code snippets")
    return doc_data
```

**Implementation Notes:**
- Identifies headings and section structure
- Extracts code examples with language detection
- Preserves important formatting elements
- Handles reference links and cross-references

### `@staticmethod format_pypi_info(package_data: Dict) -> str`
Formats PyPI package data into a readable markdown format.

**Parameters:**
- `package_data`: Package data from PyPI API

**Returns:**
- `str`: Formatted markdown text

**Error Handling:**
- Handles missing fields by omitting sections
- Generates consistent output even with partial data

**Example:**
```python
async def format_pypi_example():
    html = await BSWebCrawler.fetch_url_content("https://pypi.org/project/requests/")
    package_data = BSWebCrawler.extract_pypi_content(html, "requests")
    formatted = BSWebCrawler.format_pypi_info(package_data)
    print(formatted)
    return formatted
```

**Implementation Notes:**
- Creates consistent markdown structure
- Includes installation instructions
- Formats dependencies as bulleted lists
- Adds links to documentation and source code

### `@staticmethod format_documentation(doc_data: Dict) -> str`
Formats extracted documentation content into readable markdown.

**Parameters:**
- `doc_data`: Documentation data extracted from the website

**Returns:**
- `str`: Formatted markdown text

**Error Handling:**
- Formats whatever data is available
- Skips missing sections without errors

**Example:**
```python
async def format_docs_example():
    html = await BSWebCrawler.fetch_url_content("https://docs.python.org/3/library/asyncio.html")
    doc_data = BSWebCrawler.extract_documentation_content(html, "https://docs.python.org/3/library/asyncio.html")
    formatted = BSWebCrawler.format_documentation(doc_data)
    print(formatted[:500] + "...")  # Print the first 500 chars
    return formatted
```

**Implementation Notes:**
- Preserves heading hierarchy
- Adds syntax highlighting to code blocks
- Includes links to original documentation
- Creates a readable table of contents

### `async crawl_documentation_site(url: str) -> str`
Crawls a documentation website and extracts formatted content.

**Parameters:**
- `url`: URL of the documentation website

**Returns:**
- `str`: Formatted documentation content as markdown

**Error Handling:**
- Returns error message if crawling fails
- Handles redirects and page not found errors

**Example:**
```python
async def crawl_docs_example():
    formatted_content = await crawler.crawl_documentation_site(
        "https://docs.python.org/3/library/asyncio.html"
    )
    # Save to file for easier viewing
    with open("asyncio_docs.md", "w", encoding="utf-8") as f:
        f.write(formatted_content)
    
    print(f"Documentation crawled and saved to asyncio_docs.md")
    return formatted_content
```

**Implementation Notes:**
- Automatically saves results to Parquet file
- Detects documentation site type (Sphinx, MkDocs, etc.)
- Follows relevant links for more complete documentation
- Creates self-contained markdown document

## 6. ArXiv Crawler API

*Location: `oarc_crawlers.core.crawlers.arxiv_crawler`*

### `__init__(data_dir: Optional[str]=None)`
Initializes the ArXivCrawler instance.

**Parameters:**
- `data_dir` (`Optional[str]`, default=`None`): Directory to store all arXiv data. If not provided, uses the default data directory.

**Example:**
```python
crawler = ArxivCrawler(data_dir='./arxiv_data')
```

---

### `@staticmethod extract_arxiv_id(arxiv_input: str) -> str`
Extracts a normalized arXiv ID from a URL or direct ID string.

**Parameters:**
- `arxiv_input` (`str`): An arXiv URL or ID string.

**Returns:**
- `str`: The extracted arXiv ID.

**Error Handling:**
- Raises `ValueError` if the input is invalid or cannot be parsed as an arXiv ID.

**Example:**
```python
arxiv_id = ArxivCrawler.extract_arxiv_id("https://arxiv.org/abs/2103.13630")
# arxiv_id == "2103.13630"
```

**Implementation Notes:**
- Supports both new and old arXiv ID formats.
- Handles URLs with `/abs/`, `/pdf/`, and strips `.pdf` extensions.
- Validates ID format.

---

### `async fetch_paper_info(arxiv_id: str) -> Dict`
Fetches paper metadata from the arXiv API and stores it as Parquet.

**Parameters:**
- `arxiv_id` (`str`): arXiv ID or URL.

**Returns:**
- `dict`: Paper metadata, including title, authors, abstract, published date, categories, links, and optional fields.

**Error Handling:**
- Returns a dict with an `'error'` key if the paper is not found or the API fails.

**Example:**
```python
info = await crawler.fetch_paper_info("2103.13630")
print(info['title'])
```

**Implementation Notes:**
- Uses the `arxiv` Python package.
- Stores metadata in a per-paper Parquet file and appends to an "all papers" Parquet.

---

### `async download_source(arxiv_id: str) -> Dict`
Downloads and extracts the LaTeX source files for a paper.

**Parameters:**
- `arxiv_id` (`str`): arXiv ID or URL.

**Returns:**
- `dict`: Contains `arxiv_id`, `timestamp`, `latex_content` (concatenated .tex files), and `source_files` (dict of all files).

**Error Handling:**
- Returns a dict with an `'error'` key if download or extraction fails.

**Example:**
```python
source = await crawler.download_source("2103.13630")
print(source['latex_content'][:200])
```

**Implementation Notes:**
- Downloads the .tar.gz source archive from arXiv.
- Extracts all files, reads .tex files, and concatenates their content.
- Handles both tar archives and single-file sources.
- Saves results as Parquet.

---

### `async fetch_paper_with_latex(arxiv_id: str) -> Dict`
Fetches both paper metadata and LaTeX source, combining them.

**Parameters:**
- `arxiv_id` (`str`): arXiv ID or URL.

**Returns:**
- `dict`: Combined metadata and LaTeX content.

**Error Handling:**
- Returns a dict with an `'error'` key if either step fails.

**Example:**
```python
combined = await crawler.fetch_paper_with_latex("2103.13630")
print(combined['title'], len(combined['latex_content']))
```

**Implementation Notes:**
- Saves combined data as Parquet.

---

### `@staticmethod async format_paper_for_learning(paper_info: Dict) -> str`
Formats paper metadata as a markdown summary for learning.

**Parameters:**
- `paper_info` (`dict`): Paper metadata.

**Returns:**
- `str`: Markdown-formatted summary.

**Error Handling:**
- Handles missing fields gracefully.

**Example:**
```python
summary = await ArxivCrawler.format_paper_for_learning(info)
print(summary)
```

---

### `async batch_fetch_papers(arxiv_ids: List[str], extract_keywords=False, extract_references=False) -> Dict`
Fetches multiple papers in batch, optionally extracting keywords and references.

**Parameters:**
- `arxiv_ids` (`List[str]`): List of arXiv IDs or URLs.
- `extract_keywords` (`bool`): Extract keywords from each paper.
- `extract_references` (`bool`): Extract references from each paper.

**Returns:**
- `dict`: Contains lists of papers, keywords, references, and errors.

**Error Handling:**
- Errors for individual papers are collected in the `'errors'` list.

**Example:**
```python
results = await crawler.batch_fetch_papers(["2103.13630", "2201.00001"], extract_keywords=True)
```

---

### `async search(query: str, limit: int=5) -> Dict`
Searches arXiv for papers matching a query.

**Parameters:**
- `query` (`str`): Search query.
- `limit` (`int`): Max number of results.

**Returns:**
- `dict`: Search results and metadata.

**Error Handling:**
- Returns a dict with an `'error'` key if the search fails.

**Example:**
```python
results = await crawler.search("transformer language model", limit=3)
```

---

### `async extract_references(arxiv_id_or_source_info: Union[str, dict]) -> Dict`
Extracts bibliography references from a paper's LaTeX source.

**Parameters:**
- `arxiv_id_or_source_info` (`str` or `dict`): arXiv ID or source info dict.

**Returns:**
- `dict`: Contains extracted references.

**Error Handling:**
- Returns a dict with an `'error'` key if extraction fails.

**Example:**
```python
refs = await crawler.extract_references("2103.13630")
```

**Implementation Notes:**
- Supports both `\bibitem` and BibTeX entries.

---

### `async extract_keywords(arxiv_id_or_paper_info: Union[str, dict], max_keywords=10) -> Dict`
Extracts keywords from the abstract and title using NLP.

**Parameters:**
- `arxiv_id_or_paper_info` (`str` or `dict`): arXiv ID or paper info dict.
- `max_keywords` (`int`): Max number of keywords.

**Returns:**
- `dict`: Contains extracted keywords.

**Error Handling:**
- Returns a dict with an `'error'` key if extraction fails.

**Example:**
```python
keywords = await crawler.extract_keywords("2103.13630")
```

**Implementation Notes:**
- Uses NLTK for tokenization and stopword removal.
- Combines unigrams, bigrams, and trigrams.

---

### `async fetch_category_papers(category: str, max_results: int=100, sort_by: str='submittedDate') -> Dict`
Fetches papers from a specific arXiv category.

**Parameters:**
- `category` (`str`): arXiv category (e.g., 'cs.AI').
- `max_results` (`int`): Max number of papers.
- `sort_by` (`str`): Sort criterion.

**Returns:**
- `dict`: Papers and metadata.

**Error Handling:**
- Returns a dict with an `'error'` key if fetching fails.

**Example:**
```python
cat_papers = await crawler.fetch_category_papers("cs.CL", max_results=10)
```

---

### `async extract_math_equations(arxiv_id_or_source_info: Union[str, dict]) -> Dict`
Extracts mathematical equations from LaTeX source.

**Parameters:**
- `arxiv_id_or_source_info` (`str` or `dict`): arXiv ID or source info dict.

**Returns:**
- `dict`: Inline and display equations.

**Error Handling:**
- Returns a dict with an `'error'` key if extraction fails.

**Example:**
```python
eqs = await crawler.extract_math_equations("2103.13630")
```

---

### `async generate_citation_network(seed_papers: List[str], max_depth: int=1) -> Dict`
Generates a citation network from seed papers.

**Parameters:**
- `seed_papers` (`List[str]`): List of arXiv IDs.
- `max_depth` (`int`): Reference depth.

**Returns:**
- `dict`: Citation network with nodes and edges.

**Error Handling:**
- Skips papers with errors; logs errors internally.

**Example:**
```python
network = await crawler.generate_citation_network(["2103.13630"], max_depth=2)
```

---

**General Implementation Notes:**
- All methods are coroutine functions (`async def`).
- All data is stored in Parquet format using the `ParquetStorage` API.
- Handles errors gracefully, returning error info in the result dict.
- Designed for programmatic/script usage, not CLI.

## 7. Model Context Protocol (MCP) Integration

OARC-Crawlers provides a Visual Studio Code-compatible MCP server that exposes all crawler functionalities through a unified interface.

### Server Configuration

The MCP server runs on WebSocket transport with the following default configuration:
- Port: 3000
- Transport: WebSocket (ws://)
- Streaming Support: Enabled

### Installation

```bash
# Install the package
pip install oarc-crawlers

# Install for VS Code integration
python -m oarc_crawlers.mcp_api install --name "OARC Crawlers"
```

### Available Tools

Each tool is exposed through the MCP interface with proper error handling and response formatting:

#### YouTube Operations
```json
{
    "name": "download_youtube_video",
    "description": "Download a YouTube video with specified format and resolution",
    "parameters": {
        "url": "string",
        "format": "string?",
        "resolution": "string?"
    },
    "returns": "object"
}
```

#### GitHub Operations
```json
{
    "name": "analyze_github_repo",
    "description": "Get a summary analysis of a GitHub repository",
    "parameters": {
        "repo_url": "string"
    },
    "returns": "string"
}
```

#### DuckDuckGo Search
```json
{
    "name": "ddg_text_search",
    "description": "Perform a DuckDuckGo text search",
    "parameters": {
        "query": "string",
        "max_results": "number?"
    },
    "returns": "string"
}
```

### Error Handling

The server provides detailed error responses in the following format:
```json
{
    "error": {
        "code": "string",
        "message": "string",
        "details": "object?"
    }
}
```

Common error codes:
- `TRANSPORT_ERROR`: Connection or communication issues
- `CLIENT_ERROR`: Invalid request or parameters
- `TOOL_ERROR`: Error during tool execution
- `AUTH_ERROR`: Authentication or permission issues

### VS Code Integration

To use with Visual Studio Code:

1. Install the package and register the MCP server
2. Open VS Code settings (Ctrl+,)
3. Search for "MCP Server"
4. Add a new server with:
   - Name: "OARC Crawlers"
   - Port: 3000
   - Transport: ws

Example VS Code configuration:
```json
{
    "mcp.servers": [
        {
            "name": "OARC Crawlers",
            "port": 3000,
            "transport": "ws"
        }
    ]
}
```

### Programmatic Usage

```python
# This example demonstrates starting the server programmatically.
# Ensure you have the necessary dependencies installed.
from oarc_crawlers.core.mcp.mcp_server import MCPServer

# Initialize server with desired configuration
server = MCPServer(
    data_dir="./mcp_data",
    name="OARC Crawlers (Programmatic)",
    port=3001,
    transport="ws"
)

# Start the server (this will typically run indefinitely)
try:
    print(f"Starting MCP server '{server.name}' on {server.transport}://localhost:{server.port}...")
    server.run()
except KeyboardInterrupt:
    print("\nServer stopped.")
except Exception as e:
    print(f"Server error: {e}")

```

### MCP Server API

#### `MCPServer(data_dir: str = "./data", name: str = "OARC Crawlers", port: int = 3000, transport: str = "ws")`
Initializes the MCP server.

**Parameters:**
- `data_dir`: Directory for persistent data storage.
- `name`: Name of the MCP server (for VS Code integration).
- `port`: Port to run the server on (default: 3000).
- `transport`: Transport protocol, e.g., `"ws"` (WebSocket) or `"sse"`.

**Example:**
```python
from oarc_crawlers.core.mcp.mcp_server import MCPServer

server = MCPServer(
    data_dir="./data",
    name="OARC Crawlers",
    port=3000,

server = MCPServer(
    data_dir="./data",
    name="OARC Crawlers",
    port=3000,
    transport="ws"
)
server.run()
```

#### `run()`
Starts the MCP server and begins listening for requests.

**Example:**
```python
server = MCPServer()
server.run()
```

#### `configure_vscode(server_name: str, port: int, supports_streaming: bool = True)`
Configures VS Code integration for the MCP server.

**Parameters:**
- `server_name`: Name to display in VS Code.
- `port`: Port to use.
- `supports_streaming`: Whether streaming is enabled.

**Example:**
```python
server = MCPServer()
server.configure_vscode(server_name="OARC Crawlers", port=3000)
```

### Example Usage

```python
from oarc_crawlers.core.mcp.mcp_server import MCPServer

server = MCPServer(data_dir="./data", name="OARC Crawlers", port=3000)
server.run()
```
