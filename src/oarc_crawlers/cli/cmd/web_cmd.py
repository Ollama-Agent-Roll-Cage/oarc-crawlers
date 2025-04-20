"""Web crawler command module for OARC Crawlers.

This module provides CLI commands for crawling and extracting content 
from websites, documentation sites, and PyPI packages.
"""

import click

from oarc_log import log, enable_debug_logging
from oarc_decorators import (
    asyncio_run, 
    handle_error, 
    DataExtractionError, 
    ResourceNotFoundError,
)

from oarc_crawlers.cli.help_texts import (
    WEB_GROUP_HELP,
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
from oarc_crawlers.utils.const import SUCCESS, PYPI_PACKAGE_URL


@click.group(help=WEB_GROUP_HELP)
@click.option('--verbose', is_flag=True, help=ARGS_VERBOSE_HELP, callback=enable_debug_logging)
@click.option('--config', help=ARGS_CONFIG_HELP, callback=apply_config_file)
def web(verbose, config):
    """Group of web crawler commands for extracting content from websites."""
    pass


@web.command(help=WEB_CRAWL_HELP)
@click.option('--url', required=True, help=ARGS_URL_HELP)
@click.option('--output-file', help=ARGS_OUTPUT_FILE_HELP)
@asyncio_run
@handle_error
async def crawl(url, output_file):
    """Crawl and extract content from a webpage."""
    crawler = WebCrawler()
    
    click.echo(f"Crawling webpage: {url}")
    log.debug(f"Using output file: {output_file or 'None (stdout)'}")
    
    html = await crawler.fetch_url_content(url)
    if not html:
        raise ResourceNotFoundError(f"Failed to fetch content from {url}")
    
    log.debug(f"Successfully fetched HTML ({len(html)} bytes)")
    content = await crawler.extract_text_from_html(html)
    log.debug(f"Extracted {len(content)} bytes of text content")
    
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
@asyncio_run
@handle_error
async def docs(url):
    """Crawl and extract content from a documentation site."""
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
@asyncio_run
@handle_error
async def pypi(package):
    """Extract and display information about a PyPI package."""
    crawler = WebCrawler()
    
    click.echo(f"Fetching PyPI information for: {package}")
    log.debug(f"Connecting to PyPI for package {package}")
    
    html = await crawler.fetch_url_content(PYPI_PACKAGE_URL.format(package=package))
    if not html:
        raise ResourceNotFoundError(f"Failed to fetch PyPI page for {package}")
    
    log.debug(f"Successfully fetched PyPI page ({len(html)} bytes)")
    result = await crawler.extract_pypi_content(html, package)
    if not result:
        raise DataExtractionError(f"Failed to extract PyPI information for {package}")
    
    click.secho(f"✓ Package: {result['name']}", fg='green')
    log.debug(f"Extracted metadata for {len(result.get('metadata', {}))} sections")
    
    for section, items in result.get('metadata', {}).items():
        click.echo(f"\n{section}:")
        for item in items:
            click.echo(f"  • {item}")
    
    doc = result.get('documentation', '')[:500]
    if doc:
        log.debug(f"Showing documentation preview ({len(doc)} chars)")
        click.echo(f"\nDocumentation Preview:")
        click.echo(doc + ("..." if len(result.get('documentation', '')) > 500 else ""))
    
    return SUCCESS
