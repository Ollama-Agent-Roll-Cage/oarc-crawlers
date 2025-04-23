# OARC-Crawlers Examples

This document provides practical examples for using the `oarc-crawlers` package. It covers the core functionalities, including data storage with the `ParquetStorage` system, usage of individual crawler modules for platforms like YouTube, GitHub, ArXiv, and DuckDuckGo, as well as techniques for accessing and analyzing the collected data.

## Table of Contents

- [CLI Examples](#cli-examples)
  - [Basic CLI Usage](#basic-cli-usage)
  - [YouTube CLI Examples](#youtube-cli-examples)
  - [GitHub CLI Examples](#github-cli-examples)
  - [ArXiv CLI Examples](#arxiv-cli-examples)
    - [Download LaTeX Source](#download-latex-source)
    - [Search for Papers](#search-for-papers)
    - [Extract LaTeX Content](#extract-latex-content)
    - [Extract Keywords](#extract-keywords)
    - [Extract References](#extract-references)
    - [Extract Mathematical Equations](#extract-mathematical-equations)
    - [Fetch Category Papers](#fetch-category-papers)
    - [Batch Processing](#batch-processing)
    - [Generate Citation Network](#generate-citation-network)
  - [Web Crawler CLI Examples](#web-crawler-cli-examples)
  - [DuckDuckGo CLI Examples](#duckduckgo-cli-examples)
  - [Data Management CLI Examples](#data-management-cli-examples)
- [API Examples](#api-examples)
  - [Basic API Usage](#basic-api-usage)
    - [Initializing Crawlers](#initializing-crawlers)
    - [Configuring Storage Paths](#configuring-storage-paths)
    - [Error Handling](#error-handling)
  - [YouTube API Examples](#youtube-api-examples)
    - [Download a Video](#download-a-video)
    - [Download a Playlist](#download-a-playlist)
    - [Extract Captions](#extract-captions)
    - [Search Videos](#search-videos)
    - [Fetch Chat Messages](#fetch-chat-messages)
  - [GitHub API Examples](#github-api-examples)
    - [Clone a Repository](#clone-a-repository)
    - [Analyze Code](#analyze-code)
    - [Search Repositories](#search-repositories)
  - [ArXiv API Examples](#arxiv-api-examples)
    - [Downloading Papers](#downloading-papers)
    - [Extracting LaTeX Sources](#extracting-latex-sources)
    - [Extracting Keywords and References](#extracting-keywords-and-references)
    - [Working with Categories](#working-with-categories)
    - [Generate Citation Network](#generate-citation-network-1)
  - [Web Crawler API Examples](#web-crawler-api-examples)
    - [Crawling Websites](#crawling-websites)
    - [Extracting Specific Content](#extracting-specific-content)
  - [DuckDuckGo API Examples](#duckduckgo-api-examples)
    - [Text Search](#text-search)
    - [News and Image Search](#news-and-image-search)
  - [Data Management API Examples](#data-management-api-examples)
    - [Working with Parquet Files](#working-with-parquet-files)
    - [Converting Between Formats](#converting-between-formats)
    - [Working with the Parquet Storage System](#working-with-the-parquet-storage-system)

---

## CLI Examples

### Basic CLI Usage

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
oarc-crawlers arxiv keywords --id "2103.00020"
oarc-crawlers arxiv references --id "2103.00020"
oarc-crawlers arxiv category --category "cs.AI"

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

Each command and subcommand in the CLI has detailed help documentation that can be accessed using the `--help` flag:

```bash
oarc-crawlers --help
oarc-crawlers yt --help
oarc-crawlers gh --help
oarc-crawlers arxiv --help
oarc-crawlers web --help
oarc-crawlers ddg --help
```

---

### YouTube CLI Examples

```bash
# Download a video with default settings
oarc-crawlers yt download --url "https://youtube.com/watch?v=dQw4w9WgXcQ"

# Download a video with specific resolution
oarc-crawlers yt download --url "https://youtube.com/watch?v=dQw4w9WgXcQ" --resolution 720p

# Extract audio only (mp3)
oarc-crawlers yt download --url "https://youtube.com/watch?v=dQw4w9WgXcQ" --extract-audio --format mp3

# Download to a specific location with custom filename
oarc-crawlers yt download --url "https://youtube.com/watch?v=dQw4w9WgXcQ" --output-path ./my_videos --filename my_video

# Download a playlist (default: 10 videos)
oarc-crawlers yt playlist --url "https://youtube.com/playlist?list=PLzH6n4zXuckpKAj1_88VS-8Z6yn9zX_P6"

# Download a playlist with more videos and different format
oarc-crawlers yt playlist --url "https://youtube.com/playlist?list=PLzH6n4zXuckpKAj1_88VS-8Z6yn9zX_P6" --max-videos 20 --format webm

# Extract captions in multiple languages
oarc-crawlers yt captions --url "https://youtube.com/watch?v=dQw4w9WgXcQ" --languages "en,es,fr"

# Search for videos
oarc-crawlers yt search --query "python asynchronous programming" --limit 5

# Fetch chat messages from a live stream
oarc-crawlers yt chat --video-id dQw4w9WgXcQ --max-messages 500 --duration 300
```

---

### GitHub CLI Examples

```bash
# Clone a repository
oarc-crawlers gh clone --url "https://github.com/Ollama-Agent-Roll-Cage/oarc-crawlers"

# Analyze a repository
oarc-crawlers gh analyze --url "https://github.com/Ollama-Agent-Roll-Cage/oarc-crawlers"

# Search for similar code
oarc-crawlers gh find-similar --url "https://github.com/Ollama-Agent-Roll-Cage/oarc-crawlers" --code "def calculate_mean(values): return sum(values) / len(values)"
```

---

### ArXiv CLI Examples

#### Download LaTeX Source

```bash
oarc-crawlers arxiv download --id 2103.00020
```

#### Search for Papers

```bash
oarc-crawlers arxiv search --query "quantum computing" --limit 5
```

#### Extract LaTeX Content

```bash
oarc-crawlers arxiv latex --id 2103.00020
```

#### Extract Keywords

```bash
oarc-crawlers arxiv keywords --id 2103.00020
oarc-crawlers arxiv keywords --id 2103.00020 --output-file keywords.json
```

#### Extract References

```bash
oarc-crawlers arxiv references --id 2103.00020
oarc-crawlers arxiv references --id 2103.00020 --output-file refs.json
```

#### Extract Mathematical Equations

```bash
oarc-crawlers arxiv equations --id 2103.00020
oarc-crawlers arxiv equations --id 2103.00020 --output-file equations.json
```

#### Fetch Category Papers

```bash
oarc-crawlers arxiv category --category cs.AI --limit 10
```

#### Batch Processing

```bash
oarc-crawlers arxiv batch --ids "2103.00020,2304.12749" --keywords --references
```

#### Generate Citation Network

```bash
oarc-crawlers arxiv citation-network --ids "2103.00020,2304.12749" --max-depth 2 --output-file network.json
```

---

### Web Crawler CLI Examples

```bash
# Crawl a website
oarc-crawlers web crawl --url "https://www.python.org/"

# Extract documentation content
oarc-crawlers web docs --url "https://docs.python.org/3/library/asyncio.html"
```

---

### DuckDuckGo CLI Examples

```bash
# Perform a text search
oarc-crawlers ddg text --query "OARC Python framework" --max-results 5

# Perform a news search
oarc-crawlers ddg news --query "artificial intelligence" --max-results 3

# Perform an image search
oarc-crawlers ddg images --query "python programming" --max-results 5
```

---

### Data Management CLI Examples

```bash
# View a Parquet file
oarc-crawlers data view ./data/example.parquet --max-rows 20
```

---

## API Examples

### Basic API Usage

#### Initializing Crawlers

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

#### Configuring Storage Paths

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

#### Error Handling

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

---

### YouTube API Examples

```python
import asyncio
from oarc_crawlers import YTCrawler

async def download_video_example():
    yt = YTCrawler(data_dir="./data")
    # Download a video with default settings
    result = await yt.download_video(
        url="https://youtube.com/watch?v=dQw4w9WgXcQ"
    )
    print(f"Downloaded: {result['file_path']} ({result['format']})")

    # Download with specific resolution and format
    result = await yt.download_video(
        url="https://youtube.com/watch?v=dQw4w9WgXcQ",
        video_format="mp4",
        resolution="720p",
        output_path="./my_videos/",
        filename="custom_name"
    )
    print(f"Downloaded: {result['file_path']}")

    # Download audio only as mp3
    result = await yt.download_video(
        url="https://youtube.com/watch?v=dQw4w9WgXcQ",
        video_format="mp3",
        extract_audio=True
    )
    print(f"Downloaded audio: {result['file_path']}")

asyncio.run(download_video_example())
```

```python
import asyncio
from oarc_crawlers import YTCrawler

async def download_playlist_example():
    yt = YTCrawler(data_dir="./data")
    # Download a playlist (limit to 5 videos)
    result = await yt.download_playlist(
        playlist_url="https://www.youtube.com/playlist?list=PLzH6n4zXuckpKAj1_88VS-8Z6yn9zX_P6",
        format="mp4",
        max_videos=5
    )
    print(f"Downloaded {len(result['videos'])} videos from playlist '{result['title']}'")

asyncio.run(download_playlist_example())
```

```python
import asyncio
from oarc_crawlers import YTCrawler

async def captions_example():
    yt = YTCrawler(data_dir="./data")
    # Extract captions in multiple languages
    captions_result = await yt.extract_captions(
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        languages=['en', 'es', 'fr']
    )
    print(f"Captions available: {list(captions_result['captions'].keys())}")

asyncio.run(captions_example())
```

```python
import asyncio
from oarc_crawlers import YTCrawler

async def search_videos_example():
    yt = YTCrawler(data_dir="./data")
    results = await yt.search_videos(
        query="python asynchronous programming tutorial",
        limit=10
    )
    print(f"Found {results['result_count']} videos")
    for video in results['results']:
        print(f"- {video['title']} ({video['url']})")

asyncio.run(search_videos_example())
```

```python
import asyncio
from oarc_crawlers import YTCrawler

async def fetch_chat_example():
    yt = YTCrawler(data_dir="./data")
    chat_result = await yt.fetch_stream_chat(
        video_id="dQw4w9WgXcQ",
        max_messages=100,
        duration=60
    )
    print(f"Collected {chat_result['message_count']} chat messages")
    print(f"Saved to: {chat_result.get('parquet_path', 'N/A')}")

asyncio.run(fetch_chat_example())
```

---

### GitHub API Examples

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

---

### ArXiv API Examples

#### Downloading Papers

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

#### Extracting LaTeX Sources

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

#### Extracting Keywords and References

```python
import asyncio
from oarc_crawlers import ArxivCrawler

async def extract_metadata_example():
    arxiv = ArxivCrawler(data_dir="./data")
    arxiv_id = "2103.00020"
    
    # Extract keywords
    keywords = await arxiv.extract_keywords(arxiv_id)
    print("Top keywords:")
    for kw in keywords['keywords'][:5]:
        print(f"  • {kw['keyword']} (score: {kw['score']})")
    
    # Extract references
    references = await arxiv.extract_references(arxiv_id)
    print(f"\nFound {references['reference_count']} references")
    for i, ref in enumerate(references['references'][:3], 1):
        if 'fields' in ref:  # BibTeX entry
            authors = ref.get('fields', {}).get('author', 'Unknown')
            title = ref.get('fields', {}).get('title', 'Untitled')
            print(f"  {i}. {authors}: {title}")
        else:  # Standard citation
            citation = ref.get('citation', 'Unknown citation')
            print(f"  {i}. {citation[:100]}...")

# Run the async function
asyncio.run(extract_metadata_example())
```

#### Working with Categories

```python
import asyncio
from oarc_crawlers import ArxivCrawler

async def category_example():
    arxiv = ArxivCrawler(data_dir="./data")
    
    # Get recent papers in computer science AI category
    papers = await arxiv.fetch_category_papers("cs.AI", max_results=10)
    
    print(f"Found {papers['papers_count']} recent papers in cs.AI:")
    for i, paper in enumerate(papers['papers']):
        print(f"{i+1}. {paper['title']}")
        print(f"   Published: {paper['published'].split('T')[0]}")
        print()

# Run the async function
asyncio.run(category_example())
```

#### Generate Citation Network

```python
import asyncio
import json
from oarc_crawlers import ArxivCrawler

async def create_citation_network():
    crawler = ArxivCrawler()
    
    # Generate a citation network starting from two seed papers
    seed_papers = ["2304.12749", "2310.06825"]
    network = await crawler.generate_citation_network(seed_papers, max_depth=1)
    
    print(f"Created network with {len(network['nodes'])} nodes and {len(network['edges'])} edges")
    
    # Save network to a JSON file
    with open("citation_network.json", "w") as f:
        json.dump(network, f, indent=2)

if __name__ == "__main__":
    asyncio.run(create_citation_network())
```

---

### Web Crawler API Examples

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

---

### DuckDuckGo API Examples

```python
import asyncio
from oarc_crawlers import DDGCrawler

async def ddg_examples():
    # Initialize the searcher
    searcher = DDGCrawler(data_dir="./data")

    # Text search (returns markdown-formatted string)
    try:
        text_results = await searcher.text_search("quantum computing", max_results=3)
        print(text_results)
    except Exception as e:
        print(f"Error during text search: {e}")

    # Image search (returns markdown-formatted string)
    try:
        image_results = await searcher.image_search("mountain landscape", max_results=2)
        print(image_results)
    except Exception as e:
        print(f"Error during image search: {e}")

    # News search (returns markdown-formatted string)
    try:
        news_results = await searcher.news_search("artificial intelligence", max_results=3)
        print(news_results)
    except Exception as e:
        print(f"Error during news search: {e}")

    # Error handling demonstration
    try:
        invalid_result = await searcher.text_search("", max_results=-1)
        print(invalid_result)
    except Exception as e:
        print(f"Caught exception: {e}")

asyncio.run(ddg_examples())
```

**Note:**  
- All DuckDuckGo API methods return markdown-formatted strings for direct printing.
- Errors are raised as exceptions and should be caught as shown above.
- Results are also saved to Parquet files in the configured data directory.

---

### Data Management API Examples

#### Working with Parquet Files

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

#### Converting Between Formats

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

#### Working with the Parquet Storage System

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