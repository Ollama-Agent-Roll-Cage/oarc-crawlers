# OARC-Crawlers API Reference

This document provides detailed API reference for all components in the OARC-Crawlers system.

## Table of Contents
- [1. Parquet Storage API](#1-parquet-storage-api)
    - [`save_to_parquet(data, file_path)`](#save_to_parquetdata-file_path)
    - [`load_from_parquet(file_path)`](#load_from_parquetfile_path)
    - [`append_to_parquet(data, file_path)`](#append_to_parquetdata-file_path)
- [2. YouTube Downloader API](#2-youtube-downloader-api)
    - [`__init__(data_dir=None)`](#__init__data_dirnone)
    - [`download_video(...)`](#download_videourl-formatmp4-resolutionhighest-output_pathnone-filenamenone-extract_audiofalse)
    - [`download_playlist(...)`](#download_playlistplaylist_url-formatmp4-max_videos10-output_pathnone)
    - [`extract_captions(...)`](#extract_captionsurl-languagesen)
    - [`search_videos(...)`](#search_videosquery-limit10)
- [3. GitHub Crawler API](#3-github-crawler-api)
    - [`__init__(data_dir=None)`](#__init__data_dirnone-1)
    - [`extract_repo_info_from_url(url)`](#extract_repo_info_from_urlurl)
    - [`clone_repo(repo_url, temp_dir=None)`](#clone_reporepo_url-temp_dirnone)
    - [`process_repo_to_dataframe(...)`](#process_repo_to_datareframerepo_path-max_file_size_kb500)
    - [`clone_and_store_repo(repo_url)`](#clone_and_store_reporepo_url)
    - [`get_repo_summary(repo_url)`](#get_repo_summaryrepo_url)
    - [`find_similar_code(...)`](#find_similar_coderepo_url-code_snippet)
    - [`query_repo_content(...)`](#query_repo_contentrepo_url-query)
- [4. DuckDuckGo Searcher API](#4-duckduckgo-searcher-api)
    - [`__init__(data_dir=None)`](#__init__data_dirnone-2)
    - [`text_search(...)`](#text_searchsearch_query-max_results5)
    - [`image_search(...)`](#image_searchsearch_query-max_results10)
    - [`news_search(...)`](#news_searchsearch_query-max_results20)
- [5. BeautifulSoup Web Crawler API](#5-beautifulsoup-web-crawler-api)
    - [`__init__(data_dir=None)`](#__init__data_dirnone-3)
    - [`fetch_url_content(url)`](#fetch_url_contenturl)
    - [`extract_text_from_html(html)`](#extract_text_from_htmlhtml)
    - [`extract_pypi_content(...)`](#extract_pypi_contenthtml-package_name)
    - [`extract_documentation_content(...)`](#extract_documentation_contenthtml-url)
    - [`format_pypi_info(package_data)`](#format_pypi_infopackage_data)
    - [`format_documentation(doc_data)`](#format_documentationdoc_data)
    - [`crawl_documentation_site(url)`](#crawl_documentation_siteurl)
- [6. ArXiv Fetcher API](#6-arxiv-fetcher-api)
    - [`__init__(data_dir=None)`](#__init__data_dirnone-4)
    - [`extract_arxiv_id(url_or_id)`](#extract_arxiv_idurl_or_id)
    - [`fetch_paper_info(arxiv_id)`](#fetch_paper_infoarxiv_id)
    - [`download_source(arxiv_id)`](#download_sourcearxiv_id)
    - [`fetch_paper_with_latex(arxiv_id)`](#fetch_paper_with_latexarxiv_id)
    - [`format_paper_for_learning(paper_info)`](#format_paper_for_learningpaper_info)

## 1. Parquet Storage API

### `save_to_parquet(data, file_path)`
Saves data to a Parquet file.

**Parameters:**
- `data`: Dictionary, list of dictionaries, or Pandas DataFrame
- `file_path`: Path where the Parquet file will be saved

**Returns:**
- `bool`: True if successful, False otherwise

**Example:**
```python
data = {'name': 'Model XYZ', 'accuracy': 0.95, 'parameters': 10000000}
success = ParquetStorage.save_to_parquet(data, 'model_metrics.parquet')
```

### `load_from_parquet(file_path)`
Loads data from a Parquet file.

**Parameters:**
- `file_path`: Path to the Parquet file

**Returns:**
- `DataFrame`: Pandas DataFrame containing the loaded data, or None if failed

**Example:**
```python
df = ParquetStorage.load_from_parquet('model_metrics.parquet')
if df is not None:
    print(f"Model name: {df['name'].iloc[0]}, Accuracy: {df['accuracy'].iloc[0]}")
```

### `append_to_parquet(data, file_path)`
Appends data to an existing Parquet file (creates new file if it doesn't exist).

**Parameters:**
- `data`: Dictionary, list of dictionaries, or Pandas DataFrame
- `file_path`: Path to the Parquet file

**Returns:**
- `bool`: True if successful, False otherwise

**Example:**
```python
new_data = {'name': 'Model ABC', 'accuracy': 0.97, 'parameters': 15000000}
success = ParquetStorage.append_to_parquet(new_data, 'model_metrics.parquet')
```

## 2. YouTube Downloader API

### `__init__(data_dir=None)`
Initializes the YouTube Downloader.

**Parameters:**
- `data_dir`: Directory to store data (optional)

**Example:**
```python
downloader = YouTubeDownloader(data_dir='./my_data')
```

### `download_video(url, format="mp4", resolution="highest", output_path=None, filename=None, extract_audio=False)`
Downloads a YouTube video.

**Parameters:**
- `url`: YouTube video URL
- `format`: Video format (mp4, webm, etc.)
- `resolution`: Video resolution ("highest", "lowest", or specific like "720p")
- `output_path`: Directory to save the video (optional)
- `filename`: Custom filename for the downloaded video (optional)
- `extract_audio`: Whether to extract audio only (boolean)

**Returns:**
- `dict`: Information about the downloaded video

**Example:**
```python
async def download_hd_video():
    result = await downloader.download_video(
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        resolution="1080p",
        output_path="./videos",
        filename="my_video"
    )
    return result
```

### `download_playlist(playlist_url, format="mp4", max_videos=10, output_path=None)`
Downloads videos from a YouTube playlist.

**Parameters:**
- `playlist_url`: YouTube playlist URL
- `format`: Video format (mp4, webm, etc.)
- `max_videos`: Maximum number of videos to download
- `output_path`: Directory to save the videos (optional)

**Returns:**
- `dict`: Information about the downloaded playlist

**Example:**
```python
async def download_playlist_example():
    result = await downloader.download_playlist(
        playlist_url="https://www.youtube.com/playlist?list=PLQVvvaa0QuDdttJXlLtAJxJetJcqmqlQq",
        max_videos=5
    )
    return result
```

### `extract_captions(url, languages=['en'])`
Extracts captions/subtitles from a YouTube video.

**Parameters:**
- `url`: YouTube video URL
- `languages`: List of language codes to extract (e.g., ['en', 'es', 'fr'])

**Returns:**
- `dict`: Captions data

**Example:**
```python
async def get_multilingual_captions():
    captions = await downloader.extract_captions(
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        languages=['en', 'es', 'fr', 'de']
    )
    return captions
```

### `search_videos(query, limit=10)`
Searches for YouTube videos using a query.

**Parameters:**
- `query`: Search query
- `limit`: Maximum number of results

**Returns:**
- `dict`: Search results

**Example:**
```python
async def search_educational_videos():
    results = await downloader.search_videos(
        query="python programming tutorial for beginners",
        limit=15
    )
    return results
```

## 3. GitHub Crawler API

### `__init__(data_dir=None)`
Initializes the GitHub Crawler.

**Parameters:**
- `data_dir`: Directory to store data (optional)

**Example:**
```python
crawler = GitHubCrawler(data_dir='./github_data')
```

### `extract_repo_info_from_url(url)`
Extracts repository owner, name, and branch from GitHub URL.

**Parameters:**
- `url`: GitHub repository URL

**Returns:**
- `tuple`: Repository owner, name, and branch

**Example:**
```python
owner, repo_name, branch = GitHubCrawler.extract_repo_info_from_url(
    "https://github.com/pytorch/pytorch/tree/master"
)
print(f"Owner: {owner}, Repo: {repo_name}, Branch: {branch}")
```

### `clone_repo(repo_url, temp_dir=None)`
Clones a GitHub repository.

**Parameters:**
- `repo_url`: GitHub repository URL
- `temp_dir`: Temporary directory path (optional)

**Returns:**
- `Path`: Path to the cloned repository

**Example:**
```python
async def clone_example():
    repo_path = await crawler.clone_repo(
        repo_url="https://github.com/pytorch/pytorch",
        temp_dir="./temp_repos"
    )
    return repo_path
```

### `process_repo_to_dataframe(repo_path, max_file_size_kb=500)`
Processes repository files and converts to DataFrame.

**Parameters:**
- `repo_path`: Path to cloned repository
- `max_file_size_kb`: Maximum file size in KB to process

**Returns:**
- `DataFrame`: DataFrame containing file information

**Example:**
```python
async def process_repo_example():
    repo_path = await crawler.clone_repo("https://github.com/pytorch/pytorch")
    df = await crawler.process_repo_to_dataframe(
        repo_path=repo_path,
        max_file_size_kb=1000
    )
    return df
```

### `clone_and_store_repo(repo_url)`
Clones a GitHub repository and stores its data in Parquet format.

**Parameters:**
- `repo_url`: GitHub repository URL

**Returns:**
- `str`: Path to the Parquet file containing repository data

**Example:**
```python
async def store_repo_example():
    parquet_path = await crawler.clone_and_store_repo(
        "https://github.com/pytorch/pytorch"
    )
    return parquet_path
```

### `get_repo_summary(repo_url)`
Gets a summary of the repository.

**Parameters:**
- `repo_url`: GitHub repository URL

**Returns:**
- `str`: Repository summary formatted as markdown

**Example:**
```python
async def summary_example():
    summary = await crawler.get_repo_summary(
        "https://github.com/pytorch/pytorch"
    )
    return summary
```

### `find_similar_code(repo_url, code_snippet)`
Finds similar code in the repository.

**Parameters:**
- `repo_url`: GitHub repository URL
- `code_snippet`: Code snippet to find similar code for

**Returns:**
- `str`: Similar code findings formatted as markdown

**Example:**
```python
async def find_similar_code_example():
    code = "def calculate_mean(values):\n    return sum(values) / len(values)"
    similar = await crawler.find_similar_code(
        repo_url="https://github.com/pytorch/pytorch",
        code_snippet=code
    )
    return similar
```

### `query_repo_content(repo_url, query)`
Queries repository content using natural language.

**Parameters:**
- `repo_url`: GitHub repository URL
- `query`: Natural language query about the repository

**Returns:**
- `str`: Query result formatted as markdown

**Example:**
```python
async def query_repo_example():
    result = await crawler.query_repo_content(
        repo_url="https://github.com/pytorch/pytorch",
        query="Find all files related to tensor operations"
    )
    return result
```

## 4. DuckDuckGo Searcher API

### `__init__(data_dir=None)`
Initializes the DuckDuckGo Searcher.

**Parameters:**
- `data_dir`: Directory to store data (optional)

**Example:**
```python
searcher = DuckDuckGoSearcher(data_dir='./search_data')
```

### `text_search(search_query, max_results=5)`
Performs a text search using DuckDuckGo.

**Parameters:**
- `search_query`: Query to search for
- `max_results`: Maximum number of results to return

**Returns:**
- `str`: Formatted search results in markdown

**Example:**
```python
async def text_search_example():
    results = await searcher.text_search(
        search_query="python asynchronous programming",
        max_results=10
    )
    return results
```

### `image_search(search_query, max_results=10)`
Performs an image search using DuckDuckGo.

**Parameters:**
- `search_query`: Query to search for images
- `max_results`: Maximum number of results to return

**Returns:**
- `str`: Formatted image search results in markdown

**Example:**
```python
async def image_search_example():
    results = await searcher.image_search(
        search_query="neural network visualization",
        max_results=15
    )
    return results
```

### `news_search(search_query, max_results=20)`
Performs a news search using DuckDuckGo.

**Parameters:**
- `search_query`: Query to search for news
- `max_results`: Maximum number of results to return

**Returns:**
- `str`: Formatted news search results in markdown

**Example:**
```python
async def news_search_example():
    results = await searcher.news_search(
        search_query="artificial intelligence breakthroughs",
        max_results=12
    )
    return results
```

## 5. BeautifulSoup Web Crawler API

### `__init__(data_dir=None)`
Initializes the Web Crawler.

**Parameters:**
- `data_dir`: Directory to store data (optional)

**Example:**
```python
crawler = BSWebCrawler(data_dir='./web_data')
```

### `fetch_url_content(url)`
Fetches content from a URL. *Note: This is an instance method.*

**Parameters:**
- `url`: The URL to fetch content from

**Returns:**
- `str`: HTML content of the page or None if failed

**Example:**
```python
async def fetch_example():
    # Assuming 'crawler' is an initialized BSWebCrawler instance
    html = await crawler.fetch_url_content(
        "https://www.python.org/about/"
    )
    return html
```

### `extract_text_from_html(html)`
Extracts main text content from HTML using BeautifulSoup. *Note: This is a static method.*

**Parameters:**
- `html`: HTML content

**Returns:**
- `str`: Extracted text content

**Example:**
```python
async def extract_text_example():
    html = await BSWebCrawler.fetch_url_content("https://www.python.org/about/")
    text = await BSWebCrawler.extract_text_from_html(html)
    return text
```

### `extract_pypi_content(html, package_name)`
Specifically extracts PyPI package documentation from HTML. *Note: This is a static method.*

**Parameters:**
- `html`: HTML content from PyPI page
- `package_name`: Name of the package

**Returns:**
- `dict`: Structured package data or None if failed

**Example:**
```python
async def extract_pypi_example():
    html = await BSWebCrawler.fetch_url_content("https://pypi.org/project/requests/")
    package_data = await BSWebCrawler.extract_pypi_content(html, "requests")
    return package_data
```

### `extract_documentation_content(html, url)`
Extracts content from documentation websites. *Note: This is a static method.*

**Parameters:**
- `html`: HTML content from the documentation site
- `url`: URL of the documentation page

**Returns:**
- `dict`: Structured documentation data

**Example:**
```python
async def extract_docs_example():
    html = await BSWebCrawler.fetch_url_content("https://docs.python.org/3/library/asyncio.html")
    doc_data = await BSWebCrawler.extract_documentation_content(html, "https://docs.python.org/3/library/asyncio.html")
    return doc_data
```

### `format_pypi_info(package_data)`
Formats PyPI package data into a readable markdown format. *Note: This is a static method.*

**Parameters:**
- `package_data`: Package data from PyPI API

**Returns:**
- `str`: Formatted markdown text

**Example:**
```python
async def format_pypi_example():
    html = await BSWebCrawler.fetch_url_content("https://pypi.org/project/requests/")
    package_data = await BSWebCrawler.extract_pypi_content(html, "requests")
    formatted = await BSWebCrawler.format_pypi_info(package_data)
    return formatted
```

### `format_documentation(doc_data)`
Formats extracted documentation content into readable markdown. *Note: This is a static method.*

**Parameters:**
- `doc_data`: Documentation data extracted from the website

**Returns:**
- `str`: Formatted markdown text

**Example:**
```python
async def format_docs_example():
    html = await BSWebCrawler.fetch_url_content("https://docs.python.org/3/library/asyncio.html")
    doc_data = await BSWebCrawler.extract_documentation_content(html, "https://docs.python.org/3/library/asyncio.html")
    formatted = await BSWebCrawler.format_documentation(doc_data)
    return formatted
```

### `crawl_documentation_site(url)`
Crawls a documentation website and extracts formatted content. *Note: This is an instance method.*

**Parameters:**
- `url`: URL of the documentation website

**Returns:**
- `str`: Formatted documentation content as markdown

**Example:**
```python
async def crawl_docs_example():
    formatted_content = await crawler.crawl_documentation_site(
        "https://docs.python.org/3/library/asyncio.html"
    )
    return formatted_content
```

## 6. ArXiv Fetcher API

### `__init__(data_dir=None)`
Initializes the ArXiv Fetcher.

**Parameters:**
- `data_dir`: Directory to store data (optional)

**Example:**
```python
fetcher = ArxivFetcher(data_dir='./arxiv_data')
```

### `extract_arxiv_id(url_or_id)`
Extracts arXiv ID from a URL or direct ID string. *Note: This is a static method.*

**Parameters:**
- `url_or_id`: URL or ID string

**Returns:**
- `str`: ArXiv ID

**Example:**
```python
arxiv_id = ArxivFetcher.extract_arxiv_id("https://arxiv.org/abs/2103.13630")
print(f"Extracted ID: {arxiv_id}")  # Outputs: Extracted ID: 2103.13630
```

### `fetch_paper_info(arxiv_id)`
Fetches paper metadata from arXiv API.

**Parameters:**
- `arxiv_id`: ArXiv ID

**Returns:**
- `dict`: Paper metadata

**Example:**
```python
async def fetch_paper_example():
    paper_info = await fetcher.fetch_paper_info("2103.13630")
    print(f"Title: {paper_info['title']}")
    print(f"Authors: {', '.join(paper_info['authors'])}")
    return paper_info
```

### `download_source(arxiv_id)`
Downloads the LaTeX source files for a paper.

**Parameters:**
- `arxiv_id`: ArXiv ID of the paper

**Returns:**
- `dict`: Dictionary containing source information and content

**Example:**
```python
async def download_source_example():
    source_info = await fetcher.download_source("2103.13630")
    print(f"Number of files: {len(source_info['source_files'])}")
    return source_info
```

### `fetch_paper_with_latex(arxiv_id)`
Fetches both paper metadata and LaTeX source.

**Parameters:**
- `arxiv_id`: ArXiv ID or URL

**Returns:**
- `dict`: Combined paper metadata and source information

**Example:**
```python
async def fetch_paper_with_latex_example():
    complete_info = await fetcher.fetch_paper_with_latex("2103.13630")
    print(f"Title: {complete_info['title']}")
    print(f"Has LaTeX: {len(complete_info['latex_content']) > 0}")
    return complete_info
```

### `format_paper_for_learning(paper_info)`
Formats paper information for learning. *Note: This is a static method.*

**Parameters:**
- `paper_info`: Paper information dictionary

**Returns:**
- `str`: Formatted markdown text

**Example:**
```python
async def format_paper_example():
    paper_info = await fetcher.fetch_paper_info("2103.13630")
    formatted = await ArxivFetcher.format_paper_for_learning(paper_info)
    return formatted
```
