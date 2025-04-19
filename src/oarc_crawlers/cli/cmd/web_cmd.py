"""
Web crawler CLI commands for OARC Crawlers.

Provides commands to crawl web pages, documentation sites, and PyPI packages,
with options for output, error handling, and logging.
"""
import click

from oarc_crawlers.cli.help_texts import (
    WEB_HELP,
    WEB_CRAWL_HELP,
    WEB_DOCS_HELP,
    WEB_PYPI_HELP,
    ARGS_VERBOSE_HELP,
    ARGS_CONFIG_HELP,
    ARGS_URL_HELP,
    ARGS_OUTPUT_FILE_HELP,
    ARGS_PACKAGE_HELP,
)
from oarc_crawlers.config.config import apply_config_file
from oarc_crawlers.core.crawlers.web_crawler import WebCrawler
from oarc_crawlers.decorators import asyncio_run, handle_error
from oarc_crawlers.utils.const import SUCCESS, PYPI_PACKAGE_URL
from oarc_crawlers.utils.errors import DataExtractionError, ResourceNotFoundError
from oarc_crawlers.utils.log import log, enable_debug_logging


@click.group(help=WEB_HELP)
def web():
    """Group of web crawler CLI commands for extracting content from websites, documentation, and PyPI packages."""
    pass


@web.command(help=WEB_CRAWL_HELP)
@click.option('--url', required=True, help=ARGS_URL_HELP)
@click.option('--output-file', help=ARGS_OUTPUT_FILE_HELP)
@click.option('--verbose', is_flag=True, help=ARGS_VERBOSE_HELP, callback=enable_debug_logging)
@click.option('--config', help=ARGS_CONFIG_HELP, callback=apply_config_file)
@asyncio_run
@handle_error
async def crawl(url, output_file, verbose, config):
    """
    Crawl and extract content from a webpage.

    Args:
        url (str): The URL of the webpage to crawl.
        output_file (str, optional): Path to save the extracted content. If not provided, output is printed to console.

    Returns:
        int: SUCCESS if crawling and extraction succeed.

    Raises:
        ResourceNotFoundError: If the webpage cannot be fetched.
        DataExtractionError: If content extraction fails.
    """
    crawler = WebCrawler()
    
    click.echo(f"Crawling webpage: {url}")
    log.debug(f"Using output file: {output_file or 'None (stdout)'}")
    
    # Using custom exceptions for better error handling
    html = await crawler.fetch_url_content(url)
    if not html:
        raise ResourceNotFoundError(f"Failed to fetch content from {url}")
    
    log.debug(f"Successfully fetched HTML ({len(html)} bytes)")
    content = await crawler.extract_text_from_html(html)
    log.debug(f"Extracted {len(content)} bytes of text content")
    
    # Save to file if specified
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        click.secho(f"✓ Content saved to {output_file}", fg='green')
    else:
        log.debug("Displaying content to console (no output file specified)")
        click.echo(content)
    
    return SUCCESS


@web.command(help=WEB_DOCS_HELP)
@click.option('--url', required=True, help=ARGS_URL_HELP)
@click.option('--verbose', is_flag=True, help=ARGS_VERBOSE_HELP,
              callback=enable_debug_logging)
@click.option('--config', help=ARGS_CONFIG_HELP, callback=apply_config_file)
@asyncio_run
@handle_error
async def docs(url, verbose, config):
    """
    Crawl and extract content from a documentation site.

    Args:
        url (str): The URL of the documentation site to crawl.

    Returns:
        int: SUCCESS if extraction succeeds.

    Raises:
        DataExtractionError: If extraction fails.
    """
    crawler = WebCrawler()
    
    click.echo(f"Crawling documentation site: {url}")
    log.debug(f"Starting documentation crawler on {url}")
    
    result = await crawler.crawl_documentation_site(url)
    if not result:
        raise DataExtractionError(f"Failed to extract content from documentation site: {url}")
    
    log.debug(f"Successfully extracted documentation content ({len(result)} bytes)")
    click.echo(result)
    return SUCCESS


@web.command(help=WEB_PYPI_HELP)
@click.option('--package', required=True, help=ARGS_PACKAGE_HELP)
@click.option('--verbose', is_flag=True, help=ARGS_VERBOSE_HELP,
              callback=enable_debug_logging)
@click.option('--config', help=ARGS_CONFIG_HELP, callback=apply_config_file)
@asyncio_run
@handle_error
async def pypi(package, verbose, config):
    """
    Extract and display information about a PyPI package.

    Args:
        package (str): The name of the PyPI package to fetch.

    Returns:
        int: SUCCESS if extraction and display succeed.

    Raises:
        ResourceNotFoundError: If the PyPI page cannot be fetched.
        DataExtractionError: If extraction of package information fails.
    """
    crawler = WebCrawler()
    
    click.echo(f"Fetching PyPI information for: {package}")
    log.debug(f"Connecting to PyPI for package {package}")
    
    # Using custom exceptions for better error handling
    # Using constant for PyPI URL
    html = await crawler.fetch_url_content(PYPI_PACKAGE_URL.format(package=package))
    if not html:
        raise ResourceNotFoundError(f"Failed to fetch PyPI page for {package}")
    
    log.debug(f"Successfully fetched PyPI page ({len(html)} bytes)")
    result = await crawler.extract_pypi_content(html, package)
    if not result:
        raise DataExtractionError(f"Failed to extract PyPI information for {package}")
    
    # Format and display results
    click.secho(f"✓ Package: {result['name']}", fg='green')
    log.debug(f"Extracted metadata for {len(result.get('metadata', {}))} sections")
    
    # Show metadata sections
    for section, items in result.get('metadata', {}).items():
        click.echo(f"\n{section}:")
        for item in items:
            click.echo(f"  • {item}")
    
    # Show documentation preview
    doc_preview = result.get('documentation', '')[:500]
    if doc_preview:
        log.debug(f"Showing documentation preview ({len(doc_preview)} chars)")
        click.echo(f"\nDocumentation Preview:")
        click.echo(doc_preview + ("..." if len(result.get('documentation', '')) > 500 else ""))
    
    return SUCCESS
