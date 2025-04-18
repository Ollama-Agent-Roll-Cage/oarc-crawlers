"""
Help text constants for the OARC Crawlers CLI.

This module centralizes all help and usage text for CLI commands and options,
ensuring consistent and maintainable documentation across the toolkit.
"""

# Command group descriptions
YOUTUBE_GROUP_HELP = "YouTube operations for downloading videos and extracting information."
GITHUB_GROUP_HELP = "GitHub operations for cloning, analyzing and extracting from repositories."
ARXIV_GROUP_HELP = "ArXiv operations for downloading papers and extracting content."
WEB_GROUP_HELP = "Web crawler operations for extracting content from websites."
DUCK_GROUP_HELP = "DuckDuckGo search operations for finding information online."
BUILD_GROUP_HELP = "Build operations for package management."
PUBLISH_GROUP_HELP = "Publish operations for distributing packages."

# Main help text for the CLI
# Main help text for the CLI
MAIN_HELP = f"""
Usage:
  oarc-crawlers [--verbose] [--version] <command> [options]

For detailed information about any command:
  oarc-crawlers <command> --help
"""

# Help for each command group
BUILD_HELP = """
Build Command Help

Usage:
  oarc-crawlers build COMMAND [OPTIONS]

Commands:
  package     Build the OARC Crawlers package

Options:
  --verbose     Enable verbose error output
  --help        Show this help message

Example Usage:
  oarc-crawlers build package
  oarc-crawlers build package --clean
"""

PUBLISH_HELP = """
Publish Command Help

Usage:
  oarc-crawlers publish COMMAND [OPTIONS]

Commands:
  pypi         Publish to PyPI or TestPyPI

Options:
  --verbose     Enable verbose error output
  --help        Show this help message

Example Usage:
  oarc-crawlers publish pypi
  oarc-crawlers publish pypi --test
"""

YOUTUBE_HELP = """
YouTube Command Help

Usage:
  oarc-crawlers youtube COMMAND [OPTIONS]

Commands:
  download    Download a YouTube video
  playlist    Download videos from a YouTube playlist
  captions    Extract captions/subtitles from a YouTube video
  search      Search for videos on YouTube
  chat        Fetch chat messages from a YouTube live stream

Options:
  --verbose     Enable verbose error output
  --help        Show this help message

Example Usage:
  oarc-crawlers youtube download --url https://youtube.com/watch?v=example
  oarc-crawlers youtube search --query "python tutorials"
"""

GH_HELP = """
GitHub Command Help

Usage:
  oarc-crawlers github COMMAND [OPTIONS]

Commands:
  clone         Clone a GitHub repository
  analyze       Analyze a GitHub repository's content
  find-similar  Find code similar to a snippet in a repository

Options:
  --verbose     Enable verbose error output
  --help        Show this help message

Example Usage:
  oarc-crawlers github clone --url https://github.com/username/repo
  oarc-crawlers github analyze --url https://github.com/username/repo
"""

ARXIV_HELP = """
arXiv Command Help

Usage:
  oarc-crawlers arxiv COMMAND [OPTIONS]

Commands:
  download    Download LaTeX source files for a paper
  search      Search for papers on arXiv
  latex       Download and extract LaTeX content from a paper

Options:
  --verbose     Enable verbose error output
  --help        Show this help message

Example Usage:
  oarc-crawlers arxiv download --id 2310.12123
  oarc-crawlers arxiv latex --id 1909.11065
"""

WEB_HELP = """
Web Crawler Command Help

Usage:
  oarc-crawlers web COMMAND [OPTIONS]

Commands:
  crawl       Extract content from a webpage
  docs        Extract content from a documentation site
  pypi        Extract information about a PyPI package

Options:
  --verbose     Enable verbose error output
  --help        Show this help message

Example Usage:
  oarc-crawlers web crawl --url https://example.com
  oarc-crawlers web pypi --package requests
"""

DDG_HELP = """
DuckDuckGo Command Help

Usage:
  oarc-crawlers duck COMMAND [OPTIONS]

Commands:
  text        Perform a DuckDuckGo text search
  images      Perform a DuckDuckGo image search
  news        Perform a DuckDuckGo news search

Options:
  --verbose     Enable verbose error output
  --help        Show this help message

Example Usage:
  oarc-crawlers duck text --query "quantum computing"
  oarc-crawlers duck images --query "cute cats"
"""

# YouTube command detailed help
YOUTUBE_DOWNLOAD_HELP = """
Download a YouTube video with specified parameters.

Usage:
  oarc-crawlers youtube download [OPTIONS]

Options:
  --url TEXT                  YouTube video URL [required]
  --format TEXT               Video format (mp4, webm, mp3) [default: mp4]
  --resolution TEXT           Video resolution ("highest", "lowest", or specific like "720p") [default: highest]
  --extract-audio/--no-extract-audio
                              Extract audio only [default: no-extract-audio]
  --output-path TEXT          Directory to save the video
  --filename TEXT             Custom filename for the downloaded video
  --verbose                   Show detailed error information
  --help                      Show this help message

Examples:
  oarc-crawlers youtube download --url https://youtube.com/watch?v=dQw4w9WgXcQ
  oarc-crawlers youtube download --url https://youtube.com/watch?v=dQw4w9WgXcQ --format mp3 --extract-audio
  oarc-crawlers youtube download --url https://youtube.com/watch?v=dQw4w9WgXcQ --resolution 720p --output-path ./videos
"""

YOUTUBE_PLAYLIST_HELP = """
Download videos from a YouTube playlist.

Usage:
  oarc-crawlers youtube playlist [OPTIONS]

Options:
  --url TEXT                  YouTube playlist URL [required]
  --format TEXT               Video format (mp4, webm) [default: mp4]
  --max-videos INTEGER        Maximum number of videos to download [default: 10]
  --output-path TEXT          Directory to save the playlist videos
  --verbose                   Show detailed error information
  --help                      Show this help message

Examples:
  oarc-crawlers youtube playlist --url https://youtube.com/playlist?list=PLzH6n4zXuckquVnQ0KlMDxyXxiSO2DXOQ
  oarc-crawlers youtube playlist --url https://youtube.com/playlist?list=PLzH6n4zXuckquVnQ0KlMDxyXxiSO2DXOQ --max-videos 5
  oarc-crawlers youtube playlist --url https://youtube.com/playlist?list=PLzH6n4zXuckquVnQ0KlMDxyXxiSO2DXOQ --format mp4 --output-path ./playlists
"""

YOUTUBE_CAPTIONS_HELP = """
Extract captions/subtitles from a YouTube video.

Usage:
  oarc-crawlers youtube captions [OPTIONS]

Options:
  --url TEXT                  YouTube video URL [required]
  --languages TEXT            Comma-separated language codes (e.g. "en,es,fr") [default: en]
  --verbose                   Show detailed error information
  --help                      Show this help message

Examples:
  oarc-crawlers youtube captions --url https://youtube.com/watch?v=dQw4w9WgXcQ
  oarc-crawlers youtube captions --url https://youtube.com/watch?v=dQw4w9WgXcQ --languages "en,es,fr"
"""

YOUTUBE_SEARCH_HELP = """
Search for YouTube videos.

Usage:
  oarc-crawlers youtube search [OPTIONS]

Options:
  --query TEXT                Search query [required]
  --limit INTEGER             Maximum number of results [default: 10]
  --verbose                   Show detailed error information
  --help                      Show this help message

Examples:
  oarc-crawlers youtube search --query "python tutorials"
  oarc-crawlers youtube search --query "cooking recipes" --limit 20
"""

YOUTUBE_CHAT_HELP = """
Fetch chat messages from a YouTube live stream or premiere.

Usage:
  oarc-crawlers youtube chat [OPTIONS]

Options:
  --video-id TEXT             YouTube video ID or URL [required]
  --max-messages INTEGER      Maximum number of messages to collect [default: 1000]
  --duration INTEGER          Duration to collect messages in seconds
  --verbose                   Show detailed error information
  --help                      Show this help message

Examples:
  oarc-crawlers youtube chat --video-id dQw4w9WgXcQ
  oarc-crawlers youtube chat --video-id dQw4w9WgXcQ --max-messages 500 --duration 300
"""

# GitHub command detailed help
GH_CLONE_HELP = """
Clone and analyze a GitHub repository.

Usage:
  oarc-crawlers github clone [OPTIONS]

Options:
  --url TEXT                  GitHub repository URL [required]
  --output-path TEXT          Directory to save the cloned repository
  --verbose                   Show detailed error information
  --help                      Show this help message

Examples:
  oarc-crawlers github clone --url https://github.com/username/repo
  oarc-crawlers github clone --url https://github.com/username/repo --output-path ./repos
"""

GH_ANALYZE_HELP = """
Get a summary analysis of a GitHub repository.

Usage:
  oarc-crawlers github analyze [OPTIONS]

Options:
  --url TEXT                  GitHub repository URL [required]
  --verbose                   Show detailed error information
  --help                      Show this help message

Examples:
  oarc-crawlers github analyze --url https://github.com/username/repo
"""

GH_FIND_SIMILAR_HELP = """
Find similar code in a GitHub repository.

Usage:
  oarc-crawlers github find-similar [OPTIONS]

Options:
  --url TEXT                  GitHub repository URL [required]
  --code TEXT                 Code snippet to find similar code for [required]
  --language TEXT             Programming language of the code snippet
  --verbose                   Show detailed error information
  --help                      Show this help message

Examples:
  oarc-crawlers github find-similar --url https://github.com/username/repo --code "def hello_world():"
  oarc-crawlers github find-similar --url https://github.com/username/repo --code "import numpy as np" --language python
"""

# ArXiv command detailed help
ARXIV_DOWNLOAD_HELP = """
Download LaTeX source files for an arXiv paper.

Usage:
  oarc-crawlers arxiv download [OPTIONS]

Options:
  --id TEXT                   arXiv paper ID [required]
  --verbose                   Show detailed error information
  --help                      Show this help message

Examples:
  oarc-crawlers arxiv download --id 2310.12123
  oarc-crawlers arxiv download --id 1909.11065
"""

ARXIV_SEARCH_HELP = """
Search for papers on arXiv.

Usage:
  oarc-crawlers arxiv search [OPTIONS]

Options:
  --query TEXT                Search query [required]
  --limit INTEGER             Maximum number of results [default: 5]
  --verbose                   Show detailed error information
  --help                      Show this help message

Examples:
  oarc-crawlers arxiv search --query "quantum computing" --limit 10
  oarc-crawlers arxiv search --query "machine learning"
"""

ARXIV_LATEX_HELP = """
Download and extract LaTeX content from an arXiv paper.

Usage:
  oarc-crawlers arxiv latex [OPTIONS]

Options:
  --id TEXT                   arXiv paper ID [required]
  --verbose                   Show detailed error information
  --help                      Show this help message

Examples:
  oarc-crawlers arxiv latex --id 2310.12123
  oarc-crawlers arxiv latex --id 1909.11065
"""

# Web command detailed help
WEB_CRAWL_HELP = """
Crawl and extract content from a webpage.

Usage:
  oarc-crawlers web crawl [OPTIONS]

Options:
  --url TEXT                  URL to crawl [required]
  --output-file TEXT          File to save the extracted content
  --verbose                   Show detailed error information
  --help                      Show this help message

Examples:
  oarc-crawlers web crawl --url https://example.com
  oarc-crawlers web crawl --url https://example.com/blog --output-file blog.txt
"""

WEB_DOCS_HELP = """
Crawl and extract content from a documentation site.

Usage:
  oarc-crawlers web docs [OPTIONS]

Options:
  --url TEXT                  URL of documentation site [required]
  --verbose                   Show detailed error information
  --help                      Show this help message

Examples:
  oarc-crawlers web docs --url https://docs.python.org
  oarc-crawlers web docs --url https://docs.sqlalchemy.org
"""

WEB_PYPI_HELP = """
Extract information about a PyPI package.

Usage:
  oarc-crawlers web pypi [OPTIONS]

Options:
  --package TEXT              PyPI package name [required]
  --verbose                   Show detailed error information
  --help                      Show this help message

Examples:
  oarc-crawlers web pypi --package requests
  oarc-crawlers web pypi --package numpy
"""

# DuckDuckGo command detailed help
DDG_TEXT_HELP = """
Perform a DuckDuckGo text search.

Usage:
  oarc-crawlers duck text [OPTIONS]

Options:
  --query TEXT                Search query [required]
  --max-results INTEGER       Maximum number of results [default: 5]
  --verbose                   Show detailed error information
  --help                      Show this help message

Examples:
  oarc-crawlers duck text --query "quantum computing"
  oarc-crawlers duck text --query "machine learning" --max-results 10
"""

DDG_IMAGES_HELP = """
Perform a DuckDuckGo image search.

Usage:
  oarc-crawlers duck images [OPTIONS]

Options:
  --query TEXT                Search query [required]
  --max-results INTEGER       Maximum number of results [default: 10]
  --verbose                   Show detailed error information
  --help                      Show this help message

Examples:
  oarc-crawlers duck images --query "cute cats"
  oarc-crawlers duck images --query "landscapes" --max-results 20
"""

DDG_NEWS_HELP = """
Perform a DuckDuckGo news search.

Usage:
  oarc-crawlers duck news [OPTIONS]

Options:
  --query TEXT                Search query [required]
  --max-results INTEGER       Maximum number of results [default: 20]
  --verbose                   Show detailed error information
  --help                      Show this help message

Examples:
  oarc-crawlers duck news --query "breaking news"
  oarc-crawlers duck news --query "technology" --max-results 30
"""

# Build command detailed help
BUILD_PACKAGE_HELP = """
Build the OARC Crawlers package.

Usage:
  oarc-crawlers build package [OPTIONS]

Options:
  --clean/--no-clean          Clean build directories first [default: no-clean]
  --verbose                   Show detailed error information
  --help                      Show this help message

Examples:
  oarc-crawlers build package
  oarc-crawlers build package --clean
"""

# Publish command detailed help
PUBLISH_PYPI_HELP = """
Publish the package to PyPI.

Usage:
  oarc-crawlers publish pypi [OPTIONS]

Options:
  --test                      Upload to TestPyPI instead of PyPI
  --build/--no-build          Build the package before publishing [default: build]
  --username TEXT             PyPI username (if not using keyring)
  --password TEXT             PyPI password (if not using keyring)
  --config-file TEXT          Path to PyPI config file (.pypirc)
  --verbose                   Show detailed error information
  --help                      Show this help message

Examples:
  oarc-crawlers publish pypi
  oarc-crawlers publish pypi --test
  oarc-crawlers publish pypi --no-build --config-file ~/.pypirc
"""

# Model Context Protocol (MCP) command detailed help
MCP_HELP = """
MCP Command Help

Usage:
  oarc-crawlers mcp COMMAND [OPTIONS]

Commands:
  run          Run the MCP server
  install      Install the MCP server for VS Code integration

Options:
  --verbose     Enable verbose error output
  --help        Show this help message

Example Usage:
  oarc-crawlers mcp run
  oarc-crawlers mcp install --name "OARC Tools"
"""

MCP_RUN_HELP = """
Run an MCP server for OARC Crawlers.

Usage:
  oarc-crawlers mcp run [OPTIONS]

Options:
  --port INTEGER            Port to run the server on [default: 3000]
  --transport TEXT          Transport method to use (e.g., 'sse', 'ws') [default: ws]
  --data-dir TEXT           Directory to store data
  --verbose                 Show detailed error information
  --help                    Show this help message

Examples:
  oarc-crawlers mcp run
  oarc-crawlers mcp run --port 5000 --transport sse
"""

MCP_INSTALL_HELP = """
Install the MCP server for VS Code integration.

Usage:
  oarc-crawlers mcp install [OPTIONS]

Options:
  --name TEXT               Custom name for the server in VS Code
  --verbose                 Show detailed error information
  --help                    Show this help message

Examples:
  oarc-crawlers mcp install
  oarc-crawlers mcp install --name "OARC Tools"
"""