import asyncio
import os
from pathlib import Path
from oarc_crawlers import ArxivFetcher

async def arxiv_examples():
    """Examples for using the ArXiv Fetcher module."""
    
    # Initialize the fetcher
    data_dir = Path("./data")
    fetcher = ArxivFetcher(data_dir=data_dir)
    
    print("=== ArXiv Fetcher Examples ===")
    
    # Example 1: Extract ArXiv ID from different formats
    print("\n1. Extract ArXiv ID from different formats")
    arxiv_formats = [
        "2103.00020",
        "https://arxiv.org/abs/2103.00020",
        "https://arxiv.org/pdf/2103.00020.pdf"
    ]
    
    for format_example in arxiv_formats:
        arxiv_id = ArxivFetcher.extract_arxiv_id(format_example)
        print(f"From '{format_example}' extracted ID: {arxiv_id}")
    
    # Example 2: Fetch paper metadata
    print("\n2. Fetch paper metadata")
    paper_info = await fetcher.fetch_paper_info("2103.00020")
    print(f"Title: {paper_info.get('title')}")
    print(f"Authors: {', '.join(paper_info.get('authors', []))}")
    print(f"Categories: {', '.join(paper_info.get('categories', []))}")
    print(f"Abstract: {paper_info.get('abstract')[:150]}...")
    
    # Example 3: Format paper for learning
    print("\n3. Format paper for learning")
    formatted_paper = await ArxivFetcher.format_paper_for_learning(paper_info)
    print(f"{formatted_paper[:300]}...\n")
    
    # Example 4: Download LaTeX source files
    print("\n4. Download LaTeX source files")
    print("This might take a moment...")
    source_result = await fetcher.download_source("2103.00020")
    print(f"Downloaded source files: {list(source_result.get('source_files', {}).keys())[:5]}")
    
    # Print a small snippet of the LaTeX content
    latex_preview = source_result.get('latex_content', '')[:200]
    print(f"LaTeX content preview: {latex_preview}...\n")
    
    # Example 5: Complete paper fetch with LaTeX
    print("\n5. Complete paper fetch with LaTeX source")
    print("This combines metadata and source files...")
    complete_paper = await fetcher.fetch_paper_with_latex("2103.00020")
    print(f"Complete paper object has keys: {list(complete_paper.keys())}")
    print(f"Has source files: {complete_paper.get('has_source_files')}")

if __name__ == "__main__":
    asyncio.run(arxiv_examples())