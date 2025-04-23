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
CONFIG_GROUP_HELP = "Manage configuration settings for OARC Crawlers."
MCP_GROUP_HELP = "Model Context Protocol (MCP) server operations."

# Command option descriptions
ARGS_HELP = "Show this help message and exit."
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
ARGS_CATEGORY_HELP = "ArXiv category to fetch papers from"
ARGS_IDS_HELP = "Comma-separated list of arXiv paper IDs"
ARGS_MAX_DEPTH_HELP = "Maximum depth for citation network generation"

# --- Main CLI Help ---
# This shorter version is meant to be used as a docstring with Click's built-in help formatting
MAIN_HELP = """OARC Crawlers Command-Line Interface."""

# This is the original longer version, renamed so you can choose which to use in your CLI code
MAIN_HELP_DETAILED = f"""
OARC Crawlers Command-Line Interface.

USAGE:
  oarc-crawlers [OPTIONS] COMMAND [ARGS]...

  For detailed information about any command:
    oarc-crawlers <command> --help

Options:
  --version             Show the version and exit.
  --verbose             {ARGS_VERBOSE_HELP}
  --config TEXT         {ARGS_CONFIG_HELP}
  --help                {ARGS_HELP}

Commands:
  arxiv                 {ARXIV_GROUP_HELP}
  build                 {BUILD_GROUP_HELP}
  config                Manage configuration settings for OARC Crawlers.
  data                  {DATA_GROUP_HELP}
  ddg                   {DDG_GROUP_HELP}
  gh                    {GH_GROUP_HELP}
  mcp                   Model Context Protocol (MCP) server operations.
  publish               {PUBLISH_GROUP_HELP}
  web                   {WEB_GROUP_HELP}
  yt                    {YOUTUBE_GROUP_HELP}
"""

# --- Command Group Help Texts ---

BUILD_HELP = f"""
Build operations for package management.

USAGE:
  oarc-crawlers build COMMAND [OPTIONS]

Commands:
  package               Build the OARC Crawlers package.

Options:
  --verbose             {ARGS_VERBOSE_HELP}
  --config TEXT         {ARGS_CONFIG_HELP}
  --help                {ARGS_HELP}

Examples:
  oarc-crawlers build package
  oarc-crawlers build package --clean
  oarc-crawlers build package --config ~/.oarc/config.ini

"""

PUBLISH_HELP = f"""
Publish operations for distributing packages.

USAGE:
  oarc-crawlers publish COMMAND [OPTIONS]

Commands:
  pypi                  Publish to PyPI or TestPyPI.

Options:
  --verbose             {ARGS_VERBOSE_HELP}
  --config TEXT         {ARGS_CONFIG_HELP}
  --help                {ARGS_HELP}

Examples:
  oarc-crawlers publish pypi
  oarc-crawlers publish pypi --test
  oarc-crawlers publish pypi --config ~/.oarc/config.ini

"""

YOUTUBE_HELP = f"""
YouTube operations for downloading videos and extracting information.

USAGE:
  oarc-crawlers youtube COMMAND [OPTIONS]

Commands:
  download              Download a YouTube video.
  playlist              Download videos from a YouTube playlist.
  captions              Extract captions/subtitles from a YouTube video.
  search                Search for videos on YouTube.
  chat                  Fetch chat messages from a YouTube live stream.

Options:
  --verbose             {ARGS_VERBOSE_HELP}
  --config TEXT         {ARGS_CONFIG_HELP}
  --help                {ARGS_HELP}

Examples:
  oarc-crawlers yt download --url https://youtube.com/watch?v=example
  oarc-crawlers yt search --query "python tutorials"
  oarc-crawlers yt download --url https://youtube.com/watch?v=example --config ~/.oarc/config.ini

"""

GH_HELP = f"""
GitHub operations for cloning, analyzing and extracting from repositories.

USAGE:
  oarc-crawlers gh COMMAND [OPTIONS]

Commands:
  clone                 Clone a GitHub repository.
  analyze               Analyze a GitHub repository's content.
  find-similar          Find code similar to a snippet in a repository.

Options:
  --verbose             {ARGS_VERBOSE_HELP}
  --config TEXT         {ARGS_CONFIG_HELP}
  --help                {ARGS_HELP}

Examples:
  oarc-crawlers gh clone --url https://github.com/username/repo
  oarc-crawlers gh analyze --url https://github.com/username/repo
  oarc-crawlers gh clone --url https://github.com/username/repo --config ~/.oarc/config.ini

"""

ARXIV_HELP = f"""
ArXiv operations for downloading papers and extracting content.

USAGE:
  oarc-crawlers arxiv COMMAND [OPTIONS]

Commands:
  download              Download LaTeX source files for a paper.
  search                Search for papers on arXiv.
  latex                 Download and extract LaTeX content from a paper.
  keywords              Extract keywords from an arXiv paper.
  references            Extract bibliography references from an arXiv paper.
  equations             Extract mathematical equations from an arXiv paper.
  category              Fetch recent papers from an arXiv category.
  batch                 Process multiple papers in batch.
  citation-network      Generate a citation network from seed papers.

Options:
  --verbose             {ARGS_VERBOSE_HELP}
  --config TEXT         {ARGS_CONFIG_HELP}
  --help                {ARGS_HELP}

Examples:
  oarc-crawlers arxiv download --id 2310.12123
  oarc-crawlers arxiv latex --id 1909.11065
  oarc-crawlers arxiv download --id 2310.12123 --config ~/.oarc/config.ini

"""

WEB_HELP = f"""
Web crawler operations for extracting content from websites.

USAGE:
  oarc-crawlers web COMMAND [OPTIONS]

Commands:
  crawl                 Extract content from a webpage.
  docs                  Extract content from a documentation site.
  pypi                  Extract information about a PyPI package.

Options:
  --verbose             {ARGS_VERBOSE_HELP}
  --config TEXT         {ARGS_CONFIG_HELP}
  --help                {ARGS_HELP}

Examples:
  oarc-crawlers web crawl --url https://example.com
  oarc-crawlers web pypi --package requests
  oarc-crawlers web crawl --url https://example.com --config ~/.oarc/config.ini

"""

DDG_HELP = f"""
DuckDuckGo search operations for finding information online.

USAGE:
  oarc-crawlers ddg COMMAND [OPTIONS]

Commands:
  text                  Perform a DuckDuckGo text search.
  images                Perform a DuckDuckGo image search.
  news                  Perform a DuckDuckGo news search.

Options:
  --verbose             {ARGS_VERBOSE_HELP}
  --config TEXT         {ARGS_CONFIG_HELP}
  --help                {ARGS_HELP}

Examples:
  oarc-crawlers ddg text --query "quantum computing"
  oarc-crawlers ddg images --query "cute cats"
  oarc-crawlers ddg text --query "quantum computing" --config ~/.oarc/config.ini

"""

MCP_HELP = f"""
Model Context Protocol (MCP) server operations.

USAGE:
  oarc-crawlers mcp COMMAND [OPTIONS]

Commands:
  run                   Run the MCP server.
  install               Install the MCP server for VS Code integration.

Options:
  --verbose             {ARGS_VERBOSE_HELP}
  --config TEXT         {ARGS_CONFIG_HELP}
  --help                {ARGS_HELP}

Examples:
  oarc-crawlers mcp run
  oarc-crawlers mcp install --name "OARC Tools"
  oarc-crawlers mcp run --config ~/.oarc/config.ini

"""

DATA_HELP = f"""
Data management operations for viewing and manipulating data files.

USAGE:
  oarc-crawlers data COMMAND [OPTIONS]

Commands:
  view                  View contents of a Parquet file.

Options:
  --verbose             {ARGS_VERBOSE_HELP}
  --config TEXT         {ARGS_CONFIG_HELP}
  --help                {ARGS_HELP}

Examples:
  oarc-crawlers data view data/sources/example.parquet
  oarc-crawlers data view data/sources/example.parquet --max-rows 20

"""

CONFIG_HELP = f"""
Manage configuration settings for OARC Crawlers.

USAGE:
  oarc-crawlers config [CONFIG_FILE] [OPTIONS]

Arguments:
  CONFIG_FILE           Optional path to a specific configuration file.
                        If not provided, the default configuration file will be used or created.

Options:
  --verbose             {ARGS_VERBOSE_HELP}
  --help                {ARGS_HELP}

Description:
  This command launches an interactive menu-based interface for:
    * Viewing current configuration settings
    * Editing configuration values
    * Creating new configuration files
    * Resetting to default values
    * Setting environment variables

Examples:
  oarc-crawlers config
  oarc-crawlers config ~/.oarc/config/crawlers.ini
  oarc-crawlers --config ~/my-config.ini youtube download --url https://youtu.be/example

"""

# --- Detailed Command Help Texts ---

# YouTube
YOUTUBE_DOWNLOAD_HELP = f"""
Download a YouTube video with specified parameters.

USAGE:
  oarc-crawlers yt download [OPTIONS]

Options:
  --url TEXT                  {ARGS_URL_HELP} [required]
  --format TEXT               Video format (mp4, webm, mp3) [default: mp4]
  --resolution TEXT           {ARGS_RESOLUTION_HELP} [default: highest]
  --extract-audio / --no-extract-audio
                              {ARGS_EXTRACT_AUDIO_HELP} [default: no-extract-audio]
  --output-path TEXT          {ARGS_OUTPUT_PATH_HELP}
  --filename TEXT             {ARGS_FILENAME_HELP}
  --verbose                   {ARGS_VERBOSE_HELP}
  --config TEXT               {ARGS_CONFIG_HELP}
  --help                      {ARGS_HELP}

Examples:
  oarc-crawlers yt download --url https://youtube.com/watch?v=dQw4w9WgXcQ
  oarc-crawlers yt download --url https://youtube.com/watch?v=dQw4w9WgXcQ --format mp3 --extract-audio
  oarc-crawlers yt download --url https://youtube.com/watch?v=dQw4w9WgXcQ --resolution 720p --output-path ./videos
  oarc-crawlers yt download --url https://youtube.com/watch?v=dQw4w9WgXcQ --config ~/.oarc/config.ini

"""

YOUTUBE_PLAYLIST_HELP = f"""
Download videos from a YouTube playlist.

USAGE:
  oarc-crawlers youtube playlist [OPTIONS]

Options:
  --url TEXT                  {ARGS_PLAYLIST_URL_HELP} [required]
  --format TEXT               Video format (mp4, webm) [default: mp4]
  --max-videos INTEGER        {ARGS_MAX_VIDEOS_HELP} [default: 10]
  --output-path TEXT          {ARGS_OUTPUT_PATH_HELP}
  --verbose                   {ARGS_VERBOSE_HELP}
  --config TEXT               {ARGS_CONFIG_HELP}
  --help                      {ARGS_HELP}

Examples:
  oarc-crawlers yt playlist --url https://youtube.com/playlist?list=PLzH6n4zXuckquVnQ0KlMDxyXxiSO2DXOQ
  oarc-crawlers yt playlist --url https://youtube.com/playlist?list=PLzH6n4zXuckquVnQ0KlMDxyXxiSO2DXOQ --max-videos 5
  oarc-crawlers yt playlist --url https://youtube.com/playlist?list=PLzH6n4zXuckquVnQ0KlMDxyXxiSO2DXOQ --format mp4 --output-path ./playlists
  oarc-crawlers yt playlist --url https://youtube.com/playlist?list=PLzH6n4zXuckquVnQ0KlMDxyXxiSO2DXOQ --config ~/.oarc/config.ini

"""

YOUTUBE_CAPTIONS_HELP = f"""
Extract captions/subtitles from a YouTube video.

USAGE:
  oarc-crawlers youtube captions [OPTIONS]

Options:
  --url TEXT                  {ARGS_VIDEO_URL_HELP} [required]
  --languages TEXT            {ARGS_LANGUAGES_HELP} [default: en]
  --verbose                   {ARGS_VERBOSE_HELP}
  --config TEXT               {ARGS_CONFIG_HELP}
  --help                      {ARGS_HELP}

Examples:
  oarc-crawlers yt captions --url https://youtube.com/watch?v=dQw4w9WgXcQ
  oarc-crawlers yt captions --url https://youtube.com/watch?v=dQw4w9WgXcQ --languages "en,es,fr"
  oarc-crawlers yt captions --url https://youtube.com/watch?v=dQw4w9WgXcQ --config ~/.oarc/config.ini

"""

YOUTUBE_SEARCH_HELP = f"""
Search for YouTube videos.

USAGE:
  oarc-crawlers youtube search [OPTIONS]

Options:
  --query TEXT                {ARGS_QUERY_HELP} [required]
  --limit INTEGER             {ARGS_LIMIT_HELP} [default: 10]
  --verbose                   {ARGS_VERBOSE_HELP}
  --config TEXT               {ARGS_CONFIG_HELP}
  --help                      {ARGS_HELP}

Examples:
  oarc-crawlers yt search --query "python tutorials"
  oarc-crawlers yt search --query "cooking recipes" --limit 20
  oarc-crawlers yt search --query "python tutorials" --config ~/.oarc/config.ini

"""

YOUTUBE_CHAT_HELP = f"""
Fetch chat messages from a YouTube live stream or premiere.

USAGE:
  oarc-crawlers yt chat [OPTIONS]

Options:
  --video-id TEXT             {ARGS_VIDEO_ID_HELP} [required]
  --max-messages INTEGER      {ARGS_MAX_MESSAGES_HELP} [default: 1000]
  --duration INTEGER          {ARGS_DURATION_HELP}
  --verbose                   {ARGS_VERBOSE_HELP}
  --config TEXT               {ARGS_CONFIG_HELP}
  --help                      {ARGS_HELP}

Examples:
  oarc-crawlers yt chat --video-id dQw4w9WgXcQ
  oarc-crawlers yt chat --video-id dQw4w9WgXcQ --max-messages 500 --duration 300
  oarc-crawlers yt chat --video-id dQw4w9WgXcQ --config ~/.oarc/config.ini

"""

# GitHub
GH_CLONE_HELP = f"""
Clone and analyze a GitHub repository.

USAGE:
  oarc-crawlers gh clone [OPTIONS]

Options:
  --url TEXT                  {ARGS_REPO_URL_HELP} [required]
  --output-path TEXT          {ARGS_OUTPUT_PATH_HELP}
  --verbose                   {ARGS_VERBOSE_HELP}
  --config TEXT               {ARGS_CONFIG_HELP}
  --help                      {ARGS_HELP}

Examples:
  oarc-crawlers gh clone --url https://github.com/username/repo
  oarc-crawlers gh clone --url https://github.com/username/repo --output-path ./repos
  oarc-crawlers gh clone --url https://github.com/username/repo --config ~/.oarc/config.ini

"""

GH_ANALYZE_HELP = f"""
Get a summary analysis of a GitHub repository.

USAGE:
  oarc-crawlers gh analyze [OPTIONS]

Options:
  --url TEXT                  {ARGS_REPO_URL_HELP} [required]
  --verbose                   {ARGS_VERBOSE_HELP}
  --config TEXT               {ARGS_CONFIG_HELP}
  --help                      {ARGS_HELP}

Examples:
  oarc-crawlers gh analyze --url https://github.com/username/repo
  oarc-crawlers gh analyze --url https://github.com/username/repo --config ~/.oarc/config.ini

"""

GH_FIND_SIMILAR_HELP = f"""
Find similar code in a GitHub repository.

USAGE:
  oarc-crawlers gh find-similar [OPTIONS]

Options:
  --url TEXT                  {ARGS_REPO_URL_HELP} [required]
  --code TEXT                 {ARGS_CODE_HELP} [required]
  --language TEXT             {ARGS_LANGUAGE_HELP}
  --verbose                   {ARGS_VERBOSE_HELP}
  --config TEXT               {ARGS_CONFIG_HELP}
  --help                      {ARGS_HELP}

Examples:
  oarc-crawlers gh find-similar --url https://github.com/username/repo --code "def hello_world():"
  oarc-crawlers gh find-similar --url https://github.com/username/repo --code "import numpy as np" --language python
  oarc-crawlers gh find-similar --url https://github.com/username/repo --code "def hello_world():" --config ~/.oarc/config.ini

"""

# ArXiv
ARXIV_DOWNLOAD_HELP = f"""
Download LaTeX source files for an arXiv paper.

USAGE:
  oarc-crawlers arxiv download [OPTIONS]

Options:
  --id TEXT                   {ARGS_ID_HELP} [required]
  --verbose                   {ARGS_VERBOSE_HELP}
  --config TEXT               {ARGS_CONFIG_HELP}
  --help                      {ARGS_HELP}

Examples:
  oarc-crawlers arxiv download --id 2310.12123
  oarc-crawlers arxiv download --id 1909.11065
  oarc-crawlers arxiv download --id 2310.12123 --config ~/.oarc/config.ini

"""

ARXIV_SEARCH_HELP = f"""
Search for papers on arXiv.

USAGE:
  oarc-crawlers arxiv search [OPTIONS]

Options:
  --query TEXT                {ARGS_QUERY_HELP} [required]
  --limit INTEGER             {ARGS_LIMIT_HELP} [default: 5]
  --verbose                   {ARGS_VERBOSE_HELP}
  --config TEXT               {ARGS_CONFIG_HELP}
  --help                      {ARGS_HELP}

Examples:
  oarc-crawlers arxiv search --query "quantum computing" --limit 10
  oarc-crawlers arxiv search --query "machine learning"
  oarc-crawlers arxiv search --query "quantum computing" --config ~/.oarc/config.ini

"""

ARXIV_LATEX_HELP = f"""
Download and extract LaTeX content from an arXiv paper.

USAGE:
  oarc-crawlers arxiv latex [OPTIONS]

Options:
  --id TEXT                   {ARGS_ID_HELP} [required]
  --verbose                   {ARGS_VERBOSE_HELP}
  --config TEXT               {ARGS_CONFIG_HELP}
  --help                      {ARGS_HELP}

Examples:
  oarc-crawlers arxiv latex --id 2310.12123
  oarc-crawlers arxiv latex --id 1909.11065
  oarc-crawlers arxiv latex --id 2310.12123 --config ~/.oarc/config.ini

"""

ARXIV_KEYWORDS_HELP = f"""
Extract keywords from an arXiv paper.

USAGE:
  oarc-crawlers arxiv keywords [OPTIONS]

Options:
  --id TEXT                   {ARGS_ID_HELP} [required]
  --output-file TEXT          {ARGS_OUTPUT_FILE_HELP}
  --verbose                   {ARGS_VERBOSE_HELP}
  --config TEXT               {ARGS_CONFIG_HELP}
  --help                      {ARGS_HELP}

Examples:
  oarc-crawlers arxiv keywords --id 2310.12123
  oarc-crawlers arxiv keywords --id 2310.12123 --output-file keywords.json
  oarc-crawlers arxiv keywords --id 2310.12123 --config ~/.oarc/config.ini
"""

ARXIV_REFERENCES_HELP = f"""
Extract bibliography references from an arXiv paper.

USAGE:
  oarc-crawlers arxiv references [OPTIONS]

Options:
  --id TEXT                   {ARGS_ID_HELP} [required]
  --output-file TEXT          {ARGS_OUTPUT_FILE_HELP}
  --verbose                   {ARGS_VERBOSE_HELP}
  --config TEXT               {ARGS_CONFIG_HELP}
  --help                      {ARGS_HELP}

Examples:
  oarc-crawlers arxiv references --id 2310.12123
  oarc-crawlers arxiv references --id 2310.12123 --output-file refs.json
  oarc-crawlers arxiv references --id 2310.12123 --verbose
"""

ARXIV_EQUATIONS_HELP = f"""
Extract mathematical equations from an arXiv paper.

USAGE:
  oarc-crawlers arxiv equations [OPTIONS]

Options:
  --id TEXT                   {ARGS_ID_HELP} [required]
  --output-file TEXT          {ARGS_OUTPUT_FILE_HELP}
  --verbose                   {ARGS_VERBOSE_HELP}
  --config TEXT               {ARGS_CONFIG_HELP}
  --help                      {ARGS_HELP}

Examples:
  oarc-crawlers arxiv equations --id 2310.12123
  oarc-crawlers arxiv equations --id 2310.12123 --output-file equations.json
  oarc-crawlers arxiv equations --id 2310.12123 --verbose
"""

ARXIV_CATEGORY_HELP = f"""
Fetch recent papers from an arXiv category.

USAGE:
  oarc-crawlers arxiv category [OPTIONS]

Options:
  --category TEXT             {ARGS_CATEGORY_HELP} [required]
  --limit INTEGER             {ARGS_LIMIT_HELP}
  --verbose                   {ARGS_VERBOSE_HELP}
  --config TEXT               {ARGS_CONFIG_HELP}
  --help                      {ARGS_HELP}

Examples:
  oarc-crawlers arxiv category --category cs.AI
  oarc-crawlers arxiv category --category physics.optics --limit 50
  oarc-crawlers arxiv category --category math.CO --verbose
"""

ARXIV_BATCH_HELP = f"""
Process multiple papers in batch.

USAGE:
  oarc-crawlers arxiv batch [OPTIONS]

Options:
  --ids TEXT                  {ARGS_IDS_HELP} [required]
  --keywords / --no-keywords  Extract keywords from papers
  --references / --no-references  Extract references from papers
  --verbose                   {ARGS_VERBOSE_HELP}
  --config TEXT               {ARGS_CONFIG_HELP}
  --help                      {ARGS_HELP}

Examples:
  oarc-crawlers arxiv batch --ids "2304.12749,2310.06825,2401.00123"
  oarc-crawlers arxiv batch --ids "2304.12749,2310.06825" --keywords --references
  oarc-crawlers arxiv batch --ids "2304.12749" --keywords --verbose
"""

ARXIV_CITATION_NETWORK_HELP = f"""
Generate a citation network from seed papers.

USAGE:
  oarc-crawlers arxiv citation-network [OPTIONS]

Options:
  --ids TEXT                  {ARGS_IDS_HELP} [required]
  --max-depth INTEGER         {ARGS_MAX_DEPTH_HELP}
  --output-file TEXT          {ARGS_OUTPUT_FILE_HELP}
  --verbose                   {ARGS_VERBOSE_HELP}
  --config TEXT               {ARGS_CONFIG_HELP}
  --help                      {ARGS_HELP}

Examples:
  oarc-crawlers arxiv citation-network --ids "2304.12749,2310.06825"
  oarc-crawlers arxiv citation-network --ids "2304.12749" --max-depth 2
  oarc-crawlers arxiv citation-network --ids "2304.12749" --output-file network.json
"""

# Web
WEB_CRAWL_HELP = f"""
Crawl and extract content from a webpage.

USAGE:
  oarc-crawlers web crawl [OPTIONS]

Options:
  --url TEXT                  {ARGS_URL_HELP} [required]
  --output-file TEXT          {ARGS_OUTPUT_FILE_HELP}
  --verbose                   {ARGS_VERBOSE_HELP}
  --config TEXT               {ARGS_CONFIG_HELP}
  --help                      {ARGS_HELP}

Examples:
  oarc-crawlers web crawl --url https://example.com
  oarc-crawlers web crawl --url https://example.com/blog --output-file blog.txt
  oarc-crawlers web crawl --url https://example.com --config ~/.oarc/config.ini

"""

WEB_DOCS_HELP = f"""
Crawl and extract content from a documentation site.

USAGE:
  oarc-crawlers web docs [OPTIONS]

Options:
  --url TEXT                  URL of documentation site [required]
  --verbose                   {ARGS_VERBOSE_HELP}
  --config TEXT               {ARGS_CONFIG_HELP}
  --help                      {ARGS_HELP}

Examples:
  oarc-crawlers web docs --url https://docs.python.org
  oarc-crawlers web docs --url https://docs.sqlalchemy.org
  oarc-crawlers web docs --url https://docs.python.org --config ~/.oarc/config.ini

"""

WEB_PYPI_HELP = f"""
Extract information about a PyPI package.

USAGE:
  oarc-crawlers web pypi [OPTIONS]

Options:
  --package TEXT              {ARGS_PACKAGE_HELP} [required]
  --verbose                   {ARGS_VERBOSE_HELP}
  --config TEXT               {ARGS_CONFIG_HELP}
  --help                      {ARGS_HELP}

Examples:
  oarc-crawlers web pypi --package requests
  oarc-crawlers web pypi --package numpy
  oarc-crawlers web pypi --package requests --config ~/.oarc/config.ini

"""

# DuckDuckGo
DDG_TEXT_HELP = f"""
Perform a DuckDuckGo text search.

USAGE:
  oarc-crawlers ddg text [OPTIONS]

Options:
  --query TEXT                {ARGS_QUERY_HELP} [required]
  --max-results INTEGER       {ARGS_MAX_RESULTS_HELP} [default: 5]
  --verbose                   {ARGS_VERBOSE_HELP}
  --config TEXT               {ARGS_CONFIG_HELP}
  --help                      {ARGS_HELP}

Examples:
  oarc-crawlers ddg text --query "quantum computing"
  oarc-crawlers ddg text --query "machine learning" --max-results 10
  oarc-crawlers ddg text --query "quantum computing" --config ~/.oarc/config.ini

"""

DDG_IMAGES_HELP = f"""
Perform a DuckDuckGo image search.

USAGE:
  oarc-crawlers ddg images [OPTIONS]

Options:
  --query TEXT                {ARGS_QUERY_HELP} [required]
  --max-results INTEGER       {ARGS_MAX_RESULTS_HELP} [default: 10]
  --verbose                   {ARGS_VERBOSE_HELP}
  --config TEXT               {ARGS_CONFIG_HELP}
  --help                      {ARGS_HELP}

Examples:
  oarc-crawlers ddg images --query "cute cats"
  oarc-crawlers ddg images --query "landscapes" --max-results 20
  oarc-crawlers ddg images --query "cute cats" --config ~/.oarc/config.ini

"""

DDG_NEWS_HELP = f"""
Perform a DuckDuckGo news search.

USAGE:
  oarc-crawlers ddg news [OPTIONS]

Options:
  --query TEXT                {ARGS_QUERY_HELP} [required]
  --max-results INTEGER       {ARGS_MAX_RESULTS_HELP} [default: 20]
  --verbose                   {ARGS_VERBOSE_HELP}
  --config TEXT               {ARGS_CONFIG_HELP}
  --help                      {ARGS_HELP}

Examples:
  oarc-crawlers ddg news --query "breaking news"
  oarc-crawlers ddg news --query "technology" --max-results 30
  oarc-crawlers ddg news --query "breaking news" --config ~/.oarc/config.ini

"""

# Build
BUILD_PACKAGE_HELP = f"""
Build the OARC Crawlers package.

USAGE:
  oarc-crawlers build package [OPTIONS]

Options:
  --clean / --no-clean        {ARGS_CLEAN_HELP} [default: no-clean]
  --verbose                   {ARGS_VERBOSE_HELP}
  --config TEXT               {ARGS_CONFIG_HELP}
  --help                      {ARGS_HELP}

Examples:
  oarc-crawlers build package
  oarc-crawlers build package --clean
  oarc-crawlers build package --clean --config ~/.oarc/config.ini

"""

# Publish
PUBLISH_PYPI_HELP = f"""
Publish the package to PyPI.

USAGE:
  oarc-crawlers publish pypi [OPTIONS]

Options:
  --test                      {ARGS_TEST_HELP}
  --build / --no-build        {ARGS_BUILD_HELP} [default: build]
  --username TEXT             {ARGS_PYPI_USERNAME_HELP}
  --password TEXT             {ARGS_PYPI_PASSWORD_HELP}
  --config-file TEXT          {ARGS_PYPI_CONFIG_FILE_HELP}
  --verbose                   {ARGS_VERBOSE_HELP}
  --config TEXT               {ARGS_CONFIG_HELP}
  --help                      {ARGS_HELP}

Examples:
  oarc-crawlers publish pypi
  oarc-crawlers publish pypi --test
  oarc-crawlers publish pypi --no-build --config-file ~/.pypirc
  oarc-crawlers publish pypi --config ~/.oarc/config.ini

"""

# MCP
MCP_RUN_HELP = f"""
Run an MCP server for OARC Crawlers.

USAGE:
  oarc-crawlers mcp run [OPTIONS]

Options:
  --port INTEGER              {ARGS_PORT_HELP} [default: 3000]
  --transport TEXT            {ARGS_TRANSPORT_HELP} (e.g., 'sse', 'ws') [default: ws]
  --data-dir TEXT             {ARGS_DATA_DIR_HELP}
  --verbose                   {ARGS_VERBOSE_HELP}
  --config TEXT               {ARGS_CONFIG_HELP}
  --help                      {ARGS_HELP}

Examples:
  oarc-crawlers mcp run
  oarc-crawlers mcp run --port 5000 --transport sse
  oarc-crawlers mcp run --config ~/.oarc/config.ini

"""

MCP_INSTALL_HELP = f"""
Install the MCP server for VS Code integration.

USAGE:
  oarc-crawlers mcp install [OPTIONS]

Options:
  --name TEXT                 {ARGS_MCP_NAME_HELP}
  --verbose                   {ARGS_VERBOSE_HELP}
  --config TEXT               {ARGS_CONFIG_HELP}
  --help                      {ARGS_HELP}

Examples:
  oarc-crawlers mcp install
  oarc-crawlers mcp install --name "OARC Tools"
  oarc-crawlers mcp install --config ~/.oarc/config.ini

"""

# Data
DATA_VIEW_HELP = f"""
View contents of a Parquet file.

USAGE:
  oarc-crawlers data view [OPTIONS] FILE_PATH

Arguments:
  FILE_PATH                   {ARGS_FILE_PATH_HELP} [required]

Options:
  --max-rows INTEGER          {ARGS_MAX_ROWS_HELP} [default: 10]
  --verbose                   {ARGS_VERBOSE_HELP}
  --config TEXT               {ARGS_CONFIG_HELP}
  --help                      {ARGS_HELP}

Examples:
  oarc-crawlers data view data/sources/example.parquet
  oarc-crawlers data view data/sources/example.parquet --max-rows 20
  oarc-crawlers data view data/sources/example.parquet --config ~/.oarc/config.ini

"""

# --- Deprecated/Internal Help Texts (Keep as is or remove if unused) ---
# These seem less critical for user-facing help consistency but are included for completeness.
# If they are not directly used by Click's help generation, they might not need formatting.

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

CONFIG_EXAMPLES = """
Examples:
  oarc-crawlers config
  oarc-crawlers config ~/.oarc/config/crawlers.ini
  oarc-crawlers --config ~/my-config.ini youtube download --url https://youtu.be/example
"""

# --- Command Group Descriptions (Used in MAIN_HELP, keep as is) ---
YOUTUBE_GROUP_HELP = "YouTube operations for downloading videos and extracting information."
GH_GROUP_HELP = "GitHub operations for cloning, analyzing and extracting from repositories."
ARXIV_GROUP_HELP = "ArXiv operations for downloading papers and extracting content."
WEB_GROUP_HELP = "Web crawler operations for extracting content from websites."
DDG_GROUP_HELP = "DuckDuckGo search operations for finding information online."
BUILD_GROUP_HELP = "Build operations for package management."
PUBLISH_GROUP_HELP = "Publish operations for distributing packages."
DATA_GROUP_HELP = "Data management operations for viewing and manipulating data files."
CONFIG_GROUP_HELP = "Manage configuration settings for OARC Crawlers."