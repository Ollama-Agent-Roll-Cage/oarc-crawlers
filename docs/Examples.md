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
from oarc_crawlers import YTCrawler, GHCrawler, ArxivCrawler, DDGCrawler, WebCrawler

# Initialize with default data directory
yt = YTCrawler()
gh = GHCrawler()
arxiv = ArxivCrawler()
ddg = DDGCrawler()
web = WebCrawler()

# Initialize with custom data directory
data_dir = "./my_custom_data"
yt_custom = YTCrawler(data_dir=data_dir)
gh_custom = GHCrawler(data_dir=data_dir)
arxiv_custom = ArxivCrawler(data_dir=data_dir)
ddg_custom = DDGCrawler(data_dir=data_dir)
web_custom = WebCrawler(data_dir=data_dir)
```

### Configuring Storage Paths

The storage system can be configured through initialization parameters or environment variables.

```python
import os
from oarc_crawlers import YTCrawler, ParquetStorage

# Method 1: Set environment variable
os.environ["OARC_DATA_DIR"] = "/path/to/data"

# Method 2: Pass directly to crawler instances
yt = YTCrawler(data_dir="/custom/path/data")

# Method 3: Create directory structure programmatically
import pathlib
data_dir = pathlib.Path("./project_data")
data_dir.mkdir(exist_ok=True)
yt = YTCrawler(data_dir=str(data_dir))

# Accessing default paths within a module
yt = YTCrawler()
video_dir = yt.data_dir / "videos"
print(f"Videos will be stored in: {video_dir}")
```

### Error Handling

The crawlers provide comprehensive error handling to manage common issues.

```python
import asyncio
from oarc_crawlers import YTCrawler, GHCrawler, ArxivCrawler

async def error_handling_examples():
    # Example 1: Using try/except with the API
    yt = YTCrawler()
    try:
        result = await yt.download_video("https://youtube.com/watch?v=invalid_id")
    except Exception as e:
        print(f"Error downloading video: {e}")

    # Example 2: Checking return values
    gh = GHCrawler()
    result = await gh.clone_repo("https://github.com/nonexistent/repo")
    if result is None:
        print("Repository cloning failed")

    # Example 3: Using built-in fallback mechanisms
    try:
        paper = await arxiv.fetch_paper_info("invalid_id")
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
# YouTube operations
oarc-crawlers yt download --url "https://youtube.com/watch?v=..."
oarc-crawlers yt playlist --url "https://youtube.com/playlist?list=..."
oarc-crawlers yt captions --url "https://youtube.com/watch?v=..."
oarc-crawlers yt search --query "machine learning"

# GitHub operations
oarc-crawlers gh clone --url "https://github.com/user/repo"
oarc-crawlers gh analyze --url "https://github.com/user/repo"
oarc-crawlers gh find-similar --url "https://github.com/user/repo" --code "def foo():"

# ArXiv operations
oarc-crawlers arxiv download --id "2103.00020"
oarc-crawlers arxiv search --query "quantum computing"
oarc-crawlers arxiv latex --id "2103.00020"

# Web crawling (BeautifulSoup)
oarc-crawlers web crawl --url "https://example.com"
oarc-crawlers web docs --url "https://docs.python.org"
oarc-crawlers web pypi --package "requests"

# DuckDuckGo search
oarc-crawlers ddg text --query "python programming" --max-results 5
oarc-crawlers ddg images --query "cute cats" --max-results 10
oarc-crawlers ddg news --query "technology" --max-results 3

# Data management
oarc-crawlers data view ./data/example.parquet --max-rows 20
```

### Getting Help with Commands

Each command and subcommand in the CLI has detailed help documentation that can be accessed using the `--help` flag:

```bash
oarc-crawlers --help
oarc-crawlers yt --help
oarc-crawlers gh --help
oarc-crawlers arxiv --help
oarc-crawlers web --help
oarc-crawlers ddg --help
```

For example, running `oarc-crawlers yt --help` will display all available YouTube operations and their parameters, while `oarc-crawlers yt download --help` will show the specific options for downloading YouTube videos.

## YouTube Operations

### Downloading Videos

```python
import asyncio
from oarc_crawlers import YTCrawler

async def download_videos_example():
    yt = YTCrawler(data_dir="./data")
    # Basic video download
    result = await yt.download_video(
        url="https://youtube.com/watch?v=dQw4w9WgXcQ",
        video_format="mp4",
        resolution="highest"
    )
    if result:
        print(f"Video downloaded successfully to {result['file_path']}")
        print(f"Video title: {result.get('title', 'Unknown')}")

    # Download with specific format and resolution
    result = await yt.download_video(
        url="https://youtube.com/watch?v=dQw4w9WgXcQ",
        video_format="mp4",
        resolution="720p",
        output_path="./my_videos/",
        filename="custom_name"
    )

# Run the async function
asyncio.run(download_videos_example())
```

### Working with Playlists

```python
import asyncio
from oarc_crawlers import YTCrawler

async def playlist_example():
    yt = YTCrawler(data_dir="./data")
    # Download a playlist (limited to first 5 videos)
    results = await yt.download_playlist(
        playlist_url="https://www.youtube.com/playlist?list=PLzH6n4zXuckpKAj1_88VS-8Z6yn9zX_P6",
        format="mp4",
        max_videos=5
    )
    if results and "results" in results:
        print(f"Downloaded {results['success_count']} videos from playlist")
        for i, video in enumerate(results['results']):
            print(f"Video {i+1}: {video.get('title', 'Unknown')}")

# Run the async function
asyncio.run(playlist_example())
```

### Extracting Captions

```python
import asyncio
from oarc_crawlers import YTCrawler

async def captions_example():
    yt = YTCrawler(data_dir="./data")
    captions_result = await yt.extract_captions(
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        languages=['en', 'es', 'fr']
    )
    if captions_result and "captions" in captions_result:
        available_langs = captions_result["captions"].keys()
        print(f"Captions available in: {', '.join(available_langs)}")
        if 'en' in captions_result["captions"]:
            en_captions = captions_result["captions"]["en"]
            print(f"English captions sample: {en_captions[:100]}...")

# Run the async function
asyncio.run(captions_example())
```

## GitHub Operations

### Cloning Repositories

```python
import asyncio
from oarc_crawlers import GHCrawler

async def clone_repo_example():
    gh = GHCrawler(data_dir="./data")
    repo_url = "https://github.com/Ollama-Agent-Roll-Cage/oarc-crawlers"
    repo_path = await gh.clone_repo(repo_url)
    if repo_path:
        print(f"Repository cloned to: {repo_path}")

# Run the async function
asyncio.run(clone_repo_example())
```

### Analyzing Code

```python
import asyncio
from oarc_crawlers import GHCrawler

async def analyze_code_example():
    gh = GHCrawler(data_dir="./data")
    repo_url = "https://github.com/Ollama-Agent-Roll-Cage/oarc-crawlers"
    repo_path = await gh.clone_repo(repo_url)
    if repo_path:
        df = await gh.process_repo_to_dataframe(repo_path, max_file_size_kb=500)
        print(df.head())
        summary = await gh.get_repo_summary(repo_url)
        print(f"\nRepository Summary:\n{summary}")

# Run the async function
asyncio.run(analyze_code_example())
```

### Search Repositories

```python
import asyncio
from oarc_crawlers import GHCrawler

async def search_repo_example():
    gh = GHCrawler(data_dir="./data")
    repo_url = "https://github.com/Ollama-Agent-Roll-Cage/oarc-crawlers"
    query_result = await gh.query_repo_content(
        repo_url=repo_url,
        query="ParquetStorage"
    )
    print(f"Search results for 'ParquetStorage':\n{query_result}")

    code_snippet = """def calculate_mean(values):
    return sum(values) / len(values)"""
    similar_code = await gh.find_similar_code(
        repo_url=repo_url,
        code_snippet=code_snippet
    )
    print(f"\nSimilar code found:\n{similar_code}")

# Run the async function
asyncio.run(search_repo_example())
```

## Search Operations

### DuckDuckGo Text Search

```python
import asyncio
from oarc_crawlers import DDGCrawler

async def text_search_example():
    ddg = DDGCrawler(data_dir="./data")
    results = await ddg.text_search(
        search_query="OARC Python framework",
        max_results=5
    )
    if results:
        print(results)

# Run the async function
asyncio.run(text_search_example())
```

### News and Image Search

```python
import asyncio
from oarc_crawlers import DDGCrawler

async def multimedia_search_example():
    ddg = DDGCrawler(data_dir="./data")
    news_results = await ddg.news_search(
        search_query="artificial intelligence",
        max_results=3
    )
    print(news_results)
    image_results = await ddg.image_search(
        search_query="python programming",
        max_results=5
    )
    print(image_results)

# Run the async function
asyncio.run(multimedia_search_example())
```

## ArXiv Operations

### Downloading Papers

```python
import asyncio
from oarc_crawlers import ArxivCrawler

async def download_papers_example():
    arxiv = ArxivCrawler(data_dir="./data")
    arxiv_id = "2103.00020"
    paper_info = await arxiv.fetch_paper_info(arxiv_id)
    if paper_info:
        print(f"Paper Title: {paper_info.get('title', 'Unknown')}")
        print(f"Authors: {', '.join(paper_info.get('authors', ['Unknown']))}")
        print(f"Categories: {', '.join(paper_info.get('categories', ['None']))}")
        if 'abstract' in paper_info:
            print(f"Abstract preview: {paper_info['abstract'][:150]}...")

# Run the async function
asyncio.run(download_papers_example())
```

### Extracting LaTeX Sources

```python
import asyncio
from oarc_crawlers import ArxivCrawler

async def latex_source_example():
    arxiv = ArxivCrawler(data_dir="./data")
    arxiv_id = "2103.00020"
    result = await arxiv.fetch_paper_with_latex(arxiv_id)
    if result and 'latex_content' in result:
        latex_content = result['latex_content']
        print(f"LaTeX content length: {len(latex_content)} characters")
        print(f"LaTeX preview: {latex_content[:200]}...")

    source_result = await arxiv.download_source(arxiv_id)
    if source_result and 'source_files' in source_result:
        print(f"\nDownloaded {len(source_result['source_files'])} source files")
        for i, file in enumerate(list(source_result['source_files'].keys())[:5]):
            print(f"Source file {i+1}: {file}")

# Run the async function
asyncio.run(latex_source_example())
```

## Web Crawling

### Crawling Websites

```python
import asyncio
from oarc_crawlers import WebCrawler

async def crawl_website_example():
    web = WebCrawler(data_dir="./data")
    url = "https://www.python.org/"
    html_content = await web.fetch_url_content(url)
    if html_content:
        text_content = WebCrawler.extract_text_from_html(html_content)
        print(f"Extracted {len(text_content)} characters of text")
        print(f"Text preview: {text_content[:150]}...")

# Run the async function
asyncio.run(crawl_website_example())
```

### Extracting Specific Content

```python
import asyncio
from oarc_crawlers import WebCrawler

async def extract_specific_content_example():
    web = WebCrawler(data_dir="./data")
    doc_url = "https://docs.python.org/3/library/asyncio.html"
    html_content = await web.fetch_url_content(doc_url)
    if html_content:
        doc_data = WebCrawler.extract_documentation_content(html_content, doc_url)
        if doc_data:
            print(f"Documentation title: {doc_data.get('title', 'Unknown')}")
            if 'code_snippets' in doc_data and doc_data['code_snippets']:
                print(f"Found {len(doc_data['code_snippets'])} code snippets")
                print(f"First snippet: {doc_data['code_snippets'][0][:100]}...")

# Run the async function
asyncio.run(extract_specific_content_example())
```

## Data Management

### Working with Parquet Files

```python
import pandas as pd
from oarc_crawlers import ParquetStorage
from pathlib import Path

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
    print(updated_df.tail(3))
```

### Converting Between Formats

```python
import pandas as pd
import json
from pathlib import Path
from oarc_crawlers import ParquetStorage

data_dir = Path("./test_data")
data_dir.mkdir(exist_ok=True)

# Convert JSON to Parquet
json_data = {
    "papers": [
        {"id": "1901.00001", "title": "Paper 1", "authors": ["Author A", "Author B"]},
        {"id": "1901.00002", "title": "Paper 2", "authors": ["Author C"]},
        {"id": "1901.00003", "title": "Paper 3", "authors": ["Author A", "Author D"]}
    ]
}
json_path = data_dir / "papers.json"
with open(json_path, 'w') as f:
    json.dump(json_data, f)
print(f"JSON data saved to {json_path}")

with open(json_path, 'r') as f:
    loaded_json = json.load(f)
papers_df = pd.DataFrame(loaded_json["papers"])
parquet_path = data_dir / "papers.parquet"
ParquetStorage.save_to_parquet(papers_df, parquet_path)
print(f"Converted JSON to Parquet: {parquet_path}")

# Convert Parquet to CSV
loaded_df = ParquetStorage.load_from_parquet(parquet_path)
if loaded_df is not None:
    csv_path = data_dir / "papers.csv"
    loaded_df.to_csv(csv_path, index=False)
    print(f"Converted Parquet to CSV: {csv_path}")

    # Convert back from CSV to Parquet
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