"""OEIS Crawler Module

This module provides functions for crawling and extracting sequence data from the 
Online Encyclopedia of Integer Sequences (OEIS). It builds on the WebCrawler class
to provide specialized functionality for OEIS sequences.

Author: @LeoBorcherding
Date: 5/03/2025
"""

import re
import json
from datetime import datetime, UTC
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
import asyncio

from bs4 import BeautifulSoup
import pandas as pd

from oarc_log import log
from oarc_utils.errors import ResourceNotFoundError, DataExtractionError
from oarc_crawlers.core.storage.parquet_storage import ParquetStorage
from oarc_crawlers.core.crawlers.web_crawler import WebCrawler
from oarc_crawlers.config.config import Config
from oarc_crawlers.utils.paths import Paths

class OEISCrawler(WebCrawler):
    """Class for crawling and extracting data from the OEIS website."""
    
    BASE_URL = "https://oeis.org"
    SEQUENCE_URL = "https://oeis.org/A{sequence_id}"
    SEARCH_URL = "https://oeis.org/search?q={search_term}&fmt=json"
    
    def __init__(self, data_dir=None):
        """Initialize the OEIS Crawler.
        
        Args:
            data_dir (str, optional): Directory to store data. Defaults to Config's data_dir.
        """
        super().__init__(data_dir)
        self.oeis_data_dir = Paths.ensure_path(Path(self.data_dir) / "oeis")
        log.debug(f"Initialized OEISCrawler with OEIS data directory: {self.oeis_data_dir}")
    
    async def fetch_sequence(self, sequence_id: str) -> Dict[str, Any]:
        """Fetch and parse data for a specific OEIS sequence.
        
        Args:
            sequence_id (str): The OEIS sequence ID (with or without 'A' prefix)
            
        Returns:
            Dict[str, Any]: Parsed sequence data
            
        Raises:
            ResourceNotFoundError: If the sequence doesn't exist
            DataExtractionError: If parsing fails
        """
        # Normalize the sequence ID
        sequence_id = sequence_id.lstrip('A')
        sequence_id = sequence_id.zfill(6)  # Pad with zeros to 6 digits
        
        log.debug(f"Fetching OEIS sequence A{sequence_id}")
        
        # Construct the URL
        url = self.SEQUENCE_URL.format(sequence_id=sequence_id)
        
        # Fetch the HTML content
        html = await self.fetch_url_content(url)
        
        # Parse the HTML to extract sequence data
        sequence_data = await self._parse_sequence_html(html, sequence_id)
        
        # Save the data
        file_path = Path(self.oeis_data_dir) / f"A{sequence_id}.parquet"
        ParquetStorage.save_to_parquet(sequence_data, str(file_path))
        log.debug(f"Saved sequence data to {file_path}")
        
        return sequence_data
    
    async def _parse_sequence_html(self, html: str, sequence_id: str) -> Dict[str, Any]:
        """Parse the HTML content of an OEIS sequence page.
        
        Args:
            html (str): HTML content of the sequence page
            sequence_id (str): The OEIS sequence ID
            
        Returns:
            Dict[str, Any]: Parsed sequence data
            
        Raises:
            DataExtractionError: If parsing fails
        """
        log.debug(f"Parsing HTML for sequence A{sequence_id}")
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Initialize the data dictionary
        sequence_data = {
            'id': f"A{sequence_id}",
            'title': '',
            'values': [],
            'formula': [],
            'example': [],
            'comment': [],
            'reference': [],
            'link': [],
            'offset': '',
            'author': '',
            'time': datetime.now(UTC).isoformat(),
        }
        
        # Extract the title/description
        title_elem = soup.find('title')
        if title_elem:
            title_text = title_elem.get_text()
            # Remove the standard prefix "A123456 - OEIS"
            title_match = re.match(r'A\d+ - OEIS - (.*)', title_text)
            if title_match:
                sequence_data['title'] = title_match.group(1).strip()
            else:
                sequence_data['title'] = title_text.replace("- OEIS", "").strip()
        
        # Extract the sequence values
        sequence_list = soup.find('tt', class_='sequence')
        if sequence_list:
            sequence_text = sequence_list.get_text().strip()
            # Parse the comma-separated values
            try:
                values = [int(v.strip()) for v in sequence_text.split(',')]
                sequence_data['values'] = values
            except ValueError:
                log.warning(f"Failed to parse some sequence values for A{sequence_id}")
                # Try to extract whatever we can
                values = []
                for v in sequence_text.split(','):
                    try:
                        values.append(int(v.strip()))
                    except ValueError:
                        continue
                sequence_data['values'] = values
        
        # Extract different sections
        sections = soup.find_all('table', class_='list')
        for section in sections:
            section_text = section.get_text()
            
            # Process each section based on its header
            if 'FORMULA' in section_text:
                formulas = self._extract_section_items(section, 'formula')
                sequence_data['formula'] = formulas
            
            elif 'EXAMPLE' in section_text:
                examples = self._extract_section_items(section, 'example')
                sequence_data['example'] = examples
            
            elif 'COMMENT' in section_text:
                comments = self._extract_section_items(section, 'comment')
                sequence_data['comment'] = comments
            
            elif 'REFERENCE' in section_text:
                references = self._extract_section_items(section, 'reference')
                sequence_data['reference'] = references
            
            elif 'LINK' in section_text:
                links = self._extract_section_items(section, 'link')
                sequence_data['link'] = links
            
            elif 'OFFSET' in section_text:
                offset_match = re.search(r'OFFSET\s+([^<]+)', section_text)
                if offset_match:
                    sequence_data['offset'] = offset_match.group(1).strip()
            
            elif 'AUTHOR' in section_text:
                author_match = re.search(r'AUTHOR\s+([^<]+)', section_text)
                if author_match:
                    sequence_data['author'] = author_match.group(1).strip()
        
        log.debug(f"Extracted data for A{sequence_id}: {len(sequence_data['values'])} values, "
                 f"{len(sequence_data['formula'])} formulas, {len(sequence_data['comment'])} comments")
        
        return sequence_data
    
    def _extract_section_items(self, section_elem, section_type: str) -> List[str]:
        """Extract items from a section in the OEIS page.
        
        Args:
            section_elem: BeautifulSoup element containing the section
            section_type (str): Type of section (formula, comment, etc.)
            
        Returns:
            List[str]: Extracted items
        """
        items = []
        rows = section_elem.find_all('tr')
        
        # Skip the header row
        for row in rows[1:]:
            # Get all <td> elements in the row
            cells = row.find_all('td')
            if len(cells) >= 2:
                # The content is in the second cell
                content = cells[1].get_text().strip()
                if content:
                    items.append(content)
        
        log.debug(f"Extracted {len(items)} {section_type} items")
        return items
    
    async def search_sequences(self, search_term: str) -> List[Dict[str, Any]]:
        """Search OEIS for sequences matching the given term.
        
        Args:
            search_term (str): Search term (e.g., "fibonacci", "prime numbers")
            
        Returns:
            List[Dict[str, Any]]: List of matching sequence summaries
            
        Raises:
            ResourceNotFoundError: If the search fails
        """
        log.debug(f"Searching OEIS for: {search_term}")
        
        # Construct the search URL
        url = self.SEARCH_URL.format(search_term=search_term)
        
        try:
            # Fetch the JSON response
            html = await self.fetch_url_content(url)
            
            # Parse the JSON
            # The HTML will likely contain a JSON structure we need to extract
            json_match = re.search(r'({.*})', html)
            if not json_match:
                raise DataExtractionError(f"Failed to extract JSON from OEIS search response")
            
            json_str = json_match.group(1)
            search_data = json.loads(json_str)
            
            results = []
            for result in search_data.get('results', []):
                sequence_summary = {
                    'id': result.get('number'),
                    'title': result.get('name', ''),
                    'values': result.get('data', '').split(','),
                    'offset': result.get('offset', ''),
                }
                results.append(sequence_summary)
            
            log.debug(f"Found {len(results)} matching sequences")
            
            # Save search results
            search_file = Path(self.oeis_data_dir) / f"search_{datetime.now().strftime('%Y%m%d%H%M%S')}.parquet"
            search_data = {
                'search_term': search_term,
                'time': datetime.now(UTC).isoformat(),
                'results': results
            }
            ParquetStorage.save_to_parquet(search_data, str(search_file))
            log.debug(f"Saved search results to {search_file}")
            
            return results
        
        except Exception as e:
            log.error(f"Error searching OEIS: {str(e)}")
            raise ResourceNotFoundError(f"Failed to search OEIS: {str(e)}")
    
    async def build_sequence_report(self, sequence_id: str) -> Dict[str, Any]:
        """Build a comprehensive report for a specific sequence."""
        log.debug(f"Building report for sequence {sequence_id}")
        
        # Normalize the sequence ID
        sequence_id = sequence_id.lstrip('A')
        
        # Check if we have data cached
        cache_file = Path(self.oeis_data_dir) / f"A{sequence_id}.parquet"
        if cache_file.exists():
            log.debug(f"Loading cached data from {cache_file}")
            try:
                df = ParquetStorage.load_from_parquet(str(cache_file))
                if df is not None and len(df.index) > 0:  # Fixed empty array check
                    sequence_data = df.iloc[0].to_dict()
                    # Check if the data is complete and has values
                    if sequence_data.get('values') and len(sequence_data['values']) > 0:
                        log.debug(f"Using cached data for A{sequence_id}")
                        return sequence_data
            except Exception as e:
                log.warning(f"Failed to load cached data: {str(e)}")
        
        # Fetch new data if not cached or cache is incomplete
        sequence_data = await self.fetch_sequence(sequence_id)
        
        # Validate sequence data
        if not sequence_data.get('values'):
            log.warning(f"No values found for sequence {sequence_id}")
            sequence_data['values'] = []
        
        # Enhance the report with additional analysis
        enhanced_data = await self._enhance_sequence_data(sequence_data)
        
        # Save the enhanced report
        report_file = Path(self.oeis_data_dir) / f"report_A{sequence_id}.parquet"
        ParquetStorage.save_to_parquet(enhanced_data, str(report_file))
        log.debug(f"Saved enhanced report to {report_file}")
        
        return enhanced_data
    
    async def _enhance_sequence_data(self, sequence_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance sequence data with additional analysis.
        
        Args:
            sequence_data (Dict[str, Any]): Base sequence data
            
        Returns:
            Dict[str, Any]: Enhanced sequence data
        """
        log.debug(f"Enhancing data for sequence {sequence_data['id']}")
        
        # Create a copy to avoid modifying the original
        enhanced_data = sequence_data.copy()
        
        # Extract the sequence values
        values = sequence_data.get('values', [])
        
        # Skip analysis if we don't have enough values
        if len(values) < 3:
            log.warning(f"Not enough values for sequence {sequence_data['id']} to perform analysis")
            return enhanced_data
        
        # Calculate basic statistics
        if values:
            enhanced_data['statistics'] = {
                'min': min(values),
                'max': max(values),
                'mean': sum(values) / len(values),
                'length': len(values)
            }
        
        # Calculate differences between consecutive terms
        if len(values) >= 2:
            differences = [values[i+1] - values[i] for i in range(len(values)-1)]
            enhanced_data['differences'] = differences
            
            # Check if differences are constant (arithmetic sequence)
            if len(set(differences)) == 1:
                enhanced_data['pattern'] = 'arithmetic'
                enhanced_data['common_difference'] = differences[0]
            
            # Check if the sequence is geometric
            if all(values[i] != 0 for i in range(len(values))):
                ratios = [values[i+1] / values[i] for i in range(len(values)-1) if values[i] != 0]
                if len(set([round(r, 10) for r in ratios])) == 1:  # Allow for small floating point differences
                    enhanced_data['pattern'] = 'geometric'
                    enhanced_data['common_ratio'] = ratios[0]
        
        # Try to find a polynomial fit
        # This is a simple approach - for more advanced analysis, consider using
        # libraries like numpy.polyfit
        
        # Look for relationships with other common sequences
        # This would involve comparing with known patterns
        
        # Add a timestamp for when the analysis was performed
        enhanced_data['analysis_time'] = datetime.now(UTC).isoformat()
        
        log.debug(f"Enhanced data for {sequence_data['id']} with statistics and pattern analysis")
        
        return enhanced_data
    
    async def build_ontology(self, sequence_ids: List[str]) -> Dict[str, Any]:
        """Build an ontology of relationships between multiple sequences."""
        log.debug(f"Building ontology for {len(sequence_ids)} sequences")
        
        # Fetch data for all sequences
        sequence_data_list = []
        nodes = {}
        
        for seq_id in sequence_ids:
            try:
                data = await self.build_sequence_report(seq_id)
                sequence_data_list.append(data)
                # Add to nodes dictionary with proper structure
                nodes[seq_id] = {
                    'id': data['id'],
                    'title': data['title'],
                    'values': data.get('values', [])[:5],  # First 5 values
                    'depth': 0 if seq_id == sequence_ids[0] else 1  # Main sequence has depth 0
                }
            except Exception as e:
                log.warning(f"Failed to fetch data for sequence {seq_id}: {str(e)}")
        
        # Build relationships between sequences
        relationships = []
        for i, seq1 in enumerate(sequence_data_list):
            for j, seq2 in enumerate(sequence_data_list[i+1:], i+1):
                relation = self._find_relationship(seq1, seq2)
                if relation:
                    relationships.append({
                        'source': seq1['id'],
                        'target': seq2['id'],
                        'relationship': relation
                    })
        
        # Create the ontology with proper structure
        ontology = {
            'nodes': nodes,
            'sequences': [seq['id'] for seq in sequence_data_list],
            'relationships': relationships,
            'time': datetime.now(UTC).isoformat(),
        }
        
        # Save the ontology
        ontology_file = Path(self.oeis_data_dir) / f"ontology_{datetime.now().strftime('%Y%m%d%H%M%S')}.parquet"
        ParquetStorage.save_to_parquet(ontology, str(ontology_file))
        log.debug(f"Saved ontology to {ontology_file}")
        
        return ontology
    
    def _find_relationship(self, seq1: Dict[str, Any], seq2: Dict[str, Any]) -> Optional[str]:
        """Find relationships between two sequences.
        
        Args:
            seq1 (Dict[str, Any]): First sequence data
            seq2 (Dict[str, Any]): Second sequence data
            
        Returns:
            Optional[str]: Description of the relationship, if any
        """
        values1 = seq1.get('values', [])
        values2 = seq2.get('values', [])
        
        # Check for too few values
        if len(values1) < 3 or len(values2) < 3:
            return None
        
        # Check if one sequence is a subsequence of the other
        if all(v in values2 for v in values1):
            return "subsequence"
        if all(v in values1 for v in values2):
            return "supersequence"
        
        # Check if one is the difference of the other
        if len(values1) >= len(values2) + 1:
            diffs = [values1[i+1] - values1[i] for i in range(len(values1)-1)]
            if diffs[:len(values2)] == values2:
                return "first_difference"
        
        if len(values2) >= len(values1) + 1:
            diffs = [values2[i+1] - values2[i] for i in range(len(values2)-1)]
            if diffs[:len(values1)] == values1:
                return "first_difference"
        
        # Check for other relationships - could be extended with more patterns
        
        return None
    
    async def create_sequence_database(self, sequence_ids: List[str]) -> str:
        """Create a comprehensive database of multiple sequences.
        
        Args:
            sequence_ids (List[str]): List of sequence IDs to include
            
        Returns:
            str: Path to the generated database file
        """
        log.debug(f"Creating database for {len(sequence_ids)} sequences")
        
        # Fetch data for all sequences
        all_data = []
        for seq_id in sequence_ids:
            try:
                data = await self.build_sequence_report(seq_id)
                all_data.append(data)
            except Exception as e:
                log.warning(f"Failed to fetch data for sequence {seq_id}: {str(e)}")
        
        # Convert to DataFrame
        if not all_data:
            log.warning("No sequence data fetched successfully")
            return ""
        
        # Normalize the data for DataFrame structure
        normalized_data = []
        for data in all_data:
            entry = {
                'id': data['id'],
                'title': data['title'],
                'values_str': ','.join(str(v) for v in data.get('values', [])),
                'offset': data.get('offset', ''),
                'formula_count': len(data.get('formula', [])),
                'comment_count': len(data.get('comment', [])),
                'reference_count': len(data.get('reference', [])),
                'link_count': len(data.get('link', [])),
            }
            
            # Add first few formulas directly
            for i, formula in enumerate(data.get('formula', [])[:3]):
                entry[f'formula_{i+1}'] = formula
            
            normalized_data.append(entry)
        
        # Create database file
        db_file = Path(self.oeis_data_dir) / f"sequences_db_{datetime.now().strftime('%Y%m%d%H%M%S')}.parquet"
        ParquetStorage.save_to_parquet(normalized_data, str(db_file))
        log.debug(f"Saved sequence database to {db_file}")
        
        return str(db_file)
    
    @staticmethod
    async def run_example():
        """Run an example crawler operation to demonstrate usage."""
        # Create the crawler
        crawler = OEISCrawler()
        
        # Example 1: Fetch a specific sequence (A003215 - Hex numbers)
        try:
            sequence_data = await crawler.fetch_sequence("003215")
            print(f"Fetched sequence {sequence_data['id']}: {sequence_data['title']}")
            print(f"First few values: {sequence_data['values'][:10]}")
            
            # Print a few formulas if available
            if sequence_data.get('formula'):
                print("\nFormulas:")
                for i, formula in enumerate(sequence_data['formula'][:3]):
                    print(f"  {i+1}. {formula}")
        except Exception as e:
            print(f"Error fetching sequence: {str(e)}")
        
        # Example 2: Search for sequences
        try:
            results = await crawler.search_sequences("hexagonal numbers")
            print(f"\nFound {len(results)} sequences related to hexagonal numbers")
            for i, result in enumerate(results[:5]):
                print(f"  {i+1}. {result['id']}: {result['title']}")
        except Exception as e:
            print(f"Error searching: {str(e)}")
        
        # Example 3: Build an ontology
        try:
            ontology = await crawler.build_ontology(["003215", "000217", "000290"])
            print(f"\nBuilt ontology with {len(ontology['relationships'])} relationships")
            for rel in ontology['relationships']:
                print(f"  {rel['source']} is {rel['relationship']} of {rel['target']}")
        except Exception as e:
            print(f"Error building ontology: {str(e)}")
        
        # Example 4: Create a database of related sequences
        try:
            db_path = await crawler.create_sequence_database(["003215", "000217", "000290", "000578"])
            print(f"\nCreated sequence database at: {db_path}")
        except Exception as e:
            print(f"Error creating database: {str(e)}")

# Main execution for standalone operation
if __name__ == "__main__":
    # Run the example asynchronously
    asyncio.run(OEISCrawler.run_example())
