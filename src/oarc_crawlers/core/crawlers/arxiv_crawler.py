"""arxiv_fetcher.py

ArXiv Advanced Fetcher Module
This module provides functionality to fetch paper metadata and sources from arXiv,
and extract LaTeX content.

Classes:
    ArxivFetcher:
        Manages fetching paper metadata, source downloads, LaTeX extraction, and database storage.
Functions:
    main:
        Entry point for the interactive command line interface.
    A class to fetch and process papers from arXiv.

Author: @BorcherdingL
Date: 4/10/2025
"""

import re
import os
from typing import Optional
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import tarfile
import io
import tempfile
import shutil

from datetime import datetime, UTC
from pathlib import Path

from oarc_log import log

from oarc_crawlers.core.storage.parquet_storage import ParquetStorage
from oarc_crawlers.utils.paths import Paths
from oarc_crawlers.utils.const import (
    ARXIV_API_BASE_URL, 
    ARXIV_SOURCE_URL_FORMAT,
    ARXIV_ABS_URL_FORMAT,
    ARXIV_PDF_URL_FORMAT,
    ARXIV_NAMESPACES
)


class ArxivCrawler:
    """Class for searching and retrieving ArXiv papers."""
    
    def __init__(self, data_dir: Optional[str] = None):
        """Initialize the ArXiv Fetcher.
        
        Args:
            data_dir (str, optional): Directory to store data. Defaults to Config's data_dir.
        """
        log.debug("Initializing ArxivCrawler")
        if data_dir:
            self.data_dir = Path(data_dir)
            log.debug(f"Using specified data directory: {self.data_dir}")
        else:
            self.data_dir = Paths.get_default_data_dir()
            log.debug(f"Using default data directory: {self.data_dir}")
            
        self.papers_dir = Paths.arxiv_papers_dir(self.data_dir)
        log.debug(f"Papers will be stored in: {self.papers_dir}")
        
        self.sources_dir = Paths.arxiv_sources_dir(self.data_dir)
        log.debug(f"Sources will be stored in: {self.sources_dir}")
        
        self.combined_dir = Paths.arxiv_combined_dir(self.data_dir)
        log.debug(f"Combined data will be stored in: {self.combined_dir}")
    
    @staticmethod
    def extract_arxiv_id(arxiv_input):
        """Extract the ArXiv ID from a URL or ID string."""
        log.debug(f"Extracting ArXiv ID from input: {arxiv_input}")
        
        if not arxiv_input or not isinstance(arxiv_input, str):
            log.error(f"Invalid input: {arxiv_input}. Expected a string.")
            raise ValueError(f"Invalid input: {arxiv_input}. Expected a string.")
            
        # Extract from URL
        if arxiv_input.startswith("https://arxiv.org/"):
            # Handle common URL patterns: /abs/, /pdf/
            url_patterns = ["/abs/", "/pdf/"]
            for pattern in url_patterns:
                if pattern in arxiv_input:
                    # Extract the ID part after the pattern
                    id_part = arxiv_input.split(pattern)[1]
                    # Remove any query parameters or anchors
                    id_part = id_part.split("?")[0].split("#")[0]
                    # Remove .pdf extension if present
                    clean_id = id_part.replace(".pdf", "")
                    log.debug(f"Extracted ArXiv ID: {clean_id} from URL")
                    return clean_id
            
            # If no known pattern was found, but still an arxiv.org URL
            log.error(f"Unrecognized ArXiv URL format: {arxiv_input}")
            raise ValueError(f"Unrecognized ArXiv URL format: {arxiv_input}")
        
        # If it's already an ID, validate it
        if re.match(r'^\d+\.\d+$', arxiv_input) or re.match(r'^[a-z\-]+/\d+$', arxiv_input):
            log.debug(f"Input is already a valid ArXiv ID: {arxiv_input}")
            return arxiv_input
            
        # If we got here, the input is in an invalid format
        log.error(f"Invalid ArXiv ID or URL format: {arxiv_input}")
        raise ValueError(f"Invalid ArXiv ID or URL format: {arxiv_input}")

    async def fetch_paper_info(self, arxiv_id):
        """Fetch paper metadata from arXiv API."""
        log.debug(f"Fetching paper info for ArXiv ID: {arxiv_id}")
        
        query_params = {
            'id_list': arxiv_id,
            'max_results': 1
        }
        
        url = f"{ARXIV_API_BASE_URL}?{urllib.parse.urlencode(query_params)}"
        log.debug(f"ArXiv API URL: {url}")
        
        try:
            log.debug("Sending request to ArXiv API")
            with urllib.request.urlopen(url) as response:
                xml_data = response.read().decode('utf-8')
            
            log.debug(f"Received response length: {len(xml_data)} characters")
            root = ET.fromstring(xml_data)
            
            entry = root.find('atom:entry', ARXIV_NAMESPACES)
            if entry is None:
                log.error(f"No paper found with ID: {arxiv_id}")
                raise ValueError(f"No paper found with the provided ID: {arxiv_id}")
            
            log.debug("Parsing paper metadata from XML response")
            paper_info = {
                'arxiv_id': arxiv_id,
                'title': entry.find('atom:title', ARXIV_NAMESPACES).text.strip(),
                'authors': [author.find('atom:name', ARXIV_NAMESPACES).text 
                           for author in entry.findall('atom:author', ARXIV_NAMESPACES)],
                'abstract': entry.find('atom:summary', ARXIV_NAMESPACES).text.strip(),
                'published': entry.find('atom:published', ARXIV_NAMESPACES).text,
                'pdf_link': next(
                    link.get('href') for link in entry.findall('atom:link', ARXIV_NAMESPACES)
                    if link.get('type') == 'application/pdf'
                ),
                'arxiv_url': next(
                    link.get('href') for link in entry.findall('atom:link', ARXIV_NAMESPACES)
                    if link.get('rel') == 'alternate'
                ),
                'categories': [cat.get('term') for cat in entry.findall('atom:category', ARXIV_NAMESPACES)],
                'timestamp': datetime.now(UTC).isoformat()
            }
            
            log.debug(f"Found paper: {paper_info['title']} by {', '.join(paper_info['authors'][:2])}{'...' if len(paper_info['authors']) > 2 else ''}")
            
            # Add optional fields if present
            optional_fields = ['comment', 'journal_ref', 'doi']
            for field in optional_fields:
                elem = entry.find(f'arxiv:{field}', ARXIV_NAMESPACES)
                if elem is not None:
                    paper_info[field] = elem.text
                    log.debug(f"Added optional field {field}: {elem.text[:50]}{'...' if len(elem.text) > 50 else ''}")
                    
            # Save paper info to Parquet
            file_path = Paths.arxiv_paper_path(self.data_dir, arxiv_id)
            log.debug(f"Saving paper info to: {file_path}")
            ParquetStorage.save_to_parquet(paper_info, file_path)
            
            # Also append to all papers list
            all_papers_path = self.papers_dir / "all_papers.parquet"
            log.debug(f"Appending to all papers list: {all_papers_path}")
            ParquetStorage.append_to_parquet(paper_info, str(all_papers_path))
            
            return paper_info
            
        except urllib.error.URLError as e:
            log.error(f"Failed to connect to arXiv API: {e}")
            return {'error': f"Failed to connect to arXiv API: {e}"}
        except ET.ParseError as e:
            log.error(f"Failed to parse API response: {e}")
            return {'error': f"Failed to parse API response: {e}"}

    @staticmethod
    async def format_paper_for_learning(paper_info):
        """Format paper information for learning."""
        log.debug(f"Formatting paper for learning: {paper_info.get('title', 'Unknown title')}")
        
        formatted_text = f"""# {paper_info['title']}

**Authors:** {', '.join(paper_info['authors'])}

**Published:** {paper_info['published'][:10]}

**Categories:** {', '.join(paper_info['categories'])}

## Abstract
{paper_info['abstract']}

**Links:**
- [ArXiv Page]({paper_info['arxiv_url']})
- [PDF Download]({paper_info['pdf_link']})
"""
        if 'comment' in paper_info and paper_info['comment']:
            formatted_text += f"\n**Comments:** {paper_info['comment']}\n"
            
        if 'journal_ref' in paper_info and paper_info['journal_ref']:
            formatted_text += f"\n**Journal Reference:** {paper_info['journal_ref']}\n"
            
        if 'doi' in paper_info and paper_info['doi']:
            formatted_text += f"\n**DOI:** {paper_info['doi']}\n"
            
        log.debug(f"Formatted paper, length: {len(formatted_text)} characters")
        return formatted_text
        
    async def download_source(self, arxiv_id):
        """Download the LaTeX source files for a paper.
        
        Args:
            arxiv_id (str): ArXiv ID of the paper
            
        Returns:
            dict: Dictionary containing source information and content
        """
        arxiv_id = self.extract_arxiv_id(arxiv_id)
        source_url = ARXIV_SOURCE_URL_FORMAT.format(arxiv_id=arxiv_id)
        
        log.debug(f"Downloading source files for {arxiv_id} from {source_url}")
        
        try:
            # Create temp directory to extract files
            temp_dir = tempfile.mkdtemp()
            log.debug(f"Created temporary directory: {temp_dir}")
            
            # Download the source tarball
            log.debug("Sending request to download source files")
            with urllib.request.urlopen(source_url) as response:
                tar_data = response.read()
                log.debug(f"Downloaded {len(tar_data)} bytes of source data")
                
            # Check if this is a tar file
            source_content = {}
            latex_content = ""
            
            try:
                # Try extracting as tar file
                log.debug("Attempting to extract source as tar archive")
                with io.BytesIO(tar_data) as tar_bytes:
                    with tarfile.open(fileobj=tar_bytes, mode='r:*') as tar:
                        tar.extractall(path=temp_dir)
                        log.debug(f"Extracted tar archive to {temp_dir}")
                        
                        # Collect all files
                        file_count = 0
                        tex_count = 0
                        for root, _, files in os.walk(temp_dir):
                            for file in files:
                                file_path = os.path.join(root, file)
                                relative_path = os.path.relpath(file_path, temp_dir)
                                
                                try:
                                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                        file_content = f.read()
                                    
                                    log.debug(f"Read file: {relative_path} ({len(file_content)} characters)")
                                    source_content[relative_path] = file_content
                                    file_count += 1
                                    
                                    # Collect LaTeX content from .tex files
                                    if file.endswith('.tex'):
                                        latex_content += f"\n% File: {relative_path}\n"
                                        latex_content += file_content
                                        tex_count += 1
                                except Exception as e:
                                    log.warning(f"Could not read file {file_path}: {e}")
                
                log.debug(f"Processed {file_count} files, including {tex_count} .tex files")
                
            except tarfile.ReadError:
                # Not a tar file, might be a single TeX file
                log.debug("Not a tar file, attempting to interpret as a single TeX file")
                try:
                    content = tar_data.decode('utf-8', errors='ignore')
                    source_content['main.tex'] = content
                    latex_content = content
                    log.debug(f"Successfully interpreted as text file ({len(content)} characters)")
                except UnicodeDecodeError:
                    log.warning("Downloaded source is not a tar file or text file")
                    source_content['raw'] = str(tar_data[:100]) + "... (binary data)"
                                
            # Store results in a dictionary
            source_info = {
                'arxiv_id': arxiv_id,
                'timestamp': datetime.now(UTC).isoformat(),
                'latex_content': latex_content,
                'source_files': source_content
            }
            
            # Save to Parquet
            source_path = self.sources_dir / f"{arxiv_id}_source.parquet"
            log.debug(f"Saving source data to: {source_path}")
            ParquetStorage.save_to_parquet(source_info, str(source_path))
            
            return source_info
            
        except urllib.error.URLError as e:
            log.error(f"Failed to download source for {arxiv_id}: {e}")
            return {'error': f"Failed to download source: {e}"}
        finally:
            # Clean up temp directory
            if 'temp_dir' in locals():
                log.debug(f"Cleaning up temporary directory: {temp_dir}")
                shutil.rmtree(temp_dir, ignore_errors=True)

    async def fetch_paper_with_latex(self, arxiv_id):
        """Fetch both paper metadata and LaTeX source.
        
        Args:
            arxiv_id (str): ArXiv ID or URL
            
        Returns:
            dict: Combined paper metadata and source information
        """
        log.debug(f"Fetching paper with LaTeX content for: {arxiv_id}")
        
        arxiv_id = self.extract_arxiv_id(arxiv_id)
        
        # Fetch metadata
        log.debug(f"Fetching metadata for {arxiv_id}")
        paper_info = await self.fetch_paper_info(arxiv_id)
        
        if 'error' in paper_info:
            log.error(f"Error fetching paper info: {paper_info['error']}")
            return paper_info
        
        # Download source
        log.debug(f"Downloading source for {arxiv_id}")
        source_info = await self.download_source(arxiv_id)
        
        if 'error' in source_info:
            log.error(f"Error downloading source: {source_info['error']}")
            return source_info
        
        # Combine information
        log.debug("Combining paper metadata with source information")
        combined_info = {**paper_info}
        combined_info['latex_content'] = source_info.get('latex_content', '')
        combined_info['has_source_files'] = len(source_info.get('source_files', {})) > 0
        
        # Save combined info
        combined_path = self.combined_dir / f"{arxiv_id}_complete.parquet"
        log.debug(f"Saving combined data to: {combined_path}")
        ParquetStorage.save_to_parquet(combined_info, str(combined_path))
        
        log.debug(f"Successfully fetched paper with LaTeX for {arxiv_id}")
        return combined_info

    async def search(self, query, limit=5):
        """Search for papers on ArXiv.
        
        Args:
            query (str): Search query
            limit (int): Maximum number of results to return
            
        Returns:
            dict: Dictionary containing search results
        """
        log.debug(f"Searching ArXiv for: '{query}' with limit {limit}")
        
        query_params = {
            'search_query': f'all:{query}',
            'max_results': limit,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }
        
        url = f"{ARXIV_API_BASE_URL}?{urllib.parse.urlencode(query_params)}"
        log.debug(f"ArXiv search API URL: {url}")
        
        try:
            log.debug("Sending search request to ArXiv API")
            with urllib.request.urlopen(url) as response:
                xml_data = response.read().decode('utf-8')
            
            log.debug(f"Received search response length: {len(xml_data)} characters")
            root = ET.fromstring(xml_data)
            
            entries = root.findall('atom:entry', ARXIV_NAMESPACES)
            log.debug(f"Found {len(entries)} entries in search results")
            
            results = []
            for entry in entries:
                paper = {
                    'id': entry.find('atom:id', ARXIV_NAMESPACES).text.split('/abs/')[-1],
                    'title': entry.find('atom:title', ARXIV_NAMESPACES).text.strip(),
                    'authors': [author.find('atom:name', ARXIV_NAMESPACES).text 
                               for author in entry.findall('atom:author', ARXIV_NAMESPACES)],
                    'abstract': entry.find('atom:summary', ARXIV_NAMESPACES).text.strip(),
                    'published': entry.find('atom:published', ARXIV_NAMESPACES).text,
                    'updated': entry.find('atom:updated', ARXIV_NAMESPACES).text,
                    'pdf_link': ARXIV_PDF_URL_FORMAT.format(arxiv_id=entry.find('atom:id', ARXIV_NAMESPACES).text.split('/abs/')[-1]),
                    'arxiv_url': ARXIV_ABS_URL_FORMAT.format(arxiv_id=entry.find('atom:id', ARXIV_NAMESPACES).text.split('/abs/')[-1]),
                    'categories': [cat.get('term') for cat in entry.findall('atom:category', ARXIV_NAMESPACES)]
                }
                
                # Add optional fields if present
                optional_fields = ['comment', 'journal_ref', 'doi']
                for field in optional_fields:
                    elem = entry.find(f'arxiv:{field}', ARXIV_NAMESPACES)
                    if elem is not None:
                        paper[field] = elem.text
                
                results.append(paper)
                log.debug(f"Added paper to results: {paper['title'][:50]}{'...' if len(paper['title']) > 50 else ''}")
            
            search_data = {
                'query': query,
                'timestamp': datetime.now(UTC).isoformat(),
                'limit': limit,
                'results': results
            }
            
            # Save search results to file
            search_file = self.papers_dir / f"search_{Paths.sanitize_filename(query)}_{int(datetime.now().timestamp())}.parquet"
            log.debug(f"Saving search results to: {search_file}")
            ParquetStorage.save_to_parquet(search_data, str(search_file))
            
            log.debug(f"Search complete, found {len(results)} papers")
            return search_data
            
        except urllib.error.URLError as e:
            log.error(f"Failed to connect to ArXiv API for search: {e}")
            return {'error': f"Failed to connect to ArXiv API: {e}"}
        except ET.ParseError as e:
            log.error(f"Failed to parse search results: {e}")
            return {'error': f"Failed to parse search results: {e}"}