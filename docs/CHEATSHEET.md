# OARC-Crawlers Cheat Sheet

## Table of Contents
- [Installation](#installation)
- [Common Usage](#common-usage)
  - [Setting Data Directory](#setting-data-directory)
- [YouTube Operations (yt)](#youtube-operations-yt)
- [GitHub Operations (gh)](#github-operations-gh)
- [ArXiv Operations (arxiv)](#arxiv-operations-arxiv)
- [DuckDuckGo Search (ddg)](#duckduckgo-search-ddg)
- [Web Crawling (web)](#web-crawling-web)
- [Data Management (data)](#data-management-data)
- [MCP Server (mcp)](#mcp-server-mcp)
- [Build & Publish](#build--publish)
- [Common Options](#common-options)
- [Python Package Usage](#python-package-usage)
  - [Basic Import Pattern](#basic-import-pattern)
  - [Quick Examples](#quick-examples)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)

## Installation
```bash
pip install oarc-crawlers  # Basic install
# or
pip install uv && uv pip install oarc-crawlers  # Recommended install
```

## Common Usage

### Setting Data Directory
```bash
# Windows
set OARC_DATA_DIR=C:\path\to\data

# Linux/WSL
export OARC_DATA_DIR=~/path/to/data

# Or specify in code
from oarc_crawlers import YTCrawler
crawler = YTCrawler(data_dir="./my_data_dir")
```

## YouTube Operations (yt)
```bash
# Download video
oarc-crawlers yt download --url "https://www.youtube.com/watch?v=MDbdb-W4x4w&t=330s&ab_channel=MattWilliams"

# Download specific quality
oarc-crawlers yt download --url "https://www.youtube.com/watch?v=MDbdb-W4x4w&t=330s&ab_channel=MattWilliams" --resolution 720p

# Download as audio only
oarc-crawlers yt download --url "https://www.youtube.com/watch?v=MDbdb-W4x4w&t=330s&ab_channel=MattWilliams" --extract-audio --format mp3

# Download playlist (first 10 videos)
oarc-crawlers yt playlist --url "https://www.youtube.com/playlist?list=PLzH6n4zXuckquVnQ0KlMDxyXxiSO2DXOQ"

# Get video captions
oarc-crawlers yt captions --url "https://www.youtube.com/watch?v=MDbdb-W4x4w&t=330s&ab_channel=MattWilliams" --languages "en,es,fr"

# Search videos
oarc-crawlers yt search --query "python tutorials" --limit 5

# Fetch live chat messages
oarc-crawlers yt chat --video-id dQw4w9WgXcQ --max-messages 500 --duration 300
```

## GitHub Operations (gh)
```bash
# Clone repository
oarc-crawlers gh clone --url "https://github.com/user/repo"

# Analyze repository
oarc-crawlers gh analyze --url "https://github.com/user/repo"

# Find similar code snippets
oarc-crawlers gh find-similar --url "https://github.com/user/repo" --code "def example():" --language python
```

## ArXiv Operations (arxiv)
```bash
# Download paper metadata
oarc-crawlers arxiv download --id "2310.12123"

# Search papers
oarc-crawlers arxiv search --query "quantum computing" --limit 5

# Get LaTeX source
oarc-crawlers arxiv latex --id "2310.12123"
```

## DuckDuckGo Search (ddg)
```bash
# Text search
oarc-crawlers ddg text --query "python async" --max-results 5

# Image search
oarc-crawlers ddg images --query "cute cats" --max-results 10

# News search
oarc-crawlers ddg news --query "technology" --max-results 20
```

## Web Crawling (web)
```bash
# Crawl webpage
oarc-crawlers web crawl --url "https://docs.llamaindex.ai/en/stable/examples/query_engine/pandas_query_engine/"

# Save to file
oarc-crawlers web crawl --url "https://docs.llamaindex.ai/en/stable/examples/query_engine/pandas_query_engine/" --output-file page.txt

# Get docs
oarc-crawlers web docs --url "https://docs.llamaindex.ai/en/stable/examples/query_engine/pandas_query_engine/"

# Get PyPI info
oarc-crawlers web pypi --package "requests"
```

## Data Management (data)
```bash
# View Parquet file
oarc-crawlers data view ./data/example.parquet --max-rows 20
```

## MCP Server (mcp)
```bash
# Run MCP server for agent integration (default port 3000)
oarc-crawlers mcp run

# Install MCP server for VS Code integration
oarc-crawlers mcp install --name "OARC Tools"
```

## Build & Publish
```bash
# Build the package
oarc-crawlers build package

# Publish to PyPI
oarc-crawlers publish pypi

# Publish to TestPyPI
oarc-crawlers publish pypi --test
```

## Common Options
```bash
# Enable verbose output
oarc-crawlers --verbose [command]

# Use custom config
oarc-crawlers --config ~/.oarc/config.ini [command]

# Get help
oarc-crawlers --help
oarc-crawlers [command] --help
```

## Python Package Usage

### Basic Import Pattern
```python
from oarc_crawlers import (
    YTCrawler,
    GHCrawler,
    ArxivCrawler,
    DDGCrawler,
    WebCrawler,
    ParquetStorage,
)
```

### Quick Examples

#### Download a YouTube video
```python
import asyncio
from oarc_crawlers import YTCrawler

async def download_video():
    yt = YTCrawler(data_dir="./data")
    result = await yt.download_video("https://youtube.com/watch?v=dQw4w9WgXcQ")
    print(f"Video saved to: {result.get('file_path', 'N/A')}")
    print(f"Video title: {result.get('title', 'Unknown')}")

asyncio.run(download_video())
```

#### Analyze a GitHub repository
```python
import asyncio
from oarc_crawlers import GHCrawler

async def analyze_repo():
    gh = GHCrawler(data_dir="./data")
    summary = await gh.get_repo_summary("https://github.com/pytorch/pytorch")
    print(summary)

asyncio.run(analyze_repo())
```

#### Search ArXiv and download LaTeX source
```python
import asyncio
from oarc_crawlers import ArxivCrawler

async def arxiv_example():
    arxiv = ArxivCrawler(data_dir="./data")
    paper_info = await arxiv.fetch_paper_info("2103.00020")
    print(f"Title: {paper_info['title']}")
    source = await arxiv.download_source("2103.00020")
    print(f"Main TeX file: {source.get('main_tex_file', 'N/A')}")

asyncio.run(arxiv_example())
```

#### DuckDuckGo text search
```python
import asyncio
from oarc_crawlers import DDGCrawler

async def ddg_example():
    ddg = DDGCrawler(data_dir="./data")
    results = await ddg.text_search("python async programming", max_results=5)
    print(results)

asyncio.run(ddg_example())
```

#### Crawl a webpage and extract text
```python
import asyncio
from oarc_crawlers import WebCrawler

async def crawl_example():
    web = WebCrawler(data_dir="./data")
    html = await web.fetch_url_content("https://www.python.org/")
    text = WebCrawler.extract_text_from_html(html)
    print(text[:500])

asyncio.run(crawl_example())
```

#### Parquet Storage: Save and load data
```python
from oarc_crawlers import ParquetStorage

data = {"name": "Example", "value": 42}
ParquetStorage.save_to_parquet(data, "./data/example.parquet")
df = ParquetStorage.load_from_parquet("./data/example.parquet")
print(df)
```

## Environment Variables

| Variable           | Description                                 | Default (Linux)         | Default (Windows)           |
|--------------------|---------------------------------------------|-------------------------|-----------------------------|
| OARC_DATA_DIR      | Data storage directory                      | ~/.local/share/oarc/data| %APPDATA%\oarc\data         |
| OARC_CONFIG_DIR    | Config files directory                      | ~/.config/oarc          | %APPDATA%\oarc\config       |
| OARC_CACHE_DIR     | Cache directory                             | ~/.cache/oarc           | %LOCALAPPDATA%\oarc\cache   |
| OARC_LOG_LEVEL     | Logging level (DEBUG, INFO, etc.)           | INFO                    | INFO                        |
| OARC_MAX_RETRIES   | Max network retries                         | 3                       | 3                           |
| OARC_TIMEOUT       | Network timeout (seconds)                   | 30                      | 30                          |
| OARC_USER_AGENT    | User agent string for requests              | oarc-crawlers/VERSION   | oarc-crawlers/VERSION       |
| OARC_PROXY         | HTTP/HTTPS proxy URL                        | None                    | None                        |
| OARC_NO_PROGRESS   | Disable progress bars (set to 1 to disable) | 0                       | 0                           |

## Troubleshooting

- Use `--verbose` for detailed logs.
- Check [docs/Troubleshoot.md](Troubleshoot.md) for common issues.
- For CLI help: `oarc-crawlers [command] --help`
- For API reference: see [docs/API.md](API.md)