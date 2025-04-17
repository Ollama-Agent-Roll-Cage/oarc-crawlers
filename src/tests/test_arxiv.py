import unittest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
from pathlib import Path
import xml.etree.ElementTree as ET
import io
import tarfile

from oarc_crawlers import ArxivFetcher

class TestArxivFetcher(unittest.TestCase):
    """Test the ArXiv fetcher module."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.fetcher = ArxivFetcher(data_dir=self.temp_dir.name)
        
        # Sample ArXiv ID
        self.arxiv_id = "2101.12345"
        self.arxiv_url = f"https://arxiv.org/abs/{self.arxiv_id}"
        
        # Sample XML API response
        self.sample_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
          <entry>
            <id>http://arxiv.org/abs/{self.arxiv_id}</id>
            <published>2021-01-28T00:00:00Z</published>
            <title>Test ArXiv Paper</title>
            <summary>This is a test abstract for a paper that doesn't exist.</summary>
            <author>
              <name>First Author</name>
            </author>
            <author>
              <name>Second Author</name>
            </author>
            <link href="http://arxiv.org/abs/{self.arxiv_id}" rel="alternate" type="text/html"/>
            <link href="http://arxiv.org/pdf/{self.arxiv_id}" rel="related" type="application/pdf"/>
            <category term="cs.AI"/>
            <category term="cs.LG"/>
            <arxiv:comment xmlns:arxiv="http://arxiv.org/schemas/atom">40 pages, 15 figures</arxiv:comment>
            <arxiv:journal_ref xmlns:arxiv="http://arxiv.org/schemas/atom">Journal of Test Science, Vol. 42</arxiv:journal_ref>
            <arxiv:doi xmlns:arxiv="http://arxiv.org/schemas/atom">10.1234/test.5678</arxiv:doi>
          </entry>
        </feed>
        """
        
        # Sample LaTeX content
        self.sample_latex = r"""
        \documentclass{article}
        \title{Test Paper}
        \author{First Author \and Second Author}
        
        \begin{document}
        \maketitle
        
        \begin{abstract}
        This is a test abstract.
        \end{abstract}
        
        \section{Introduction}
        This is the introduction.
        
        \section{Method}
        This is the method section.
        
        \section{Conclusion}
        This is the conclusion.
        
        \end{document}
        """
        
    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()
    
    def test_extract_arxiv_id(self):
        """Test extracting ArXiv ID from various formats."""
        # Test extracting from URL
        self.assertEqual(ArxivFetcher.extract_arxiv_id(f"https://arxiv.org/abs/{self.arxiv_id}"), self.arxiv_id)
        self.assertEqual(ArxivFetcher.extract_arxiv_id(f"https://arxiv.org/pdf/{self.arxiv_id}"), self.arxiv_id)
        
        # Test extracting from ID string
        self.assertEqual(ArxivFetcher.extract_arxiv_id(self.arxiv_id), self.arxiv_id)
        
        # Test invalid input
        with self.assertRaises(ValueError):
            ArxivFetcher.extract_arxiv_id("not_an_arxiv_id")
    
    @patch('urllib.request.urlopen')
    @patch('oarc_crawlers.arxiv_fetcher.ParquetStorage')
    async def test_fetch_paper_info(self, mock_storage, mock_urlopen):
        """Test fetching paper information."""
        # Setup mock urlopen
        mock_cm = MagicMock()
        mock_cm.__enter__.return_value.read.return_value = self.sample_xml.encode()
        mock_urlopen.return_value = mock_cm
        
        # Call the method
        result = await self.fetcher.fetch_paper_info(self.arxiv_id)
        
        # Assertions
        mock_urlopen.assert_called_once()
        mock_storage.save_to_parquet.assert_called()
        mock_storage.append_to_parquet.assert_called_once()
        
        self.assertEqual(result['arxiv_id'], self.arxiv_id)
        self.assertEqual(result['title'], "Test ArXiv Paper")
        self.assertEqual(result['authors'], ["First Author", "Second Author"])
        self.assertIn("test abstract", result['abstract'])
        self.assertEqual(result['published'], "2021-01-28T00:00:00Z")
        self.assertEqual(result['pdf_link'], f"http://arxiv.org/pdf/{self.arxiv_id}")
        self.assertEqual(result['arxiv_url'], f"http://arxiv.org/abs/{self.arxiv_id}")
        self.assertEqual(result['categories'], ["cs.AI", "cs.LG"])
        self.assertEqual(result['comment'], "40 pages, 15 figures")
        self.assertEqual(result['journal_ref'], "Journal of Test Science, Vol. 42")
        self.assertEqual(result['doi'], "10.1234/test.5678")
    
    async def test_format_paper_for_learning(self):
        """Test formatting paper information for learning."""
        paper_info = {
            'title': 'Test Paper',
            'authors': ['First Author', 'Second Author'],
            'published': '2021-01-28T00:00:00Z',
            'categories': ['cs.AI', 'cs.LG'],
            'abstract': 'This is a test abstract.',
            'arxiv_url': f'http://arxiv.org/abs/{self.arxiv_id}',
            'pdf_link': f'http://arxiv.org/pdf/{self.arxiv_id}',
            'comment': '40 pages, 15 figures',
            'journal_ref': 'Journal of Test Science, Vol. 42',
            'doi': '10.1234/test.5678'
        }
        
        result = await ArxivFetcher.format_paper_for_learning(paper_info)
        
        # Assertions
        self.assertIn("# Test Paper", result)
        self.assertIn("**Authors:** First Author, Second Author", result)
        self.assertIn("**Published:** 2021-01-28", result)
        self.assertIn("**Categories:** cs.AI, cs.LG", result)
        self.assertIn("## Abstract\nThis is a test abstract.", result)
        self.assertIn(f"[ArXiv Page](http://arxiv.org/abs/{self.arxiv_id})", result)
        self.assertIn(f"[PDF Download](http://arxiv.org/pdf/{self.arxiv_id})", result)
        self.assertIn("**Comments:** 40 pages, 15 figures", result)
        self.assertIn("**Journal Reference:** Journal of Test Science, Vol. 42", result)
        self.assertIn("**DOI:** 10.1234/test.5678", result)
    
    @patch('urllib.request.urlopen')
    @patch('oarc_crawlers.arxiv_fetcher.ParquetStorage')
    @patch('tempfile.mkdtemp')
    @patch('shutil.rmtree')
    async def test_download_source_tar(self, mock_rmtree, mock_mkdtemp, mock_storage, mock_urlopen):
        """Test downloading source files when they are in a tar file."""
        # Setup mock for temporary directory
        mock_mkdtemp.return_value = f"{self.temp_dir.name}/temp"
        Path(f"{self.temp_dir.name}/temp").mkdir(exist_ok=True)
        
        # Create a test tar file in memory with a .tex file
        tar_buffer = io.BytesIO()
        with tarfile.open(fileobj=tar_buffer, mode='w') as tar:
            tex_info = tarfile.TarInfo(name='main.tex')
            tex_file = io.BytesIO(self.sample_latex.encode())
            tex_info.size = len(self.sample_latex)
            tar.addfile(tex_info, tex_file)
        
        # Setup mock urlopen
        mock_cm = MagicMock()
        mock_cm.__enter__.return_value.read.return_value = tar_buffer.getvalue()
        mock_urlopen.return_value = mock_cm
        
        # Mock open file operation
        with patch('builtins.open', mock_open(read_data=self.sample_latex)):
            # Call the method
            result = await self.fetcher.download_source(self.arxiv_id)
        
        # Assertions
        mock_urlopen.assert_called_once()
        mock_storage.save_to_parquet.assert_called_once()
        
        self.assertEqual(result['arxiv_id'], self.arxiv_id)
        self.assertIn('main.tex', result['source_files'])
        self.assertIn(self.sample_latex, result['latex_content'])
    
    @patch('oarc_crawlers.arxiv_fetcher.ArxivFetcher.fetch_paper_info')
    @patch('oarc_crawlers.arxiv_fetcher.ArxivFetcher.download_source')
    @patch('oarc_crawlers.arxiv_fetcher.ParquetStorage')
    @patch('os.makedirs')
    async def test_fetch_paper_with_latex(self, mock_makedirs, mock_storage, mock_download, mock_fetch):
        """Test fetching both paper metadata and LaTeX source."""
        # Setup mocks
        mock_fetch.return_value = {
            'arxiv_id': self.arxiv_id,
            'title': 'Test Paper',
            'authors': ['Author1', 'Author2'],
            'abstract': 'Test abstract',
            'pdf_link': f'http://arxiv.org/pdf/{self.arxiv_id}'
        }
        
        mock_download.return_value = {
            'arxiv_id': self.arxiv_id,
            'latex_content': self.sample_latex,
            'source_files': {'main.tex': self.sample_latex}
        }
        
        # Call the method
        result = await self.fetcher.fetch_paper_with_latex(self.arxiv_id)
        
        # Assertions
        mock_fetch.assert_called_once_with(self.arxiv_id)
        mock_download.assert_called_once_with(self.arxiv_id)
        mock_storage.save_to_parquet.assert_called_once()
        
        self.assertEqual(result['arxiv_id'], self.arxiv_id)
        self.assertEqual(result['title'], 'Test Paper')
        self.assertEqual(result['authors'], ['Author1', 'Author2'])
        self.assertEqual(result['abstract'], 'Test abstract')
        self.assertEqual(result['latex_content'], self.sample_latex)
        self.assertTrue(result['has_source_files'])

if __name__ == '__main__':
    unittest.main()