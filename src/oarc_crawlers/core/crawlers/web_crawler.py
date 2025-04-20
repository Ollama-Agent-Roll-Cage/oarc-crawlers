"""Web Crawler Module

This module provides functions for crawling and extracting content from web pages
using BeautifulSoup. Includes specialized extractors for documentation sites, PyPI,
and general web content.

Author: @BorcherdingL, RawsonK
Date: 4/18/2025
"""

from datetime import datetime, UTC
from pathlib import Path
import re

from bs4 import BeautifulSoup
import aiohttp

from oarc_log import log
from oarc_utils.errors import (
    ResourceNotFoundError,
    DataExtractionError
)


from oarc_crawlers.core.storage.parquet_storage import ParquetStorage
from oarc_crawlers.config.config import Config
from oarc_crawlers.utils.paths import Paths

class WebCrawler:
    """Class for crawling web pages and extracting content."""
    
    def __init__(self, data_dir=None):
        """Initialize the Web Crawler.
        
        Args:
            data_dir (str, optional): Directory to store data. Defaults to Config's data_dir.
        """
        # Use the global config if no data_dir provided
        if data_dir is None:
            data_dir = str(Config().data_dir)
        self.data_dir = data_dir
        self.crawl_data_dir = Paths.web_crawls_dir(self.data_dir)
        log.debug(f"Initialized WebCrawler with data directory: {self.data_dir}")
    
    async def fetch_url_content(self, url):
        """Fetch content from a URL.
        
        Args:
            url (str): The URL to fetch content from
            
        Returns:
            str: HTML content of the page
            
        Raises:
            NetworkError: If connection or network issues occur
            ResourceNotFoundError: If the URL returns a non-200 status code
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        log.debug(f"Starting HTTP request to {url} with headers: {headers}")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                log.debug(f"Received response with status code: {response.status}, content-type: {response.headers.get('content-type')}")
                
                if response.status == 200:
                    html = await response.text()
                    log.debug(f"Successfully fetched {len(html)} bytes of HTML content")
                    
                    # Save crawled content
                    crawl_data = {
                        'url': url,
                        'timestamp': datetime.now(UTC).isoformat(),
                        'content': html[:100000]  # Limit content size
                    }
                    
                    # Generate a filename from the URL
                    filename = re.sub(r'[^\w]', '_', url.split('//')[-1])[:50]
                    file_path = f"{self.data_dir}/crawls/{filename}_{int(datetime.now().timestamp())}.parquet"
                    log.debug(f"Saving crawl data to: {file_path}")
                    
                    # Ensure directory exists
                    Path(f"{self.data_dir}/crawls").mkdir(parents=True, exist_ok=True)
                    
                    # Save the data
                    ParquetStorage.save_to_parquet(crawl_data, file_path)
                    
                    return html
                else:
                    log.debug(f"Request failed with status code {response.status}")
                    raise ResourceNotFoundError(f"Failed to fetch URL {url}: HTTP Status {response.status}")

    @staticmethod
    async def extract_text_from_html(html):
        """Extract main text content from HTML using BeautifulSoup.
        
        Args:
            html (str): HTML content
            
        Returns:
            str: Extracted text content
            
        Raises:
            DataExtractionError: If text extraction fails
        """
        if not html:
            raise DataExtractionError("Cannot extract text from empty HTML content")
        
        log.debug(f"Starting text extraction from {len(html)} bytes of HTML")
        
        # First attempt with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        script_tags = len(soup(["script"]))
        style_tags = len(soup(["style"]))
        log.debug(f"Removing {script_tags} script tags and {style_tags} style tags")
        
        for script in soup(["script", "style"]):
            script.extract()
            
        # Get text
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        log.debug(f"Extracted raw text: {len(text)} characters, {len(text.split())} words")
        
        # Limit to first ~15,000 characters
        truncated = len(text) > 15000
        result = text[:15000] + ("..." if truncated else "")
        if truncated:
            log.debug(f"Text was truncated from {len(text)} to 15,000 characters")
        
        return result

    @staticmethod
    async def extract_pypi_content(html, package_name):
        """Specifically extract PyPI package documentation from HTML.
        
        Args:
            html (str): HTML content from PyPI page
            package_name (str): Name of the package
            
        Returns:
            dict: Structured package data
            
        Raises:
            DataExtractionError: If PyPI content extraction fails
        """
        if not html:
            raise DataExtractionError(f"Cannot extract PyPI content from empty HTML for package {package_name}")
        
        log.debug(f"Parsing PyPI HTML for package: {package_name}")
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract package metadata from the sidebar
        metadata = {}
        sidebar = soup.find('div', {'class': 'sidebar'})
        
        log.debug(f"Found sidebar: {sidebar is not None}")
        
        if (sidebar):
            sections = sidebar.find_all('div', {'class': 'sidebar-section'})
            log.debug(f"Found {len(sections)} sidebar sections")
            
            for section in sections:
                title_elem = section.find(['h3', 'h4'])
                if title_elem:
                    section_title = title_elem.get_text().strip()
                    content_list = []
                    for p in section.find_all('p'):
                        content_list.append(p.get_text().strip())
                    metadata[section_title] = content_list
                    log.debug(f"Extracted sidebar section: {section_title} with {len(content_list)} items")
        
        # Find the project description section which contains the actual documentation
        description_div = soup.find('div', {'class': 'project-description'})
        log.debug(f"Found project description: {description_div is not None}")
        
        if not description_div:
            raise DataExtractionError(f"No project description found for PyPI package {package_name}")
        
        # Extract text while preserving structure
        content = ""
        element_count = 0
        
        for element in description_div.children:
            if hasattr(element, 'name'):  # Check if it's a tag
                element_count += 1
                if element.name in ['h1', 'h2', 'h3', 'h4']:
                    heading_level = int(element.name[1])
                    heading_text = element.get_text().strip()
                    content += f"{'#' * heading_level} {heading_text}\n\n"
                    log.debug(f"Found heading (L{heading_level}): {heading_text}")
                elif element.name == 'p':
                    content += f"{element.get_text().strip()}\n\n"
                elif element.name == 'pre':
                    code = element.get_text().strip()
                    # Detect if there's a code element inside
                    code_element = element.find('code')
                    language = "python" if code_element and 'python' in str(code_element.get('class', [])).lower() else ""
                    content += f"```{language}\n{code}\n```\n\n"
                    if language:
                        log.debug(f"Found code block with language: {language}, {len(code)} chars")
                    else:
                        log.debug(f"Found unlabeled code block, {len(code)} chars")
                elif element.name == 'ul':
                    items = element.find_all('li', recursive=False)
                    log.debug(f"Found list with {len(items)} items")
                    for li in items:
                        content += f"- {li.get_text().strip()}\n"
                    content += "\n"
        
        log.debug(f"Processed {element_count} elements from project description")
        
        # Construct a structured representation
        package_info = {
            'name': package_name,
            'metadata': metadata,
            'documentation': content
        }
        
        return package_info

    @staticmethod
    async def extract_documentation_content(html, url):
        """Extract content from documentation websites like ReadTheDocs, LlamaIndex, etc.
        
        Args:
            html (str): HTML content from the documentation site
            url (str): URL of the documentation page
            
        Returns:
            dict: Structured documentation data
            
        Raises:
            DataExtractionError: If documentation extraction fails
        """
        if not html:
            raise DataExtractionError(f"Cannot extract documentation from empty HTML for URL {url}")
        
        log.debug(f"Parsing documentation HTML from URL: {url}")
        soup = BeautifulSoup(html, 'html.parser')
        doc_data = {
            'url': url,
            'title': '',
            'content': '',
            'toc': [],
            'metadata': {},
            'code_snippets': []
        }
        
        # Extract title - different websites have different structures
        title_candidates = [
            # ReadTheDocs/Sphinx style
            soup.find('div', {'class': 'document'}),
            # MkDocs style
            soup.find('div', {'class': 'md-content'}),
            # Generic
            soup.find('main'),
            soup.find('article')
        ]
        
        log.debug("Trying to extract page title from various containers")
        # Try to find the title
        for i, candidate in enumerate(title_candidates):
            if candidate:
                title_elem = candidate.find(['h1', 'h2'])
                if title_elem:
                    doc_data['title'] = title_elem.get_text().strip()
                    log.debug(f"Found title in candidate #{i+1}: '{doc_data['title']}'")
                    break
        
        # If no title found using above methods, use the page title
        if not doc_data['title'] and soup.title:
            doc_data['title'] = soup.title.get_text().strip()
            log.debug(f"Using HTML title tag: '{doc_data['title']}'")
        else:
            log.debug("No title found in the document")
        
        # Identify main content container based on common documentation site structures
        content_candidates = [
            # ReadTheDocs/Sphinx
            soup.find('div', {'class': 'section'}),
            soup.find('div', {'class': 'body', 'role': 'main'}),
            soup.find('div', {'class': 'document'}),
            # MkDocs
            soup.find('div', {'class': 'md-content'}),
            soup.find('article', {'class': 'md-content__inner'}),
            # LlamaIndex style
            soup.find('div', {'class': 'prose'}),
            soup.find('div', {'class': 'content'}),
            # Generic fallbacks
            soup.find('main'),
            soup.find('article'),
            soup.find('div', {'id': 'content'})
        ]
        
        # Find the main content container
        main_content = None
        log.debug("Searching for main content container")
        for i, candidate in enumerate(content_candidates):
            if candidate:
                main_content = candidate
                log.debug(f"Found main content in candidate #{i+1}: {candidate.name}.{candidate.get('class', '')}")
                break
        
        # If we still can't find a content container, use the body
        if main_content is None:
            log.debug("No specific content container found, using body tag")
            main_content = soup.body
        
        if main_content:
            # Extract text preserving structure
            content = ""
            code_snippets = []
            
            # Extract table of contents if available
            toc_candidates = [
                soup.find('div', {'class': 'toc'}),
                soup.find('div', {'class': 'toctree'}),
                soup.find('nav', {'class': 'md-nav'}),
                soup.find('ul', {'class': 'toc'}),
                soup.find('div', {'class': 'sidebar'})
            ]
            
            log.debug("Searching for table of contents")
            for i, toc in enumerate(toc_candidates):
                if toc:
                    # Extract TOC items
                    toc_items = []
                    for a in toc.find_all('a'):
                        if a.get_text().strip():
                            toc_items.append({
                                'title': a.get_text().strip(),
                                'url': a.get('href', '')
                            })
                    doc_data['toc'] = toc_items
                    log.debug(f"Found table of contents in candidate #{i+1} with {len(toc_items)} items")
                    break
            
            # Process the content by element type
            log.debug("Processing content elements")
            element_counts = {'h1': 0, 'h2': 0, 'h3': 0, 'h4': 0, 'p': 0, 'ul': 0, 'ol': 0, 'pre': 0, 'code': 0, 'div': 0}
            
            for element in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'ul', 'ol', 'pre', 'code', 'div']):
                element_counts[element.name] += 1
                
                if element.name in ['h1', 'h2', 'h3', 'h4']:
                    heading_text = element.get_text().strip()
                    if heading_text:
                        heading_level = int(element.name[1])
                        content += f"{'#' * heading_level} {heading_text}\n\n"
                
                elif element.name == 'p':
                    para_text = element.get_text().strip()
                    if para_text:
                        content += f"{para_text}\n\n"
                
                elif element.name in ['ul', 'ol']:
                    for li in element.find_all('li', recursive=False):
                        content += f"- {li.get_text().strip()}\n"
                    content += "\n"
                
                elif element.name == 'pre' or (element.name == 'div' and 'highlight' in element.get('class', [])):
                    code = element.get_text().strip()
                    if code:
                        # Try to detect language
                        lang = ""
                        if 'python' in str(element.get('class', [])).lower():
                            lang = "python"
                        elif 'javascript' in str(element.get('class', [])).lower():
                            lang = "javascript"
                        
                        # Add code to content
                        content += f"```{lang}\n{code}\n```\n\n"
                        
                        # Also save separately for easier access
                        code_snippets.append({
                            'language': lang,
                            'code': code
                        })
            
            doc_data['content'] = content
            doc_data['code_snippets'] = code_snippets
            
            log.debug(f"Content extraction complete: {len(content)} chars, {len(code_snippets)} code snippets")
            log.debug(f"Element counts: {element_counts}")
            
            # Extract metadata if available (e.g., version, last updated)
            meta_tags = soup.find_all('meta')
            meta_count = 0
            for tag in meta_tags:
                name = tag.get('name', '')
                if name in ['description', 'keywords', 'author', 'version']:
                    doc_data['metadata'][name] = tag.get('content', '')
                    meta_count += 1
            
            log.debug(f"Extracted {meta_count} metadata items from {len(meta_tags)} meta tags")
            
            # Get last updated time if available
            last_updated = None
            update_candidates = [
                soup.find('time'),
                soup.find(lambda tag: tag.name == 'p' and ('updated' in tag.text.lower() or 'modified' in tag.text.lower())),
                soup.find('div', {'class': 'last-updated'})
            ]
            
            for update_elem in update_candidates:
                if update_elem:
                    last_updated = update_elem.get_text().strip()
                    doc_data['metadata']['last_updated'] = last_updated
                    log.debug(f"Found last updated info: {last_updated}")
                    break
        
        return doc_data

    @staticmethod
    async def format_pypi_info(package_data):
        """Format PyPI package data into a readable markdown format.
        
        Args:
            package_data (dict): Package data from PyPI API
            
        Returns:
            str: Formatted markdown text
            
        Raises:
            DataExtractionError: If formatting fails
        """
        if not package_data:
            raise DataExtractionError("Cannot format empty package data")
        
        log.debug(f"Formatting PyPI data for package: {package_data.get('info', {}).get('name', 'Unknown')}")
        info = package_data.get('info', {})
        
        # Basic package information
        name = info.get('name', 'Unknown')
        version = info.get('version', 'Unknown')
        summary = info.get('summary', 'No summary available')
        description = info.get('description', 'No description available')
        author = info.get('author', 'Unknown')
        author_email = info.get('author_email', 'No email available')
        home_page = info.get('home_page', '')
        project_urls = info.get('project_urls', {})
        requires_dist = info.get('requires_dist', [])
        
        log.debug(f"Package info: {name} v{version} by {author}, {len(requires_dist)} dependencies")
        
        # Format the markdown response
        md = f"""# {name} v{version}

## Summary
{summary}

## Basic Information
- **Author**: {author} ({author_email})
- **License**: {info.get('license', 'Not specified')}
- **Homepage**: {home_page}

## Project URLs
"""
        
        for name, url in project_urls.items():
            md += f"- **{name}**: {url}\n"
        
        md += "\n## Dependencies\n"
        
        if requires_dist:
            for dep in requires_dist:
                md += f"- {dep}\n"
        else:
            md += "No dependencies listed.\n"
        
        md += "\n## Quick Install\n```\npip install " + name + "\n```\n"
        
        # Truncate the description if it's too long
        desc_length = len(description)
        log.debug(f"Description length: {desc_length} chars")
        
        if desc_length > 1000:
            short_desc = description[:1000] + "...\n\n(Description truncated for brevity)"
            md += f"\n## Description Preview\n{short_desc}"
            log.debug("Description was truncated to 1000 chars")
        else:
            md += f"\n## Description\n{description}"
        
        return md

    @staticmethod
    async def format_documentation(doc_data):
        """Format extracted documentation content into readable markdown.
        
        Args:
            doc_data (dict): Documentation data extracted from the website
            
        Returns:
            str: Formatted markdown text
            
        Raises:
            DataExtractionError: If formatting fails
        """
        if not doc_data:
            raise DataExtractionError("Cannot format empty documentation data")
            
        if 'error' in doc_data:
            raise DataExtractionError(f"Error in documentation data: {doc_data.get('error', 'Unknown error')}")
        
        title = doc_data.get('title', 'Untitled Document')
        log.debug(f"Formatting documentation with title: {title}")
        
        # Format the markdown response
        md = f"# {title}\n\n"
        
        # Add metadata if available
        metadata = doc_data.get('metadata', {})
        if metadata:
            md += "## Page Information\n"
            log.debug(f"Adding {len(metadata)} metadata items")
            for key, value in metadata.items():
                if value:
                    md += f"- **{key.title()}**: {value}\n"
            md += "\n"
        
        # Add table of contents if available
        toc = doc_data.get('toc', [])
        if toc:
            toc_count = len(toc)
            display_count = min(10, toc_count)
            log.debug(f"Adding table of contents with {toc_count} items (showing {display_count})")
            
            md += "## Table of Contents\n"
            for item in toc[:display_count]:
                md += f"- [{item['title']}]({item['url']})\n"
            if toc_count > 10:
                md += f"- ... ({toc_count - 10} more items)\n"
            md += "\n"
        
        # Add content
        content = doc_data.get('content', '')
        if content:
            content_length = len(content)
            log.debug(f"Adding content section with {content_length} chars, {content.count('#')} headings")
            
            md += "## Content\n\n"
            # Limit content length for readability
            if content_length > 4000:
                md += content[:4000] + "\n\n... (content truncated for readability)\n"
                log.debug("Content was truncated to 4000 chars")
            else:
                md += content + "\n"
        
        # Add code snippets section if available
        code_snippets = doc_data.get('code_snippets', [])
        if code_snippets:
            snippet_count = len(code_snippets)
            display_count = min(3, snippet_count)
            
            log.debug(f"Adding {display_count} of {snippet_count} code snippets")
            md += "\n## Code Examples\n\n"
            
            for i, snippet in enumerate(code_snippets[:display_count]):
                lang = snippet['language'] or ""
                code_length = len(snippet['code'])
                log.debug(f"Snippet {i+1}: language={lang or 'none'}, {code_length} chars")
                
                md += f"### Example {i+1}\n\n```{lang}\n{snippet['code']}\n```\n\n"
            
            if snippet_count > 3:
                md += f"(+ {snippet_count - 3} more code examples)\n"
        
        # Add source link
        md += f"\n[View original documentation]({doc_data['url']})\n"
        
        return md

    async def crawl_documentation_site(self, url: str) -> str:
        """Crawl a documentation website and extract formatted content.
        
        Args:
            url (str): URL of the documentation website
            
        Returns:
            str: Formatted documentation content as markdown
            
        Raises:
            NetworkError: If connection to the site fails
            ResourceNotFoundError: If the URL returns a non-200 status code
            DataExtractionError: If content extraction or processing fails
        """
        log.debug(f"Starting documentation crawl for URL: {url}")
        
        # Fetch the HTML content
        html = await self.fetch_url_content(url)
        log.debug(f"Successfully fetched HTML content ({len(html)} bytes)")
        
        # Extract documentation content
        doc_data = await self.extract_documentation_content(html, url)
        log.debug(f"Documentation data extracted: {len(doc_data.get('content', ''))} chars of content, " +
                 f"{len(doc_data.get('code_snippets', []))} code snippets")
        
        # Format the documentation data
        formatted_doc = await self.format_documentation(doc_data)
        log.debug(f"Documentation formatted: {len(formatted_doc)} chars of markdown")
        
        # Save to Parquet
        doc_data['formatted_content'] = formatted_doc
        
        # Generate a filename from the URL
        filename = re.sub(r'[^\w]', '_', url.split('//')[-1])[:50]
        file_path = f"{self.data_dir}/crawls/doc_{filename}_{int(datetime.now().timestamp())}.parquet"
        log.debug(f"Saving documentation data to: {file_path}")
        
        ParquetStorage.save_to_parquet(doc_data, file_path)
        
        return formatted_doc
