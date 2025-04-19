"""
GitHub Crawler Module

This module provides the GitHubCrawler class, which enables cloning GitHub repositories,
extracting their file contents and metadata, and storing the results in a structured format
(e.g., Parquet). It also supports querying repository content, generating summaries, and
finding similar code snippets within repositories.

Features:
- Clone GitHub repositories and process their files.
- Extract file metadata (language, size, author, last modified, etc.).
- Store repository data in Parquet format for efficient querying.
- Query repository content using natural language or structured queries.
- Generate repository summaries and language statistics.
- Find similar code snippets within a repository.

Typical usage:
    crawler = GitHubCrawler(data_dir="path/to/data")
    await crawler.clone_and_store_repo("https://github.com/owner/repo")
    summary = await crawler.get_repo_summary("https://github.com/owner/repo")
"""
import os
import re
import glob
import git
import shutil
import tempfile
from pathlib import Path
from datetime import datetime, UTC
from typing import Optional, Tuple

import pandas as pd

from ..storage.parquet_storage import ParquetStorage
from oarc_crawlers.utils.log import log
from oarc_crawlers.utils.paths import Paths
from oarc_crawlers.utils.errors import (
    ResourceNotFoundError, 
    NetworkError,
    DataExtractionError
)

class GHCrawler:
    """Class for crawling and extracting content from GitHub repositories."""

    def __init__(self, data_dir=None):
        """Initialize the GitHub Crawler.
        
        Args:
            data_dir (str, optional): Directory to store data.
        """
        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            self.data_dir = Paths.get_default_data_dir()
            
        self.github_data_dir = Paths.ensure_path(self.data_dir / "github_repos")
        log.debug(f"Initialized GitHubCrawler with data directory: {self.data_dir}")

    @staticmethod
    def extract_repo_info_from_url(url: str) -> Tuple[str, str, str]:
        """Extract repository owner and name from GitHub URL.
        
        Args:
            url (str): GitHub repository URL
            
        Returns:
            Tuple[str, str, str]: Repository owner, name, and branch (if available)
            
        Raises:
            ResourceNotFoundError: If URL is not a valid GitHub repository URL
        """
        # Handle different GitHub URL formats
        
        # TODO move to crawler_utils.py
        
        github_patterns = [
            r'github\.com[:/]([^/]+)/([^/]+)(?:/tree/([^/]+))?',  # Standard GitHub URL or git URL
            r'github\.com/([^/]+)/([^/\.]+)(?:\.git)?'  # GitHub URL with or without .git
        ]
        
        for pattern in github_patterns:
            match = re.search(pattern, url)
            if match:
                owner = match.group(1)
                repo_name = match.group(2)
                # Remove .git if it exists in the repo name
                repo_name = repo_name.replace('.git', '')
                
                # Extract branch if it exists (group 3)
                branch = match.group(3) if len(match.groups()) > 2 and match.group(3) else "main"
                return owner, repo_name, branch
                
        raise ResourceNotFoundError(f"Invalid GitHub repository URL: {url}")

    def get_repo_dir_path(self, owner: str, repo_name: str) -> Path:
        """Get the directory path for storing repository data.
        
        Args:
            owner (str): Repository owner
            repo_name (str): Repository name
            
        Returns:
            Path: Directory path
        """
        return self.github_data_dir / f"{owner}_{repo_name}"

    async def clone_repo(self, repo_url: str, temp_dir: Optional[str] = None) -> Path:
        """Clone a GitHub repository to a temporary directory.
        
        Args:
            repo_url (str): GitHub repository URL
            temp_dir (str, optional): Temporary directory path. If None, creates one.
            
        Returns:
            Path: Path to the cloned repository
            
        Raises:
            NetworkError: If cloning fails
        """
        owner, repo_name, branch = self.extract_repo_info_from_url(repo_url)
        
        # Create a temporary directory if not provided
        if temp_dir is None:
            temp_dir = tempfile.mkdtemp(prefix=f"github_repo_{owner}_{repo_name}_")
        else:
            temp_dir = Path(temp_dir)
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Clone the repository
        log.debug(f"Cloning repository {repo_url} to {temp_dir}")
        
        try:
            repo = git.Repo.clone_from(repo_url, temp_dir)
            
            # Checkout the specified branch if not the default
            if branch != "main" and branch != "master":
                try:
                    repo.git.checkout(branch)
                except git.exc.GitCommandError:
                    log.debug(f"Branch {branch} not found, staying on default branch")
        except git.exc.GitCommandError as e:
            raise NetworkError(f"Error cloning repository {repo_url}: {str(e)}")
        except Exception as e:
            raise NetworkError(f"Error cloning repository {repo_url}: {str(e)}")
            
        return Path(temp_dir)

    def is_binary_file(self, file_path: str) -> bool:
        """Check if a file is binary.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            bool: True if file is binary, False otherwise
        """
        # File extensions to exclude
        
        # TODO move this to the config.py or const.py
        
        binary_extensions = {
            '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.webp',
            '.zip', '.tar', '.gz', '.rar', '.7z',
            '.exe', '.dll', '.so', '.dylib',
            '.pyc', '.pyd', '.pyo',
            '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pdf',
            '.mp3', '.mp4', '.wav', '.avi', '.mov', '.mkv',
            '.ttf', '.otf', '.woff', '.woff2'
        }
        
        _, ext = os.path.splitext(file_path.lower())
        if ext in binary_extensions:
            return True
            
        # Check file contents
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\0' in chunk  # Binary files typically contain null bytes
        except Exception:
            return True  # If we can't read it, treat as binary

    async def process_repo_to_dataframe(self, repo_path: Path, max_file_size_kb: int = 500) -> pd.DataFrame:
        """Process repository files and convert to DataFrame.
        
        Args:
            repo_path (Path): Path to cloned repository
            max_file_size_kb (int): Maximum file size in KB to process
            
        Returns:
            pd.DataFrame: DataFrame containing file information
            
        Raises:
            DataExtractionError: If processing fails
        """
        data = []
        max_file_size = max_file_size_kb * 1024  # Convert to bytes
        log.debug(f"Processing repository at {repo_path} (max file size: {max_file_size_kb} KB)")
        
        # Get git repository object for metadata
        try:
            repo = git.Repo(repo_path)
        except git.exc.InvalidGitRepositoryError:
            log.debug("Not a valid git repo, processing without git metadata")
            repo = None
        
        # Process each file
        file_count = 0
        binary_count = 0
        error_count = 0
        
        for file_path in glob.glob(str(repo_path / '**' / '*'), recursive=True):
            file_path = Path(file_path)
            
            # Skip directories
            if file_path.is_dir():
                continue
                
            # Skip binary files and check file size
            if self.is_binary_file(str(file_path)):
                binary_count += 1
                continue
                
            if file_path.stat().st_size > max_file_size:
                log.debug(f"Skipping large file: {file_path.name} ({file_path.stat().st_size / 1024:.1f} KB)")
                continue
            
            # Skip .git files
            if '.git' in str(file_path):
                continue
                
            try:
                # Get relative path
                rel_path = str(file_path.relative_to(repo_path))
                
                # Get file content
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Get file metadata
                file_ext = file_path.suffix
                
                # Get language from extension
                language = self.get_language_from_extension(file_ext)
                
                # Get file metadata using git if available
                last_modified = None
                author = None
                
                if repo:
                    try:
                        # Try to get git blame information
                        for commit, lines in repo.git.blame('--incremental', str(rel_path)).items():
                            author = lines.split('author ')[1].split('\n')[0]
                            last_modified = lines.split('author-time ')[1].split('\n')[0]
                            break  # Just get the first author
                    except git.exc.GitCommandError:
                        # If blame fails, use file modification time
                        last_modified = datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                else:
                    last_modified = datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                
                # Add to data
                data.append({
                    'file_path': rel_path,
                    'content': content,
                    'language': language,
                    'extension': file_ext,
                    'size_bytes': file_path.stat().st_size,
                    'last_modified': last_modified,
                    'author': author,
                    'line_count': len(content.splitlines()),
                    'timestamp': datetime.now(UTC).isoformat()
                })
                
                file_count += 1
                
            except Exception as e:
                error_count += 1
                log.debug(f"Error processing file {file_path}: {str(e)}")
                continue
        
        log.debug(f"Repository processing complete: {file_count} files processed, {binary_count} binary files skipped, {error_count} errors")
        
        if not data:
            raise DataExtractionError(f"No readable files found in repository at {repo_path}")
            
        return pd.DataFrame(data)

    @staticmethod
    def get_language_from_extension(extension: str) -> str:
        """Get programming language name from file extension.
        
        Args:
            extension (str): File extension with leading dot
            
        Returns:
            str: Language name or 'Unknown'
        """

        # TODO move this to the config.py or const.py

        ext_to_lang = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'React',
            '.tsx': 'React TypeScript',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.java': 'Java',
            '.c': 'C',
            '.cpp': 'C++',
            '.cs': 'C#',
            '.go': 'Go',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.rs': 'Rust',
            '.sh': 'Shell',
            '.md': 'Markdown',
            '.json': 'JSON',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.xml': 'XML',
            '.sql': 'SQL',
            '.r': 'R',
            '.m': 'Objective-C',
            '.dart': 'Dart',
            '.lua': 'Lua',
            '.pl': 'Perl',
            '.toml': 'TOML',
            '.ipynb': 'Jupyter Notebook'
        }
        
        return ext_to_lang.get(extension.lower(), 'Unknown')

    async def clone_and_store_repo(self, repo_url: str) -> str:
        """Clone a GitHub repository and store its data in Parquet format.
        
        Args:
            repo_url (str): GitHub repository URL
            
        Returns:
            str: Path to the Parquet file containing repository data
            
        Raises:
            NetworkError: If cloning fails
            DataExtractionError: If processing fails
        """
        # Extract repo information
        owner, repo_name, _ = self.extract_repo_info_from_url(repo_url)
        repo_dir = self.get_repo_dir_path(owner, repo_name)
        log.debug(f"Cloning and storing repository: {owner}/{repo_name}")
        
        # Create a temporary directory for cloning
        temp_dir = tempfile.mkdtemp(prefix=f"github_repo_{owner}_{repo_name}_")
        
        try:
            # Clone the repository
            cloned_path = await self.clone_repo(repo_url, temp_dir)
            
            # Process repository to DataFrame
            df = await self.process_repo_to_dataframe(cloned_path)
            
            # Save to Parquet
            parquet_path = f"{self.github_data_dir}/{owner}_{repo_name}.parquet"
            ParquetStorage.save_to_parquet(df, parquet_path)
            
            log.debug(f"Successfully stored repository {repo_url} to {parquet_path}")
            return parquet_path
            
        finally:
            # Clean up temporary directory
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                log.debug(f"Removed temporary directory: {temp_dir}")

    async def query_repo_content(self, repo_url: str, query: str) -> str:
        """Query repository content using natural language.
        
        Args:
            repo_url (str): GitHub repository URL
            query (str): Natural language query about the repository
            
        Returns:
            str: Query result formatted as markdown
            
        Raises:
            ResourceNotFoundError: If repository data isn't found
            DataExtractionError: If querying fails
        """
        # Extract repo information
        owner, repo_name, _ = self.extract_repo_info_from_url(repo_url)
        log.debug(f"Querying repository: {owner}/{repo_name} with query: {query}")
        
        # Check if repository data exists
        parquet_path = f"{self.github_data_dir}/{owner}_{repo_name}.parquet"
        
        if not os.path.exists(parquet_path):
            log.debug(f"Repository data not found, cloning first")
            # Clone and store repository if not already done
            parquet_path = await self.clone_and_store_repo(repo_url)
        
        # Load repository data
        df = ParquetStorage.load_from_parquet(parquet_path)
        log.debug(f"Loaded repository data: {len(df)} files")
        
        from llama_index.experimental.query_engine import PandasQueryEngine
        log.debug("Using PandasQueryEngine for advanced querying")
        
        # Execute query
        result = await PandasQueryEngine.execute_query(df, query)
        
        if result["success"]:

            # TODO move to a separate templates script

            response = f"""# GitHub Repository Query Results
Repository: {owner}/{repo_name}
Query: `{query}`

{result["result"]}

"""
            # Add summary if we have a count
            if "count" in result:
                response += f"Found {result['count']} matching results."
        else:
            response = f"""# Query Error
Sorry, I couldn't process that query: {result["error"]}

Try queries like:
- "find all Python files"
- "count files by language"
- "find functions related to authentication"
- "show the largest files in the repository"
"""
        
        return response

    async def get_repo_summary(self, repo_url: str) -> str:
        """Get a summary of the repository.
        
        Args:
            repo_url (str): GitHub repository URL
            
        Returns:
            str: Repository summary formatted as markdown
            
        Raises:
            ResourceNotFoundError: If repository data isn't found
            DataExtractionError: If processing fails
        """
        # Extract repo information
        owner, repo_name, _ = self.extract_repo_info_from_url(repo_url)
        log.debug(f"Creating summary for repository: {owner}/{repo_name}")
        
        # Check if repository data exists
        parquet_path = f"{self.github_data_dir}/{owner}_{repo_name}.parquet"
        
        if not os.path.exists(parquet_path):
            log.debug(f"Repository data not found, cloning first")
            # Clone and store repository if not already done
            parquet_path = await self.clone_and_store_repo(repo_url)
        
        # Load repository data
        df = ParquetStorage.load_from_parquet(parquet_path)
        log.debug(f"Loaded repository data: {len(df)} files")
        
        # Generate summary statistics
        total_files = len(df)
        total_lines = df['line_count'].sum()
        
        # Language distribution
        lang_counts = df['language'].value_counts().to_dict()
        
        # Format repository summary

        # TODO move to a separate templates script

        summary = f"""# GitHub Repository Summary: {owner}/{repo_name}

## Statistics
- **Total Files:** {total_files}
- **Total Lines of Code:** {total_lines:,}
- **Repository URL:** {repo_url}

## Language Distribution
"""
        
        for lang, count in lang_counts.items():
            percentage = (count / total_files) * 100
            summary += f"- **{lang}:** {count} files ({percentage:.1f}%)\n"
        
        # List main directories
        main_dirs = set()
        for path in df['file_path']:
            parts = path.split('/')
            if len(parts) > 1:
                main_dirs.add(parts[0])
                
        summary += "\n## Main Directories\n"
        for directory in sorted(main_dirs):
            summary += f"- {directory}/\n"
        
        # Include README if available
        readme_row = df[df['file_path'].str.lower().str.contains('readme.md')].head(1)
        if not readme_row.empty:
            readme_content = readme_row.iloc[0]['content']
            summary += "\n## README Preview\n"
            
            # Limit README preview to first 500 characters
            if len(readme_content) > 500:
                summary += readme_content[:500] + "...\n"
            else:
                summary += readme_content + "\n"
        
        log.debug("Repository summary created successfully")
        return summary

    async def find_similar_code(self, repo_url: str, code_snippet: str) -> str:
        """Find similar code in the repository.
        
        Args:
            repo_url (str): GitHub repository URL
            code_snippet (str): Code snippet to find similar code for
            
        Returns:
            str: Similar code findings formatted as markdown
            
        Raises:
            ResourceNotFoundError: If repository data isn't found
            DataExtractionError: If processing fails
        """
        # Extract repo information
        owner, repo_name, _ = self.extract_repo_info_from_url(repo_url)
        log.debug(f"Finding similar code in repository: {owner}/{repo_name}")
        
        # Check if repository data exists
        parquet_path = f"{self.github_data_dir}/{owner}_{repo_name}.parquet"
        
        if not os.path.exists(parquet_path):
            log.debug(f"Repository data not found, cloning first")
            # Clone and store repository if not already done
            parquet_path = await self.clone_and_store_repo(repo_url)
        
        # Load repository data
        df = ParquetStorage.load_from_parquet(parquet_path)
        log.debug(f"Loaded repository data: {len(df)} files")
        
        # Detect language from code snippet (basic detection)
        lang = "Unknown"
        if "def " in code_snippet and ":" in code_snippet:
            lang = "Python"
        elif "function" in code_snippet and "{" in code_snippet:
            lang = "JavaScript"
        elif "class" in code_snippet and "{" in code_snippet:
            lang = "Java"
        
        log.debug(f"Detected language for code snippet: {lang}")
        
        # Filter by language if detected
        if lang != "Unknown":
            df = df[df['language'] == lang]
            log.debug(f"Filtered to {len(df)} {lang} files")
        
        # Simple similarity function
        def simple_similarity(content):
            # Count how many non-trivial lines from code_snippet appear in content
            snippet_lines = set(line.strip() for line in code_snippet.splitlines() if len(line.strip()) > 10)
            if not snippet_lines:
                return 0
                
            content_lines = content.splitlines()
            matches = sum(1 for line in snippet_lines if any(line in c_line for c_line in content_lines))
            return matches / len(snippet_lines) if snippet_lines else 0
        
        # Calculate similarity
        df['similarity'] = df['content'].apply(simple_similarity)
        
        # Filter files with at least some similarity
        similar_files = df[df['similarity'] > 0.1].sort_values('similarity', ascending=False)
        log.debug(f"Found {len(similar_files)} files with similarity > 0.1")
        
        if len(similar_files) == 0:
            return "No similar code found in the repository."
            
        # Format results

        # TODO move to a separate templates script

        results = f"""# Similar Code Findings

Found {len(similar_files)} files with potentially similar code:

"""
        for idx, row in similar_files.head(5).iterrows():
            similarity_percent = row['similarity'] * 100
            results += f"## {row['file_path']} ({similarity_percent:.1f}% similarity)\n\n"
            
            # Extract a relevant portion of the content
            content_lines = row['content'].splitlines()
            best_section = ""
            max_matches = 0
            
            for i in range(0, len(content_lines), 10):
                section = '\n'.join(content_lines[i:i+20])
                snippet_lines = set(line.strip() for line in code_snippet.splitlines() if len(line.strip()) > 10)
                matches = sum(1 for line in snippet_lines if any(line in c_line for c_line in section.splitlines()))
                
                if matches > max_matches:
                    max_matches = matches
                    best_section = section
            
            # Display the best matching section
            if best_section:
                results += f"```{row['language'].lower()}\n{best_section}\n```\n\n"
        
        return results


