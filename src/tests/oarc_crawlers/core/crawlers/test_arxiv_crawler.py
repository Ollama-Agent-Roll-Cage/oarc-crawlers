import pytest
from unittest.mock import patch, MagicMock
import tempfile
import io
import tarfile
import datetime
import json
from pathlib import Path

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
    
    # Sample arXiv result
    class MockAuthor:
        def __init__(self, name):
            self.name = name
    
    class MockArxivResult:
        def __init__(self):
            self.title = "Test ArXiv Paper"
            self.authors = [MockAuthor("First Author"), MockAuthor("Second Author")]
            self.summary = "This is a test abstract for a paper that doesn't exist."
            self.published = datetime.datetime(2021, 1, 28, 0, 0, 0)
            self.updated = datetime.datetime(2021, 1, 28, 0, 0, 0)
            self.entry_id = f"http://arxiv.org/abs/{arxiv_id}"
            self.pdf_url = f"http://arxiv.org/pdf/{arxiv_id}"
            self.categories = ["cs.AI", "cs.LG"]
            self.comment = "40 pages, 15 figures"
            self.journal_ref = "Journal of Test Science, Vol. 42"
            self.doi = "10.1234/test.5678"
            
        def get_short_id(self):
            return self.entry_id.split('/abs/')[-1]
    
    # Return a dict with all the test data
    test_data = {
        'temp_dir': temp_dir,
        'fetcher': fetcher,
        'arxiv_id': arxiv_id,
        'arxiv_url': arxiv_url,
        'sample_latex': sample_latex,
        'mock_arxiv_result': MockArxivResult()
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
    mock_result = arxiv_setup['mock_arxiv_result']
    
    # Mock the arxiv.Search class
    mock_search = MagicMock()
    mock_search.results.return_value = [mock_result]
    
    # Mock the ParquetStorage methods
    with patch('arxiv.Search', return_value=mock_search), \
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

@pytest.mark.asyncio
async def test_search(arxiv_setup):
    """Test searching for papers on ArXiv."""
    fetcher = arxiv_setup['fetcher']
    mock_result = arxiv_setup['mock_arxiv_result']
    
    # Mock the arxiv.Search class
    mock_search = MagicMock()
    mock_search.results.return_value = [mock_result]
    
    with patch('arxiv.Search', return_value=mock_search), \
         patch('oarc_crawlers.ParquetStorage.save_to_parquet', return_value=None):
        
        # Call the method and properly await it
        search_data = await fetcher.search("test query", 5)
        
        # Assertions
        assert search_data['query'] == "test query"
        assert search_data['limit'] == 5
        assert len(search_data['results']) == 1
        assert search_data['results'][0]['title'] == 'Test ArXiv Paper'

@pytest.mark.asyncio
async def test_extract_references(arxiv_setup):
    """Test extracting references from LaTeX source."""
    fetcher = arxiv_setup['fetcher']
    arxiv_id = arxiv_setup['arxiv_id']
    
    sample_latex = r"""
    \begin{thebibliography}{10}
    \bibitem{Author2021} Author, A. (2021). Title of the paper. Journal, 10(2), 100-120.
    \bibitem{Smith2020} Smith, B., & Jones, C. (2020). Another paper title. Conference Name, 45-50.
    \end{thebibliography}
    """
    
    source_info = {
        'arxiv_id': arxiv_id,
        'latex_content': sample_latex,
        'source_files': {'main.tex': sample_latex}
    }
    
    with patch('oarc_crawlers.core.storage.parquet_storage.ParquetStorage.save_to_parquet', return_value=None):
        result = await fetcher.extract_references(source_info)
        
        assert result['arxiv_id'] == arxiv_id
        assert result['reference_count'] == 2
        assert len(result['references']) == 2
        assert result['references'][0]['key'] == 'Author2021'
        assert "Title of the paper" in result['references'][0]['citation']
        assert result['references'][1]['key'] == 'Smith2020'
        assert "Another paper title" in result['references'][1]['citation']

@pytest.mark.asyncio
async def test_extract_references_bibtex(arxiv_setup):
    """Test extracting BibTeX references."""
    fetcher = arxiv_setup['fetcher']
    arxiv_id = arxiv_setup['arxiv_id']
    
    sample_latex = r"""
    \begin{document}
    Some text with citation \cite{Author2021}.
    
    @article{Author2021,
      title={Title of the paper},
      author={Author, A.},
      journal={Journal},
      volume={10},
      number={2},
      pages={100--120},
      year={2021}
    }
    
    @inproceedings{Smith2020,
      title={Another paper title},
      author={Smith, B. and Jones, C.},
      booktitle={Conference Name},
      pages={45--50},
      year={2020}
    }
    \end{document}
    """
    
    source_info = {
        'arxiv_id': arxiv_id,
        'latex_content': sample_latex,
        'source_files': {'main.tex': sample_latex}
    }
    
    with patch('oarc_crawlers.core.storage.parquet_storage.ParquetStorage.save_to_parquet', return_value=None):
        result = await fetcher.extract_references(source_info)
        
        assert result['arxiv_id'] == arxiv_id
        assert result['reference_count'] == 2
        assert len(result['references']) == 2
        
        # Check first reference
        bibtex_entry = next((ref for ref in result['references'] if ref.get('key') == 'Author2021'), None)
        assert bibtex_entry is not None
        assert bibtex_entry['type'] == 'article'
        assert bibtex_entry['fields']['title'] == 'Title of the paper'
        
        # Check second reference
        bibtex_entry = next((ref for ref in result['references'] if ref.get('key') == 'Smith2020'), None)
        assert bibtex_entry is not None
        assert bibtex_entry['type'] == 'inproceedings'
        assert bibtex_entry['fields']['author'] == 'Smith, B. and Jones, C.'

@pytest.mark.asyncio
@patch('nltk.tokenize.word_tokenize', return_value=['deep', 'learning', 'nlp', 'transformer', 'models', 'attention', 'mechanisms', 'machine', 'translation'])
@patch('nltk.corpus.stopwords.words', return_value=['for', 'in', 'the', 'and', 'to', 'this', 'we', 'a', 'of', 'on', 'is', 'by', 'with', 'as', 'an', 'are', 'that', 'be', 'from'])
async def test_extract_keywords(mock_stopwords, mock_word_tokenize, arxiv_setup):
    """Test extracting keywords from paper abstract."""
    fetcher = arxiv_setup['fetcher']
    
    paper_info = {
        'arxiv_id': '2101.12345',
        'title': 'Deep Learning for Natural Language Processing',
        'abstract': 'This paper presents advances in deep learning approaches for NLP. ' +
                   'We discuss transformer models, attention mechanisms, and their applications ' +
                   'to machine translation, text classification, and question answering tasks.',
        'authors': ['Author A', 'Author B']
    }
    
    # Mock Counter.most_common to return predictable results
    with patch('oarc_crawlers.core.crawlers.arxiv_crawler.Counter') as mock_counter:
        mock_counter_instance = MagicMock()
        mock_counter_instance.most_common.return_value = [
            ('deep learning', 3),
            ('nlp', 2),
            ('transformer models', 2),
            ('attention mechanisms', 1),
            ('machine translation', 1)
        ]
        mock_counter.return_value = mock_counter_instance
        mock_counter_instance.__add__.return_value = mock_counter_instance
        
        with patch('oarc_crawlers.core.storage.parquet_storage.ParquetStorage.save_to_parquet', return_value=None):
            result = await fetcher.extract_keywords(paper_info)
            
            assert result['arxiv_id'] == '2101.12345'
            assert result['title'] == 'Deep Learning for Natural Language Processing'
            assert len(result['keywords']) == 5
            assert result['keywords'][0]['keyword'] == 'deep learning'
            assert result['keywords'][0]['score'] == 3

@pytest.mark.asyncio
async def test_batch_fetch_papers(arxiv_setup):
    """Test batch fetching of papers."""
    fetcher = arxiv_setup['fetcher']
    mock_result = arxiv_setup['mock_arxiv_result']
    
    # Create a list of paper IDs
    paper_ids = ['2101.12345', '2101.12346', '2101.12347']
    
    # Mock the fetch_paper_info method
    async def mock_fetch_info(arxiv_id):
        return {
            'arxiv_id': arxiv_id,
            'title': f'Test Paper {arxiv_id}',
            'authors': ['Author A', 'Author B'],
            'abstract': 'Test abstract'
        }
    
    with patch.object(fetcher, 'fetch_paper_info', side_effect=mock_fetch_info), \
         patch.object(fetcher, 'extract_keywords', return_value={'keywords': ['test']}), \
         patch.object(fetcher, 'download_source', return_value={'latex_content': 'test'}), \
         patch.object(fetcher, 'extract_references', return_value={'references': []}), \
         patch('oarc_crawlers.core.storage.parquet_storage.ParquetStorage.save_to_parquet', return_value=None):
        
        # Call with keyword and reference extraction
        result = await fetcher.batch_fetch_papers(paper_ids, extract_keywords=True, extract_references=True)
        
        # Assertions
        assert len(result['papers']) == 3
        assert result['papers'][0]['arxiv_id'] == '2101.12345'
        assert result['papers'][1]['arxiv_id'] == '2101.12346'
        assert result['papers'][2]['arxiv_id'] == '2101.12347'
        
        # Check that keywords and references were extracted
        assert result['keywords'] is not None
        assert result['references'] is not None

@pytest.mark.asyncio
@patch('arxiv.Search')
async def test_fetch_category_papers(mock_search, arxiv_setup):
    """Test fetching papers by category."""
    fetcher = arxiv_setup['fetcher']
    
    # Create a mock search results
    mock_search_instance = MagicMock()
    mock_search.return_value = mock_search_instance
    
    # Create mock results
    mock_paper1 = MagicMock()
    mock_paper1.entry_id = 'http://arxiv.org/abs/2101.12345'
    mock_paper1.title = 'Test Paper 1'
    mock_paper1.authors = [MagicMock(name='Author A'), MagicMock(name='Author B')]
    mock_paper1.summary = 'Test abstract 1'
    mock_paper1.categories = ['cs.AI', 'cs.LG']
    mock_paper1.published = datetime.datetime(2021, 1, 1)
    mock_paper1.updated = datetime.datetime(2021, 1, 2)
    mock_paper1.pdf_url = 'http://arxiv.org/pdf/2101.12345'
    
    mock_paper2 = MagicMock()
    mock_paper2.entry_id = 'http://arxiv.org/abs/2101.12346'
    mock_paper2.title = 'Test Paper 2'
    mock_paper2.authors = [MagicMock(name='Author C')]
    mock_paper2.summary = 'Test abstract 2'
    mock_paper2.categories = ['cs.AI']
    mock_paper2.published = datetime.datetime(2021, 1, 3)
    mock_paper2.updated = datetime.datetime(2021, 1, 4)
    mock_paper2.pdf_url = 'http://arxiv.org/pdf/2101.12346'
    
    mock_search_instance.results.return_value = [mock_paper1, mock_paper2]
    
    with patch('oarc_crawlers.core.storage.parquet_storage.ParquetStorage.save_to_parquet', return_value=None):
        result = await fetcher.fetch_category_papers('cs.AI', max_results=2)
        
        assert result['category'] == 'cs.AI'
        assert result['papers_count'] == 2
        assert len(result['papers']) == 2
        assert result['papers'][0]['arxiv_id'] == '2101.12345'
        assert result['papers'][1]['arxiv_id'] == '2101.12346'
        
        # Verify the search was called with correct parameters
        mock_search.assert_called_once()
        call_args = mock_search.call_args[1]
        assert call_args['query'] == 'cat:cs.AI'
        assert call_args['max_results'] == 2

@pytest.mark.asyncio
async def test_extract_math_equations(arxiv_setup):
    """Test extracting mathematical equations from LaTeX source."""
    fetcher = arxiv_setup['fetcher']
    arxiv_id = arxiv_setup['arxiv_id']
    
    sample_latex = r"""
    This is a test document with inline math: $E = mc^2$ and $F = ma$.
    
    And display equations:
    \begin{equation}
    y = mx + b
    \end{equation}
    
    \begin{align}
    a &= b + c \\
    &= d + e
    \end{align}
    
    \[ \int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi} \]
    """
    
    source_info = {
        'arxiv_id': arxiv_id,
        'latex_content': sample_latex,
        'source_files': {'main.tex': sample_latex}
    }
    
    with patch('oarc_crawlers.core.storage.parquet_storage.ParquetStorage.save_to_parquet', return_value=None):
        result = await fetcher.extract_math_equations(source_info)
        
        assert result['arxiv_id'] == arxiv_id
        assert result['inline_equation_count'] == 2
        assert result['display_equation_count'] == 3
        
        # Check inline equations
        assert 'E = mc^2' in result['inline_equations']
        assert 'F = ma' in result['inline_equations']
        
        # Check display equations
        assert any('y = mx + b' in eq for eq in result['display_equations'])
        assert any('a &= b + c' in eq for eq in result['display_equations'])
        assert any(r'\int_{-\infty}^{\infty}' in eq for eq in result['display_equations'])