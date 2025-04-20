import unittest
from unittest.mock import patch
import tempfile

from oarc_crawlers import WebCrawler

class MockResponse:
    def __init__(self, status, text):
        self.status = status
        self._text = text
        
    async def text(self):
        return self._text

class TestWebCrawler(unittest.TestCase):
    """Test the BeautifulSoup web crawler module."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.crawler = WebCrawler(data_dir=self.temp_dir.name)
        
        # Sample HTML for testing
        self.sample_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Page</title>
            <meta name="description" content="Test description">
            <meta name="keywords" content="test, page, sample">
        </head>
        <body>
            <div class="content">
                <h1>Test Header</h1>
                <p>This is a test paragraph.</p>
                <ul>
                    <li>Item 1</li>
                    <li>Item 2</li>
                </ul>
                <pre><code class="python">
                def hello_world():
                    print("Hello World")
                </code></pre>
            </div>
            <div class="sidebar">
                <h2>Related Links</h2>
                <ul>
                    <li><a href="https://example.com/1">Link 1</a></li>
                    <li><a href="https://example.com/2">Link 2</a></li>
                </ul>
            </div>
        </body>
        </html>
        """
        
        # PyPI sample HTML
        self.pypi_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>package-name · PyPI</title>
        </head>
        <body>
            <div class="sidebar">
                <div class="sidebar-section">
                    <h3>Project Details</h3>
                    <p>Version: 1.0.0</p>
                    <p>License: MIT</p>
                </div>
                <div class="sidebar-section">
                    <h3>Statistics</h3>
                    <p>Downloads: 5000</p>
                </div>
            </div>
            <div class="project-description">
                <h1>Package Name</h1>
                <p>This is a sample package description.</p>
                <h2>Installation</h2>
                <pre><code>pip install package-name</code></pre>
                <h2>Usage</h2>
                <p>Here's how to use the package:</p>
                <pre><code class="python">
                import package_name
                package_name.do_something()
                </code></pre>
            </div>
        </body>
        </html>
        """
        
        # Documentation site sample HTML
        self.docs_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Documentation Site</title>
            <meta name="author" content="Test Author">
            <meta name="version" content="1.0">
        </head>
        <body>
            <div class="toc">
                <ul>
                    <li><a href="#intro">Introduction</a></li>
                    <li><a href="#usage">Usage</a></li>
                </ul>
            </div>
            <div class="section">
                <h1 id="intro">Introduction</h1>
                <p>This is an introduction to the library.</p>
                <h2 id="usage">Usage</h2>
                <p>Here's how to use the library:</p>
                <div class="highlight">
                <pre><code class="python">
                import library
                result = library.process()
                print(result)
                </code></pre>
                </div>
            </div>
            <p class="last-updated">Last updated: 2025-04-10</p>
        </body>
        </html>
        """
    
    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()
    
    @patch('aiohttp.ClientSession.get')
    @patch('oarc_crawlers.beautiful_soup.ParquetStorage')
    async def test_fetch_url_content(self, mock_storage, mock_get):
        """Test fetching URL content."""
        # Set self.fetch_url_content to BSWebCrawler.fetch_url_content
        # because it's a method that requires the class instance
        WebCrawler.fetch_url_content = WebCrawler.fetch_url_content.__get__(self.crawler)
        
        # Setup mock response
        mock_resp = MockResponse(200, self.sample_html)
        mock_get.return_value.__aenter__.return_value = mock_resp
        
        # Call the method
        with patch('pathlib.Path.mkdir'):
            result = await WebCrawler.fetch_url_content("https://example.com")
        
        # Assertions
        mock_get.assert_called_once_with("https://example.com", headers=unittest.mock.ANY)
        mock_storage.save_to_parquet.assert_called_once()
        self.assertEqual(result, self.sample_html)
    
    async def test_extract_text_from_html(self):
        """Test extracting text from HTML."""
        result = await WebCrawler.extract_text_from_html(self.sample_html)
        
        # Assertions
        self.assertIn("Test Header", result)
        self.assertIn("This is a test paragraph", result)
        self.assertIn("Item 1", result)
        self.assertIn("Item 2", result)
        
        # Check that script tags are removed
        sample_with_script = """
        <html>
        <head><script>alert('Test')</script></head>
        <body><p>Content</p></body>
        </html>
        """
        result = await WebCrawler.extract_text_from_html(sample_with_script)
        self.assertNotIn("alert", result)
        self.assertIn("Content", result)
    
    async def test_extract_pypi_content(self):
        """Test extracting PyPI content."""
        result = await WebCrawler.extract_pypi_content(self.pypi_html, "package-name")
        
        # Assertions
        self.assertEqual(result['name'], "package-name")
        self.assertIn('Project Details', result['metadata'])
        self.assertIn('Statistics', result['metadata'])
        self.assertIn('Version: 1.0.0', result['metadata']['Project Details'])
        self.assertIn('Downloads: 5000', result['metadata']['Statistics'])
        
        # Check documentation content
        self.assertIn("# Package Name", result['documentation'])
        self.assertIn("## Installation", result['documentation'])
        self.assertIn("## Usage", result['documentation'])
        self.assertIn("```", result['documentation'])
        self.assertIn("import package_name", result['documentation'])
    
    async def test_extract_documentation_content(self):
        """Test extracting documentation content."""
        result = await WebCrawler.extract_documentation_content(self.docs_html, "https://docs.example.com")
        
        # Assertions
        self.assertEqual(result['url'], "https://docs.example.com")
        self.assertEqual(result['title'], "Documentation Site")
        
        # Check metadata
        self.assertEqual(result['metadata']['author'], "Test Author")
        self.assertEqual(result['metadata']['version'], "1.0")
        self.assertEqual(result['metadata']['last_updated'], "Last updated: 2025-04-10")
        
        # Check TOC
        self.assertEqual(len(result['toc']), 2)
        self.assertEqual(result['toc'][0]['title'], "Introduction")
        self.assertEqual(result['toc'][0]['url'], "#intro")
        self.assertEqual(result['toc'][1]['title'], "Usage")
        
        # Check content
        self.assertIn("# Introduction", result['content'])
        self.assertIn("This is an introduction to the library.", result['content'])
        self.assertIn("## Usage", result['content'])
        
        # Check code snippets
        self.assertEqual(len(result['code_snippets']), 1)
        self.assertEqual(result['code_snippets'][0]['language'], "python")
        self.assertIn("import library", result['code_snippets'][0]['code'])
    
    @patch('oarc_crawlers.beautiful_soup.BSWebCrawler.fetch_url_content')
    @patch('oarc_crawlers.beautiful_soup.BSWebCrawler.extract_documentation_content')
    @patch('oarc_crawlers.beautiful_soup.BSWebCrawler.format_documentation')
    @patch('oarc_crawlers.beautiful_soup.ParquetStorage')
    async def test_crawl_documentation_site(self, mock_storage, mock_format, mock_extract, mock_fetch):
        """Test crawling a documentation site."""
        # Setup mocks
        mock_fetch.return_value = self.docs_html
        mock_extract.return_value = {
            'url': 'https://docs.example.com',
            'title': 'Test Doc',
            'content': 'Test content',
            'metadata': {'version': '1.0'}
        }
        mock_format.return_value = "# Test Doc\n\nTest content"
        
        # Call the method
        result = await self.crawler.crawl_documentation_site("https://docs.example.com")
        
        # Assertions
        mock_fetch.assert_called_once_with("https://docs.example.com")
        mock_extract.assert_called_once_with(self.docs_html, "https://docs.example.com")
        mock_format.assert_called_once()
        mock_storage.save_to_parquet.assert_called_once()
        self.assertEqual(result, "# Test Doc\n\nTest content")
    
    async def test_format_documentation(self):
        """Test formatting documentation data."""
        # Create test data
        doc_data = {
            'title': 'Test Documentation',
            'metadata': {
                'version': '1.0',
                'author': 'Test Author',
                'last_updated': '2025-04-10'
            },
            'toc': [
                {'title': 'Section 1', 'url': '#section1'},
                {'title': 'Section 2', 'url': '#section2'}
            ],
            'content': '# Section 1\nContent for section 1\n\n# Section 2\nContent for section 2',
            'code_snippets': [
                {'language': 'python', 'code': 'print("Hello World")'},
                {'language': 'javascript', 'code': 'console.log("Hello World")'}
            ],
            'url': 'https://docs.example.com'
        }
        
        result = await WebCrawler.format_documentation(doc_data)
        
        # Assertions
        self.assertIn("# Test Documentation", result)
        self.assertIn("- **Version**: 1.0", result)
        self.assertIn("- **Author**: Test Author", result)
        self.assertIn("- **Last_updated**: 2025-04-10", result)
        self.assertIn("- [Section 1](#section1)", result)
        self.assertIn("- [Section 2](#section2)", result)
        self.assertIn("Content for section 1", result)
        self.assertIn("Content for section 2", result)
        self.assertIn("### Example 1", result)
        self.assertIn("```python\nprint(\"Hello World\")", result)
        self.assertIn("### Example 2", result)
        self.assertIn("```javascript\nconsole.log(\"Hello World\")", result)
        self.assertIn("[View original documentation](https://docs.example.com)", result)
    
    async def test_format_pypi_info(self):
        """Test formatting PyPI data."""
        # Create test data
        package_data = {
            'info': {
                'name': 'test-package',
                'version': '1.2.3',
                'summary': 'A test package',
                'description': 'This is a longer description of the test package.',
                'author': 'Test Author',
                'author_email': 'author@example.com',
                'license': 'MIT',
                'home_page': 'https://example.com',
                'project_urls': {
                    'Documentation': 'https://docs.example.com',
                    'Source': 'https://github.com/example/test-package'
                },
                'requires_dist': [
                    'requests>=2.0.0',
                    'numpy>=1.0.0'
                ]
            }
        }
        
        result = await WebCrawler.format_pypi_info(package_data)
        
        # Assertions
        self.assertIn("# test-package v1.2.3", result)
        self.assertIn("## Summary\nA test package", result)
        self.assertIn("**Author**: Test Author (author@example.com)", result)
        self.assertIn("**License**: MIT", result)
        self.assertIn("**Homepage**: https://example.com", result)
        self.assertIn("- **Documentation**: https://docs.example.com", result)
        self.assertIn("- **Source**: https://github.com/example/test-package", result)
        self.assertIn("- requests>=2.0.0", result)
        self.assertIn("- numpy>=1.0.0", result)
        self.assertIn("```\npip install test-package\n```", result)
        self.assertIn("This is a longer description of the test package.", result)

if __name__ == '__main__':
    unittest.main()