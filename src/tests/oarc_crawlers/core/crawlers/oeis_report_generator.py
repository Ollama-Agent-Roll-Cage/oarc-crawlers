"""OEIS Report Generator

This script demonstrates how to use the OEISCrawler class to generate
comprehensive reports on integer sequences from OEIS and store them
in parquet files.

Author: @LeoBorcherding
Date: 5/01/2025
"""

import os
import sys
import asyncio
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Add the project root to sys.path if needed
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from oarc_log import log
from oarc_crawlers.core.oeis.oeis_crawler import OEISCrawler
from oarc_crawlers.core.storage.parquet_storage import ParquetStorage
from oarc_crawlers.config.config import Config
from oarc_crawlers.utils.paths import Paths

class OEISReportGenerator:
    """Generate comprehensive reports for OEIS sequences."""
    
    def __init__(self, data_dir=None):
        """Initialize the report generator.
        
        Args:
            data_dir (str, optional): Directory to store data. Defaults to Config's data_dir.
        """
        self.config = Config()
        if data_dir is None:
            data_dir = str(self.config.data_dir)
        self.data_dir = data_dir
        self.reports_dir = Paths.ensure_dir(Path(self.data_dir) / "oeis" / "reports")
        self.crawler = OEISCrawler(data_dir)
        log.debug(f"Initialized OEISReportGenerator with reports directory: {self.reports_dir}")
    
    async def generate_sequence_report(self, sequence_id: str, output_path=None):
        """Generate a comprehensive report for a specific sequence.
        
        Args:
            sequence_id (str): The OEIS sequence ID
            output_path (str, optional): Path to save the report. Defaults to reports_dir.
            
        Returns:
            str: Path to the generated report file
        """
        log.debug(f"Generating report for sequence {sequence_id}")
        
        # Normalize sequence ID
        sequence_id = sequence_id.lstrip('A')
        
        # Fetch enhanced sequence data
        sequence_data = await self.crawler.build_sequence_report(sequence_id)
        
        # Generate a report file path if not provided
        if output_path is None:
            output_path = str(self.reports_dir / f"report_A{sequence_id}_{pd.Timestamp.now().strftime('%Y%m%d')}.parquet")
        
        # Create the report structure
        report = {
            'id': sequence_data['id'],
            'title': sequence_data['title'],
            'values': sequence_data.get('values', []),
            'offset': sequence_data.get('offset', ''),
            'report_sections': {}
        }
        
        # Add different sections to the report
        report['report_sections']['summary'] = self._generate_summary_section(sequence_data)
        report['report_sections']['mathematical_analysis'] = self._generate_math_analysis(sequence_data)
        report['report_sections']['references'] = self._generate_references_section(sequence_data)
        report['report_sections']['related_sequences'] = await self._find_related_sequences(sequence_id)
        report['report_sections']['visualizations'] = self._generate_visualizations(sequence_data)
        
        # Save the report
        ParquetStorage.save_to_parquet(report, output_path)
        log.debug(f"Saved report to {output_path}")
        
        return output_path
    
    def _generate_summary_section(self, sequence_data):
        """Generate a summary section for the report.
        
        Args:
            sequence_data (dict): Sequence data
            
        Returns:
            dict: Summary section data
        """
        log.debug(f"Generating summary for {sequence_data['id']}")
        
        summary = {
            'description': sequence_data['title'],
            'first_terms': sequence_data.get('values', [])[:15],
            'offset': sequence_data.get('offset', ''),
            'author': sequence_data.get('author', 'Unknown'),
        }
        
        # Add formulas if available
        if sequence_data.get('formula'):
            summary['formulas'] = sequence_data['formula'][:3]  # First three formulas
        
        # Add comments if available
        if sequence_data.get('comment'):
            summary['comments'] = sequence_data['comment'][:5]  # First five comments
        
        return summary
    
    def _generate_math_analysis(self, sequence_data):
        """Generate mathematical analysis of the sequence.
        
        Args:
            sequence_data (dict): Sequence data
            
        Returns:
            dict: Mathematical analysis data
        """
        log.debug(f"Generating mathematical analysis for {sequence_data['id']}")
        
        analysis = {
            'pattern_type': sequence_data.get('pattern', 'unknown'),
        }
        
        values = sequence_data.get('values', [])
        if len(values) < 3:
            analysis['limited_data'] = "Insufficient data for analysis"
            return analysis
        
        # Calculate differences
        differences = sequence_data.get('differences', [values[i+1] - values[i] for i in range(len(values)-1)])
        analysis['differences'] = differences[:10]  # First 10 differences
        
        # Calculate ratios if applicable
        if all(v != 0 for v in values[:-1]):  # Avoid division by zero
            ratios = [values[i+1] / values[i] for i in range(len(values)-1)]
            analysis['ratios'] = [round(r, 4) for r in ratios[:10]]  # First 10 ratios
        
        # Check for common sequences
        analysis['sequence_properties'] = []
        
        # Check if arithmetic
        if len(set(differences)) == 1:
            analysis['sequence_properties'].append({
                'type': 'arithmetic',
                'details': f"Common difference: {differences[0]}"
            })
        
        # Check if geometric
        if all(values[i] != 0 for i in range(len(values)-1)):
            ratios = [values[i+1] / values[i] for i in range(len(values)-1)]
            if len(set([round(r, 10) for r in ratios])) == 1:
                analysis['sequence_properties'].append({
                    'type': 'geometric',
                    'details': f"Common ratio: {round(ratios[0], 4)}"
                })
        
        # Check if matches a^2, a^3, etc.
        # Check for squares
        if all(int(v**0.5)**2 == v for v in values):
            analysis['sequence_properties'].append({
                'type': 'perfect_squares',
                'details': f"Terms are perfect squares"
            })
        
        # Check for cubes
        if all(round(v**(1/3))**3 == v for v in values):
            analysis['sequence_properties'].append({
                'type': 'perfect_cubes',
                'details': f"Terms are perfect cubes"
            })
        
        # Additional properties based on formulas from the data
        if sequence_data.get('formula'):
            analysis['derived_from_formulas'] = True
            analysis['formula_notes'] = []
            
            # Look for polynomial formulas
            for formula in sequence_data.get('formula', []):
                if 'n^2' in formula or 'n**2' in formula:
                    analysis['formula_notes'].append("Quadratic term present")
                if 'n^3' in formula or 'n**3' in formula:
                    analysis['formula_notes'].append("Cubic term present")
        
        return analysis
    
    async def _find_related_sequences(self, sequence_id):
        """Find sequences related to the target sequence.
        
        Args:
            sequence_id (str): OEIS sequence ID
            
        Returns:
            dict: Related sequences data
        """
        log.debug(f"Finding related sequences for A{sequence_id}")
        
        # Search for related sequences using key terms from the sequence title
        sequence_data = await self.crawler.build_sequence_report(sequence_id)
        title = sequence_data.get('title', '')
        
        # Extract key terms for searching
        key_terms = []
        for term in title.lower().split():
            if len(term) > 4 and term not in ['numbers', 'sequence', 'integer', 'function']:
                key_terms.append(term)
        
        related = {
            'by_title_similarity': [],
            'by_cross_reference': [],
            'by_formula_similarity': []
        }
        
        # Only search if we have meaningful terms
        if key_terms:
            search_term = ' '.join(key_terms[:2])  # Use the first two substantial terms
            try:
                search_results = await self.crawler.search_sequences(search_term)
                # Filter out the original sequence
                related['by_title_similarity'] = [
                    {'id': r['id'], 'title': r['title']} 
                    for r in search_results 
                    if r['id'] != f"A{sequence_id}"
                ][:5]  # Limit to top 5
            except Exception as e:
                log.warning(f"Error searching for related sequences: {str(e)}")
        
        # Check cross-references from the sequence data
        if sequence_data.get('link'):
            for link in sequence_data.get('link', []):
                # Look for references to other sequences (A123456)
                seq_refs = re.findall(r'A(\d{6})', link)
                for ref in seq_refs:
                    if ref != sequence_id:
                        related['by_cross_reference'].append({
                            'id': f"A{ref}",
                            'context': link[:100] + "..." if len(link) > 100 else link
                        })
        
        return related
    
    def _generate_references_section(self, sequence_data):
        """Generate a references section for the report.
        
        Args:
            sequence_data (dict): Sequence data
            
        Returns:
            dict: References section data
        """
        log.debug(f"Generating references for {sequence_data['id']}")
        
        references = {
            'academic': [],
            'links': [],
            'implementation': []
        }
        
        # Process reference entries
        for ref in sequence_data.get('reference', []):
            references['academic'].append(ref)
        
        # Process link entries
        for link in sequence_data.get('link', []):
            if 'http' in link:
                references['links'].append(link)
        
        # Look for implementation code in the comments or examples
        for comment in sequence_data.get('comment', []):
            if any(lang in comment.lower() for lang in ['program', 'code', 'algorithm', 'implementation']):
                references['implementation'].append(comment)
        
        for example in sequence_data.get('example', []):
            if any(lang in example.lower() for lang in ['program', 'code', 'algorithm', 'implementation']):
                references['implementation'].append(example)
        
        return references
    
    def _generate_visualizations(self, sequence_data):
        """Generate visualization data for the sequence.
        
        Args:
            sequence_data (dict): Sequence data
            
        Returns:
            dict: Visualization section data
        """
        log.debug(f"Generating visualizations for {sequence_data['id']}")
        
        values = sequence_data.get('values', [])
        if len(values) < 2:
            return {'error': 'Insufficient data for visualization'}
        
        visualizations = {
            'plots': [],
            'patterns': []
        }
        
        # Generate plot data
        plot_data = {
            'type': 'line',
            'title': f"Growth of {sequence_data['id']}",
            'x_values': list(range(len(values))),
            'y_values': values,
            'x_label': 'Index',
            'y_label': 'Value'
        }
        visualizations['plots'].append(plot_data)
        
        # Growth rate plot (if enough values)
        if len(values) >= 3:
            growth_rates = [values[i+1]/values[i] if values[i] != 0 else 0 for i in range(len(values)-1)]
            growth_plot = {
                'type': 'line',
                'title': f"Growth Rate of {sequence_data['id']}",
                'x_values': list(range(len(growth_rates))),
                'y_values': growth_rates,
                'x_label': 'Index',
                'y_label': 'Ratio a(n+1)/a(n)'
            }
            visualizations['plots'].append(growth_plot)
        
        # Look for patterns to visualize
        if 'hexagonal' in sequence_data['title'].lower():
            visualizations['patterns'].append({
                'type': 'hexagonal',
                'description': 'Hexagonal number pattern visualization'
            })
        elif 'triangular' in sequence_data['title'].lower():
            visualizations['patterns'].append({
                'type': 'triangular',
                'description': 'Triangular number pattern visualization'
            })
        
        return visualizations
    
    async def generate_multi_sequence_report(self, sequence_ids, output_path=None):
        """Generate a comprehensive report comparing multiple sequences.
        
        Args:
            sequence_ids (list): List of OEIS sequence IDs
            output_path (str, optional): Path to save the report. Defaults to reports_dir.
            
        Returns:
            str: Path to the generated report file
        """
        log.debug(f"Generating multi-sequence report for {len(sequence_ids)} sequences")
        
        # Generate a report file path if not provided
        if output_path is None:
            seq_list = '_'.join(s.lstrip('A') for s in sequence_ids[:3])
            if len(sequence_ids) > 3:
                seq_list += f"_plus_{len(sequence_ids)-3}"
            output_path = str(self.reports_dir / f"multi_report_{seq_list}_{pd.Timestamp.now().strftime('%Y%m%d')}.parquet")
        
        # Fetch data for all sequences
        sequences = []
        for seq_id in sequence_ids:
            try:
                data = await self.crawler.build_sequence_report(seq_id.lstrip('A'))
                sequences.append(data)
            except Exception as e:
                log.warning(f"Failed to fetch data for sequence {seq_id}: {str(e)}")
        
        # Create report structure
        report = {
            'title': f"Comparative Analysis of {len(sequences)} Integer Sequences",
            'sequences': [seq['id'] for seq in sequences],
            'report_date': pd.Timestamp.now().isoformat(),
            'sequence_data': sequences,
            'comparative_analysis': self._generate_comparative_analysis(sequences)
        }
        
        # Generate ontology
        try:
            ontology = await self.crawler.build_ontology([seq['id'].lstrip('A') for seq in sequences])
            report['ontology'] = ontology
        except Exception as e:
            log.warning(f"Failed to build ontology: {str(e)}")
        
        # Save the report
        ParquetStorage.save_to_parquet(report, output_path)
        log.debug(f"Saved multi-sequence report to {output_path}")
        
        return output_path
    
    def _generate_comparative_analysis(self, sequences):
        """Generate comparative analysis of multiple sequences.
        
        Args:
            sequences (list): List of sequence data dictionaries
            
        Returns:
            dict: Comparative analysis data
        """
        log.debug(f"Generating comparative analysis for {len(sequences)} sequences")
        
        analysis = {
            'growth_comparison': [],
            'formula_comparison': [],
            'shared_properties': []
        }
        
        # Compare growth rates
        for seq in sequences:
            values = seq.get('values', [])
            if len(values) >= 5:  # Need at least 5 values for meaningful comparison
                growth_data = {
                    'id': seq['id'],
                    'first_values': values[:5],
                    'growth_type': 'unknown'
                }
                
                # Determine growth type
                differences = [values[i+1] - values[i] for i in range(len(values)-1)]
                
                if len(set(differences)) == 1:
                    growth_data['growth_type'] = 'linear'
                    growth_data['growth_rate'] = differences[0]
                elif all(values[i] != 0 for i in range(len(values)-1)):
                    ratios = [values[i+1] / values[i] for i in range(len(values)-1)]
                    if len(set([round(r, 4) for r in ratios])) == 1:
                        growth_data['growth_type'] = 'exponential'
                        growth_data['growth_rate'] = round(ratios[0], 4)
                    else:
                        # Check for polynomial growth
                        if all(v > 0 for v in values):
                            log_values = [math.log(v) for v in values]
                            log_diffs = [log_values[i+1] - log_values[i] for i in range(len(log_values)-1)]
                            if all(0.9 < log_diffs[i+1]/log_diffs[i] < 1.1 for i in range(len(log_diffs)-1)):
                                growth_data['growth_type'] = 'polynomial'
                
                analysis['growth_comparison'].append(growth_data)
        
        # Look for shared properties
        properties = set()
        for seq in sequences:
            # Extract properties from comments
            for comment in seq.get('comment', []):
                lower_comment = comment.lower()
                for prop in ['prime', 'fibonacci', 'catalan', 'euler', 'bernoulli', 'square', 'cube']:
                    if prop in lower_comment:
                        properties.add(prop)
        
        analysis['shared_properties'] = list(properties)
        
        return analysis

    @staticmethod
    async def run_example(sequence_id="003215"):
        """Run an example report generation to demonstrate usage.
        
        Args:
            sequence_id (str): OEIS sequence ID to analyze (without 'A' prefix)
        """
        generator = OEISReportGenerator()
        
        print(f"Generating report for A{sequence_id}...")
        report_path = await generator.generate_sequence_report(sequence_id)
        
        print(f"Report saved to: {report_path}")
        
        # Load and display parts of the report
        report_df = ParquetStorage.load_from_parquet(report_path)
        if report_df is not None:
            report = report_df.iloc[0].to_dict()
            
            print("\n===== SEQUENCE REPORT =====")
            print(f"ID: {report['id']}")
            print(f"Title: {report['title']}")
            print(f"Values: {report['values'][:10]}...")
            
            # Display sections
            summary = report['report_sections']['summary']
            print("\n--- SUMMARY ---")
            print(f"Description: {summary['description']}")
            print(f"First terms: {summary['first_terms']}")
            
            # Display mathematical analysis
            math_analysis = report['report_sections']['mathematical_analysis']
            print("\n--- MATHEMATICAL ANALYSIS ---")
            print(f"Pattern type: {math_analysis.get('pattern_type', 'unknown')}")
            
            if 'differences' in math_analysis:
                print(f"First differences: {math_analysis['differences']}")
            
            if 'sequence_properties' in math_analysis:
                print("\nSequence properties:")
                for prop in math_analysis['sequence_properties']:
                    print(f"  - {prop['type']}: {prop['details']}")
            
            # Display related sequences
            related = report['report_sections']['related_sequences']
            print("\n--- RELATED SEQUENCES ---")
            
            if related.get('by_title_similarity'):
                print("\nBy title similarity:")
                for seq in related['by_title_similarity'][:3]:
                    print(f"  - {seq['id']}: {seq['title']}")
            
            if related.get('by_cross_reference'):
                print("\nBy cross-reference:")
                for seq in related['by_cross_reference'][:3]:
                    print(f"  - {seq['id']}: {seq['context'][:50]}...")

# Main execution for standalone operation
if __name__ == "__main__":
    # Run the example asynchronously
    if len(sys.argv) > 1:
        sequence_id = sys.argv[1].lstrip('A')
        asyncio.run(OEISReportGenerator.run_example(sequence_id))
    else:
        asyncio.run(OEISReportGenerator.run_example())
