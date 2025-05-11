# Getting Started with OARC-Crawlers

## Installation

```bash
# Basic installation
pip install oarc-crawlers

# Or recommended installation with UV (faster)
pip install uv
uv pip install oarc-crawlers

# CLI Quick Start

# Show available commands
oarc-crawlers --help

# YouTube Examples
oarc-crawlers yt download --url "https://youtube.com/watch?v=dQw4w9WgXcQ"
oarc-crawlers yt playlist --url "https://youtube.com/playlist?list=..." --max-videos 5
oarc-crawlers yt captions --url "https://youtube.com/watch?v=..." --languages "en,es"

# GitHub Examples
oarc-crawlers gh clone --url "https://github.com/username/repo"
oarc-crawlers gh analyze --url "https://github.com/username/repo"

# ArXiv Examples
oarc-crawlers arxiv download --id "2103.00020"
oarc-crawlers arxiv search --query "quantum computing" --limit 5

# DuckDuckGo Search Examples
oarc-crawlers ddg text --query "python async programming" --max-results 5 
oarc-crawlers ddg news --query "artificial intelligence" --max-results 3

# Web Crawling Examples
oarc-crawlers web crawl --url "https://example.com"
oarc-crawlers web pypi --package "requests"

# Python Development Examples

import asyncio
from oarc_crawlers import (
    YTCrawler,
    GHCrawler, 
    ArxivCrawler,
    DDGCrawler,
    WebCrawler
)

async def youtube_example():
    """Download a YouTube video."""
    yt = YTCrawler(data_dir="./data")
    result = await yt.download_video(
        url="https://youtube.com/watch?v=dQw4w9WgXcQ",
        video_format="mp4",
        resolution="720p"
    )
    print(f"Video saved to: {result['file_path']}")

async def github_example():
    """Analyze a GitHub repository."""
    gh = GHCrawler(data_dir="./data")
    summary = await gh.get_repo_summary(
        "https://github.com/pytorch/pytorch"
    )
    print(summary)

async def arxiv_example():
    """Download an ArXiv paper."""
    arxiv = ArxivCrawler(data_dir="./data")
    paper = await arxiv.fetch_paper_info("2103.00020")
    print(f"Title: {paper['title']}")
    print(f"Authors: {', '.join(paper['authors'])}")

async def search_example():
    """Search using DuckDuckGo."""
    ddg = DDGCrawler(data_dir="./data")
    results = await ddg.text_search(
        "python async programming",
        max_results=3
    )
    print(results)

async def web_example():
    """Crawl a webpage."""
    web = WebCrawler(data_dir="./data")
    content = await web.fetch_url_content("https://python.org")
    text = await WebCrawler.extract_text_from_html(content)
    print(text[:500])

async def main():
    """Run all examples."""
    print("\n=== YouTube Example ===")
    await youtube_example()
    
    print("\n=== GitHub Example ===")
    await github_example()
    
    print("\n=== ArXiv Example ===")
    await arxiv_example()
    
    print("\n=== Search Example ===")
    await search_example()
    
    print("\n=== Web Example ===")
    await web_example()

if __name__ == "__main__":
    asyncio.run(main())

# Basic Imports Guide

```python
# Import individual crawlers
from oarc_crawlers import YTCrawler
from oarc_crawlers import GHCrawler
from oarc_crawlers import ArxivCrawler 
from oarc_crawlers import DDGCrawler
from oarc_crawlers import WebCrawler
from oarc_crawlers import OEISCrawler

# Import ParquetStorage utility
from oarc_crawlers import ParquetStorage

# Import everything at once
from oarc_crawlers import (
    YTCrawler,
    GHCrawler, 
    ArxivCrawler,
    DDGCrawler,
    WebCrawler,
    OEISCrawler,
    ParquetStorage
)

# Example using ParquetStorage
data = {'name': 'Example', 'value': 42}
ParquetStorage.save_to_parquet(data, 'example.parquet')

# Example using OEISCrawler 
async def oeis_example():
    oeis = OEISCrawler()
    sequence = await oeis.fetch_sequence('A000045')  # Fibonacci
    print(f"Name: {sequence['name']}")
    print(f"Values: {sequence['values'][:10]}")

# Example using multiple crawlers together
async def combined_example():
    yt = YTCrawler()
    gh = GHCrawler()
    arxiv = ArxivCrawler()
    
    # Download a YouTube video about algorithms
    video = await yt.download_video("https://youtube.com/...")
    
    # Find related GitHub repos
    repos = await gh.search_repos("algorithm visualization")
    
    # Search for papers on the topic
    papers = await arxiv.search("algorithm visualization")
    
    # Save all results using ParquetStorage
    ParquetStorage.save_to_parquet({
        'video': video,
        'repos': repos,
        'papers': papers
    }, 'algorithm_research.parquet')

# Run async examples
import asyncio
asyncio.run(oeis_example())
asyncio.run(combined_example())
```

# Key Features

- Asynchronous Design: All operations are async for better performance
- Unified Storage: All data saved in Parquet format for analysis
- Modular Architecture: Each crawler is independent but shares common interfaces
- Rich CLI: Comprehensive command-line interface for all operations
- Error Handling: Built-in error handling and retry mechanisms
- Data Persistence: Automatic storage of metadata and content

# Common Configuration

```bash
# Set data directory
export OARC_DATA_DIR=~/path/to/data  # Unix/Linux
set OARC_DATA_DIR=C:\path\to\data    # Windows

# Enable debug logging
oarc-crawlers --verbose [command]

# Use custom config file
oarc-crawlers --config ~/.oarc/config.ini [command]
```