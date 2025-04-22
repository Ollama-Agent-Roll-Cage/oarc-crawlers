"""arXiv CLI command module for OARC Crawlers.

Provides commands to interact with arXiv papers, including:
    • Downloading LaTeX source files
    • Searching for papers
    • Extracting LaTeX content

Intended for use via the OARC Crawlers command-line interface.
"""

import click

from oarc_log import log, enable_debug_logging
from oarc_utils.decorators import asyncio_run, handle_error
from oarc_utils.errors import ResourceNotFoundError

from oarc_crawlers.cli.help_texts import (
    ARGS_VERBOSE_HELP,
    ARGS_CONFIG_HELP,
    ARGS_ID_HELP,
    ARGS_QUERY_HELP,
    ARGS_LIMIT_HELP,
)
from oarc_crawlers.config.config import apply_config_file
from oarc_crawlers.core.crawlers.arxiv_crawler import ArxivCrawler
from oarc_crawlers.utils.const import SUCCESS, ERROR


@click.group()
@click.option('--verbose', is_flag=True, help=ARGS_VERBOSE_HELP, callback=enable_debug_logging)
@click.option('--config', help=ARGS_CONFIG_HELP, callback=apply_config_file)
def arxiv(verbose, config):
    """Group of arXiv-related CLI commands.

    This group provides commands to interact with arXiv papers, including:
      • Downloading LaTeX sources
      • Searching for papers
      • Extracting LaTeX content

    Use --help with subcommands for more details.

    Examples:

      Download LaTeX source for a paper:

        $ oarc-crawlers arxiv download --id 2304.12749

      Search for papers on quantum computing:

        $ oarc-crawlers arxiv search --query "quantum computing" --limit 5

      Extract LaTeX content from a paper:

        $ oarc-crawlers arxiv latex --id 2304.12749
    """
    pass


@arxiv.command()
@click.option('--id', required=True, help=ARGS_ID_HELP)
@asyncio_run
@handle_error
async def download(id):
    """Download LaTeX source files for an arXiv paper.

    Downloads the LaTeX source files for the specified arXiv paper ID.
    Displays a summary of the downloaded files. Shows up to 10 files by default,
    or all files if debug logging is enabled.

    Examples:

      Download source for a paper using its ID:

        $ oarc-crawlers arxiv download --id 2304.12749

      Download with verbose logging:

        $ oarc-crawlers arxiv download --id 2304.12749 --verbose

      Download using custom configuration:

        $ oarc-crawlers arxiv download --id 2304.12749 --config custom_config.ini

    Args:
        id (str): The arXiv paper identifier.

    Returns:
        int: SUCCESS constant if download completes successfully.

    Raises:
        ResourceNotFoundError: If the paper or its source files cannot be found.
    """
    crawler = ArxivCrawler()
    
    click.echo(f"Downloading source for arXiv ID: {id}") 
    
    result = await crawler.download_source(id)
    
    if ERROR in result:
        raise ResourceNotFoundError(f"Error: {result['error']}")
    
    # Show file listing
    num_files = len(result.get('source_files', {}))
    source_files = result.get('source_files', {})
    is_debug = log.is_debug_enabled()

    filenames = sorted(source_files.keys())
    display_files = filenames if is_debug else filenames[:10]

    for filename in display_files:
        if is_debug:
            log.debug(f"File details: {filename}, size: {len(source_files[filename])}")
        else:
            click.echo(f"  • {filename}")

    if not is_debug and num_files > 10:
        click.echo(f"  ... and {num_files - 10} more files")
    
    click.secho(f"✓ Downloaded {num_files} source files for paper {id} ({sum(len(f) for f in result.get('source_files', {}).values())} Bytes)", fg='green')
    
    return SUCCESS


@arxiv.command()
@click.option('--query', required=True, help=ARGS_QUERY_HELP)
@click.option('--limit', default=5, type=int, help=ARGS_LIMIT_HELP)
@asyncio_run
@handle_error
async def search(query, limit):
    """Search for papers on arXiv.

    Performs a search using the provided query string and displays a summary
    of the top matching papers (up to the specified limit).

    Examples:

      Search for papers on quantum computing:

        $ oarc-crawlers arxiv search --query "quantum computing"

      Search with a custom limit:

        $ oarc-crawlers arxiv search --query "machine learning" --limit 10

      Search with quotes in query:

        $ oarc-crawlers arxiv search --query '"deep learning"'

      Search with verbose output:

        $ oarc-crawlers arxiv search --query "robotics" --verbose

    Args:
        query (str): The search query for arXiv.
        limit (int): Maximum number of papers to display.

    Returns:
        int: SUCCESS constant if search completes successfully.

    Raises:
        ResourceNotFoundError: If the search fails or no results are found.
    """
    crawler = ArxivCrawler()

    click.echo(f"Searching arXiv for: {query}")
    log.debug(f"Using limit: {limit}")

    result = await crawler.search(query, limit=limit)

    if 'error' in result:
        raise ResourceNotFoundError(f"Search failed: {result['error']}")

    papers = result.get('results', [])
    if not papers:
        click.secho("No papers found.", fg='yellow')
    else:
        for i, paper in enumerate(papers, 1):
            click.echo(f"{i}. {paper.get('title', 'No title')}")
            click.echo(f"   Authors: {', '.join(paper.get('authors', []))}")
            click.echo(f"   ID: {paper.get('id', 'N/A')}")
            click.echo(f"   Abstract: {paper.get('abstract', '')[:200]}...")
            click.echo("")

        click.secho(f"✓ Found {len(papers)} papers", fg='green')

    return SUCCESS
    

@arxiv.command()
@click.option('--id', required=True, help=ARGS_ID_HELP)
@asyncio_run
@handle_error
async def latex(id):
    """Download and extract LaTeX content from an arXiv paper.

    Retrieves the LaTeX source for the specified arXiv paper ID,
    extracts the main LaTeX content, and displays summary information.

    Examples:

      Extract LaTeX from a paper:

        $ oarc-crawlers arxiv latex --id 2304.12749

      Extract LaTeX with verbose output:

        $ oarc-crawlers arxiv latex --id 2304.12749 --verbose

      Extract LaTeX using custom configuration:

        $ oarc-crawlers arxiv latex --id 2304.12749 --config custom_config.ini

    Args:
        id (str): The arXiv paper identifier.

    Returns:
        int: SUCCESS constant if extraction completes successfully.

    Raises:
        ResourceNotFoundError: If the paper or LaTeX content cannot be found.
    """
    crawler = ArxivCrawler()
    
    click.echo(f"Fetching LaTeX content for arXiv ID: {id}")

    result = await crawler.fetch_paper_with_latex(id)
    
    if 'error' in result:
        raise ResourceNotFoundError(f"Error: {result['error']}")
    
    # Display paper information
    click.secho(f"✓ Downloaded paper: {result.get('title')}", fg='green')
    click.echo(f"Authors: {', '.join(result.get('authors', []))}")
    click.echo(f"Abstract: {result.get('abstract', '')[:200]}...")
    
    if result.get('has_source_files', False):
        click.echo(f"LaTeX content extracted successfully")
    else:
        click.secho("No LaTeX source files found", fg='yellow')
    
    return SUCCESS
