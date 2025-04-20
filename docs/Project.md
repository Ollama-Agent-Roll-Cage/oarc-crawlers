# OARC Crawlers Project Structure

```bash
.
├── .flake8                 # Flake8 configuration
├── .github/                # GitHub Actions workflows and templates
├── .gitignore              # Specifies intentionally untracked 
├── .pylintrc               # Pylint configuration
├── docs/                   # Project documentation
│   ├── API.md
│   ├── Crawlers.md
│   ├── Project.md
│   ├── Specification.md
│   └── __TODO.md
├── examples/               # Example usage scripts for different crawlers
│   ├── arxiv_example.py
│   ├── beautifulsoup_example.py
│   ├── ddg_example.py
│   ├── example_usage.py
│   ├── github_example.py
│   ├── run_example.py
│   └── youtube_example.py
├── LICENSE                 # Project license file
├── pyproject.toml          # Build system requirements and package metadata
├── pytest.ini              # Pytest configuration
├── README.md               # Main project README file
├── src/                    # Source code directory
│   └── oarc_crawlers/      # Main package directory
│       ├── arxiv_fetcher.py        # ArXiv fetching logic
│       ├── beautiful_soup.py       # BeautifulSoup based web crawler
│       ├── cli/                    # Command Line Interface related modules
│       │   ├── main.py             # Main CLI entry point
│       │   └── youtube_cli.py      # YouTube specific CLI commands
│       ├── ddg_search.py           # DuckDuckGo search crawler
│       ├── fastmcp_wrapper.py      # Wrapper for FastMCP (if applicable)
│       ├── gh_crawler.py           # GitHub crawler logic
│       ├── parquet_storage.py      # Parquet file storage handler
│       ├── yt_crawler.py       # YouTube script fetching logic
│       └── __init__.py             # Makes 'oarc_crawlers' a Python package
└── tests/                  # Unit and integration tests
   ├── run_tests.py            # Script to run tests (if needed)
   ├── test_arxiv.py
   ├── test_bs_crawler.py
   ├── test_ddg.py
   ├── test_github_crawler.py
   ├── test_parquet_storage.py
   └── test_yt_crawler.py

# Notes:
# - .git/ directory (Git repository data) is omitted for brevity.
# - .venv/ directory (virtual environment) is omitted.
# - *.egg-info/ directories (build metadata) are omitted.
```