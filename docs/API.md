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
    - [`__init__(data_dir: Optional[str]=None)`](#__init__data_dirnone-1)
    - [`@staticmethod extract_repo_info_from_url(url: str) -> Tuple[str, str, str]`](#extract_repo_info_from_urlurl)
    - [`async clone_repo(repo_url: str, temp_dir: Optional[str]=None) -> Path`](#clone_reporepo_url-temp_dirnone)
    - [`async process_repo_to_dataframe(...)`](#process_repo_to_datareframerepo_path-max_file_size_kb500)
    - [`async clone_and_store_repo(repo_url: str) -> str`](#clone_and_store_reporepo_url)
    - [`async get_repo_summary(repo_url: str) -> str`](#get_repo_summaryrepo_url)
    - [`async find_similar_code(...)`](#find_similar_coderepo_url-code_snippet)
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
- [6. ArXiv Fetcher API](#6-arxiv-fetcher-api)
    - [`__init__(data_dir: Optional[str]=None)`](#__init__data_dirnone-4)
    - [`@staticmethod extract_arxiv_id(url_or_id: str) -> str`](#extract_arxiv_idurl_or_id)
    - [`async fetch_paper_info(arxiv_id: str) -> Dict`](#fetch_paper_infoarxiv_id)
    - [`async download_source(arxiv_id: str) -> Dict`](#download_sourcearxiv_id)
    - [`async fetch_paper_with_latex(arxiv_id: str) -> Dict`](#fetch_paper_with_latexarxiv_id)
    - [`@staticmethod format_paper_for_learning(paper_info: Dict) -> str`](#format_paper_for_learningpaper_info)
- [7. Model Context Protocol (MCP) Integration](#7-model-context-protocol-mcp-integration)
    - [Server Configuration](#server-configuration)
    - [Installation](#installation)
    - [Available Tools](#available-tools)
    - [Error Handling](#error-handling)
    - [VS Code Integration](#vs-code-integration)
    - [Programmatic Usage](#programmatic-usage)

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

### `__init__(data_dir: Optional[str]=None)`
Initializes the GitHub Crawler.

**Parameters:**
- `data_dir`: Directory to store data (optional)

**Example:**
```python
crawler = GitHubCrawler(data_dir='./github_data')
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
owner, repo_name, branch = GitHubCrawler.extract_repo_info_from_url(
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

### `async clone_and_store_repo(repo_url: str) -> str`
Clones a GitHub repository and stores its data in Parquet format.

**Parameters:**
- `repo_url`: GitHub repository URL

**Returns:**
- `str`: Path to the Parquet file containing repository data

**Error Handling:**
- Handles cloning errors and returns error information
- Creates data directory if it doesn't exist

**Example:**
```python
async def store_repo_example():
    parquet_path = await crawler.clone_and_store_repo(
        "https://github.com/pytorch/pytorch"
    )
    print(f"Repository data stored at {parquet_path}")
    
    # Load the data
    repo_data = ParquetStorage.load_from_parquet(parquet_path)
    python_files = repo_data[repo_data['language'] == 'Python']
    print(f"Repository contains {len(python_files)} Python files")
    return parquet_path
```

**Implementation Notes:**
- Uses temporary directory for cloning
- Filters out binary files larger than 500KB by default
- Saves repository structure to allow reconstruction
- Stores file content and metadata as separate columns

### `async get_repo_summary(repo_url: str) -> str`
Gets a summary of the repository.

**Parameters:**
- `repo_url`: GitHub repository URL

**Returns:**
- `str`: Repository summary formatted as markdown

**Error Handling:**
- Returns error message if repository cannot be processed
- Handles timeouts and connection issues gracefully

**Example:**
```python
async def summary_example():
    summary = await crawler.get_repo_summary(
        "https://github.com/pytorch/pytorch"
    )
    print(summary)
    return summary
```

**Implementation Notes:**
- Analyzes language distribution
- Summarizes directory structure
- Identifies key files like README, LICENSE, etc.
- Creates a formatted markdown summary for easy reading

### `async find_similar_code(repo_url: str, code_snippet: str) -> str`
Finds similar code in the repository.

**Parameters:**
- `repo_url`: GitHub repository URL
- `code_snippet`: Code snippet to find similar code for

**Returns:**
- `str`: Similar code findings formatted as markdown

**Error Handling:**
- Returns empty results if no similar code found
- Handles language detection errors

**Example:**
```python
async def find_similar_code_example():
    code = "def calculate_mean(values):\n    return sum(values) / len(values)"
    similar = await crawler.find_similar_code(
        repo_url="https://github.com/pytorch/pytorch",
        code_snippet=code
    )
    print(similar)
    return similar
```

**Implementation Notes:**
- Uses fuzzy matching algorithm for code similarity
- Prioritizes matches by similarity score
- Includes file path and line numbers for each match
- Formats results as markdown with syntax highlighting

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
searcher = DuckDuckGoSearcher(data_dir='./search_data')
```

### `async text_search(search_query: str, max_results: int=5) -> str`
Performs a text search using DuckDuckGo.

**Parameters:**
- `search_query`: Query to search for
- `max_results`: Maximum number of results to return

**Returns:**
- `str`: Formatted search results in markdown

**Error Handling:**
- Returns error explanation if search fails
- Handles network timeouts gracefully

**Example:**
```python
async def text_search_example():
    results = await searcher.text_search(
        search_query="python asynchronous programming",
        max_results=10
    )
    print(results)
    
    # Also store the results programmatically
    result_dict = await searcher.text_search_to_dict(
        search_query="python asynchronous programming",
        max_results=10
    )
    return results
```

**Implementation Notes:**
- Uses DuckDuckGo's HTML API for privacy
- Automatically saves search results to Parquet file
- Includes title, description, and URL for each result
- Formats results in readable markdown format

### `async image_search(search_query: str, max_results: int=10) -> str`
Performs an image search using DuckDuckGo.

**Parameters:**
- `search_query`: Query to search for images
- `max_results`: Maximum number of results to return

**Returns:**
- `str`: Formatted image search results in markdown

**Error Handling:**
- Skips images that fail to download
- Returns partial results if some images failed

**Example:**
```python
async def image_search_example():
    results = await searcher.image_search(
        search_query="neural network visualization",
        max_results=15
    )
    print(results)
    return results
```

**Implementation Notes:**
- Includes image URLs, thumbnails, and source pages
- Embeds image thumbnails in markdown output
- Respects content filtering settings
- Avoids storing inappropriate content

### `async news_search(search_query: str, max_results: int=20) -> str`
Performs a news search using DuckDuckGo.

**Parameters:**
- `search_query`: Query to search for news
- `max_results`: Maximum number of results to return

**Returns:**
- `str`: Formatted news search results in markdown

**Error Handling:**
- Returns empty results if no news found
- Handles API rate limiting automatically

**Example:**
```python
async def news_search_example():
    results = await searcher.news_search(
        search_query="artificial intelligence breakthroughs",
        max_results=12
    )
    print(results)
    
    # Extract information programmatically
    articles = await searcher.news_search_to_dict(
        search_query="artificial intelligence breakthroughs",
        max_results=12
    )
    for article in articles['results']:
        print(f"- {article['title']} ({article['date']})")
    
    return results
```

**Implementation Notes:**
- Includes publication date, source, and summary
- Sorts results by relevance and recency
- Saves full article metadata to Parquet format
- Provides both human-readable and machine-readable outputs

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

## 6. ArXiv Fetcher API

### `__init__(data_dir: Optional[str]=None)`
Initializes the ArXiv Fetcher.

**Parameters:**
- `data_dir`: Directory to store data (optional)

**Example:**
```python
fetcher = ArxivFetcher(data_dir='./arxiv_data')
```

### `@staticmethod extract_arxiv_id(url_or_id: str) -> str`
Extracts arXiv ID from a URL or direct ID string.

**Parameters:**
- `url_or_id`: URL or ID string

**Returns:**
- `str`: ArXiv ID

**Error Handling:**
- Raises `ValueError` if ID cannot be extracted
- Validates ID format before returning

**Example:**
```python
arxiv_id = ArxivFetcher.extract_arxiv_id("https://arxiv.org/abs/2103.13630")
print(f"Extracted ID: {arxiv_id}")  # Outputs: Extracted ID: 2103.13630

# Also works with direct IDs
arxiv_id = ArxivFetcher.extract_arxiv_id("2103.13630")
print(f"Extracted ID: {arxiv_id}")  # Outputs: Extracted ID: 2103.13630
```

**Implementation Notes:**
- Supports multiple arXiv URL formats
- Handles both new and old arXiv ID formats
- Strips version numbers if present (e.g., v1, v2)
- Normalizes ID format for consistency

### `async fetch_paper_info(arxiv_id: str) -> Dict`
Fetches paper metadata from arXiv API.

**Parameters:**
- `arxiv_id`: ArXiv ID

**Returns:**
- `dict`: Paper metadata

**Error Handling:**
- Raises `ConnectionError` if cannot connect to arXiv API
- Raises `ValueError` if API response cannot be parsed
- Returns error information if paper not found

**Example:**
```python
async def fetch_paper_example():
    paper_info = await fetcher.fetch_paper_info("2103.13630")
    print(f"Title: {paper_info['title']}")
    print(f"Authors: {', '.join(paper_info['authors'])}")
    print(f"Categories: {', '.join(paper_info['categories'])}")
    print(f"Abstract: {paper_info['abstract'][:200]}...")
    return paper_info
```

**Implementation Notes:**
- Uses arXiv's official API
- Respects rate limiting requirements
- Extracts comprehensive metadata including:
  - Title, authors, abstract, categories
  - Publication/revision dates
  - DOI and journal references
  - Download links

### `async download_source(arxiv_id: str) -> Dict`
Downloads the LaTeX source files for a paper.

**Parameters:**
- `arxiv_id`: ArXiv ID of the paper

**Returns:**
- `dict`: Dictionary containing source information and content

**Error Handling:**
- Returns error details if source cannot be downloaded
- Handles corrupted or invalid tar files
- Creates storage directory if it doesn't exist

**Example:**
```python
async def download_source_example():
    source_info = await fetcher.download_source("2103.13630")
    print(f"Source files downloaded to: {source_info['path']}")
    print(f"Number of files: {len(source_info['source_files'])}")
    
    # Print main TeX file content (if available)
    if source_info['main_tex_file'] and source_info['latex_content']:
        print(f"Main TeX file: {source_info['main_tex_file']}")
        print(f"Content preview: {source_info['latex_content'][:200]}...")
        
    return source_info
```

**Implementation Notes:**
- Downloads .tar.gz source archive from arXiv
- Extracts all files to dedicated directory
- Identifies main LaTeX file automatically
- Organizes figures, bibliography, and supplementary files
- Saves extracted content to Parquet for analysis

### `async fetch_paper_with_latex(arxiv_id: str) -> Dict`
Fetches both paper metadata and LaTeX source.

**Parameters:**
- `arxiv_id`: ArXiv ID or URL

**Returns:**
- `dict`: Combined paper metadata and source information

**Error Handling:**
- Handles partial success (metadata without source)
- Logs detailed error information for troubleshooting

**Example:**
```python
async def fetch_paper_with_latex_example():
    complete_info = await fetcher.fetch_paper_with_latex("2103.13630")
    print(f"Title: {complete_info['title']}")
    print(f"Has LaTeX: {len(complete_info['latex_content']) > 0}")
    
    # Save the complete information for later use
    ParquetStorage.save_to_parquet(
        {k: v for k, v in complete_info.items() if k != 'source_files'},  # Exclude binary file data
        f"./data/papers/{complete_info['arxiv_id']}_complete.parquet"
    )
    
    return complete_info
```

**Implementation Notes:**
- Concurrently fetches metadata and source
- Combines results into unified structure
- Formats LaTeX content for readability
- Preserves original document structure
- Extracts mathematical formulas for analysis

### `@staticmethod format_paper_for_learning(paper_info: Dict) -> str`
Formats paper information for learning.

**Parameters:**
- `paper_info`: Paper information dictionary

**Returns:**
- `str`: Formatted markdown text

**Error Handling:**
- Handles missing information gracefully
- Returns partial content if some fields are missing

**Example:**
```python
async def format_paper_example():
    paper_info = await fetcher.fetch_paper_info("2103.13630")
    formatted = ArxivFetcher.format_paper_for_learning(paper_info)
    
    # Save to file for reference
    with open(f"{paper_info['arxiv_id']}_summary.md", "w", encoding="utf-8") as f:
        f.write(formatted)
        
    print(f"Paper summary saved to {paper_info['arxiv_id']}_summary.md")
    return formatted
```

**Implementation Notes:**
- Creates structured markdown document
- Formats abstract with proper paragraph breaks
- Lists authors with affiliations when available
- Includes clickable links to paper and references
- Highlights key mathematical formulas

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
from oarc_crawlers import OARCCrawlersMCP

# Initialize server
mcp = OARCCrawlersMCP(
    data_dir="./data",
    name="OARC Crawlers",
    port=3000
)

# Start server
mcp.run()
```

For custom configuration:
```python
mcp = OARCCrawlersMCP()

# Configure VS Code integration
mcp.mcp.configure_vscode(
    server_name="Custom OARC Server",
    port=4000,
    supports_streaming=True
)

# Start with custom transport
mcp.run(transport="ws", port=4000)
```
