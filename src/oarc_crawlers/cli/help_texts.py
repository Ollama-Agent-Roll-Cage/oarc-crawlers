"""
Help text constants for the OARC Crawlers CLI.

This module centralizes all help and usage text for CLI commands and options,
ensuring consistent and maintainable documentation across the toolkit.
"""

# Command group descriptions
YOUTUBE_GROUP_HELP = "YouTube operations for downloading videos and extracting information."
GH_GROUP_HELP = "GitHub operations for cloning, analyzing and extracting from repositories."
ARXIV_GROUP_HELP = "ArXiv operations for downloading papers and extracting content."
WEB_GROUP_HELP = "Web crawler operations for extracting content from websites."
DDG_GROUP_HELP = "DuckDuckGo search operations for finding information online."
BUILD_GROUP_HELP = "Build operations for package management."
PUBLISH_GROUP_HELP = "Publish operations for distributing packages."
DATA_GROUP_HELP = "Data management operations for viewing and manipulating data files."

# Command option descriptions
ARGS_VERBOSE_HELP = "Enable verbose output and debug logging"
ARGS_CONFIG_HELP = "Path to custom configuration file"
ARGS_URL_HELP = "URL to process"
ARGS_REPO_URL_HELP = "GitHub repository URL"
ARGS_VIDEO_URL_HELP = "YouTube video URL"
ARGS_VIDEO_ID_HELP = "YouTube video ID or URL"
ARGS_PLAYLIST_URL_HELP = "YouTube playlist URL"
ARGS_QUERY_HELP = "Search query"
ARGS_MAX_RESULTS_HELP = "Maximum number of results to return"
ARGS_LIMIT_HELP = "Maximum number of results to return"
ARGS_ID_HELP = "arXiv paper ID"
ARGS_OUTPUT_PATH_HELP = "Directory to save the output"
ARGS_OUTPUT_FILE_HELP = "File to save the output"
ARGS_LANGUAGE_HELP = "Programming language of the code"
ARGS_LANGUAGES_HELP = "Comma-separated language codes (e.g. \"en,es,fr\")"
ARGS_FORMAT_HELP = "Output format"
ARGS_CODE_HELP = "Code snippet to search for"
ARGS_CLEAN_HELP = "Clean build directories first"
ARGS_TEST_HELP = "Upload to TestPyPI instead of PyPI"
ARGS_BUILD_HELP = "Build the package before publishing"
ARGS_PORT_HELP = "Port to run the server on"
ARGS_TRANSPORT_HELP = "Transport method to use"
ARGS_DATA_DIR_HELP = "Directory to store data"
ARGS_PACKAGE_HELP = "PyPI package name"
ARGS_RESOLUTION_HELP = "Video resolution (\"highest\", \"lowest\", or specific like \"720p\")"
ARGS_EXTRACT_AUDIO_HELP = "Extract audio only"
ARGS_FILENAME_HELP = "Custom filename for the downloaded file"
ARGS_MAX_VIDEOS_HELP = "Maximum number of videos to download"
ARGS_MAX_MESSAGES_HELP = "Maximum number of messages to collect"
ARGS_DURATION_HELP = "Duration in seconds to collect messages"
ARGS_MCP_NAME_HELP = "Custom name for the MCP server in VS Code"
ARGS_PYPI_USERNAME_HELP = "PyPI username (if not using keyring)'"
ARGS_PYPI_PASSWORD_HELP = "PyPI password (if not using keyring)"
ARGS_PYPI_CONFIG_FILE_HELP = "Path to PyPI config file (.pypirc)"
ARGS_FILE_PATH_HELP = "Path to the file"
ARGS_MAX_ROWS_HELP = "Maximum number of rows to display"

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
  --verbose     Enable verbose output and debug logging
  --config      Path to custom configuration file
  --help        Show this help message

Example Usage:
  oarc-crawlers build package
  oarc-crawlers build package --clean
  oarc-crawlers build package --config ~/.oarc/config.ini
"""

PUBLISH_HELP = """
Publish Command Help

Usage:
  oarc-crawlers publish COMMAND [OPTIONS]

Commands:
  pypi         Publish to PyPI or TestPyPI

Options:
  --verbose     Enable verbose output and debug logging
  --config      Path to custom configuration file
  --help        Show this help message

Example Usage:
  oarc-crawlers publish pypi
  oarc-crawlers publish pypi --test
  oarc-crawlers publish pypi --config ~/.oarc/config.ini
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
  --verbose     Enable verbose output and debug logging
  --config      Path to custom configuration file
  --help        Show this help message

Example Usage:
  oarc-crawlers youtube download --url https://youtube.com/watch?v=example
  oarc-crawlers youtube search --query "python tutorials"
  oarc-crawlers youtube download --url https://youtube.com/watch?v=example --config ~/.oarc/config.ini
"""

GH_HELP = """
GitHub Command Help

Usage:
  oarc-crawlers gh COMMAND [OPTIONS]

Commands:
  clone         Clone a GitHub repository
  analyze       Analyze a GitHub repository's content
  find-similar  Find code similar to a snippet in a repository

Options:
  --verbose     Enable verbose output and debug logging
  --config      Path to custom configuration file
  --help        Show this help message

Example Usage:
  oarc-crawlers gh clone --url https://github.com/username/repo
  oarc-crawlers gh analyze --url https://github.com/username/repo
  oarc-crawlers gh clone --url https://github.com/username/repo --config ~/.oarc/config.ini
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
  --verbose     Enable verbose output and debug logging
  --config      Path to custom configuration file
  --help        Show this help message

Example Usage:
  oarc-crawlers arxiv download --id 2310.12123
  oarc-crawlers arxiv latex --id 1909.11065
  oarc-crawlers arxiv download --id 2310.12123 --config ~/.oarc/config.ini
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
  --verbose     Enable verbose output and debug logging
  --config      Path to custom configuration file
  --help        Show this help message

Example Usage:
  oarc-crawlers web crawl --url https://example.com
  oarc-crawlers web pypi --package requests
  oarc-crawlers web crawl --url https://example.com --config ~/.oarc/config.ini
"""

DDG_HELP = """
DuckDuckGo Command Help

Usage:
  oarc-crawlers ddg COMMAND [OPTIONS]

Commands:
  text        Perform a DuckDuckGo text search
  images      Perform a DuckDuckGo image search
  news        Perform a DuckDuckGo news search

Options:
  --verbose     Enable verbose output and debug logging
  --config      Path to custom configuration file
  --help        Show this help message

Example Usage:
  oarc-crawlers ddg text --query "quantum computing"
  oarc-crawlers ddg images --query "cute cats"
  oarc-crawlers ddg text --query "quantum computing" --config ~/.oarc/config.ini
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
  --verbose                   Enable verbose output and debug logging
  --config                    Path to custom configuration file
  --help                      Show this help message

Examples:
  oarc-crawlers youtube download --url https://youtube.com/watch?v=dQw4w9WgXcQ
  oarc-crawlers youtube download --url https://youtube.com/watch?v=dQw4w9WgXcQ --format mp3 --extract-audio
  oarc-crawlers youtube download --url https://youtube.com/watch?v=dQw4w9WgXcQ --resolution 720p --output-path ./videos
  oarc-crawlers youtube download --url https://youtube.com/watch?v=dQw4w9WgXcQ --config ~/.oarc/config.ini
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
  --verbose                   Enable verbose output and debug logging
  --config                    Path to custom configuration file
  --help                      Show this help message

Examples:
  oarc-crawlers youtube playlist --url https://youtube.com/playlist?list=PLzH6n4zXuckquVnQ0KlMDxyXxiSO2DXOQ
  oarc-crawlers youtube playlist --url https://youtube.com/playlist?list=PLzH6n4zXuckquVnQ0KlMDxyXxiSO2DXOQ --max-videos 5
  oarc-crawlers youtube playlist --url https://youtube.com/playlist?list=PLzH6n4zXuckquVnQ0KlMDxyXxiSO2DXOQ --format mp4 --output-path ./playlists
  oarc-crawlers youtube playlist --url https://youtube.com/playlist?list=PLzH6n4zXuckquVnQ0KlMDxyXxiSO2DXOQ --config ~/.oarc/config.ini
"""

YOUTUBE_CAPTIONS_HELP = """
Extract captions/subtitles from a YouTube video.

Usage:
  oarc-crawlers youtube captions [OPTIONS]

Options:
  --url TEXT                  YouTube video URL [required]
  --languages TEXT            Comma-separated language codes (e.g. "en,es,fr") [default: en]
  --verbose                   Enable verbose output and debug logging
  --config                    Path to custom configuration file
  --help                      Show this help message

Examples:
  oarc-crawlers youtube captions --url https://youtube.com/watch?v=dQw4w9WgXcQ
  oarc-crawlers youtube captions --url https://youtube.com/watch?v=dQw4w9WgXcQ --languages "en,es,fr"
  oarc-crawlers youtube captions --url https://youtube.com/watch?v=dQw4w9WgXcQ --config ~/.oarc/config.ini
"""

YOUTUBE_SEARCH_HELP = """
Search for YouTube videos.

Usage:
  oarc-crawlers youtube search [OPTIONS]

Options:
  --query TEXT                Search query [required]
  --limit INTEGER             Maximum number of results [default: 10]
  --verbose                   Enable verbose output and debug logging
  --config                    Path to custom configuration file
  --help                      Show this help message

Examples:
  oarc-crawlers youtube search --query "python tutorials"
  oarc-crawlers youtube search --query "cooking recipes" --limit 20
  oarc-crawlers youtube search --query "python tutorials" --config ~/.oarc/config.ini
"""

YOUTUBE_CHAT_HELP = """
Fetch chat messages from a YouTube live stream or premiere.

Usage:
  oarc-crawlers youtube chat [OPTIONS]

Options:
  --video-id TEXT             YouTube video ID or URL [required]
  --max-messages INTEGER      Maximum number of messages to collect [default: 1000]
  --duration INTEGER          Duration to collect messages in seconds
  --verbose                   Enable verbose output and debug logging
  --config                    Path to custom configuration file
  --help                      Show this help message

Examples:
  oarc-crawlers youtube chat --video-id dQw4w9WgXcQ
  oarc-crawlers youtube chat --video-id dQw4w9WgXcQ --max-messages 500 --duration 300
  oarc-crawlers youtube chat --video-id dQw4w9WgXcQ --config ~/.oarc/config.ini
"""

# GitHub command detailed help
GH_CLONE_HELP = """
Clone and analyze a GitHub repository.

Usage:
  oarc-crawlers gh clone [OPTIONS]

Options:
  --url TEXT                  GitHub repository URL [required]
  --output-path TEXT          Directory to save the cloned repository
  --verbose                   Enable verbose output and debug logging
  --config                    Path to custom configuration file
  --help                      Show this help message

Examples:
  oarc-crawlers gh clone --url https://github.com/username/repo
  oarc-crawlers gh clone --url https://github.com/username/repo --output-path ./repos
  oarc-crawlers gh clone --url https://github.com/username/repo --config ~/.oarc/config.ini
"""

GH_ANALYZE_HELP = """
Get a summary analysis of a GitHub repository.

Usage:
  oarc-crawlers gh analyze [OPTIONS]

Options:
  --url TEXT                  GitHub repository URL [required]
  --verbose                   Enable verbose output and debug logging
  --config                    Path to custom configuration file
  --help                      Show this help message

Examples:
  oarc-crawlers gh analyze --url https://github.com/username/repo
  oarc-crawlers gh analyze --url https://github.com/username/repo --config ~/.oarc/config.ini
"""

GH_FIND_SIMILAR_HELP = """
Find similar code in a GitHub repository.

Usage:
  oarc-crawlers gh find-similar [OPTIONS]

Options:
  --url TEXT                  GitHub repository URL [required]
  --code TEXT                 Code snippet to find similar code for [required]
  --language TEXT             Programming language of the code snippet
  --verbose                   Enable verbose output and debug logging
  --config                    Path to custom configuration file
  --help                      Show this help message

Examples:
  oarc-crawlers gh find-similar --url https://github.com/username/repo --code "def hello_world():"
  oarc-crawlers gh find-similar --url https://github.com/username/repo --code "import numpy as np" --language python
  oarc-crawlers gh find-similar --url https://github.com/username/repo --code "def hello_world():" --config ~/.oarc/config.ini
"""

# ArXiv command detailed help
ARXIV_DOWNLOAD_HELP = """
Download LaTeX source files for an arXiv paper.

Usage:
  oarc-crawlers arxiv download [OPTIONS]

Options:
  --id TEXT                   arXiv paper ID [required]
  --verbose                   Enable verbose output and debug logging
  --config                    Path to custom configuration file
  --help                      Show this help message

Examples:
  oarc-crawlers arxiv download --id 2310.12123
  oarc-crawlers arxiv download --id 1909.11065
  oarc-crawlers arxiv download --id 2310.12123 --config ~/.oarc/config.ini
"""

ARXIV_SEARCH_HELP = """
Search for papers on arXiv.

Usage:
  oarc-crawlers arxiv search [OPTIONS]

Options:
  --query TEXT                Search query [required]
  --limit INTEGER             Maximum number of results [default: 5]
  --verbose                   Enable verbose output and debug logging
  --config                    Path to custom configuration file
  --help                      Show this help message

Examples:
  oarc-crawlers arxiv search --query "quantum computing" --limit 10
  oarc-crawlers arxiv search --query "machine learning"
  oarc-crawlers arxiv search --query "quantum computing" --config ~/.oarc/config.ini
"""

ARXIV_LATEX_HELP = """
Download and extract LaTeX content from an arXiv paper.

Usage:
  oarc-crawlers arxiv latex [OPTIONS]

Options:
  --id TEXT                   arXiv paper ID [required]
  --verbose                   Enable verbose output and debug logging
  --config                    Path to custom configuration file
  --help                      Show this help message

Examples:
  oarc-crawlers arxiv latex --id 2310.12123
  oarc-crawlers arxiv latex --id 1909.11065
  oarc-crawlers arxiv latex --id 2310.12123 --config ~/.oarc/config.ini
"""

# Web command detailed help
WEB_CRAWL_HELP = """
Crawl and extract content from a webpage.

Usage:
  oarc-crawlers web crawl [OPTIONS]

Options:
  --url TEXT                  URL to crawl [required]
  --output-file TEXT          File to save the extracted content
  --verbose                   Enable verbose output and debug logging
  --config                    Path to custom configuration file
  --help                      Show this help message

Examples:
  oarc-crawlers web crawl --url https://example.com
  oarc-crawlers web crawl --url https://example.com/blog --output-file blog.txt
  oarc-crawlers web crawl --url https://example.com --config ~/.oarc/config.ini
"""

WEB_DOCS_HELP = """
Crawl and extract content from a documentation site.

Usage:
  oarc-crawlers web docs [OPTIONS]

Options:
  --url TEXT                  URL of documentation site [required]
  --verbose                   Enable verbose output and debug logging
  --config                    Path to custom configuration file
  --help                      Show this help message

Examples:
  oarc-crawlers web docs --url https://docs.python.org
  oarc-crawlers web docs --url https://docs.sqlalchemy.org
  oarc-crawlers web docs --url https://docs.python.org --config ~/.oarc/config.ini
"""

WEB_PYPI_HELP = """
Extract information about a PyPI package.

Usage:
  oarc-crawlers web pypi [OPTIONS]

Options:
  --package TEXT              PyPI package name [required]
  --verbose                   Enable verbose output and debug logging
  --config                    Path to custom configuration file
  --help                      Show this help message

Examples:
  oarc-crawlers web pypi --package requests
  oarc-crawlers web pypi --package numpy
  oarc-crawlers web pypi --package requests --config ~/.oarc/config.ini
"""

# DuckDuckGo command detailed help
DDG_TEXT_HELP = """
Perform a DuckDuckGo text search.

Usage:
  oarc-crawlers ddg text [OPTIONS]

Options:
  --query TEXT                Search query [required]
  --max-results INTEGER       Maximum number of results [default: 5]
  --verbose                   Enable verbose output and debug logging
  --config                    Path to custom configuration file
  --help                      Show this help message

Examples:
  oarc-crawlers ddg text --query "quantum computing"
  oarc-crawlers ddg text --query "machine learning" --max-results 10
  oarc-crawlers ddg text --query "quantum computing" --config ~/.oarc/config.ini
"""

DDG_IMAGES_HELP = """
Perform a DuckDuckGo image search.

Usage:
  oarc-crawlers ddg images [OPTIONS]

Options:
  --query TEXT                Search query [required]
  --max-results INTEGER       Maximum number of results [default: 10]
  --verbose                   Enable verbose output and debug logging
  --config                    Path to custom configuration file
  --help                      Show this help message

Examples:
  oarc-crawlers ddg images --query "cute cats"
  oarc-crawlers ddg images --query "landscapes" --max-results 20
  oarc-crawlers ddg images --query "cute cats" --config ~/.oarc/config.ini
"""

DDG_NEWS_HELP = """
Perform a DuckDuckGo news search.

Usage:
  oarc-crawlers ddg news [OPTIONS]

Options:
  --query TEXT                Search query [required]
  --max-results INTEGER       Maximum number of results [default: 20]
  --verbose                   Enable verbose output and debug logging
  --config                    Path to custom configuration file
  --help                      Show this help message

Examples:
  oarc-crawlers ddg news --query "breaking news"
  oarc-crawlers ddg news --query "technology" --max-results 30
  oarc-crawlers ddg news --query "breaking news" --config ~/.oarc/config.ini
"""

# Build command detailed help
BUILD_PACKAGE_HELP = """
Build the OARC Crawlers package.

Usage:
  oarc-crawlers build package [OPTIONS]

Options:
  --clean/--no-clean          Clean build directories first [default: no-clean]
  --verbose                   Enable verbose output and debug logging
  --config                    Path to custom configuration file
  --help                      Show this help message

Examples:
  oarc-crawlers build package
  oarc-crawlers build package --clean
  oarc-crawlers build package --clean --config ~/.oarc/config.ini
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
  --verbose                   Enable verbose output and debug logging
  --config                    Path to custom configuration file
  --help                      Show this help message

Examples:
  oarc-crawlers publish pypi
  oarc-crawlers publish pypi --test
  oarc-crawlers publish pypi --no-build --config-file ~/.pypirc
  oarc-crawlers publish pypi --config ~/.oarc/config.ini
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
  --verbose     Enable verbose output and debug logging
  --config      Path to custom configuration file
  --help        Show this help message

Example Usage:
  oarc-crawlers mcp run
  oarc-crawlers mcp install --name "OARC Tools"
  oarc-crawlers mcp run --config ~/.oarc/config.ini
"""

MCP_RUN_HELP = """
Run an MCP server for OARC Crawlers.

Usage:
  oarc-crawlers mcp run [OPTIONS]

Options:
  --port INTEGER            Port to run the server on [default: 3000]
  --transport TEXT          Transport method to use (e.g., 'sse', 'ws') [default: ws]
  --data-dir TEXT           Directory to store data
  --verbose                 Enable verbose output and debug logging
  --config                  Path to custom configuration file
  --help                    Show this help message

Examples:
  oarc-crawlers mcp run
  oarc-crawlers mcp run --port 5000 --transport sse
  oarc-crawlers mcp run --config ~/.oarc/config.ini
"""

MCP_INSTALL_HELP = """
Install the MCP server for VS Code integration.

Usage:
  oarc-crawlers mcp install [OPTIONS]

Options:
  --name TEXT               Custom name for the server in VS Code
  --verbose                 Enable verbose output and debug logging
  --config                  Path to custom configuration file
  --help                    Show this help message

Examples:
  oarc-crawlers mcp install
  oarc-crawlers mcp install --name "OARC Tools"
  oarc-crawlers mcp install --config ~/.oarc/config.ini
"""

# Data command detailed help
DATA_HELP = """
Data Command Help

Usage:
  oarc-crawlers data COMMAND [OPTIONS]

Commands:
  view        View contents of a Parquet file

Options:
  --verbose     Enable verbose output and debug logging
  --config      Path to custom configuration file
  --help        Show this help message

Example Usage:
  oarc-crawlers data view data/sources/example.parquet
  oarc-crawlers data view data/sources/example.parquet --max-rows 20
"""

DATA_VIEW_HELP = """
View contents of a Parquet file.

Usage:
  oarc-crawlers data view [OPTIONS] FILE_PATH

Arguments:
  FILE_PATH            Path to the Parquet file [required]

Options:
  --max-rows INTEGER   Maximum number of rows to display [default: 10]
  --verbose           Enable verbose output and debug logging
  --config            Path to custom configuration file
  --help             Show this help message

Examples:
  oarc-crawlers data view data/sources/example.parquet
  oarc-crawlers data view data/sources/example.parquet --max-rows 20
  oarc-crawlers data view data/sources/example.parquet --config ~/.oarc/config.ini
"""

# Config command help texts
CONFIG_HELP = """
Manage configuration settings for OARC Crawlers.

Usage:
  oarc-crawlers config [CONFIG_FILE]

Arguments:
  CONFIG_FILE    Optional path to a specific configuration file.
                 If not provided, the default configuration file will be used or created.

Options:
  --verbose      Enable verbose output and debug logging
  --help         Show this help message

This command launches an interactive menu-based interface for:
  • Viewing current configuration settings
  • Editing configuration values
  • Creating new configuration files
  • Resetting to default values
  • Setting environment variables
"""

CONFIG_SHOW_HELP = """
Show current configuration settings.

Displays all current configuration values and their sources
(default, environment variable, or config file).
"""

CONFIG_CREATE_HELP = """
Create a new configuration file with current settings.

Generates a new INI file containing all current configuration
values. The file can then be edited to customize settings.
"""

CONFIG_EDIT_HELP = """
Edit the configuration file.

Opens the configuration file in your default editor. If no config
file exists, one will be created first.
"""

# Config examples for the main help text
CONFIG_EXAMPLES = """
Examples:
  oarc-crawlers config
  oarc-crawlers config ~/.oarc/config/crawlers.ini
  oarc-crawlers --config ~/my-config.ini youtube download --url https://youtu.be/example
"""