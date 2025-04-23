"""arxiv_fetcher.py

ArXiv Advanced Fetcher Module
This module provides functionality to fetch paper metadata and sources from arXiv,
and extract LaTeX content.

Classes:
    ArxivFetcher:
        Manages fetching paper metadata, source downloads, LaTeX extraction, and database storage.
    A class to fetch and process papers from arXiv.

Author: @BorcherdingL
Date: 4/10/2023
"""

import io
import os
import re
import shutil
import tarfile
import tempfile
import urllib.request
from collections import Counter
from datetime import datetime, UTC
from pathlib import Path
from typing import List, Optional

import arxiv
from tqdm import tqdm

from oarc_log import log
from oarc_crawlers.core.storage.parquet_storage import ParquetStorage
from oarc_crawlers.utils.crawler_utils import CrawlerUtils
from oarc_crawlers.utils.const import (
    ARXIV_BASE_URL,
    ARXIV_SOURCE_URL_FORMAT,
    ARXIV_URL_PATTERNS,
)
from oarc_crawlers.utils.paths import Paths


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
        
        # Initialize NLTK resources
        self._nltk_available = True
        CrawlerUtils.init_nltk()


    @staticmethod
    def extract_arxiv_id(arxiv_input):
        """Extract the ArXiv ID from a URL or ID string."""
        log.debug(f"Extracting ArXiv ID from input: {arxiv_input}")
        
        if not arxiv_input or not isinstance(arxiv_input, str):
            log.error(f"Invalid input: {arxiv_input}. Expected a string.")
            raise ValueError(f"Invalid input: {arxiv_input}. Expected a string.")
            
        # Extract from URL
        if arxiv_input.startswith(ARXIV_BASE_URL):
            # Handle common URL patterns: /abs/, /pdf/
            for pattern in ARXIV_URL_PATTERNS:
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
        
        # Clean the arXiv ID
        arxiv_id = self.extract_arxiv_id(arxiv_id)
        
        try:
            # Create search client
            search = arxiv.Search(
                id_list=[arxiv_id],
                max_results=1
            )
            
            log.debug(f"Querying the arXiv API for paper with ID: {arxiv_id}")
            results = list(search.results())
            
            if not results:
                log.error(f"No paper found with ID: {arxiv_id}")
                raise ValueError(f"No paper found with the provided ID: {arxiv_id}")
                
            paper = results[0]
            log.debug(f"Found paper: {paper.title}")
            
            # Convert to our expected format
            paper_info = {
                'arxiv_id': arxiv_id,
                'title': paper.title.strip(),
                'authors': [author.name for author in paper.authors],
                'abstract': paper.summary.strip(),
                'published': paper.published.isoformat(),
                'pdf_link': paper.pdf_url,
                'arxiv_url': paper.entry_id,
                'categories': [cat for cat in paper.categories],
                'timestamp': datetime.now(UTC).isoformat()
            }
            
            # Add optional fields if present
            if hasattr(paper, 'comment') and paper.comment:
                paper_info['comment'] = paper.comment
                
            if hasattr(paper, 'journal_ref') and paper.journal_ref:
                paper_info['journal_ref'] = paper.journal_ref
                
            if hasattr(paper, 'doi') and paper.doi:
                paper_info['doi'] = paper.doi
            
            log.debug(f"Found paper: {paper_info['title']} by {', '.join(paper_info['authors'][:2])}{'...' if len(paper_info['authors']) > 2 else ''}")
            
            # Save paper info to Parquet
            file_path = Paths.arxiv_paper_path(self.data_dir, arxiv_id)
            log.debug(f"Saving paper info to: {file_path}")
            ParquetStorage.save_to_parquet(paper_info, file_path)
            
            # Also append to all papers list
            all_papers_path = self.papers_dir / "all_papers.parquet"
            log.debug(f"Appending to all papers list: {all_papers_path}")
            ParquetStorage.append_to_parquet(paper_info, str(all_papers_path))
            
            return paper_info
            
        except Exception as e:
            log.error(f"Failed to fetch paper info: {e}")
            return {'error': f"Failed to fetch paper info: {e}"}

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

    async def batch_fetch_papers(self, arxiv_ids: List[str], extract_keywords=False, extract_references=False):
        """Fetch multiple papers in batch, with optional extraction of keywords and references.
        
        Args:
            arxiv_ids (List[str]): List of arXiv IDs to fetch
            extract_keywords (bool): Whether to extract keywords
            extract_references (bool): Whether to extract references
            
        Returns:
            dict: Dictionary containing fetched papers and optional extracted data
        """
        log.debug(f"Batch fetching {len(arxiv_ids)} papers")
        
        results = {
            'papers': [],
            'keywords': [] if extract_keywords else None,
            'references': [] if extract_references else None,
            'errors': []
        }
        
        for arxiv_id in tqdm(arxiv_ids, desc="Fetching papers"):
            try:
                # Get paper info
                paper_info = await self.fetch_paper_info(arxiv_id)
                
                if 'error' in paper_info:
                    results['errors'].append({'arxiv_id': arxiv_id, 'error': paper_info['error']})
                    continue
                    
                results['papers'].append(paper_info)
                
                # Extract keywords if requested
                if extract_keywords:
                    keywords = await self.extract_keywords(paper_info)
                    results['keywords'].append(keywords)
                
                # Extract references if requested
                source_info = await self.download_source(arxiv_id)
                if 'error' not in source_info:
                    refs = await self.extract_references(source_info)
                    results['references'].append(refs)
            
            except Exception as e:
                log.error(f"Error processing {arxiv_id}: {e}")
                results['errors'].append({'arxiv_id': arxiv_id, 'error': str(e)})
        
        # Save batch result using Paths API
        batch_path = Paths.timestamped_path(self.papers_dir, "batch", "parquet")
        log.debug(f"Saving batch results to: {batch_path}")
        ParquetStorage.save_to_parquet(results, str(batch_path))
        
        return results

    async def search(self, query, limit=5):
        """Search for papers on ArXiv.
        
        Args:
            query (str): Search query
            limit (int): Maximum number of results to return
            
        Returns:
            dict: Dictionary containing search results
        """
        log.debug(f"Searching ArXiv for: '{query}' with limit {limit}")
        
        try:
            # Create search object
            search = arxiv.Search(
                query=query,
                max_results=limit,
                sort_by=arxiv.SortCriterion.Relevance,
                sort_order=arxiv.SortOrder.Descending
            )
            
            log.debug("Sending search request to ArXiv API")
            results = []
            for paper in search.results():
                paper_dict = {
                    'id': paper.get_short_id(),
                    'title': paper.title.strip(),
                    'authors': [author.name for author in paper.authors],
                    'abstract': paper.summary.strip(),
                    'published': paper.published.isoformat(),
                    'updated': paper.updated.isoformat(),
                    'pdf_link': paper.pdf_url,
                    'arxiv_url': paper.entry_id,
                    'categories': [cat for cat in paper.categories]
                }
                
                # Add optional fields if present
                if hasattr(paper, 'comment') and paper.comment:
                    paper_dict['comment'] = paper.comment
                    
                if hasattr(paper, 'journal_ref') and paper.journal_ref:
                    paper_dict['journal_ref'] = paper.journal_ref
                    
                if hasattr(paper, 'doi') and paper.doi:
                    paper_dict['doi'] = paper.doi
                
                results.append(paper_dict)
                log.debug(f"Added paper to results: {paper_dict['title'][:50]}{'...' if len(paper_dict['title']) > 50 else ''}")
            
            search_data = {
                'query': query,
                'timestamp': datetime.now(UTC).isoformat(),
                'limit': limit,
                'results': results
            }
            
            # Save search results to file
            search_file = Paths.timestamped_path(
                self.papers_dir, 
                f"search_{Paths.sanitize_filename(query)}", 
                "parquet"
            )
            log.debug(f"Saving search results to: {search_file}")
            ParquetStorage.save_to_parquet(search_data, str(search_file))
            
            log.debug(f"Search complete, found {len(results)} papers")
            return search_data
            
        except Exception as e:
            log.error(f"Failed to search ArXiv: {e}")
            return {'error': f"Failed to search ArXiv: {e}"}

    async def extract_references(self, arxiv_id_or_source_info):
        """Extract bibliography references from the LaTeX source of a paper.
        
        Args:
            arxiv_id_or_source_info (str or dict): ArXiv ID or source info dict from download_source
            
        Returns:
            dict: Dictionary containing extracted references
        """
        log.debug(f"Extracting references for: {arxiv_id_or_source_info}")
        
        # Get source info if arxiv_id was provided
        if isinstance(arxiv_id_or_source_info, str):
            source_info = await self.download_source(arxiv_id_or_source_info)
        else:
            source_info = arxiv_id_or_source_info
        
        if 'error' in source_info:
            return {'error': source_info['error']}
        
        latex_content = source_info.get('latex_content', '')
        references = []
        
        # Look for bibliography entries
        bibitem_pattern = r'\\bibitem(?:\[[^\]]*\])?\{([^}]*)\}(.*?)(?=\\bibitem|\n\\end\{thebibliography\}|$)'
        bibitems = re.finditer(bibitem_pattern, latex_content, re.DOTALL)
        
        for item in bibitems:
            key = item.group(1).strip()
            citation = item.group(2).strip()
            references.append({
                'key': key,
                'citation': re.sub(r'\s+', ' ', citation)
            })
        
        # Look for BibTeX entries
        bibtex_pattern = r'@(\w+)\{([^,]+),(.*?)(?=@\w+\{|\n\s*\n|\\end\{thebibliography\}|$)'
        bibtex_entries = re.finditer(bibtex_pattern, latex_content, re.DOTALL)
        
        for entry in bibtex_entries:
            entry_type = entry.group(1).strip()
            key = entry.group(2).strip()
            content = entry.group(3).strip()
            
            # Parse BibTeX fields
            fields = {}
            field_pattern = r'(\w+)\s*=\s*[{"](.*?)[}"],?'
            for field_match in re.finditer(field_pattern, content, re.DOTALL):
                field_name = field_match.group(1).strip()
                field_value = field_match.group(2).strip()
                fields[field_name] = field_value
            
            references.append({
                'type': entry_type,
                'key': key,
                'fields': fields
            })
        
        # If no references found via bibitem or bibtex, try to find \cite commands
        if not references:
            cite_pattern = r'\\cite(?:\[[^\]]*\])?\{([^}]*)\}'
            cite_keys = set()
            for match in re.finditer(cite_pattern, latex_content):
                keys = match.group(1).split(',')
                for key in keys:
                    cite_keys.add(key.strip())
                    
            if cite_keys:
                references = [{'key': key, 'citation': 'Citation key only'} for key in cite_keys]
        
        result = {
            'arxiv_id': source_info['arxiv_id'],
            'reference_count': len(references),
            'references': references,
            'timestamp': datetime.now(UTC).isoformat()
        }
        
        # Save to Parquet
        ref_path = Paths.arxiv_references_path(self.data_dir, source_info['arxiv_id'])
        ParquetStorage.save_to_parquet(result, str(ref_path))
        
        return result

    async def extract_keywords(self, arxiv_id_or_paper_info, max_keywords=10):
        """Extract keywords from the abstract and title of a paper using NLP techniques.
        
        Args:
            arxiv_id_or_paper_info (str or dict): ArXiv ID or paper info dict from fetch_paper_info
            max_keywords (int): Maximum number of keywords to extract
            
        Returns:
            dict: Dictionary containing extracted keywords
        """
        log.debug(f"Extracting keywords for: {arxiv_id_or_paper_info}")
        
        # Get paper info if arxiv_id was provided
        if isinstance(arxiv_id_or_paper_info, str):
            paper_info = await self.fetch_paper_info(arxiv_id_or_paper_info)
        else:
            paper_info = arxiv_id_or_paper_info
        
        if 'error' in paper_info:
            return {'error': paper_info['error']}
        
        from nltk.corpus import stopwords
        from nltk.tokenize import word_tokenize
        
        # Combine title and abstract for analysis
        text = f"{paper_info['title']} {paper_info['abstract']}"
        
        # Tokenize and clean the text
        tokens = word_tokenize(text.lower())
        stop_words = set(stopwords.words('english'))
        
        # Add domain-specific stop words
        domain_stop_words = {'using', 'method', 'approach', 'paper', 'propose', 'proposed', 'show', 'result', 'results'}
        stop_words.update(domain_stop_words)
        
        # Filter out stop words and non-alphabetic tokens
        filtered_tokens = [word for word in tokens if word.isalpha() and word not in stop_words and len(word) > 2]
        
        # Extract n-grams (for multi-word terminology)
        bigrams = [' '.join(filtered_tokens[i:i+2]) for i in range(len(filtered_tokens)-1)]
        trigrams = [' '.join(filtered_tokens[i:i+3]) for i in range(len(filtered_tokens)-2)]
        
        # Count frequencies
        word_counts = Counter(filtered_tokens)
        bigram_counts = Counter(bigrams)
        trigram_counts = Counter(trigrams)
        
        # Combine and get most common
        combined_counts = word_counts + bigram_counts + trigram_counts
        keywords = [{'keyword': k, 'score': v} for k, v in combined_counts.most_common(max_keywords)]
        
        result = {
            'arxiv_id': paper_info['arxiv_id'],
            'title': paper_info['title'],
            'keywords': keywords,
            'categories': paper_info.get('categories', []),
            'timestamp': datetime.now(UTC).isoformat()
        }
        
        # Save to Parquet
        kw_path = Paths.arxiv_keywords_path(self.data_dir, paper_info['arxiv_id'])
        ParquetStorage.save_to_parquet(result, str(kw_path))
        
        return result

    async def fetch_category_papers(self, category: str, max_results: int = 100, sort_by: str = 'submittedDate'):
        """Fetch papers from a specific arXiv category.
        
        Args:
            category (str): arXiv category (e.g., 'cs.AI', 'physics.optics')
            max_results (int): Maximum number of papers to fetch
            sort_by (str): How to sort results ('relevance', 'lastUpdatedDate', 'submittedDate')
            
        Returns:
            dict: Dictionary containing fetched papers
        """
        log.debug(f"Fetching papers from category: {category}")
        
        sort_criterion = {
            'relevance': arxiv.SortCriterion.Relevance,
            'lastUpdatedDate': arxiv.SortCriterion.LastUpdatedDate,
            'submittedDate': arxiv.SortCriterion.SubmittedDate
        }.get(sort_by, arxiv.SortCriterion.SubmittedDate)
        
        search = arxiv.Search(
            query=f"cat:{category}",
            max_results=max_results,
            sort_by=sort_criterion
        )
        
        papers = []
        for result in search.results():
            paper = {
                'arxiv_id': result.entry_id.split('/')[-1],
                'title': result.title,
                'authors': [author.name for author in result.authors],
                'abstract': result.summary,
                'categories': result.categories,
                'published': result.published.isoformat(),
                'updated': result.updated.isoformat(),
                'pdf_url': result.pdf_url,
                'entry_id': result.entry_id
            }
            
            # Add optional fields if present
            if hasattr(result, 'comment') and result.comment:
                paper['comment'] = result.comment
                
            if hasattr(result, 'journal_ref') and result.journal_ref:
                paper['journal_ref'] = result.journal_ref
                
            if hasattr(result, 'doi') and result.doi:
                paper['doi'] = result.doi
                
            papers.append(paper)
        
        result = {
            'category': category,
            'papers_count': len(papers),
            'max_results': max_results,
            'sort_by': sort_by,
            'timestamp': datetime.now(UTC).isoformat(),
            'papers': papers
        }
        
        # Save to Parquet using Paths API
        cat_path = Paths.arxiv_category_path(self.data_dir, category)
        ParquetStorage.save_to_parquet(result, str(cat_path))
        # Also store the path in the result
        result['parquet_path'] = str(cat_path)
        
        return result

    async def extract_math_equations(self, arxiv_id_or_source_info):
        """Extract mathematical equations from the LaTeX source of a paper.
        
        Args:
            arxiv_id_or_source_info (str or dict): ArXiv ID or source info dict from download_source
            
        Returns:
            dict: Dictionary containing extracted equations
        """
        log.debug(f"Extracting equations for: {arxiv_id_or_source_info}")
        
        # Get source info if arxiv_id was provided
        if isinstance(arxiv_id_or_source_info, str):
            source_info = await self.download_source(arxiv_id_or_source_info)
        else:
            source_info = arxiv_id_or_source_info
        
        if 'error' in source_info:
            return {'error': source_info['error']}
        
        latex_content = source_info.get('latex_content', '')
        
        # Find inline math expressions
        inline_math = re.findall(r'\$([^\$]+?)\$', latex_content)
        
        # Find display math environments
        display_math_patterns = [
            r'\\begin\{equation\}(.*?)\\end\{equation\}',
            r'\\begin\{equation\*\}(.*?)\\end\{equation\*\}',
            r'\\begin\{align\}(.*?)\\end\{align\}',
            r'\\begin\{align\*\}(.*?)\\end\{align\*\}',
            r'\\begin\{eqnarray\}(.*?)\\end\{eqnarray\}',
            r'\\begin\{eqnarray\*\}(.*?)\\end\{eqnarray\*\}',
            r'\\\[(.*?)\\\]'
        ]
        
        display_math = []
        for pattern in display_math_patterns:
            display_math.extend(re.findall(pattern, latex_content, re.DOTALL))
        
        # Clean up equations (remove extra whitespace, etc.)
        inline_math = [re.sub(r'\s+', ' ', eq.strip()) for eq in inline_math]
        display_math = [re.sub(r'\s+', ' ', eq.strip()) for eq in display_math]
        
        result = {
            'arxiv_id': source_info['arxiv_id'],
            'inline_equation_count': len(inline_math),
            'display_equation_count': len(display_math),
            'inline_equations': inline_math,
            'display_equations': display_math,
            'timestamp': datetime.now(UTC).isoformat()
        }
        
        # Save to Parquet using Paths API
        eq_path = Paths.arxiv_equations_path(self.data_dir, source_info['arxiv_id'])
        ParquetStorage.save_to_parquet(result, str(eq_path))
        
        return result

    async def generate_citation_network(self, seed_papers: List[str], max_depth: int = 1):
        """Generate a citation network starting from seed papers.
        
        This creates a network of papers and their references, up to a specified depth.
        
        Args:
            seed_papers (List[str]): List of arXiv IDs to start from
            max_depth (int): How many layers of references to follow
            
        Returns:
            dict: Dictionary containing the citation network
        """
        log.debug(f"Generating citation network from {len(seed_papers)} seed papers")
        
        network = {
            'nodes': {},  # Papers as nodes
            'edges': [],  # References as edges
        }
        
        papers_to_process = [(paper_id, 0) for paper_id in seed_papers]  # (paper_id, depth)
        processed_papers = set()
        
        while papers_to_process:
            current_id, current_depth = papers_to_process.pop(0)
            
            if current_id in processed_papers or current_depth > max_depth:
                continue
                
            processed_papers.add(current_id)
            
            try:
                # Get paper info
                paper_info = await self.fetch_paper_info(current_id)
                if 'error' in paper_info:
                    continue
                
                # Add node to network
                network['nodes'][current_id] = {
                    'title': paper_info['title'],
                    'authors': paper_info['authors'],
                    'published': paper_info['published'],
                    'categories': paper_info.get('categories', []),
                    'depth': current_depth
                }
                
                # Get references
                references = await self.extract_references(current_id)
                if 'error' in references or not references.get('references'):
                    continue
                
                # Process references
                for ref in references['references']:
                    ref_key = ref.get('key', '')
                    ref_citation = ref.get('citation', '')
                    
                    if ref_key:
                        # Add edge to network
                        edge = {
                            'source': current_id,
                            'target': ref_key,
                            'citation': ref_citation
                        }
                        network['edges'].append(edge)
                    
                    # If we haven't reached max depth, add reference to queue for processing
                    if current_depth < max_depth:
                        # Try to extract arXiv ID from citation if possible
                        arxiv_match = re.search(r'arxiv:(\d+\.\d+|[a-z\-]+/\d+)', ref_citation, re.IGNORECASE)
                        if arxiv_match:
                            ref_arxiv_id = arxiv_match.group(1)
                            papers_to_process.append((ref_arxiv_id, current_depth + 1))
            
            except Exception as e:
                log.error(f"Error processing paper {current_id}: {e}")
        
        # Add network stats
        network['stats'] = {
            'node_count': len(network['nodes']),
            'edge_count': len(network['edges']),
            'max_depth': max_depth,
            'timestamp': datetime.now(UTC).isoformat()
        }
        
        # Save network to file using Paths API
        timestamp = int(datetime.now().timestamp())
        net_path = Paths.arxiv_network_path(self.data_dir, timestamp)
        ParquetStorage.save_to_parquet(network, str(net_path))
        
        return network