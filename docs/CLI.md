# OARC-Crawlers Command Line Interface

```
   ____    _    ____   ____      ____               
  / __ \  / \  |  _ \ / ___|    / ___|_ __ __ ___      _| | ___ _ __  
 / / _` |/ _ \ | |_) | |       | |   | '__/ _` \ \ /\ / / |/ _ \ '__/ |
| | (_| / ___ \|  _ <| |___    | |___| | | (_| |\ V  V /| |  __/ |  \ \
 \ \__,_/_/   \_\_| \_\____|    \____|_|  \__,_| \_/\_/ |_|\___|_|  |/
  \____/                                                                  
```

## Table of Contents
- [Installation](#installation)
- [Global Options](#global-options)
- [Command Overview](#command-overview)
- [ArXiv Commands](#arxiv-commands)
- [GitHub Commands](#github-commands)
- [YouTube Commands](#youtube-commands)
- [DuckDuckGo Commands](#duckduckgo-commands)
- [Web Crawler Commands](#web-crawler-commands)
- [Build Commands](#build-commands)
- [Data Commands](#data-commands)
- [Publish Commands](#publish-commands)
- [MCP Commands](#mcp-commands)
- [Configuration Commands](#configuration-commands)
- [Advanced Usage](#advanced-usage)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)

## Installation

To use the OARC-Crawlers CLI, first install the package:

```bash
# Install using pip
pip install oarc-crawlers

# Or install using uv for better dependency resolution
pip install uv
uv pip install oarc-crawlers
```

After installation, the command-line interface is available via the `oarc-crawlers` command:

```bash
oarc-crawlers --help
```

## Global Options

The following options are available for all commands:

| Option | Description |
|--------|-------------|
| `--verbose` | Enable verbose output and debug logging |
| `--config PATH` | Path to custom configuration file |
| `--help` | Show help message and exit |
| `--version` | Show the version and exit |

Example with global options:
```bash
oarc-crawlers --verbose --config ~/.oarc/config.ini yt download --url https://youtu.be/example
```

## Command Overview

OARC-Crawlers provides the following main commands:

| Command | Description |
|---------|-------------|
| `arxiv` | Download papers and extract content from ArXiv |
| `gh` | Clone, analyze, and extract from GitHub repositories |
| `yt` | Download videos and extract information from YouTube |
| `ddg` | Search for information using DuckDuckGo |
| `web` | Extract content from websites |
| `build` | Build operations for package management |
| `publish` | Publish operations for distributing packages |
| `mcp` | Run and manage Model Context Protocol server |
| `config` | Manage configuration settings interactively |

## ArXiv Commands

### Overview

```bash
oarc-crawlers arxiv [COMMAND] [OPTIONS]
```

ArXiv commands allow you to interact with academic papers from the ArXiv repository.

### Commands

#### `download`

Download LaTeX source files for an arXiv paper.

```bash
oarc-crawlers arxiv download --id [ARXIV_ID]
```

**Options:**
- `--id TEXT` - arXiv paper ID [required]
- `--verbose` - Enable verbose output and debug logging
- `--config PATH` - Path to custom configuration file

**Examples:**
```bash
oarc-crawlers arxiv download --id 2310.12123
oarc-crawlers arxiv download --id 1909.11065 --verbose
```

#### `search`

Search for papers on arXiv.

```bash
oarc-crawlers arxiv search --query [QUERY] [OPTIONS]
```

**Options:**
- `--query TEXT` - Search query [required]
- `--limit INTEGER` - Maximum number of results [default: 5]
- `--verbose` - Enable verbose output and debug logging
- `--config PATH` - Path to custom configuration file

**Examples:**
```bash
oarc-crawlers arxiv search --query "quantum computing" --limit 10
oarc-crawlers arxiv search --query "machine learning"
```

#### `latex`

Download and extract LaTeX content from an arXiv paper.

```bash
oarc-crawlers arxiv latex --id [ARXIV_ID]
```

**Options:**
- `--id TEXT` - arXiv paper ID [required]
- `--verbose` - Enable verbose output and debug logging
- `--config PATH` - Path to custom configuration file

**Examples:**
```bash
oarc-crawlers arxiv latex --id 2310.12123
oarc-crawlers arxiv latex --id 1909.11065
```

#### `keywords`

Extract keywords from an arXiv paper.

```bash
oarc-crawlers arxiv keywords --id [ARXIV_ID] [--output-file FILE]
```

**Options:**
- `--id TEXT` - arXiv paper ID [required]
- `--output-file TEXT` - Path to save keywords as JSON
- `--verbose` - Enable verbose output and debug logging
- `--config PATH` - Path to custom configuration file

**Examples:**
```bash
oarc-crawlers arxiv keywords --id 2310.12123
oarc-crawlers arxiv keywords --id 2310.12123 --output-file keywords.json
```

#### `references`

Extract bibliography references from an arXiv paper.

```bash
oarc-crawlers arxiv references --id [ARXIV_ID] [--output-file FILE]
```

**Options:**
- `--id TEXT` - arXiv paper ID [required]
- `--output-file TEXT` - Path to save references as JSON
- `--verbose` - Enable verbose output and debug logging
- `--config PATH` - Path to custom configuration file

**Examples:**
```bash
oarc-crawlers arxiv references --id 2310.12123
oarc-crawlers arxiv references --id 2310.12123 --output-file refs.json
```

#### `equations`

Extract mathematical equations from an arXiv paper.

```bash
oarc-crawlers arxiv equations --id [ARXIV_ID] [--output-file FILE]
```

**Options:**
- `--id TEXT` - arXiv paper ID [required]
- `--output-file TEXT` - Path to save equations as JSON
- `--verbose` - Enable verbose output and debug logging
- `--config PATH` - Path to custom configuration file

**Examples:**
```bash
oarc-crawlers arxiv equations --id 2310.12123
oarc-crawlers arxiv equations --id 2310.12123 --output-file equations.json
```

#### `category`

Fetch recent papers from an arXiv category.

```bash
oarc-crawlers arxiv category --category [CATEGORY] [--limit N]
```

**Options:**
- `--category TEXT` - arXiv category code (e.g., cs.AI) [required]
- `--limit INTEGER` - Maximum number of papers to fetch [default: 20]
- `--verbose` - Enable verbose output and debug logging
- `--config PATH` - Path to custom configuration file

**Examples:**
```bash
oarc-crawlers arxiv category --category cs.AI
oarc-crawlers arxiv category --category math.CO --limit 50
```

#### `batch`

Process multiple papers in batch, optionally extracting keywords and references.

```bash
oarc-crawlers arxiv batch --ids [ID1,ID2,...] [--keywords] [--references]
```

**Options:**
- `--ids TEXT` - Comma-separated list of arXiv IDs [required]
- `--keywords/--no-keywords` - Extract keywords from papers
- `--references/--no-references` - Extract references from papers
- `--verbose` - Enable verbose output and debug logging
- `--config PATH` - Path to custom configuration file

**Examples:**
```bash
oarc-crawlers arxiv batch --ids "2310.12123,2304.12749"
oarc-crawlers arxiv batch --ids "2310.12123,2304.12749" --keywords --references
```

#### `citation-network`

Generate a citation network from seed papers.

```bash
oarc-crawlers arxiv citation-network --ids [ID1,ID2,...] [--max-depth N] [--output-file FILE]
```

**Options:**
- `--ids TEXT` - Comma-separated list of arXiv IDs [required]
- `--max-depth INTEGER` - Reference depth [default: 1]
- `--output-file TEXT` - Path to save the network as JSON
- `--verbose` - Enable verbose output and debug logging
- `--config PATH` - Path to custom configuration file

**Examples:**
```bash
oarc-crawlers arxiv citation-network --ids "2310.12123,2304.12749"
oarc-crawlers arxiv citation-network --ids "2310.12123" --max-depth 2 --output-file network.json
```

## GitHub Commands

### Overview

```bash
oarc-crawlers gh [COMMAND] [OPTIONS]
```

GitHub commands allow you to interact with GitHub repositories.

### Commands

#### `clone`

Clone a GitHub repository and store it locally (as Parquet).

```bash
oarc-crawlers gh clone --url [REPO_URL] [OPTIONS]
```

**Options:**
- `--url TEXT` - GitHub repository URL [required]
- `--output-path TEXT` - Directory to save the cloned repository (optional)
- `--verbose` - Enable verbose output and debug logging
- `--config PATH` - Path to custom configuration file

**Examples:**
```bash
oarc-crawlers gh clone --url https://github.com/username/repo
oarc-crawlers gh clone --url https://github.com/username/repo --output-path ./repos
```

#### `analyze`

Analyze a GitHub repository's content and print a Markdown summary.

```bash
oarc-crawlers gh analyze --url [REPO_URL]
```

**Options:**
- `--url TEXT` - GitHub repository URL [required]
- `--verbose` - Enable verbose output and debug logging
- `--config PATH` - Path to custom configuration file

**Examples:**
```bash
oarc-crawlers gh analyze --url https://github.com/username/repo
```

#### `find-similar`

Find code in a GitHub repository that is similar to the provided code snippet.

```bash
oarc-crawlers gh find-similar --url [REPO_URL] --code [CODE_SNIPPET] [OPTIONS]
```

**Options:**
- `--url TEXT` - GitHub repository URL [required]
- `--code TEXT` - Code snippet to find similar code for [required]
- `--language TEXT` - Programming language of the code snippet (optional)
- `--verbose` - Enable verbose output and debug logging
- `--config PATH` - Path to custom configuration file

**Examples:**
```bash
oarc-crawlers gh find-similar --url https://github.com/username/repo --code "def hello_world():"
oarc-crawlers gh find-similar --url https://github.com/username/repo --code "import numpy as np" --language python
```

## YouTube Commands

### Overview

```bash
oarc-crawlers yt [COMMAND] [OPTIONS]
```

YouTube commands allow you to download videos, playlists, and extract information from YouTube.

### Commands

#### `download`

Download a YouTube video with specified parameters.

```bash
oarc-crawlers yt download --url [VIDEO_URL] [OPTIONS]
```

**Options:**
- `--url TEXT` - YouTube video URL [required]
- `--format TEXT` - Video format (mp4, webm, mp3) [default: mp4]
- `--resolution TEXT` - Video resolution ("highest", "lowest", or specific like "720p") [default: highest]
- `--extract-audio/--no-extract-audio` - Extract audio only [default: no-extract-audio]
- `--output-path TEXT` - Directory to save the video
- `--filename TEXT` - Custom filename for the downloaded video
- `--verbose` - Enable verbose output and debug logging
- `--config PATH` - Path to custom configuration file

**Examples:**
```bash
oarc-crawlers yt download --url https://youtube.com/watch?v=dQw4w9WgXcQ
oarc-crawlers yt download --url https://youtube.com/watch?v=dQw4w9WgXcQ --format mp3 --extract-audio
oarc-crawlers yt download --url https://youtube.com/watch?v=dQw4w9WgXcQ --resolution 720p --output-path ./videos
```

#### `playlist`

Download videos from a YouTube playlist.

```bash
oarc-crawlers yt playlist --url [PLAYLIST_URL] [OPTIONS]
```

**Options:**
- `--url TEXT` - YouTube playlist URL [required]
- `--format TEXT` - Video format (mp4, webm) [default: mp4]
- `--max-videos INTEGER` - Maximum number of videos to download [default: 10]
- `--output-path TEXT` - Directory to save the playlist videos
- `--verbose` - Enable verbose output and debug logging
- `--config PATH` - Path to custom configuration file

**Examples:**
```bash
oarc-crawlers yt playlist --url https://youtube.com/playlist?list=PLzH6n4zXuckquVnQ0KlMDxyXxiSO2DXOQ
oarc-crawlers yt playlist --url https://youtube.com/playlist?list=PLzH6n4zXuckquVnQ0KlMDxyXxiSO2DXOQ --max-videos 5
oarc-crawlers yt playlist --url https://youtube.com/playlist?list=PLzH6n4zXuckquVnQ0KlMDxyXxiSO2DXOQ --format mp4 --output-path ./playlists
```

#### `captions`

Extract captions/subtitles from a YouTube video.

```bash
oarc-crawlers yt captions --url [VIDEO_URL] [OPTIONS]
```

**Options:**
- `--url TEXT` - YouTube video URL [required]
- `--languages TEXT` - Comma-separated language codes (e.g. "en,es,fr") [default: en]
- `--verbose` - Enable verbose output and debug logging
- `--config PATH` - Path to custom configuration file

**Examples:**
```bash
oarc-crawlers yt captions --url https://youtube.com/watch?v=dQw4w9WgXcQ
oarc-crawlers yt captions --url https://youtube.com/watch?v=dQw4w9WgXcQ --languages "en,es,fr"
```

#### `search`

Search for YouTube videos.

```bash
oarc-crawlers yt search --query [QUERY] [OPTIONS]
```

**Options:**
- `--query TEXT` - Search query [required]
- `--limit INTEGER` - Maximum number of results [default: 10]
- `--verbose` - Enable verbose output and debug logging
- `--config PATH` - Path to custom configuration file

**Examples:**
```bash
oarc-crawlers yt search --query "python tutorials"
oarc-crawlers yt search --query "cooking recipes" --limit 20
```

#### `chat`

Fetch chat messages from a YouTube live stream or premiere.

```bash
oarc-crawlers yt chat --video-id [VIDEO_ID] [OPTIONS]
```

**Options:**
- `--video-id TEXT` - YouTube video ID or URL [required]
- `--max-messages INTEGER` - Maximum number of messages to collect [default: 1000]
- `--duration INTEGER` - Duration in seconds to collect messages
- `--verbose` - Enable verbose output and debug logging
- `--config PATH` - Path to custom configuration file

**Examples:**
```bash
oarc-crawlers yt chat --video-id dQw4w9WgXcQ
oarc-crawlers yt chat --video-id dQw4w9WgXcQ --max-messages 500 --duration 300
```

## DuckDuckGo Commands

### Overview

```bash
oarc-crawlers ddg [COMMAND] [OPTIONS]
```

DuckDuckGo commands allow you to search for information using the DuckDuckGo search engine.

### Commands

#### `text`

Perform a DuckDuckGo text search.

```bash
oarc-crawlers ddg text --query [QUERY] [OPTIONS]
```

**Options:**
- `--query TEXT` - Search query [required]
- `--max-results INTEGER` - Maximum number of results [default: 5]
- `--verbose` - Enable verbose output and debug logging
- `--config PATH` - Path to custom configuration file

**Examples:**
```bash
oarc-crawlers ddg text --query "quantum computing"
oarc-crawlers ddg text --query "machine learning" --max-results 10
```

#### `images`

Perform a DuckDuckGo image search.

```bash
oarc-crawlers ddg images --query [QUERY] [OPTIONS]
```

**Options:**
- `--query TEXT` - Search query [required]
- `--max-results INTEGER` - Maximum number of results [default: 10]
- `--verbose` - Enable verbose output and debug logging
- `--config PATH` - Path to custom configuration file

**Examples:**
```bash
oarc-crawlers ddg images --query "cute cats"
oarc-crawlers ddg images --query "landscapes" --max-results 20
```

#### `news`

Perform a DuckDuckGo news search.

```bash
oarc-crawlers ddg news --query [QUERY] [OPTIONS]
```

**Options:**
- `--query TEXT` - Search query [required]
- `--max-results INTEGER` - Maximum number of results [default: 20]
- `--verbose` - Enable verbose output and debug logging
- `--config PATH` - Path to custom configuration file

**Examples:**
```bash
oarc-crawlers ddg news --query "breaking news"
oarc-crawlers ddg news --query "technology" --max-results 30
```

## Web Crawler Commands

### Overview

```bash
oarc-crawlers web [COMMAND] [OPTIONS]
```

Web crawler commands allow you to extract content from websites.

### Commands

#### `crawl`

Crawl and extract content from a webpage.

```bash
oarc-crawlers web crawl --url [URL] [OPTIONS]
```

**Options:**
- `--url TEXT` - URL to crawl [required]
- `--output-file TEXT` - File to save the extracted content
- `--verbose` - Enable verbose output and debug logging
- `--config PATH` - Path to custom configuration file

**Examples:**
```bash
oarc-crawlers web crawl --url https://example.com
oarc-crawlers web crawl --url https://example.com/blog --output-file blog.txt
```

#### `docs`

Crawl and extract content from a documentation site.

```bash
oarc-crawlers web docs --url [URL]
```

**Options:**
- `--url TEXT` - URL of documentation site [required]
- `--verbose` - Enable verbose output and debug logging
- `--config PATH` - Path to custom configuration file

**Examples:**
```bash
oarc-crawlers web docs --url https://docs.python.org
oarc-crawlers web docs --url https://docs.sqlalchemy.org
```

#### `pypi`

Extract information about a PyPI package.

```bash
oarc-crawlers web pypi --package [PACKAGE]
```

**Options:**
- `--package TEXT` - PyPI package name [required]
- `--verbose` - Enable verbose output and debug logging
- `--config PATH` - Path to custom configuration file

**Examples:**
```bash
oarc-crawlers web pypi --package requests
oarc-crawlers web pypi --package numpy
```

## Build Commands

### Overview

```bash
oarc-crawlers build [COMMAND] [OPTIONS]
```

Build commands allow you to manage build operations for the OARC-Crawlers package.

### Commands

#### `package`

Build the OARC Crawlers package.

```bash
oarc-crawlers build package [OPTIONS]
```

**Options:**
- `--clean/--no-clean` - Clean build directories first [default: no-clean]
- `--verbose` - Enable verbose output and debug logging
- `--config PATH` - Path to custom configuration file

**Examples:**
```bash
oarc-crawlers build package
oarc-crawlers build package --clean
```

## Data Commands

### Overview

```bash
oarc-crawlers data [COMMAND] [OPTIONS]
```

Data commands allow you to view and manage data files stored by OARC Crawlers.

### Commands

#### `view`

View contents of a Parquet file, including schema and sample data.

```bash
oarc-crawlers data view [FILE_PATH] [OPTIONS]
```

**Options:**
- `FILE_PATH` - Path to the Parquet file [required]
- `--max-rows INTEGER` - Maximum number of rows to display [default: 10]
- `--verbose` - Enable verbose output and debug logging
- `--config PATH` - Path to custom configuration file

**Examples:**
```bash
oarc-crawlers data view ./data/papers/2310.12123_source.parquet
oarc-crawlers data view ./data/sources/search_results.parquet --max-rows 20
```

**Output Example:**
```
Parquet File: ./data/papers/2310.12123_source.parquet
Shape: 150 rows × 8 columns

Schema:
  • id: string
  • title: string
  • authors: list[string]
  • abstract: string
  • content: string
  • source_files: dict
  • metadata: dict
  • timestamp: datetime64[ns]

First 10 rows:
[table output...]
```

## Publish Commands

### Overview

```bash
oarc-crawlers publish [COMMAND] [OPTIONS]
```

Publish commands allow you to distribute the OARC-Crawlers package.

### Commands

#### `pypi`

Publish the package to PyPI.

```bash
oarc-crawlers publish pypi [OPTIONS]
```

**Options:**
- `--test` - Upload to TestPyPI instead of PyPI
- `--build/--no-build` - Build the package before publishing [default: build]
- `--username TEXT` - PyPI username (if not using keyring)
- `--password TEXT` - PyPI password (if not using keyring)
- `--config-file TEXT` - Path to PyPI config file (.pypirc)
- `--verbose` - Enable verbose output and debug logging
- `--config PATH` - Path to custom configuration file

**Examples:**
```bash
oarc-crawlers publish pypi
oarc-crawlers publish pypi --test
oarc-crawlers publish pypi --no-build --config-file ~/.pypirc
```

## MCP Commands

### Overview

```bash
oarc-crawlers mcp [COMMAND] [OPTIONS]
```

MCP (Model Context Protocol) commands allow you to run and manage the MCP server.

### Commands

#### `run`

Run an MCP server for OARC Crawlers.

```bash
oarc-crawlers mcp run [OPTIONS]
```

**Options:**
- `--port INTEGER` - Port to run the server on [default: 3000]
- `--transport TEXT` - Transport method to use (e.g., 'sse', 'ws') [default: ws]
- `--data-dir TEXT` - Directory to store data
- `--verbose` - Enable verbose output and debug logging
- `--config PATH` - Path to custom configuration file

**Examples:**
```bash
oarc-crawlers mcp run
oarc-crawlers mcp run --port 5000 --transport sse
```

#### `install`

Install the MCP server for VS Code integration.

```bash
oarc-crawlers mcp install [OPTIONS]
```

**Options:**
- `--name TEXT` - Custom name for the server in VS Code
- `--verbose` - Enable verbose output and debug logging
- `--config PATH` - Path to custom configuration file

**Examples:**
```bash
oarc-crawlers mcp install
oarc-crawlers mcp install --name "OARC Tools"
```

### Programmatic Usage Example

```python
from oarc_crawlers.core.mcp.mcp_server import MCPServer

server = MCPServer(data_dir="./data", name="OARC Crawlers", port=3000)
server.run()
```

## Configuration Commands

### Overview

```bash
oarc-crawlers config [CONFIG_FILE] [OPTIONS]
```

Configuration commands allow you to manage OARC-Crawlers configuration settings.

**Arguments:**
- `CONFIG_FILE` - Optional path to a specific configuration file

**Options:**
- `--verbose` - Enable verbose output and debug logging

**Examples:**
```bash
oarc-crawlers config
oarc-crawlers config ~/.oarc/config/crawlers.ini
```

The `config` command launches an interactive menu-based interface for:
- Viewing current configuration settings
- Editing configuration values
- Creating new configuration files
- Resetting to default values
- Setting environment variables

## Advanced Usage

### Command Chaining

You can chain multiple commands together using shell features:

```bash
# Download a YouTube video, then search for related papers
oarc-crawlers yt download --url https://youtu.be/example && \
oarc-crawlers arxiv search --query "subject of the video"
```

### Using Output Files

Many commands support saving output to files:

```bash
# Crawl a website and use its content for a DuckDuckGo search
oarc-crawlers web crawl --url https://example.com/topic --output-file topic.txt
QUERY=$(grep -o -m 1 "[A-Za-z]\{3,\}" topic.txt | head -1)
oarc-crawlers ddg text --query "$QUERY"
```

### Batch Processing

Process multiple items by using shell loops:

```bash
# Download multiple videos from a list
cat video_urls.txt | while read url; do
    oarc-crawlers yt download --url "$url" --output-path "./downloads"
done
```

## Platform-Specific Notes

### Windows

On Windows, the default data directory is `%APPDATA%\oarc\data`.

Example setting environment variables:
```batch
set OARC_DATA_DIR=C:\Users\username\projects\data
set OARC_LOG_LEVEL=DEBUG
```

### Linux/WSL

On Linux and WSL, the default data directory is `~/.local/share/oarc/data`.

Example setting environment variables:
```bash
export OARC_DATA_DIR=$HOME/projects/data
export OARC_LOG_LEVEL=DEBUG
```

## Environment Variables

The OARC-Crawlers CLI respects the following environment variables:

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `OARC_DATA_DIR` | Directory to store data | Windows: `%APPDATA%\oarc\data`<br>Linux: `~/.local/share/oarc/data` |
| `OARC_CONFIG_DIR` | Directory for config files | Windows: `%APPDATA%\oarc\config`<br>Linux: `~/.config/oarc` |
| `OARC_CACHE_DIR` | Directory for cache files | Windows: `%LOCALAPPDATA%\oarc\cache`<br>Linux: `~/.cache/oarc` |
| `OARC_LOG_LEVEL` | Logging level | INFO |
| `OARC_MAX_RETRIES` | Maximum number of retries for network operations | 3 |
| `OARC_TIMEOUT` | Timeout in seconds for network operations | 30 |
| `OARC_USER_AGENT` | User agent string for network requests | oarc-crawlers/VERSION |
| `OARC_PROXY` | HTTP/HTTPS proxy URL | None |
| `OARC_NO_PROGRESS` | Disable progress bars if set to 1 | 0 |

Example of setting environment variables:

```bash
# Set environment variables for a session
export OARC_DATA_DIR="~/projects/data"
export OARC_LOG_LEVEL="DEBUG"

# Use in a single command
OARC_TIMEOUT=30 oarc-crawlers yt download --url https://youtu.be/example
```

## Troubleshooting

### Common Issues

#### Command Not Found

If you see `oarc-crawlers: command not found`, ensure:
- The package is installed: `pip install oarc-crawlers`
- Your Python environment is activated (if using virtualenv)
- Your PATH includes the Python scripts directory

#### Network Issues

For connection problems:
- Check your internet connection
- Verify the URL is accessible in a browser
- Try increasing timeout: `OARC_TIMEOUT=60 oarc-crawlers [command]`
- Use `--verbose` to see detailed error information

#### Permission Issues

If you encounter permission errors:
- Ensure you have write access to the output directory
- Use `--output-path` to specify an accessible directory
- Check ownership of the default data directory (`~/.oarc/data`)

#### Dependency Issues

For dependency-related errors:
- Create a clean virtual environment
- Install with `uv`: `uv pip install oarc-crawlers`
- Specify exact version: `pip install oarc-crawlers==X.Y.Z`

### Getting Help

For detailed help on any command:

```bash
# Get general help
oarc-crawlers --help

# Get help for a specific command
oarc-crawlers yt --help

# Get help for a specific subcommand
oarc-crawlers yt download --help
```

For additional support:
- Check the [documentation](https://github.com/Ollama-Agent-Roll-Cage/oarc-crawlers/tree/main/docs)
- Submit an issue on [GitHub](https://github.com/Ollama-Agent-Roll-Cage/oarc-crawlers/issues)