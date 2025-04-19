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
import logging
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import tarfile
import io
import tempfile
import shutil

from datetime import datetime, UTC
from pathlib import Path

from ..storage.parquet_storage import ParquetStorage
from oarc_crawlers.utils.paths import Paths

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArxivCrawler:
    """Class for searching and retrieving ArXiv papers."""
    
    def __init__(self, data_dir=None):
        """Initialize the ArXiv Fetcher.
        
        Args:
            data_dir (str, optional): Directory to store data.
        """
        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            self.data_dir = Paths.get_default_data_dir()
            
        self.papers_dir = Paths.ensure_path(self.data_dir / "papers")
        self.sources_dir = Paths.ensure_path(self.data_dir / "sources")
        self.logger = logging.getLogger(__name__)
    
    @staticmethod
    def extract_arxiv_id(arxiv_input):
        """Extract the ArXiv ID from a URL or ID string."""
        if not arxiv_input or not isinstance(arxiv_input, str):
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
                    return id_part.replace(".pdf", "")
            
            # If no known pattern was found, but still an arxiv.org URL
            raise ValueError(f"Unrecognized ArXiv URL format: {arxiv_input}")
        
        # If it's already an ID, validate it
        if re.match(r'^\d+\.\d+$', arxiv_input) or re.match(r'^[a-z\-]+/\d+$', arxiv_input):
            return arxiv_input
            
        # If we got here, the input is in an invalid format
        raise ValueError(f"Invalid ArXiv ID or URL format: {arxiv_input}")

    async def fetch_paper_info(self, arxiv_id):
        """Fetch paper metadata from arXiv API."""
        base_url = 'http://export.arxiv.org/api/query'
        query_params = {
            'id_list': arxiv_id,
            'max_results': 1
        }
        
        url = f"{base_url}?{urllib.parse.urlencode(query_params)}"
        
        try:
            with urllib.request.urlopen(url) as response:
                xml_data = response.read().decode('utf-8')
            
            root = ET.fromstring(xml_data)
            namespaces = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            entry = root.find('atom:entry', namespaces)
            if entry is None:
                raise ValueError("No paper found with the provided ID")
            
            paper_info = {
                'arxiv_id': arxiv_id,
                'title': entry.find('atom:title', namespaces).text.strip(),
                'authors': [author.find('atom:name', namespaces).text 
                           for author in entry.findall('atom:author', namespaces)],
                'abstract': entry.find('atom:summary', namespaces).text.strip(),
                'published': entry.find('atom:published', namespaces).text,
                'pdf_link': next(
                    link.get('href') for link in entry.findall('atom:link', namespaces)
                    if link.get('type') == 'application/pdf'
                ),
                'arxiv_url': next(
                    link.get('href') for link in entry.findall('atom:link', namespaces)
                    if link.get('rel') == 'alternate'
                ),
                'categories': [cat.get('term') for cat in entry.findall('atom:category', namespaces)],
                'timestamp': datetime.now(UTC).isoformat()
            }
            
            # Add optional fields if present
            optional_fields = ['comment', 'journal_ref', 'doi']
            for field in optional_fields:
                elem = entry.find(f'arxiv:{field}', namespaces)
                if elem is not None:
                    paper_info[field] = elem.text
                    
            # Save paper info to Parquet
            file_path = f"{self.papers_dir}/{arxiv_id}.parquet"
            ParquetStorage.save_to_parquet(paper_info, file_path)
            
            # Also append to all papers list
            all_papers_path = f"{self.papers_dir}/all_papers.parquet"
            ParquetStorage.append_to_parquet(paper_info, all_papers_path)
            
            return paper_info
            
        except urllib.error.URLError as e:
            self.logger.error(f"Failed to connect to arXiv API: {e}")
            raise ConnectionError(f"Failed to connect to arXiv API: {e}")
        except ET.ParseError as e:
            self.logger.error(f"Failed to parse API response: {e}")
            raise ValueError(f"Failed to parse API response: {e}")

    @staticmethod
    async def format_paper_for_learning(paper_info):
        """Format paper information for learning."""
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
            
        return formatted_text
        
    async def download_source(self, arxiv_id):
        """Download the LaTeX source files for a paper.
        
        Args:
            arxiv_id (str): ArXiv ID of the paper
            
        Returns:
            dict: Dictionary containing source information and content
        """
        # Create source URL - replacing PDF with source format
        arxiv_id = self.extract_arxiv_id(arxiv_id)
        source_url = f"https://arxiv.org/e-print/{arxiv_id}"
        
        self.logger.info(f"Downloading source files for {arxiv_id} from {source_url}")
        
        try:
            # Create temp directory to extract files
            temp_dir = tempfile.mkdtemp()
            
            # Download the source tarball
            with urllib.request.urlopen(source_url) as response:
                tar_data = response.read()
                
            # Check if this is a tar file
            source_content = {}
            latex_content = ""
            
            try:
                # Try extracting as tar file
                with io.BytesIO(tar_data) as tar_bytes:
                    with tarfile.open(fileobj=tar_bytes, mode='r:*') as tar:
                        tar.extractall(path=temp_dir)
                        
                        # Collect all files
                        for root, _, files in os.walk(temp_dir):
                            for file in files:
                                file_path = os.path.join(root, file)
                                relative_path = os.path.relpath(file_path, temp_dir)
                                
                                try:
                                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                        file_content = f.read()
                                        
                                    source_content[relative_path] = file_content
                                    
                                    # Collect LaTeX content from .tex files
                                    if file.endswith('.tex'):
                                        latex_content += f"\n% File: {relative_path}\n"
                                        latex_content += file_content
                                except Exception as e:
                                    self.logger.warning(f"Could not read file {file_path}: {e}")
                
            except tarfile.ReadError:
                # Not a tar file, might be a single TeX file
                try:
                    content = tar_data.decode('utf-8', errors='ignore')
                    source_content['main.tex'] = content
                    latex_content = content
                except UnicodeDecodeError:
                    self.logger.warning("Downloaded source is not a tar file or text file")
                    source_content['raw'] = str(tar_data[:100]) + "... (binary data)"
                                
            # Store results in a dictionary
            source_info = {
                'arxiv_id': arxiv_id,
                'timestamp': datetime.now(UTC).isoformat(),
                'latex_content': latex_content,
                'source_files': source_content
            }
            
            # Save to Parquet
            source_path = f"{self.sources_dir}/{arxiv_id}_source.parquet"
            ParquetStorage.save_to_parquet(source_info, source_path)
            
            return source_info
            
        except urllib.error.URLError as e:
            self.logger.error(f"Failed to download source for {arxiv_id}: {e}")
            raise ConnectionError(f"Failed to download source: {e}")
        finally:
            # Clean up temp directory
            if 'temp_dir' in locals():
                shutil.rmtree(temp_dir, ignore_errors=True)

    async def fetch_paper_with_latex(self, arxiv_id):
        """Fetch both paper metadata and LaTeX source.
        
        Args:
            arxiv_id (str): ArXiv ID or URL
            
        Returns:
            dict: Combined paper metadata and source information
        """
        arxiv_id = self.extract_arxiv_id(arxiv_id)
        
        # Fetch metadata
        paper_info = await self.fetch_paper_info(arxiv_id)
        
        # Download source
        source_info = await self.download_source(arxiv_id)
        
        # Combine information
        combined_info = {**paper_info}
        combined_info['latex_content'] = source_info.get('latex_content', '')
        combined_info['has_source_files'] = len(source_info.get('source_files', {})) > 0
        
        # Save combined info
        combined_path = f"{self.data_dir}/combined/{arxiv_id}_complete.parquet"
        os.makedirs(os.path.dirname(combined_path), exist_ok=True)
        ParquetStorage.save_to_parquet(combined_info, combined_path)
        
        return combined_info