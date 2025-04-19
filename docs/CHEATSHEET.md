# OARC-Crawlers Cheat Sheet

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
oarc-crawlers yt playlist --url "https://www.youtube.com/watch?v=MDbdb-W4x4w&t=330s&ab_channel=MattWilliams"

# Get video captions
oarc-crawlers yt captions --url "https://www.youtube.com/watch?v=MDbdb-W4x4w&t=330s&ab_channel=MattWilliams" --languages "en,es,fr"

# Search videos
oarc-crawlers yt search --query "python tutorials" --limit 5
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
# Download paper
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
```python
from oarc_crawlers import (
    YTCrawler, 
    GHCrawler, 
    ArxivCrawler, 
    DDGCrawler
)

# Initialize with custom data directory
data_dir = "./my_data"
yt = YTCrawler(data_dir=data_dir)
gh = GHCrawler(data_dir=data_dir)
arxiv = ArxivCrawler(data_dir=data_dir)
ddg = DDGCrawler(data_dir=data_dir)

# Example: Download YouTube video
import asyncio
async def download_video():
    result = await yt.download_video(
        url="https://www.youtube.com/watch?v=MDbdb-W4x4w&t=330s&ab_channel=MattWilliams",
        format="mp4",
        resolution="720p"
    )
    print(f"Downloaded to: {result['file_path']}")

asyncio.run(download_video())
```