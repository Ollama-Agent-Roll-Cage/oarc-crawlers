import pytest
from unittest.mock import patch, MagicMock
import tempfile
import io
import tarfile

from oarc_crawlers import ArxivCrawler

# Setup fixture to replace setUp/tearDown
@pytest.fixture
def arxiv_setup():
    """Set up test environment."""
    temp_dir = tempfile.TemporaryDirectory()
    fetcher = ArxivCrawler(data_dir=temp_dir.name)
    
    # Sample ArXiv ID
    arxiv_id = "2101.12345"
    arxiv_url = f"https://arxiv.org/abs/{arxiv_id}"
    
    # Sample XML API response
    sample_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
      <entry>
        <id>http://arxiv.org/abs/{arxiv_id}</id>
        <published>2021-01-28T00:00:00Z</published>
        <title>Test ArXiv Paper</title>
        <summary>This is a test abstract for a paper that doesn't exist.</summary>
        <author>
          <name>First Author</name>
        </author>
        <author>
          <name>Second Author</name>
        </author>
        <link href="http://arxiv.org/abs/{arxiv_id}" rel="alternate" type="text/html"/>
        <link href="http://arxiv.org/pdf/{arxiv_id}" rel="related" type="application/pdf"/>
        <category term="cs.AI"/>
        <category term="cs.LG"/>
        <arxiv:comment xmlns:arxiv="http://arxiv.org/schemas/atom">40 pages, 15 figures</arxiv:comment>
        <arxiv:journal_ref xmlns:arxiv="http://arxiv.org/schemas/atom">Journal of Test Science, Vol. 42</arxiv:journal_ref>
        <arxiv:doi xmlns:arxiv="http://arxiv.org/schemas/atom">10.1234/test.5678</arxiv:doi>
      </entry>
    </feed>
    """
    
    # Sample LaTeX content
    sample_latex = r"""
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
    
    # Return a dict with all the test data
    test_data = {
        'temp_dir': temp_dir,
        'fetcher': fetcher,
        'arxiv_id': arxiv_id,
        'arxiv_url': arxiv_url,
        'sample_xml': sample_xml,
        'sample_latex': sample_latex
    }
    
    yield test_data
    
    # Clean up (equivalent to tearDown)
    temp_dir.cleanup()

def test_extract_arxiv_id(arxiv_setup):
    """Test extracting ArXiv ID from various formats."""
    arxiv_id = arxiv_setup['arxiv_id']
    
    # Test extracting from URL
    assert ArxivCrawler.extract_arxiv_id(f"https://arxiv.org/abs/{arxiv_id}") == arxiv_id
    assert ArxivCrawler.extract_arxiv_id(f"https://arxiv.org/pdf/{arxiv_id}") == arxiv_id
    
    # Test extracting from ID string
    assert ArxivCrawler.extract_arxiv_id(arxiv_id) == arxiv_id
    
    # Test invalid input
    with pytest.raises(ValueError):
        ArxivCrawler.extract_arxiv_id("not_an_arxiv_id")
    with pytest.raises(ValueError):
        ArxivCrawler.extract_arxiv_id(None)
    with pytest.raises(ValueError):
        ArxivCrawler.extract_arxiv_id("")
    with pytest.raises(ValueError):
        ArxivCrawler.extract_arxiv_id("invalid-format")

@pytest.mark.asyncio
async def test_download_source_tar(arxiv_setup):
    """Test downloading source tarball."""
    fetcher = arxiv_setup['fetcher']
    arxiv_id = arxiv_setup['arxiv_id']
    sample_latex = arxiv_setup['sample_latex']
    
    # Create a mock tarfile
    mock_tar_bytes = io.BytesIO()
    with tarfile.open(fileobj=mock_tar_bytes, mode='w:gz') as tar:
        info = tarfile.TarInfo('main.tex')
        tex_bytes = sample_latex.encode('utf-8')
        info.size = len(tex_bytes)
        tar.addfile(info, io.BytesIO(tex_bytes))
    
    # Mock the urllib.request.urlopen context manager
    mock_response = MagicMock()
    mock_response.read.return_value = mock_tar_bytes.getvalue()
    mock_urlopen = MagicMock()
    mock_urlopen.__enter__.return_value = mock_response
    
    # Mock the ParquetStorage.save_to_parquet method
    with patch('urllib.request.urlopen', return_value=mock_urlopen), \
         patch('oarc_crawlers.ParquetStorage.save_to_parquet', return_value=None):
        
        # Call the method and properly await it
        source_info = await fetcher.download_source(arxiv_id)
        
        # Assertions
        assert source_info['arxiv_id'] == arxiv_id
        assert 'latex_content' in source_info
        assert 'source_files' in source_info
        assert 'main.tex' in source_info['source_files']

@pytest.mark.asyncio
async def test_fetch_paper_info(arxiv_setup):
    """Test fetching paper metadata."""
    fetcher = arxiv_setup['fetcher']
    arxiv_id = arxiv_setup['arxiv_id']
    sample_xml = arxiv_setup['sample_xml']
    
    # Mock the urllib.request.urlopen context manager
    mock_response = MagicMock()
    mock_response.read.return_value = sample_xml.encode('utf-8')
    mock_urlopen = MagicMock()
    mock_urlopen.__enter__.return_value = mock_response
    
    # Mock the ParquetStorage methods
    with patch('urllib.request.urlopen', return_value=mock_urlopen), \
         patch('oarc_crawlers.ParquetStorage.save_to_parquet', return_value=None), \
         patch('oarc_crawlers.ParquetStorage.append_to_parquet', return_value=None):
        
        # Call the method and properly await it
        paper_info = await fetcher.fetch_paper_info(arxiv_id)
        
        # Assertions
        assert paper_info['arxiv_id'] == arxiv_id
        assert paper_info['title'] == 'Test ArXiv Paper'
        assert len(paper_info['authors']) == 2
        assert paper_info['authors'][0] == 'First Author'
        assert paper_info['authors'][1] == 'Second Author'
        assert paper_info['comment'] == '40 pages, 15 figures'
        assert paper_info['journal_ref'] == 'Journal of Test Science, Vol. 42'
        assert paper_info['doi'] == '10.1234/test.5678'

@pytest.mark.asyncio
async def test_fetch_paper_with_latex(arxiv_setup):
    """Test fetching paper with LaTeX source."""
    fetcher = arxiv_setup['fetcher']
    arxiv_id = arxiv_setup['arxiv_id']
    sample_latex = arxiv_setup['sample_latex']
    
    # We'll mock fetch_paper_info and download_source methods 
    # rather than mocking all the way down
    mock_paper_info = {
        'arxiv_id': arxiv_id,
        'title': 'Test Paper',
        'authors': ['First Author', 'Second Author'],
        'abstract': 'Test abstract',
        'published': '2021-01-01',
        'pdf_link': f'https://arxiv.org/pdf/{arxiv_id}',
        'arxiv_url': f'https://arxiv.org/abs/{arxiv_id}',
        'categories': ['cs.AI', 'cs.LG']
    }
    
    mock_source_info = {
        'arxiv_id': arxiv_id,
        'latex_content': sample_latex,
        'source_files': {'main.tex': sample_latex}
    }
    
    # Create patch for the methods
    with patch.object(fetcher, 'fetch_paper_info', return_value=mock_paper_info), \
         patch.object(fetcher, 'download_source', return_value=mock_source_info), \
         patch('oarc_crawlers.ParquetStorage.save_to_parquet', return_value=None), \
         patch('os.makedirs', return_value=None):
        
        # Call the method and properly await it
        combined_info = await fetcher.fetch_paper_with_latex(arxiv_id)
        
        # Assertions
        assert combined_info['arxiv_id'] == arxiv_id
        assert combined_info['latex_content'] == sample_latex
        assert combined_info['has_source_files'] == True

@pytest.mark.asyncio
async def test_format_paper_for_learning(arxiv_setup):
    """Test formatting paper info for learning."""
    arxiv_id = arxiv_setup['arxiv_id']
    
    mock_paper_info = {
        'arxiv_id': arxiv_id,
        'title': 'Test Paper',
        'authors': ['First Author', 'Second Author'],
        'abstract': 'Test abstract',
        'published': '2021-01-01',
        'pdf_link': f'https://arxiv.org/pdf/{arxiv_id}',
        'arxiv_url': f'https://arxiv.org/abs/{arxiv_id}',
        'categories': ['cs.AI', 'cs.LG'],
        'comment': 'Test comment',
        'journal_ref': 'Test journal',
        'doi': '10.1234/test'
    }
    
    # Call the method and properly await it
    formatted_text = await ArxivCrawler.format_paper_for_learning(mock_paper_info)
    
    # Basic structure assertions
    assert '# Test Paper' in formatted_text
    assert '**Authors:** First Author, Second Author' in formatted_text
    assert '**Published:** 2021-01-01' in formatted_text
    assert '**Categories:** cs.AI, cs.LG' in formatted_text
    assert '## Abstract' in formatted_text
    assert 'Test abstract' in formatted_text
    
    # Links assertions
    assert f'[ArXiv Page](https://arxiv.org/abs/{arxiv_id})' in formatted_text
    assert f'[PDF Download](https://arxiv.org/pdf/{arxiv_id})' in formatted_text
    
    # Additional metadata assertions
    assert '**Comments:** Test comment' in formatted_text
    assert '**Journal Reference:** Test journal' in formatted_text
    assert '**DOI:** 10.1234/test' in formatted_text