# OARC Crawlers Project Structure

```
oarc-crawlers/
├── .flake8                     # Configuration for Flake8 linter
├── .git/                       # Git version control directory (hidden)
├── .github/                    # GitHub specific files
│   └── workflows/              # GitHub Actions workflows
│       └── publish-python.yml  # Workflow for publishing to PyPI
├── .gitignore                  # Specifies intentionally untracked files for Git
├── .pylintrc                   # Configuration for Pylint linter
├── .venv/                      # Python virtual environment directory (hidden)
├── docs/                       # Project documentation files
│   ├── API.md                  # Documentation for the public API
│   ├── Crawlers.md             # Documentation for specific crawler modules
│   ├── Project.md              # Overview of project structure (this file)
│   ├── Specification.md        # Project design specifications
│   └── __TODO.md               # Internal TODO list or development notes
├── examples/                   # Example usage scripts for different crawlers
│   ├── arxiv_example.py        # Example for ArXiv fetcher
│   ├── beautifulsoup_example.py # Example for BeautifulSoup crawler
│   ├── ddg_example.py          # Example for DuckDuckGo search
│   ├── example_usage.py        # General example usage script
│   ├── github_example.py       # Example for GitHub crawler
│   ├── run_example.py          # Script to run examples
│   └── youtube_example.py      # Example for YouTube crawler
├── LICENSE                     # Project license file
├── pyproject.toml              # Build system configuration and dependencies
├── pytest.ini                  # Configuration for the pytest testing framework
├── README.md                   # Main project description and usage guide
└── src/                        # Source code directory
    ├── oarc_crawlers/          # Main Python package for the crawlers
    │   ├── __init__.py         # Initializes the Python package
    │   ├── arxiv_fetcher.py    # Module for fetching data from ArXiv
    │   ├── beautiful_soup.py   # Module for generic web scraping using BeautifulSoup
    │   ├── cli/                # Command-line interface sub-package
    │   │   ├── __init__.py     # Initializes the CLI sub-package
    │   │   ├── arxiv_cli.py    # CLI for ArXiv crawler
    │   │   ├── beautiful_soup_cli.py # CLI for BeautifulSoup crawler
    │   │   ├── ddg_cli.py      # CLI for DuckDuckGo search
    │   │   ├── github_cli.py   # CLI for GitHub crawler
    │   │   ├── main.py         # Main entry point for combined CLI tool
    │   │   └── youtube_cli.py  # CLI for YouTube crawler
    │   ├── ddg_search.py       # Module for searching DuckDuckGo
    │   ├── fastmcp_wrapper.py  # Wrapper for fast multiprocessing 
    │   ├── gh_crawler.py       # Module for crawling GitHub data
    │   ├── parquet_storage.py  # Utility for storing data in Parquet format
    │   └── youtube_script.py   # Module for fetching YouTube data
    └── tests/                  # Test directory
        ├── run_tests.py        # Script to discover and run all tests
        ├── test_arxiv.py       # Tests for ArXiv fetcher
        ├── test_bs_crawler.py  # Tests for BeautifulSoup crawler
        ├── test_ddg.py         # Tests for DuckDuckGo search
        ├── test_github_crawler.py # Tests for GitHub crawler
        ├── test_parquet_storage.py # Tests for Parquet storage
        └── test_youtube_script.py # Tests for YouTube script
```

## Key Components

1. **Crawler Modules**: Core functionality for different data sources
   - `arxiv_fetcher.py`: Retrieves papers from ArXiv
   - `beautiful_soup.py`: General web scraping using BeautifulSoup
   - `ddg_search.py`: DuckDuckGo search interface
   - `gh_crawler.py`: GitHub repository data crawler
   - `youtube_script.py`: YouTube video and channel data fetcher

2. **Command-Line Interfaces**: CLI tools for each crawler
   - Each crawler has its own dedicated CLI script
   - `main.py` provides a unified interface to all crawlers

3. **Storage**: 
   - `parquet_storage.py`: Efficient data storage using Parquet format

4. **Tests**:
   - Unit tests for each crawler module
   - `run_tests.py` for running the entire test suite