"""arXiv CLI command module for OARC Crawlers.

Provides commands to interact with arXiv papers, including:
    • Downloading LaTeX source files
    • Searching for papers
    • Extracting LaTeX content
    • Extracting keywords and references
    • Analyzing paper content

Intended for use via the OARC Crawlers command-line interface.
"""

import click
import json

from oarc_log import log, enable_debug_logging
from oarc_utils.decorators import asyncio_run, handle_error
from oarc_utils.errors import ResourceNotFoundError

from oarc_crawlers.cli.help_texts import (
    ARGS_VERBOSE_HELP,
    ARGS_CONFIG_HELP,
    ARGS_ID_HELP,
    ARGS_IDS_HELP,
    ARGS_QUERY_HELP,
    ARGS_LIMIT_HELP,
    ARGS_CATEGORY_HELP,
    ARGS_MAX_DEPTH_HELP,
    ARGS_OUTPUT_FILE_HELP,
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
      • Extracting keywords and references
      • Analyzing paper content

    Use --help with subcommands for more details.

    Examples:

      Download LaTeX source for a paper:

        $ oarc-crawlers arxiv download --id 2304.12749

      Search for papers on quantum computing:

        $ oarc-crawlers arxiv search --query "quantum computing" --limit 5

      Extract LaTeX content from a paper:

        $ oarc-crawlers arxiv latex --id 2304.12749
        
      Extract keywords from a paper:
      
        $ oarc-crawlers arxiv keywords --id 2304.12749
        
      Extract references from a paper:
      
        $ oarc-crawlers arxiv references --id 2304.12749
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

@arxiv.command()
@click.option('--id', required=True, help=ARGS_ID_HELP)
@click.option('--output-file', help=ARGS_OUTPUT_FILE_HELP)
@asyncio_run
@handle_error
async def keywords(id, output_file):
    """Extract keywords from an arXiv paper.
    
    Uses natural language processing to extract key terms and phrases
    from the paper's title and abstract. Requires NLTK to be installed.
    
    Examples:
    
      Extract keywords from a paper:
      
        $ oarc-crawlers arxiv keywords --id 2304.12749
        
      Save keywords to a JSON file:
      
        $ oarc-crawlers arxiv keywords --id 2304.12749 --output-file keywords.json
        
    Args:
        id (str): The arXiv paper identifier.
        output_file (str, optional): Path to save keywords as JSON.
        
    Returns:
        int: SUCCESS constant if extraction completes successfully.
        
    Raises:
        ResourceNotFoundError: If the paper cannot be found.
    """
    crawler = ArxivCrawler()
    
    click.echo(f"Extracting keywords from arXiv paper: {id}")
    
    result = await crawler.extract_keywords(id)
    
    if 'error' in result:
        click.secho(f"Error extracting keywords: {result['error']}", fg='red')
        return ERROR
    
    if not result.get('keywords'):
        click.secho("No keywords could be extracted.", fg='yellow')
        return SUCCESS
    
    # Display keywords
    click.secho(f"✓ Extracted {len(result['keywords'])} keywords from paper: {result.get('title', id)}", fg='green')
    click.echo("\nTop keywords:")
    for i, kw in enumerate(result['keywords'][:10], 1):
        click.echo(f"  {i}. {kw['keyword']} (score: {kw['score']})")
    
    # Save to file if requested
    if output_file:
        try:
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            click.secho(f"\nKeywords saved to {output_file}", fg='green')
        except Exception as e:
            click.secho(f"Error saving to file: {e}", fg='red')
    
    return SUCCESS

@arxiv.command()
@click.option('--id', required=True, help=ARGS_ID_HELP)
@click.option('--output-file', help=ARGS_OUTPUT_FILE_HELP)
@asyncio_run
@handle_error
async def references(id, output_file):
    """Extract bibliography references from an arXiv paper.
    
    Extracts bibliographic references from the LaTeX source files
    of an arXiv paper. Works with both BibTeX and \bibitem formats.
    
    Examples:
    
      Extract references from a paper:
      
        $ oarc-crawlers arxiv references --id 2304.12749
        
      Save references to a JSON file:
      
        $ oarc-crawlers arxiv references --id 2304.12749 --output-file refs.json
        
    Args:
        id (str): The arXiv paper identifier.
        output_file (str, optional): Path to save references as JSON.
        
    Returns:
        int: SUCCESS constant if extraction completes successfully.
        
    Raises:
        ResourceNotFoundError: If the paper cannot be found.
    """
    crawler = ArxivCrawler()
    
    click.echo(f"Extracting references from arXiv paper: {id}")
    
    result = await crawler.extract_references(id)
    
    if 'error' in result:
        click.secho(f"Error extracting references: {result['error']}", fg='red')
        return ERROR
    
    if not result.get('references'):
        click.secho("No references could be extracted.", fg='yellow')
        return SUCCESS
    
    # Display references
    click.secho(f"✓ Extracted {len(result['references'])} references from paper {id}", fg='green')
    
    # Show sample of references
    sample_size = min(5, len(result['references']))
    click.echo(f"\nSample of {sample_size} references:")
    for i, ref in enumerate(result['references'][:sample_size], 1):
        if 'fields' in ref:  # BibTeX entry
            authors = ref.get('fields', {}).get('author', 'Unknown')
            title = ref.get('fields', {}).get('title', 'Untitled')
            click.echo(f"  {i}. [{ref.get('key', 'Unknown')}] {authors}: {title}")
        else:  # Standard citation
            citation = ref.get('citation', 'Unknown citation')
            click.echo(f"  {i}. [{ref.get('key', 'Unknown')}] {citation[:100]}{'...' if len(citation) > 100 else ''}")
    
    # Save to file if requested
    if output_file:
        try:
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            click.secho(f"\nReferences saved to {output_file}", fg='green')
        except Exception as e:
            click.secho(f"Error saving to file: {e}", fg='red')
    
    return SUCCESS

@arxiv.command()
@click.option('--id', required=True, help=ARGS_ID_HELP)
@click.option('--output-file', help=ARGS_OUTPUT_FILE_HELP)
@asyncio_run
@handle_error
async def equations(id, output_file):
    """Extract mathematical equations from an arXiv paper.
    
    Extracts both inline and display math equations from
    the LaTeX source of an arXiv paper.
    
    Examples:
    
      Extract equations from a paper:
      
        $ oarc-crawlers arxiv equations --id 2304.12749
        
      Save equations to a JSON file:
      
        $ oarc-crawlers arxiv equations --id 2304.12749 --output-file equations.json
        
    Args:
        id (str): The arXiv paper identifier.
        output_file (str, optional): Path to save equations as JSON.
        
    Returns:
        int: SUCCESS constant if extraction completes successfully.
        
    Raises:
        ResourceNotFoundError: If the paper cannot be found.
    """
    crawler = ArxivCrawler()
    
    click.echo(f"Extracting mathematical equations from arXiv paper: {id}")
    
    result = await crawler.extract_math_equations(id)
    
    if 'error' in result:
        click.secho(f"Error extracting equations: {result['error']}", fg='red')
        return ERROR
    
    # Display equation counts
    inline_count = result.get('inline_equation_count', 0)
    display_count = result.get('display_equation_count', 0)
    total_count = inline_count + display_count
    
    if total_count == 0:
        click.secho("No mathematical equations found in paper.", fg='yellow')
        return SUCCESS
    
    click.secho(f"✓ Extracted {total_count} equations from paper {id}", fg='green')
    click.echo(f"  • {inline_count} inline equations")
    click.echo(f"  • {display_count} display equations")
    
    # Show sample of equations
    if display_count > 0:
        click.echo("\nSample of display equations:")
        for i, eq in enumerate(result.get('display_equations', [])[:3], 1):
            click.echo(f"  {i}. ${eq}$")
    
    if inline_count > 0:
        click.echo("\nSample of inline equations:")
        for i, eq in enumerate(result.get('inline_equations', [])[:3], 1):
            click.echo(f"  {i}. ${eq}$")
    
    # Save to file if requested
    if output_file:
        try:
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            click.secho(f"\nEquations saved to {output_file}", fg='green')
        except Exception as e:
            click.secho(f"Error saving to file: {e}", fg='red')
    
    return SUCCESS

@arxiv.command()
@click.option('--category', required=True, help=ARGS_CATEGORY_HELP)
@click.option('--limit', default=20, type=int, help=ARGS_LIMIT_HELP)
@asyncio_run
@handle_error
async def category(category, limit):
    """Fetch recent papers from an arXiv category.
    
    Retrieves the most recent papers from a specific
    arXiv category (e.g., 'cs.AI', 'math.CO', 'physics.optics').
    
    Examples:
    
      Fetch papers from the 'cs.AI' category:
      
        $ oarc-crawlers arxiv category --category cs.AI
        
      Get a larger number of papers:
      
        $ oarc-crawlers arxiv category --category math.CO --limit 50
        
    Args:
        category (str): ArXiv category code.
        limit (int): Maximum number of papers to fetch.
        
    Returns:
        int: SUCCESS constant if operation completes successfully.
        
    Raises:
        ResourceNotFoundError: If the category is invalid or unreachable.
    """
    crawler = ArxivCrawler()
    
    click.echo(f"Fetching up to {limit} papers from arXiv category: {category}")
    
    result = await crawler.fetch_category_papers(category, max_results=limit)
    
    if 'error' in result:
        raise ResourceNotFoundError(f"Error fetching category papers: {result['error']}")
    
    papers = result.get('papers', [])
    if not papers:
        click.secho(f"No papers found in category '{category}'.", fg='yellow')
    else:
        click.secho(f"✓ Found {len(papers)} recent papers in '{category}'", fg='green')
        for i, paper in enumerate(papers[:10], 1):
            click.echo(f"\n{i}. {paper.get('title', 'No title')}")
            click.echo(f"   Authors: {', '.join(paper.get('authors', []))[:60]}{'...' if len(', '.join(paper.get('authors', []))) > 60 else ''}")
            click.echo(f"   ID: {paper.get('arxiv_id', 'N/A')}")
            click.echo(f"   Published: {paper.get('published', 'N/A').split('T')[0]}")
        
        if len(papers) > 10:
            click.echo(f"\n... and {len(papers) - 10} more papers")
    
    click.echo(f"\nData saved to: {result.get('parquet_path', 'Unknown')}")
    
    return SUCCESS

@arxiv.command()
@click.option('--ids', required=True, help=ARGS_IDS_HELP)
@click.option('--keywords/--no-keywords', default=False, help="Extract keywords from papers")
@click.option('--references/--no-references', default=False, help="Extract references from papers")
@asyncio_run
@handle_error
async def batch(ids, keywords, references):
    """Process multiple papers in batch.
    
    Fetches metadata for multiple arXiv papers in a single operation.
    Can optionally extract keywords and references.
    
    Examples:
    
      Process multiple papers:
      
        $ oarc-crawlers arxiv batch --ids "2304.12749,2310.06825,2401.00123"
        
      Process with keywords and references:
      
        $ oarc-crawlers arxiv batch --ids "2304.12749,2310.06825" --keywords --references
        
    Args:
        ids (str): Comma-separated list of arXiv IDs.
        keywords (bool): Whether to extract keywords.
        references (bool): Whether to extract references.
        
    Returns:
        int: SUCCESS constant if operation completes successfully.
        
    Raises:
        ValueError: If the ID list is invalid.
    """
    crawler = ArxivCrawler()
    
    # Parse IDs
    arxiv_ids = [id.strip() for id in ids.split(",") if id.strip()]
    if not arxiv_ids:
        click.secho("No valid arXiv IDs provided.", fg='red')
        return ERROR
    
    features = []
    if keywords:
        features.append("keywords")
    if references:
        features.append("references")
        
    msg = f"Processing {len(arxiv_ids)} papers in batch"
    if features:
        msg += f" with {' and '.join(features)}"
    click.echo(msg)
    
    result = await crawler.batch_fetch_papers(
        arxiv_ids=arxiv_ids,
        extract_keywords=keywords,
        extract_references=references
    )
    
    # Show results
    success_count = len(result.get('papers', []))
    error_count = len(result.get('errors', []))
    
    if success_count > 0:
        click.secho(f"✓ Successfully processed {success_count} papers", fg='green')
        
        # Show keyword stats if requested
        if keywords and result.get('keywords'):
            total_keywords = sum(len(kw.get('keywords', [])) for kw in result.get('keywords', []))
            click.echo(f"  • Extracted {total_keywords} keywords across {len(result['keywords'])} papers")
            
        # Show reference stats if requested
        if references and result.get('references'):
            total_refs = sum(ref.get('reference_count', 0) for ref in result.get('references', []))
            click.echo(f"  • Extracted {total_refs} references across {len(result['references'])} papers")
    
    if error_count > 0:
        click.secho(f"⚠ Failed to process {error_count} papers", fg='yellow')
        for error in result.get('errors', [])[:5]:  # Show first 5 errors
            click.echo(f"  • {error.get('arxiv_id', 'Unknown')}: {error.get('error', 'Unknown error')}")
        
        if error_count > 5:
            click.echo(f"  ... and {error_count - 5} more errors")
    
    return SUCCESS

@arxiv.command()
@click.option('--ids', required=True, help=ARGS_IDS_HELP)
@click.option('--max-depth', default=1, type=int, help=ARGS_MAX_DEPTH_HELP)
@click.option('--output-file', help=ARGS_OUTPUT_FILE_HELP)
@asyncio_run
@handle_error
async def citation_network(ids, max_depth, output_file):
    """Generate a citation network from seed papers.
    
    Creates a network of papers and their references up to the specified depth.
    Useful for visualizing academic influence networks.
    
    Examples:
    
      Create a basic citation network:
      
        $ oarc-crawlers arxiv citation-network --ids "2304.12749,2310.06825"
        
      Create a deeper network:
      
        $ oarc-crawlers arxiv citation-network --ids "2304.12749" --max-depth 2 --output-file network.json
        
    Args:
        ids (str): Comma-separated list of arXiv IDs to start from.
        max_depth (int): How many layers of references to follow.
        output_file (str, optional): Path to save the network as JSON.
        
    Returns:
        int: SUCCESS constant if operation completes successfully.
    """
    crawler = ArxivCrawler()
    
    # Parse IDs
    seed_papers = [id.strip() for id in ids.split(",") if id.strip()]
    if not seed_papers:
        click.secho("No valid arXiv IDs provided.", fg='red')
        return ERROR
    
    click.echo(f"Generating citation network from {len(seed_papers)} seed papers with depth {max_depth}")
    click.echo("This may take some time depending on the number of papers and depth...")
    
    network = await crawler.generate_citation_network(
        seed_papers=seed_papers,
        max_depth=max_depth
    )
    
    node_count = len(network.get('nodes', {}))
    edge_count = len(network.get('edges', []))
    
    if node_count == 0:
        click.secho("Could not generate citation network. No nodes found.", fg='yellow')
        return SUCCESS
    
    click.secho(f"✓ Generated citation network with {node_count} nodes and {edge_count} edges", fg='green')
    
    # Show sample of the network
    if node_count > 0:
        click.echo("\nSample nodes:")
        for i, (node_id, node_data) in enumerate(list(network['nodes'].items())[:3], 1):
            click.echo(f"  {i}. {node_id}: {node_data.get('title', 'Untitled')[:60]}...")
    
    if edge_count > 0:
        click.echo("\nSample edges:")
        for i, edge in enumerate(network['edges'][:3], 1):
            click.echo(f"  {i}. {edge.get('source', 'Unknown')} → {edge.get('target', 'Unknown')}")
    
    # Save to file if requested
    if output_file:
        try:
            with open(output_file, 'w') as f:
                json.dump(network, f, indent=2)
            click.secho(f"\nCitation network saved to {output_file}", fg='green')
        except Exception as e:
            click.secho(f"Error saving to file: {e}", fg='red')
    
    return SUCCESS
