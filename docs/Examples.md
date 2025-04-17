# OARC-Crawlers Examples

This document provides practical examples for using the `oarc-crawlers` package. It covers the core functionalities, including data storage with the `ParquetStorage` system, usage of individual crawler modules for platforms like YouTube, GitHub, ArXiv, and DuckDuckGo, as well as techniques for accessing and analyzing the collected data.

## Table of Contents

- [Basic Operations](#basic-operations)
  - [Initializing Crawlers](#initializing-crawlers)
  - [Configuring Storage Paths](#configuring-storage-paths)
  - [Error Handling](#error-handling)
- [CLI Usage](#cli-usage)
  - [Command Overview](#command-overview)
  - [Getting Help with Commands](#getting-help-with-commands)
- [YouTube Operations](#youtube-operations)
  - [Downloading Videos](#downloading-videos)
  - [Working with Playlists](#working-with-playlists)
  - [Extracting Captions](#extracting-captions)
- [GitHub Operations](#github-operations)
  - [Cloning Repositories](#cloning-repositories)
  - [Analyzing Code](#analyzing-code)
  - [Search Repositories](#search-repositories)
- [Search Operations](#search-operations)
  - [DuckDuckGo Text Search](#duckduckgo-text-search)
  - [News and Image Search](#news-and-image-search)
- [ArXiv Operations](#arxiv-operations)
  - [Downloading Papers](#downloading-papers)
  - [Extracting LaTeX Sources](#extracting-latex-sources)
- [Web Crawling](#web-crawling)
  - [Crawling Websites](#crawling-websites)
  - [Extracting Specific Content](#extracting-specific-content)
- [Data Management](#data-management)
  - [Working with Parquet Files](#working-with-parquet-files)
  - [Converting Between Formats](#converting-between-formats)

## Basic Operations

### Initializing Crawlers

All crawler modules follow a consistent initialization pattern, typically accepting a `data_dir` parameter to specify where data should be stored.

```python
from oarc_crawlers import YouTubeDownloader, GitHubCrawler, ArxivFetcher, DuckDuckGoSearcher, BSWebCrawler

# Initialize with default data directory
youtube = YouTubeDownloader()
github = GitHubCrawler()
arxiv = ArxivFetcher()
ddg = DuckDuckGoSearcher()
web = BSWebCrawler()

# Initialize with custom data directory
data_dir = "./my_custom_data"
youtube_custom = YouTubeDownloader(data_dir=data_dir)
github_custom = GitHubCrawler(data_dir=data_dir)
arxiv_custom = ArxivFetcher(data_dir=data_dir)
ddg_custom = DuckDuckGoSearcher(data_dir=data_dir)
web_custom = BSWebCrawler(data_dir=data_dir)
```

### Configuring Storage Paths

The storage system can be configured through initialization parameters or environment variables.

```python
import os
from oarc_crawlers import YouTubeDownloader, ParquetStorage

# Method 1: Set environment variable
os.environ["OARC_DATA_DIR"] = "/path/to/data"

# Method 2: Pass directly to crawler instances
youtube = YouTubeDownloader(data_dir="/custom/path/data")

# Method 3: Create directory structure programmatically
import pathlib
data_dir = pathlib.Path("./project_data")
data_dir.mkdir(exist_ok=True)
youtube = YouTubeDownloader(data_dir=str(data_dir))

# Accessing default paths within a module
youtube = YouTubeDownloader()
video_dir = youtube.data_dir / "videos"
print(f"Videos will be stored in: {video_dir}")
```

### Error Handling

The crawlers provide comprehensive error handling to manage common issues.

```python
import asyncio
from oarc_crawlers import YouTubeDownloader, GitHubCrawler

async def error_handling_examples():
    # Example 1: Using try/except with the API
    youtube = YouTubeDownloader()
    try:
        result = await youtube.download_video("https://youtube.com/watch?v=invalid_id")
    except Exception as e:
        print(f"Error downloading video: {e}")
    
    # Example 2: Checking return values
    github = GitHubCrawler()
    result = await github.clone_repo("https://github.com/nonexistent/repo")
    if result is None:
        print("Repository cloning failed")
    
    # Example 3: Using built-in fallback mechanisms
    try:
        # Some crawlers may have fallback strategies implemented
        paper = await arxiv.fetch_paper_info("invalid_id", fallback_to_search=True)
        if paper.get("error"):
            print(f"Error with fallback: {paper['error']}")
    except Exception as e:
        print(f"Critical error with no fallback: {e}")

asyncio.run(error_handling_examples())
```

## CLI Usage

The OARC-Crawlers package provides a unified command-line interface for all its functionality. This section demonstrates how to use the CLI for various operations.

### Command Overview

The CLI follows a consistent pattern of `oarc-crawlers [module] [action] [--parameters]`, making it intuitive to use across different modules.

```bash
# Package management commands
uv run oarc-crawlers setup         # Setup development environment
uv run oarc-crawlers build         # Build the package
uv run oarc-crawlers publish       # Publish to PyPI
uv run oarc-crawlers publish --test # Publish to TestPyPI

# YouTube operations
uv run oarc-crawlers youtube download --url "https://youtube.com/watch?v=..."
uv run oarc-crawlers youtube playlist --url "https://youtube.com/playlist?list=..."
uv run oarc-crawlers youtube captions --url "https://youtube.com/watch?v=..."
uv run oarc-crawlers youtube search --query "machine learning"

# GitHub operations
uv run oarc-crawlers github clone --url "https://github.com/user/repo"
uv run oarc-crawlers github analyze --url "https://github.com/user/repo"
uv run oarc-crawlers github search --query "python crawler"

# ArXiv operations
uv run oarc-crawlers arxiv download --id "2103.00020"
uv run oarc-crawlers arxiv search --query "quantum computing"
uv run oarc-crawlers arxiv latex --id "2103.00020"

# Web crawling (BeautifulSoup)
uv run oarc-crawlers bs crawl --url "https://example.com"
uv run oarc-crawlers bs docs --url "https://docs.python.org"
uv run oarc-crawlers bs pypi --package "requests"

# DuckDuckGo search
uv run oarc-crawlers ddg text --query "python programming" --max-results 5
uv run oarc-crawlers ddg images --query "cute cats" --max-results 10
uv run oarc-crawlers ddg news --query "technology" --max-results 3
```

### Getting Help with Commands

Each command and subcommand in the CLI has detailed help documentation that can be accessed using the `--help` flag:

```bash
uv run oarc-crawlers --help
uv run oarc-crawlers youtube --help
uv run oarc-crawlers github --help
uv run oarc-crawlers arxiv --help
uv run oarc-crawlers bs --help
uv run oarc-crawlers ddg --help
```

For example, running `uv run oarc-crawlers youtube --help` will display all available YouTube operations and their parameters, while `uv run oarc-crawlers youtube download --help` will show the specific options for downloading YouTube videos.

## YouTube Operations

### Downloading Videos

The `YouTubeDownloader` class enables you to download videos from YouTube.

```python
import asyncio
from oarc_crawlers import YouTubeDownloader

async def download_videos_example():
    downloader = YouTubeDownloader(data_dir="./data")
    
    # Basic video download
    result = await downloader.download_video(
        url="https://youtube.com/watch?v=dQw4w9WgXcQ",
        format="mp4",
        resolution="highest"
    )
    
    if result:
        print(f"Video downloaded successfully to {result['file_path']}")
        print(f"Video title: {result['metadata']['title']}")
    
    # Download with specific format and resolution
    result = await downloader.download_video(
        url="https://youtube.com/watch?v=dQw4w9WgXcQ",
        format="mp4",
        resolution="720p",
        output_path="./my_videos/",
        filename="custom_name"
    )
    
    # Get video metadata without downloading
    metadata = await downloader._extract_video_info("https://youtube.com/watch?v=dQw4w9WgXcQ")
    print(f"Video title: {metadata['title']}")
    print(f"Duration: {metadata['duration']} seconds")
    print(f"Author: {metadata['author']}")

# Run the async function
asyncio.run(download_videos_example())
```

### Working with Playlists

Download and process entire YouTube playlists.

```python
import asyncio
from oarc_crawlers import YouTubeDownloader

async def playlist_example():
    downloader = YouTubeDownloader(data_dir="./data")
    
    # Download a playlist (limited to first 5 videos)
    results = await downloader.download_playlist(
        playlist_url="https://www.youtube.com/playlist?list=PLzH6n4zXuckpKAj1_88VS-8Z6yn9zX_P6",
        format="mp4",
        max_videos=5
    )
    
    # Process playlist results
    if results and "videos" in results:
        print(f"Downloaded {len(results['videos'])} videos from playlist")
        
        # Process each video in the playlist
        for i, video in enumerate(results['videos']):
            print(f"Video {i+1}: {video['title']}")
            if "metadata_path" in video:
                print(f"  Metadata saved at: {video['metadata_path']}")
    
    # Get playlist metadata without downloading
    playlist_info = await downloader._get_playlist_info(
        "https://www.youtube.com/playlist?list=PLzH6n4zXuckpKAj1_88VS-8Z6yn9zX_P6"
    )
    print(f"Playlist title: {playlist_info['title']}")
    print(f"Number of videos: {playlist_info['video_count']}")

# Run the async function
asyncio.run(playlist_example())
```

### Extracting Captions

Extract and process captions from YouTube videos.

```python
import asyncio
from oarc_crawlers import YouTubeDownloader

async def captions_example():
    downloader = YouTubeDownloader(data_dir="./data")
    
    # Extract captions from a video
    captions_result = await downloader.extract_captions(
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        languages=['en', 'es', 'fr']  # Try these languages
    )
    
    if captions_result and "captions" in captions_result:
        # Process available captions
        available_langs = captions_result["captions"].keys()
        print(f"Captions available in {len(available_langs)} languages: {', '.join(available_langs)}")
        
        # Access English captions if available
        if 'en' in captions_result["captions"]:
            en_captions = captions_result["captions"]["en"]
            print(f"English captions sample: {en_captions[:100]}...")
            
            # Save captions to a text file manually
            with open("captions.txt", "w", encoding="utf-8") as f:
                f.write(en_captions)
    
    # Stream chat for a livestream (if applicable)
    try:
        chat_messages = await downloader.fetch_stream_chat(
            video_id="dQw4w9WgXcQ",
            max_messages=100
        )
        print(f"Retrieved {len(chat_messages)} chat messages")
    except Exception as e:
        print(f"Could not retrieve chat: {e}")

# Run the async function
asyncio.run(captions_example())
```

## GitHub Operations

### Cloning Repositories

Clone GitHub repositories for analysis.

```python
import asyncio
from oarc_crawlers import GitHubCrawler
from pathlib import Path

async def clone_repo_example():
    crawler = GitHubCrawler(data_dir="./data")
    
    # Basic repository cloning
    repo_url = "https://github.com/Ollama-Agent-Roll-Cage/oarc-crawlers"
    repo_path = await crawler.clone_repo(repo_url)
    
    if repo_path:
        print(f"Repository cloned to: {repo_path}")
        
        # Check if specific files exist
        readme_path = repo_path / "README.md"
        if readme_path.exists():
            print("README.md found in repository")
    
    # Clone with temporary directory
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_path = await crawler.clone_repo(repo_url, temp_dir=temp_dir)
        print(f"Repository temporarily cloned to: {repo_path}")
        # The repository will be removed once the with block exits
    
    # Clone and store with comprehensive result
    result_path = await crawler.clone_and_store_repo(repo_url)
    print(f"Repository processed and stored at: {result_path}")

# Run the async function
asyncio.run(clone_repo_example())
```

### Analyzing Code

Analyze code within GitHub repositories.

```python
import asyncio
from oarc_crawlers import GitHubCrawler
import pandas as pd

async def analyze_code_example():
    crawler = GitHubCrawler(data_dir="./data")
    
    # Clone and process repository into DataFrame
    repo_url = "https://github.com/Ollama-Agent-Roll-Cage/oarc-crawlers"
    repo_path = await crawler.clone_repo(repo_url)
    
    if repo_path:
        # Process repository to DataFrame
        df = await crawler.process_repo_to_dataframe(repo_path, max_file_size_kb=500)
        
        # Analyze code by extension
        extensions = df['extension'].value_counts()
        print("File extensions in the repository:")
        print(extensions)
        
        # Find Python files
        python_files = df[df['language'] == 'Python']
        print(f"\nFound {len(python_files)} Python files")
        
        # Look for specific patterns
        if 'content' in df.columns:
            async_files = df[df['content'].str.contains('async def', na=False)]
            print(f"\nFound {len(async_files)} files with async functions")
            
            for _, row in async_files.head(3).iterrows():
                print(f"File: {row['filepath']}")
                
        # Get repository summary
        summary = await crawler.get_repo_summary(repo_url)
        print(f"\nRepository Summary:\n{summary}")

# Run the async function
asyncio.run(analyze_code_example())
```

### Search Repositories

Search within repositories for specific code patterns.

```python
import asyncio
from oarc_crawlers import GitHubCrawler

async def search_repo_example():
    crawler = GitHubCrawler(data_dir="./data")
    repo_url = "https://github.com/Ollama-Agent-Roll-Cage/oarc-crawlers"
    
    # Search for specific content in the repository
    query_result = await crawler.query_repo_content(
        repo_url=repo_url,
        query="ParquetStorage"
    )
    print(f"Search results for 'ParquetStorage':\n{query_result}")
    
    # Find similar code to a given snippet
    code_snippet = """def calculate_mean(values):
    return sum(values) / len(values)"""
    
    similar_code = await crawler.find_similar_code(
        repo_url=repo_url,
        code_snippet=code_snippet
    )
    print(f"\nSimilar code found:\n{similar_code}")
    
    # Alternative method: direct search through a cloned repository
    repo_path = await crawler.clone_repo(repo_url)
    if repo_path:
        # Process repository to DataFrame
        df = await crawler.process_repo_to_dataframe(repo_path)
        
        # Search for specific function names
        if 'content' in df.columns:
            save_functions = df[df['content'].str.contains('def save_', na=False)]
            print(f"\nFound {len(save_functions)} functions with 'save_' pattern")

# Run the async function
asyncio.run(search_repo_example())
```

## Search Operations

### DuckDuckGo Text Search

Perform text searches using the DuckDuckGo search engine.

```python
import asyncio
from oarc_crawlers import DuckDuckGoSearcher

async def text_search_example():
    searcher = DuckDuckGoSearcher(data_dir="./data")
    
    # Basic text search
    results = await searcher.text_search(
        search_query="OARC Python framework",
        max_results=5
    )
    
    if results and isinstance(results, dict) and 'results' in results:
        print(f"Found {len(results['results'])} text search results")
        
        # Process search results
        for i, result in enumerate(results['results']):
            print(f"\nResult {i+1}:")
            print(f"Title: {result.get('title', 'No title')}")
            print(f"URL: {result.get('href', 'No URL')}")
            if 'body' in result:
                body = result['body']
                print(f"Summary: {body[:100]}..." if body else "No summary")
    
    # Search with filter parameter
    filtered_results = await searcher.text_search(
        search_query="Python crawler github",
        max_results=3,
        region="wt-wt",  # Use worldwide results
        safesearch="moderate"  # moderate safesearch
    )
    
    if filtered_results:
        print(f"\nFiltered search returned {len(filtered_results.get('results', []))} results")

# Run the async function
asyncio.run(text_search_example())
```

### News and Image Search

Perform news and image searches using the DuckDuckGo search engine.

```python
import asyncio
from oarc_crawlers import DuckDuckGoSearcher

async def multimedia_search_example():
    searcher = DuckDuckGoSearcher(data_dir="./data")
    
    # News search
    news_results = await searcher.news_search(
        search_query="artificial intelligence",
        max_results=3
    )
    
    if news_results and 'results' in news_results:
        print(f"Found {len(news_results['results'])} news articles")
        
        for i, article in enumerate(news_results['results']):
            print(f"\nNews Article {i+1}:")
            print(f"Title: {article.get('title', 'No title')}")
            print(f"Source: {article.get('source', 'Unknown source')}")
            if 'excerpt' in article:
                print(f"Excerpt: {article['excerpt'][:100]}...")
    
    # Image search
    image_results = await searcher.image_search(
        search_query="python programming",
        max_results=5
    )
    
    if image_results and 'results' in image_results:
        print(f"\nFound {len(image_results['results'])} images")
        
        for i, image in enumerate(image_results['results']):
            print(f"\nImage {i+1}:")
            print(f"Title: {image.get('title', 'No title')}")
            print(f"Image URL: {image.get('image', 'No URL')}")
            print(f"Source: {image.get('source', 'Unknown source')}")

# Run the async function
asyncio.run(multimedia_search_example())
```

## ArXiv Operations

### Downloading Papers

Download and process academic papers from ArXiv.

```python
import asyncio
from oarc_crawlers import ArxivFetcher

async def download_papers_example():
    fetcher = ArxivFetcher(data_dir="./data")
    
    # Get paper info by ID
    arxiv_id = "2103.00020"  # Example ArXiv ID
    paper_info = await fetcher.fetch_paper_info(arxiv_id)
    
    if paper_info:
        print(f"Paper Title: {paper_info.get('title', 'Unknown')}")
        print(f"Authors: {', '.join(paper_info.get('authors', ['Unknown']))}")
        print(f"Categories: {', '.join(paper_info.get('categories', ['None']))}")
        
        # Access abstract
        if 'abstract' in paper_info:
            abstract = paper_info['abstract']
            print(f"Abstract preview: {abstract[:150]}...")
        
        # Download PDF
        if 'pdf_url' in paper_info:
            print(f"PDF URL: {paper_info['pdf_url']}")
            # Actual download would happen internally when requested
    
    # Format paper for learning (special formatting)
    formatted_paper = await ArxivFetcher.format_paper_for_learning(paper_info)
    print(f"\nFormatted paper sections: {len(formatted_paper.split('##'))}")

# Run the async function
asyncio.run(download_papers_example())
```

### Extracting LaTeX Sources

Extract and process LaTeX source files from ArXiv papers.

```python
import asyncio
from oarc_crawlers import ArxivFetcher

async def latex_source_example():
    fetcher = ArxivFetcher(data_dir="./data")
    
    # Get paper with LaTeX source
    arxiv_id = "2103.00020"  # Example ArXiv ID
    result = await fetcher.fetch_paper_with_latex(arxiv_id)
    
    if result:
        # Process the LaTeX source
        if 'latex_content' in result:
            latex_content = result['latex_content']
            print(f"LaTeX content length: {len(latex_content)} characters")
            
            # Preview the content
            print(f"LaTeX preview: {latex_content[:200]}...")
            
            # Save to a file (if needed)
            with open(f"{arxiv_id}.tex", "w", encoding="utf-8") as f:
                f.write(latex_content)
        
        # Extract source directly
        source_result = await fetcher.download_source(arxiv_id)
        if source_result and 'source_files' in source_result:
            print(f"\nDownloaded {len(source_result['source_files'])} source files")
            
            # List source files
            for i, file in enumerate(source_result['source_files'][:5]):  # Show first 5
                print(f"Source file {i+1}: {file}")

# Run the async function
asyncio.run(latex_source_example())
```

## Web Crawling

### Crawling Websites

Extract content from general websites using BeautifulSoup.

```python
import asyncio
from oarc_crawlers import BSWebCrawler

async def crawl_website_example():
    crawler = BSWebCrawler(data_dir="./data")
    
    # Fetch content from a URL
    url = "https://example.com"
    html_content = await BSWebCrawler.fetch_url_content(url)
    
    if html_content:
        # Extract text content
        text_content = await BSWebCrawler.extract_text_from_html(html_content)
        print(f"Extracted {len(text_content)} characters of text")
        print(f"Text preview: {text_content[:150]}...")
        
        # Full crawl with storage
        result = await crawler.crawl_website(url)
        if result:
            print(f"\nCrawl completed and stored at: {result}")
    
    # Crawl a documentation site (specialized extraction)
    doc_url = "https://docs.python.org/3/library/asyncio.html"
    doc_result = await crawler.crawl_documentation_site(doc_url)
    
    if doc_result:
        print(f"\nDocumentation crawl stored at: {doc_result}")

# Run the async function
asyncio.run(crawl_website_example())
```

### Extracting Specific Content

Extract and process specific types of content from websites.

```python
import asyncio
from oarc_crawlers import BSWebCrawler

async def extract_specific_content_example():
    crawler = BSWebCrawler(data_dir="./data")
    
    # Extract documentation content
    doc_url = "https://docs.python.org/3/library/asyncio.html"
    html_content = await BSWebCrawler.fetch_url_content(doc_url)
    
    if html_content:
        # Extract documentation-specific content
        doc_data = await BSWebCrawler.extract_documentation_content(html_content, doc_url)
        
        if doc_data:
            print(f"Documentation title: {doc_data.get('title', 'Unknown')}")
            
            # Process code snippets
            if 'code_snippets' in doc_data and doc_data['code_snippets']:
                print(f"Found {len(doc_data['code_snippets'])} code snippets")
                # Show first snippet
                if doc_data['code_snippets']:
                    print(f"First snippet: {doc_data['code_snippets'][0][:100]}...")
            
            # Format documentation for better readability
            formatted_doc = await BSWebCrawler.format_documentation(doc_data)
            print(f"\nFormatted documentation length: {len(formatted_doc)} characters")
    
    # Extract PyPI package information
    pypi_url = "https://pypi.org/project/requests/"
    pypi_html = await BSWebCrawler.fetch_url_content(pypi_url)
    
    if pypi_html:
        pypi_data = await BSWebCrawler.extract_pypi_content(pypi_html, "requests")
        
        if pypi_data:
            print(f"\nPackage name: {pypi_data.get('name', 'Unknown')}")
            print(f"Version: {pypi_data.get('version', 'Unknown')}")
            
            # Format PyPI info
            formatted_pypi = await BSWebCrawler.format_pypi_info(pypi_data)
            print(f"Formatted PyPI info length: {len(formatted_pypi)} characters")

# Run the async function
asyncio.run(extract_specific_content_example())
```

## Data Management

### Working with Parquet Files

Save, load, and manipulate data using the ParquetStorage utility.

```python
import pandas as pd
from oarc_crawlers import ParquetStorage
from pathlib import Path

# Create test data directory
data_dir = Path("./test_data")
data_dir.mkdir(exist_ok=True)

# Example 1: Save dictionary to Parquet
data = {
    'name': 'Example Dataset',
    'timestamp': '2025-04-11T14:30:00Z',
    'values': [1, 2, 3, 4, 5],
    'metadata': {'source': 'manual entry', 'version': '1.0'}
}
file_path = data_dir / "dict_example.parquet"
ParquetStorage.save_to_parquet(data, file_path)
print(f"Dictionary saved to {file_path}")

# Example 2: Save DataFrame to Parquet
df = pd.DataFrame({
    'id': range(1, 6),
    'name': ['Alice', 'Bob', 'Charlie', 'Dave', 'Eve'],
    'score': [95, 87, 91, 76, 88]
})
df_path = data_dir / "df_example.parquet"
ParquetStorage.save_to_parquet(df, df_path)
print(f"DataFrame saved to {df_path}")

# Example 3: Load data from Parquet
loaded_df = ParquetStorage.load_from_parquet(df_path)
if loaded_df is not None:
    print(f"\nLoaded DataFrame with {len(loaded_df)} rows and {len(loaded_df.columns)} columns")
    print(loaded_df.head())

# Example 4: Append data to existing Parquet
new_data = pd.DataFrame({
    'id': [6, 7],
    'name': ['Frank', 'Grace'],
    'score': [92, 89]
})
ParquetStorage.append_to_parquet(new_data, df_path)

# Verify append worked
updated_df = ParquetStorage.load_from_parquet(df_path)
if updated_df is not None:
    print(f"\nUpdated DataFrame now has {len(updated_df)} rows")
    print(updated_df.tail(3))  # Show last 3 rows (should include appended data)
```

### Converting Between Formats

Convert data between different formats using the ParquetStorage utility.

```python
import pandas as pd
import json
from pathlib import Path
from oarc_crawlers import ParquetStorage

# Create test data directory
data_dir = Path("./test_data")
data_dir.mkdir(exist_ok=True)

# Example: Convert JSON to Parquet
json_data = {
    "papers": [
        {"id": "1901.00001", "title": "Paper 1", "authors": ["Author A", "Author B"]},
        {"id": "1901.00002", "title": "Paper 2", "authors": ["Author C"]},
        {"id": "1901.00003", "title": "Paper 3", "authors": ["Author A", "Author D"]}
    ],
    "metadata": {
        "source": "ArXiv",
        "date_extracted": "2025-04-11"
    }
}

# Save JSON to a file
json_path = data_dir / "papers.json"
with open(json_path, 'w') as f:
    json.dump(json_data, f)
print(f"JSON data saved to {json_path}")

# Load JSON and convert to Parquet
with open(json_path, 'r') as f:
    loaded_json = json.load(f)

# Convert papers list to DataFrame
papers_df = pd.DataFrame(loaded_json["papers"])

# Save to Parquet
parquet_path = data_dir / "papers.parquet"
ParquetStorage.save_to_parquet(papers_df, parquet_path)
print(f"Converted JSON to Parquet: {parquet_path}")

# Convert Parquet to CSV
loaded_df = ParquetStorage.load_from_parquet(parquet_path)
if loaded_df is not None:
    csv_path = data_dir / "papers.csv"
    loaded_df.to_csv(csv_path, index=False)
    print(f"Converted Parquet to CSV: {csv_path}")
    
    # Convert back from CSV to Parquet (round trip)
    csv_df = pd.read_csv(csv_path)
    roundtrip_path = data_dir / "roundtrip.parquet"
    ParquetStorage.save_to_parquet(csv_df, roundtrip_path)
    print(f"Converted CSV back to Parquet: {roundtrip_path}")

# Create Excel file from Parquet data
if loaded_df is not None:
    excel_path = data_dir / "papers.xlsx"
    loaded_df.to_excel(excel_path, index=False)
    print(f"Converted Parquet to Excel: {excel_path}")
```

### Working with the Parquet Storage System

All crawler modules utilize the `ParquetStorage` class for efficient data handling in the Parquet format. The following examples demonstrate its basic usage for saving, loading, and appending data.

```python
from oarc_crawlers import ParquetStorage
import pandas as pd

# Example 1: Save dictionary data to parquet
data = {
    'name': 'Example Dataset',
    'timestamp': '2025-04-11T14:30:00Z',
    'values': [1, 2, 3, 4, 5],
    'metadata': {'source': 'manual entry', 'version': '1.0'}
}
ParquetStorage.save_to_parquet(data, './data/example.parquet')

# Example 2: Save DataFrame to parquet
df = pd.DataFrame({
    'id': range(1, 6),
    'name': ['Alice', 'Bob', 'Charlie', 'Dave', 'Eve'],
    'score': [95, 87, 91, 76, 88]
})
ParquetStorage.save_to_parquet(df, './data/dataframe_example.parquet')

# Example 3: Load data from parquet
loaded_df = ParquetStorage.load_from_parquet('./data/dataframe_example.parquet')
print(loaded_df.head())

# Example 4: Append data to existing parquet file
new_data = {
    'id': 6,
    'name': 'Frank',
    'score': 92
}
ParquetStorage.append_to_parquet(new_data, './data/dataframe_example.parquet')

# Example 5: Working with multiple records
records = [
    {'date': '2025-04-01', 'value': 10.5},
    {'date': '2025-04-02', 'value': 11.2},
    {'date': '2025-04-03', 'value': 9.8}
]
ParquetStorage.save_to_parquet(records, './data/time_series.parquet')
```