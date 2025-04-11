import asyncio
import os
from pathlib import Path
from src.beautiful_soup import BSWebCrawler

async def bs_examples():
    """Examples for using the BeautifulSoup Web Crawler module."""
    
    # Initialize the crawler
    data_dir = Path("./data")
    crawler = BSWebCrawler(data_dir=data_dir)
    
    print("=== BeautifulSoup Web Crawler Examples ===")
    
    # Example 1: Fetch and extract text from a web page
    print("\n1. Fetch and extract text from a web page")
    url = "https://en.wikipedia.org/wiki/Web_scraping"
    html_content = await BSWebCrawler.fetch_url_content(url)
    text_content = await BSWebCrawler.extract_text_from_html(html_content)
    print(f"Extracted text (preview): {text_content[:200]}...\n")
    
    # Example 2: Crawl a documentation site
    print("\n2. Crawl a documentation site")
    docs_url = "https://docs.python.org/3/library/asyncio.html"
    docs_content = await crawler.crawl_documentation_site(docs_url)
    print(f"Extracted documentation (preview): {docs_content[:300]}...\n")
    
    # Example 3: Extract content from a PyPI package page
    print("\n3. Extract content from a PyPI package")
    pypi_url = "https://pypi.org/project/requests/"
    package_name = "requests"
    
    # First fetch the content
    pypi_html = await BSWebCrawler.fetch_url_content(pypi_url)
    
    # Then extract package information
    package_info = await BSWebCrawler.extract_pypi_content(pypi_html, package_name)
    
    print(f"Package name: {package_info['name']}")
    print("Package metadata:")
    for section, items in package_info.get('metadata', {}).items():
        print(f"  {section}: {items[:2]}")  # Just show first two items
    
    # Example 4: Format PyPI package information
    print("\n4. Format PyPI API data")
    # This would typically come from PyPI's JSON API
    sample_pypi_data = {
        'info': {
            'name': 'example-package',
            'version': '1.0.0',
            'summary': 'An example package',
            'description': 'This is a longer description of the example package.',
            'author': 'Sample Author',
            'author_email': 'author@example.com',
            'license': 'MIT',
            'home_page': 'https://example.com',
            'project_urls': {
                'Documentation': 'https://example.com/docs',
                'Source': 'https://github.com/example/example-package'
            },
            'requires_dist': ['requests>=2.0.0', 'numpy>=1.0.0']
        }
    }
    
    formatted_info = await BSWebCrawler.format_pypi_info(sample_pypi_data)
    print(f"{formatted_info[:300]}...\n")

if __name__ == "__main__":
    asyncio.run(bs_examples())