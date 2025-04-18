"""ArXiv command module for OARC Crawlers.

This module provides CLI commands for interacting with arXiv papers,
including downloading LaTeX sources, searching for papers, and extracting LaTeX content.
"""
import click

from oarc_crawlers.cli.help_texts import (
    ARXIV_HELP,
    ARXIV_DOWNLOAD_HELP,
    ARXIV_SEARCH_HELP,
    ARXIV_LATEX_HELP,
)
from oarc_crawlers.core.crawlers.arxiv_crawler import ArxivCrawler
from oarc_crawlers.decorators import asyncio_run, handle_error
from oarc_crawlers.utils.const import SUCCESS
from oarc_crawlers.utils.errors import ResourceNotFoundError
from oarc_crawlers.utils.log import log, enable_debug_logging


@click.group(help=ARXIV_HELP)
def arxiv():
    """Group of arXiv-related CLI commands: download sources, search papers, and extract LaTeX content."""
    pass


@arxiv.command(help=ARXIV_DOWNLOAD_HELP)
@click.option('--id', required=True, help='arXiv paper ID')
@click.option('--verbose', is_flag=True, help='Show detailed error information', 
              callback=enable_debug_logging)
@asyncio_run
@handle_error
async def download(id):
    """Download LaTeX source files for an arXiv paper.

    Args:
        id (str): The arXiv paper identifier.

    Returns:
        int: SUCCESS constant if the download completes successfully.
    """
    fetcher = ArxivCrawler()
    
    click.echo(f"Downloading source for arXiv ID: {id}") # stdout output
    
    result = await fetcher.download_source(id)
    
    if 'error' in result:
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


@arxiv.command(help=ARXIV_SEARCH_HELP)
@click.option('--query', required=True, help='Search query')
@click.option('--limit', default=5, type=int, help='Maximum number of results')
@click.option('--verbose', is_flag=True, help='Show detailed error information', 
              callback=enable_debug_logging)
@asyncio_run
@handle_error
async def search(query, limit):
    """Search for papers on arXiv.

    Args:
        query (str): The search query string.
        limit (int): Maximum number of results to return.

    Returns:
        int: SUCCESS constant if the search completes successfully.
    """
    fetcher = ArxivCrawler()

    click.echo(f"Searching arXiv for: {query}")
    log.debug(f"Using limit: {limit}")

    result = await fetcher.search(query, limit=limit)

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
    

@arxiv.command(help=ARXIV_LATEX_HELP)
@click.option('--id', required=True, help='arXiv paper ID')
@click.option('--verbose', is_flag=True, help='Show detailed error information', 
              callback=enable_debug_logging)
@asyncio_run
@handle_error
async def latex(id):
    """
    Download and extract LaTeX content from an arXiv paper.

    Args:
        id (str): The arXiv paper identifier.

    Returns:
        int: SUCCESS constant if the operation completes successfully.
    """
    fetcher = ArxivCrawler()
    
    click.echo(f"Fetching LaTeX content for arXiv ID: {id}")

    result = await fetcher.fetch_paper_with_latex(id)
    
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
