# ⛏️ OARC-Crawlers ⛏️

OARC's dynamic webcrawler module collection. This package provides various web crawlers and data extractors for different sources, all with integrated Parquet storage capabilities for efficient data persistence and retrieval:

- YouTube videos and metadata
- GitHub repositories
- DuckDuckGo search results
- Web pages via BeautifulSoup
- ArXiv papers and research
- Parquet-based data storage system

## Features

- **YouTube Downloader**: Download videos, playlists, and extract captions
- **GitHub Crawler**: Clone repositories and extract code for analysis
- **DuckDuckGo Searcher**: Search for text, images, and news
- **Web Crawler**: Extract content from websites using BeautifulSoup
- **ArXiv Fetcher**: Download academic papers and their LaTeX source
- **Parquet Storage**: Utility for saving and loading data in Parquet format

## Installation

```bash
# Install UV package manager
pip install uv

# Create & activate virtual environment with UV
uv venv --python 3.11

# Quick install
uv pip install oarc-crawlers

or

# Install the package and dependencies in one step
cd dir, -> clone repo
uv run pip install -e .[dev]
```

## Usage Examples

See the `examples/` directory for full examples for each module.

### Parquet Storage

The ParquetStorage class provides a unified interface for saving and loading data in the Parquet format across all crawler modules. It serves as the foundation for data persistence throughout the system.

### Basic Usage

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

### Implementation Details

ParquetStorage handles different data types automatically:
- Single dictionaries are converted to single-row DataFrames
- Lists of dictionaries are converted to multi-row DataFrames
- Pandas DataFrames are stored directly
- All data is converted to Apache Arrow Tables before saving

### Error Handling

The class provides robust error handling for common issues:
```python
# Safe loading with error handling
try:
    data = ParquetStorage.load_from_parquet('./path/that/might/not/exist.parquet')
    if data is None:
        print("File not found or error loading data")
    else:
        print(f"Successfully loaded {len(data)} rows")
except Exception as e:
    print(f"Error: {e}")
```

### Directory Structure

Each crawler module creates its own directory structure for storing Parquet files:
```
./data/
  ├── youtube_data/
  │   ├── videos/
  │   ├── metadata/
  │   ├── captions/
  │   └── searches/
  ├── github_repos/
  ├── searches/         # DuckDuckGo searches
  ├── crawls/           # BeautifulSoup web crawls
  ├── papers/           # ArXiv papers
  └── sources/          # ArXiv LaTeX sources
```

### YouTube Downloader

```python
from oarc_crawlers import YouTubeDownloader

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
from oarc_crawlers import GitHubCrawler

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
from oarc_crawlers import DuckDuckGoSearcher

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
from oarc_crawlers import BSWebCrawler

async def web_example():
    crawler = BSWebCrawler(data_dir="./data")
    
    # Crawl documentation site
    docs = await crawler.crawl_documentation_site("https://docs.python.org/3/library/asyncio.html")
    print(docs)
```

### ArXiv Fetcher

```python
from oarc_crawlers import ArxivFetcher

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

## Advanced Examples: Working with Stored Data

The ParquetStorage class serves as the foundation for all data persistence across the different crawler modules. Here are examples of how to work with the data stored by the different crawlers:

```python
import pandas as pd
import os
from datetime import datetime
from oarc_crawlers import ParquetStorage

# Access and analyze data from multiple crawlers
async def data_analysis_example():
    # Load YouTube search results
    yt_search_path = "./data/youtube_data/searches/machine_learning_1712345678.parquet"
    yt_data = ParquetStorage.load_from_parquet(yt_search_path)
    
    # Load GitHub repository data
    repo_path = "./data/github_repos/username_repository.parquet"
    repo_data = ParquetStorage.load_from_parquet(repo_path)
    
    # Load ArXiv papers
    papers_path = "./data/papers/all_papers.parquet"
    papers_df = ParquetStorage.load_from_parquet(papers_path)
    
    # Example: Find all ArXiv papers about machine learning
    ml_papers = papers_df[papers_df['abstract'].str.contains('machine learning', case=False)]
    print(f"Found {len(ml_papers)} papers about machine learning")
    
    # Example: Export combined data to CSV
    ml_papers.to_csv('./data/analysis/ml_papers.csv', index=False)
    
    # Example: Find Python files in GitHub repository
    if repo_data is not None:
        python_files = repo_data[repo_data['language'] == 'Python']
        print(f"Found {len(python_files)} Python files in repository")
        
        # Find files with specific content
        auth_files = repo_data[repo_data['content'].str.contains('authenticate', case=False)]
        print(f"Found {len(auth_files)} files related to authentication")
    
    # Example: Analyze YouTube search results
    if isinstance(yt_data, pd.DataFrame) and 'results' in yt_data.columns:
        # Extract video data if it's stored as a list in a column
        videos = []
        for _, row in yt_data.iterrows():
            if isinstance(row['results'], list):
                videos.extend(row['results'])
        
        # Convert to DataFrame for analysis
        videos_df = pd.DataFrame(videos)
        print(f"Analyzing {len(videos_df)} YouTube videos")
        
        # Find most viewed videos
        if 'views' in videos_df.columns:
            top_videos = videos_df.sort_values('views', ascending=False).head(5)
            for _, video in top_videos.iterrows():
                print(f"Title: {video['title']}, Views: {video['views']}")
```

# Working with DuckDuckGo search results

```python
from oarc_crawlers import ParquetStorage

def analyze_search_results():
    search_dir = "./data/searches"
    results = []
    
    # Collect all search results
    for file in os.listdir(search_dir):
        if file.endswith('.parquet'):
            file_path = os.path.join(search_dir, file)
            data = ParquetStorage.load_from_parquet(file_path)
            if data is not None:
                results.append({
                    'filename': file,
                    'query': data.iloc[0]['query'] if 'query' in data.columns else 'Unknown',
                    'timestamp': data.iloc[0]['timestamp'] if 'timestamp' in data.columns else None,
                    'result_count': len(data)
                })
    
    # Convert to DataFrame
    results_df = pd.DataFrame(results)
    print(f"Found {len(results_df)} search result files")
    
    # Find most recent searches
    if 'timestamp' in results_df.columns:
        results_df['timestamp'] = pd.to_datetime(results_df['timestamp'])
        recent_searches = results_df.sort_values('timestamp', ascending=False).head(5)
        for _, search in recent_searches.iterrows():
            print(f"Query: {search['query']}, Time: {search['timestamp']}")

# Working with web crawl data
def analyze_web_crawls():
    crawls_dir = "./data/crawls"
    
    if not os.path.exists(crawls_dir):
        print(f"Directory {crawls_dir} does not exist")
        return
        
    # List all crawl files
    crawl_files = [f for f in os.listdir(crawls_dir) if f.endswith('.parquet')]
    print(f"Found {len(crawl_files)} crawl files")
    
    # Process each file
    for file in crawl_files:
        file_path = os.path.join(crawls_dir, file)
        data = ParquetStorage.load_from_parquet(file_path)
        
        if data is not None:
            # For documentation crawls
            if 'doc_' in file and 'title' in data.columns:
                print(f"Documentation: {data.iloc[0]['title']}")
                
                # Extract code snippets if available
                if 'code_snippets' in data.columns:
                    snippets = data.iloc[0]['code_snippets']
                    if isinstance(snippets, list):
                        print(f"  Found {len(snippets)} code snippets")
            
            # For regular web crawls
            elif 'url' in data.columns:
                print(f"Web crawl: {data.iloc[0]['url']}")
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
python examples/run_example.py parquet

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