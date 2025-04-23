"""
ArxivCrawler Example Usage

This example demonstrates how to use the ArxivCrawler to:
1. Fetch paper metadata
2. Download LaTeX source files
3. Extract references and keywords
4. Search for papers
5. Analyze category papers
6. Extract mathematical equations
7. Generate citation networks
"""

import asyncio
import json
from pathlib import Path
import sys

from oarc_crawlers import ArxivCrawler

# Create a custom data directory for this example
DATA_DIR = Path("./data")
DATA_DIR.mkdir(exist_ok=True)


async def main():
    """Run the arXiv crawler examples."""
    print("ArxivCrawler Example")
    print("===================\n")
    
    # Initialize the crawler
    crawler = ArxivCrawler(data_dir=str(DATA_DIR))
    
    # 1. Fetch paper metadata
    print("\n1. Fetching paper metadata")
    print("--------------------------")
    paper_id = "2304.12749"  # Replace with a paper of interest
    paper_info = await crawler.fetch_paper_info(paper_id)
    print(f"Title: {paper_info['title']}")
    print(f"Authors: {', '.join(paper_info['authors'])}")
    print(f"Abstract: {paper_info['abstract'][:200]}...")
    
    # 2. Download LaTeX source
    print("\n2. Downloading LaTeX source")
    print("---------------------------")
    source_info = await crawler.download_source(paper_id)
    num_files = len(source_info.get('source_files', {}))
    print(f"Downloaded {num_files} source files")
    
    if num_files > 0:
        # Show first few files
        print("Files:")
        for i, filename in enumerate(list(source_info['source_files'].keys())[:5]):
            print(f"  • {filename}")
        if num_files > 5:
            print(f"  ... and {num_files - 5} more files")
    
    # 3. Extract references
    print("\n3. Extracting references")
    print("------------------------")
    references = await crawler.extract_references(source_info)
    print(f"Found {references['reference_count']} references")
    
    # Show a few references
    if references['reference_count'] > 0:
        print("Sample references:")
        for i, ref in enumerate(references['references'][:3]):
            if 'fields' in ref:  # BibTeX entry
                authors = ref.get('fields', {}).get('author', 'Unknown')
                title = ref.get('fields', {}).get('title', 'Untitled')
                print(f"  [{ref.get('key', 'Unknown')}] {authors}: {title}")
            else:  # Standard citation
                citation = ref.get('citation', 'Unknown citation')
                print(f"  [{ref.get('key', 'Unknown')}] {citation[:100]}...")
    
    # 4. Extract keywords
    print("\n4. Extracting keywords")
    print("---------------------")
    try:
        keywords = await crawler.extract_keywords(paper_info)
        print(f"Top keywords:")
        for kw in keywords['keywords'][:5]:
            print(f"  • {kw['keyword']} (score: {kw['score']})")
    except Exception as e:
        print(f"Error extracting keywords: {e}")
        print("Note: Keyword extraction requires NLTK to be installed")
    
    # 5. Search for papers
    print("\n5. Searching for papers")
    print("----------------------")
    search_query = "transformer architecture"
    search_results = await crawler.search(search_query, limit=3)
    print(f"Found {len(search_results['results'])} results for '{search_query}'")
    
    for i, result in enumerate(search_results['results']):
        print(f"\n  Result {i+1}:")
        print(f"  Title: {result['title']}")
        print(f"  Authors: {', '.join(result.get('authors', []))}")
        print(f"  URL: {result.get('arxiv_url', 'N/A')}")
    
    # 6. Fetch category papers
    print("\n6. Fetching category papers")
    print("-------------------------")
    category = "cs.AI"
    category_papers = await crawler.fetch_category_papers(category, max_results=5)
    print(f"Found {category_papers['papers_count']} recent papers in category '{category}'")
    
    for i, paper in enumerate(category_papers['papers']):
        print(f"\n  Paper {i+1}:")
        print(f"  Title: {paper['title']}")
        print(f"  Authors: {', '.join(paper.get('authors', []))}")
        print(f"  Published: {paper.get('published', 'N/A').split('T')[0]}")
    
    # 7. Extract equations
    print("\n7. Extracting mathematical equations")
    print("---------------------------------")
    equations = await crawler.extract_math_equations(source_info)
    print(f"Found {equations['inline_equation_count']} inline and {equations['display_equation_count']} display equations")
    
    # Show sample equations
    if equations['display_equation_count'] > 0:
        print("\nSample display equations:")
        for i, eq in enumerate(equations['display_equations'][:2]):
            print(f"  {i+1}: ${eq}$")
    
    # 8. Generate citation network
    print("\n8. Generating citation network")
    print("----------------------------")
    print("(This may take some time...)")
    network = await crawler.generate_citation_network([paper_id], max_depth=1)
    print(f"Created network with {len(network['nodes'])} nodes and {len(network['edges'])} edges")
    
    # Save network to file
    network_file = DATA_DIR / "citation_network.json"
    with open(network_file, 'w') as f:
        json.dump(network, f, indent=2)
    print(f"Citation network saved to {network_file}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExecution interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)