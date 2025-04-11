# OARC-Crawlers

OARC's dynamic webcrawler module collection. This package provides various web crawlers and data extractors for different sources:

- YouTube videos and metadata
- GitHub repositories
- DuckDuckGo search results
- Web pages via BeautifulSoup
- ArXiv papers and research

## Features

- **YouTube Downloader**: Download videos, playlists, and extract captions
- **GitHub Crawler**: Clone repositories and extract code for analysis
- **DuckDuckGo Searcher**: Search for text, images, and news
- **Web Crawler**: Extract content from websites using BeautifulSoup
- **ArXiv Fetcher**: Download academic papers and their LaTeX source

## Installation

```bash
# Install UV package manager
pip install uv

# Create & activate virtual environment with UV
uv venv --python 3.11

# Install the package and dependencies in one step
uv run pip install -e .[dev]
```

## Usage Examples

See the `examples/` directory for full examples for each module.

### YouTube Downloader

```python
from src.youtube_script import YouTubeDownloader

async def download_example():
    downloader = YouTubeDownloader(data_dir="./data")
    # Download a video
    result = await downloader.download_video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    print(f"Video downloaded to {result['file_path']}")
    
    # Extract captions
    captions = await downloader.extract_captions("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    print(f"Found captions in languages: {list(captions['captions'].keys())}")
```

### GitHub Crawler

```python
from src.gh_crawler import GitHubCrawler

async def github_example():
    crawler = GitHubCrawler(data_dir="./data")
    
    # Get repository summary
    repo_url = "https://github.com/username/repository"
    summary = await crawler.get_repo_summary(repo_url)
    print(summary)
    
    # Find similar code
    code_snippet = "def calculate_mean(values):\n    return sum(values) / len(values)"
    matches = await crawler.find_similar_code(repo_url, code_snippet)
    print(matches)
```

### DuckDuckGo Searcher

```python
from src.ddg_search import DuckDuckGoSearcher

async def search_example():
    searcher = DuckDuckGoSearcher(data_dir="./data")
    
    # Text search
    text_results = await searcher.text_search("quantum computing", max_results=5)
    print(text_results)
    
    # News search
    news_results = await searcher.news_search("artificial intelligence", max_results=3)
    print(news_results)
```

### BeautifulSoup Web Crawler

```python
from src.beautiful_soup import BSWebCrawler

async def web_example():
    crawler = BSWebCrawler(data_dir="./data")
    
    # Crawl documentation site
    docs = await crawler.crawl_documentation_site("https://docs.python.org/3/library/asyncio.html")
    print(docs)
```

### ArXiv Fetcher

```python
from src.arxiv_fetcher import ArxivFetcher

async def arxiv_example():
    fetcher = ArxivFetcher(data_dir="./data")
    
    # Get paper info
    paper_id = "2103.00020"
    paper_info = await fetcher.fetch_paper_info(paper_id)
    print(f"Title: {paper_info['title']}")
    print(f"Authors: {', '.join(paper_info['authors'])}")
    
    # Get paper with LaTeX source
    full_paper = await fetcher.fetch_paper_with_latex(paper_id)
    print(f"LaTeX content length: {len(full_paper['latex_content'])}")
```

## Running Examples

To run the examples:

```bash
# Run specific module example
python examples/run_example.py youtube
python examples/run_example.py github
python examples/run_example.py ddg
python examples/run_example.py bs
python examples/run_example.py arxiv

# Run the combined example
python examples/run_example.py combined

# Run all examples
python examples/run_example.py all
```

## Running Tests

To run all tests:

```bash
python run_tests.py
```

Or to run a specific test:

```bash
python -m unittest tests.test_parquet_storage
```

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.