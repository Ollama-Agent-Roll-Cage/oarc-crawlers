"""
GitHub Crawler Module

This module provides the GitHubCrawler class, which enables analyzing GitHub repositories,
extracting their file contents and metadata, and storing the results in a structured format
(e.g., Parquet). It also supports querying repository content, generating summaries, and
finding similar code snippets within repositories.

Features:
- Access GitHub repositories via API without requiring Git installation
- Extract file metadata (language, size, author, last modified, etc.)
- Store repository data in Parquet format for efficient querying
- Query repository content using natural language or structured queries
- Generate repository summaries and language statistics
- Find similar code snippets within a repository

Typical usage:
    crawler = GHCrawler(data_dir="path/to/data")
    await crawler.clone_and_store_repo("https://github.com/owner/repo")
    summary = await crawler.get_repo_summary("https://github.com/owner/repo")
"""

import base64
import os
import re
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import git
import pandas as pd
from github import Github, Repository
from github.GithubException import RateLimitExceededException, UnknownObjectException

from oarc_log import log
from oarc_utils.errors import AuthenticationError, DataExtractionError, NetworkError, ResourceNotFoundError

from oarc_crawlers.config.config import Config
from oarc_crawlers.core.storage.parquet_storage import ParquetStorage
from oarc_crawlers.utils.const import GITHUB_BINARY_EXTENSIONS
from oarc_crawlers.utils.crawler_utils import CrawlerUtils
from oarc_crawlers.utils.paths import Paths


class GHCrawler:
    """Class for crawling and extracting content from GitHub repositories."""

    def __init__(self, data_dir: Optional[str] = None, token: Optional[str] = None):
        """Initialize the GitHub Crawler.
        
        Args:
            data_dir (str, optional): Directory to store data. Defaults to Config's data_dir.
            token (str, optional): GitHub API token for authenticated requests.
        """
        # Use the global config if no data_dir provided
        if data_dir is None:
            data_dir = str(Config.get_instance().data_dir)
        self.data_dir = data_dir

        # Initialize GitHub API client
        # First check explicit token, then config, then environment
        config = Config.get_instance()
        self.token = token or config.github_token or os.environ.get('GITHUB_TOKEN')
        self.github = Github(self.token) if self.token else Github()

        # Use the Paths utility for standardized path handling
        self.github_data_dir = Paths.github_repos_dir(self.data_dir)
        log.debug(f"Initialized GHCrawler with data directory: {self.data_dir}")
        log.debug(f"API authenticated: {'Yes' if self.token else 'No'}")

        # Flag to determine if Git is installed - checked lazily on first clone_repo call
        self._git_available = None

    @staticmethod
    def extract_repo_info_from_url(url: str) -> Tuple[str, str, str]:
        """Extract repository owner and name from GitHub URL.
        
        Args:
            url (str): GitHub repository URL
            
        Returns:
            Tuple[str, str, str]: Repository owner, name, and branch (if available)
            
        Raises:
            ValueError: If URL is not a valid GitHub repository URL
        """
        github_patterns = [
            r'github\.com[:/]([^/]+)/([^/]+)(?:/tree/([^/]+))?',    # Standard GitHub URL or git URL
            r'github\.com/([^/]+)/([^/\.]+)(?:\.git)?'              # GitHub URL with or without .git
        ]
        
        for pattern in github_patterns:
            match = re.search(pattern, url)
            if match:
                owner = match.group(1)
                repo_name = match.group(2)
                repo_name = repo_name.replace('.git', '')
                branch = match.group(3) if len(match.groups()) > 2 and match.group(3) else "main"
                return owner, repo_name, branch
                
        raise ValueError(f"Invalid GitHub repository URL: {url}")

    def get_repo_dir_path(self, owner: str, repo_name: str) -> Path:
        """Get the directory path for storing repository data.
        
        Args:
            owner (str): Repository owner
            repo_name (str): Repository name
            
        Returns:
            Path: Directory path
        """
        return self.github_data_dir / f"{owner}_{repo_name}"

    def _check_git_available(self) -> bool:
        """Check if Git is installed and available.
        
        Returns:
            bool: True if Git is available, False otherwise
        """
        if self._git_available is not None:
            return self._git_available
            
        try:
            import git
            # Test git by running a simple command
            git.cmd.Git().version()
            self._git_available = True
            log.debug("Git is available for repository operations")
            return True
        except (ImportError, git.GitCommandError):
            self._git_available = False
            log.debug("Git is not available - operations requiring Git will raise errors")
            return False

    async def get_repo(self, owner: str, repo_name: str, branch: Optional[str] = None) -> Repository.Repository:
        """Get a repository from GitHub API.
        
        Args:
            owner: Repository owner
            repo_name: Repository name
            branch: Specific branch (optional)
            
        Returns:
            Repository object from PyGitHub
            
        Raises:
            ResourceNotFoundError: If repo doesn't exist
            NetworkError: For GitHub API issues
            AuthenticationError: If API credentials are invalid
        """
        try:
            repo = self.github.get_repo(f"{owner}/{repo_name}")
            log.debug(f"Successfully accessed repository: {owner}/{repo_name}")
            return repo
        except UnknownObjectException:
            raise ResourceNotFoundError(f"Repository {owner}/{repo_name} not found")
        except RateLimitExceededException:
            rate_info = self.github.get_rate_limit().core
            reset_time = rate_info.reset.strftime("%Y-%m-%d %H:%M:%S")
            msg = f"GitHub API rate limit exceeded. Resets at {reset_time}."
            if not self.token:
                msg += " Consider using a GitHub token for higher rate limits."
            raise NetworkError(msg)
        except Exception as e:
            if "Bad credentials" in str(e):
                raise AuthenticationError(f"Invalid GitHub credentials: {str(e)}")
            raise NetworkError(f"Error accessing GitHub repository: {str(e)}")

    async def is_binary_file(self, file_path: str, content: Optional[str] = None) -> bool:
        """Check if a file is binary based on extension and content.
        
        Args:
            file_path: Path to the file
            content: File content (optional)
            
        Returns:
            bool: True if file is binary, False otherwise
        """
        # Check extension first
        _, ext = os.path.splitext(file_path.lower())
        if ext in GITHUB_BINARY_EXTENSIONS:
            return True
            
        # If content is provided, check for null bytes
        if content:
            try:
                # If this isn't valid UTF-8 text, it's likely binary
                content.encode('utf-8').decode('utf-8')
                return '\0' in content  # Check for null bytes
            except UnicodeError:
                return True
        # If content is None but file exists, read and check the file
        elif os.path.exists(file_path):
            try:
                with open(file_path, 'rb') as f:
                    chunk = f.read(1024)  # Read first 1KB
                    return b'\0' in chunk  # Binary files typically contain null bytes
            except Exception:
                return True  # If we can't read the file, assume it's binary
        
        # Default for files with code extensions
        if ext in ('.py', '.js', '.html', '.css', '.md', '.txt', '.json'):
            return False
            
        # Default assumption for unknown extensions
        return False

    async def get_file_content(self, repo: Repository.Repository, path: str, 
                               ref: Optional[str] = None) -> Dict[str, Any]:
        """Get content of a file from GitHub API.
        
        Args:
            repo: Repository object
            path: File path within repository
            ref: Reference (branch, tag, commit) to get content from
            
        Returns:
            Dict containing file content and metadata
            
        Raises:
            ResourceNotFoundError: If file doesn't exist
            NetworkError: For GitHub API issues
        """
        try:
            file_content = repo.get_contents(path, ref=ref)
            
            if isinstance(file_content, list):
                # This is a directory, not a file
                return {
                    'is_dir': True,
                    'path': path,
                    'content': None,
                    'size': 0,
                    'type': 'dir',
                }
            
            if hasattr(file_content, 'content'):
                try:
                    decoded_content = base64.b64decode(file_content.content).decode('utf-8')
                    is_binary = await self.is_binary_file(path, decoded_content)
                    
                    if is_binary:
                        return {
                            'is_binary': True,
                            'path': path,
                            'size': file_content.size,
                            'type': 'binary',
                        }
                    else:
                        return {
                            'is_binary': False,
                            'path': path,
                            'content': decoded_content,
                            'size': file_content.size,
                            'type': 'text',
                        }
                except UnicodeDecodeError:
                    # Binary file that couldn't be decoded as UTF-8
                    return {
                        'is_binary': True,
                        'path': path,
                        'size': file_content.size,
                        'type': 'binary',
                    }
            
            return {
                'is_binary': False,
                'path': path,
                'content': None, 
                'size': 0,
                'type': 'unknown',
            }
            
        except UnknownObjectException:
            raise ResourceNotFoundError(f"File {path} not found in repository")
        except RateLimitExceededException:
            reset_time = self.github.get_rate_limit().core.reset.strftime("%Y-%m-%d %H:%M:%S")
            raise NetworkError(f"GitHub API rate limit exceeded. Resets at {reset_time}")
        except Exception as e:
            raise NetworkError(f"Error accessing file {path}: {str(e)}")

    async def get_repo_contents(self, repo: Repository.Repository, 
                               path: str = "", ref: Optional[str] = None) -> List[Dict]:
        """Recursively get all contents of a repository.
        
        Args:
            repo: Repository object
            path: Current path within repository ('' for root)
            ref: Reference (branch, tag, commit) to get content from
            
        Returns:
            List of dictionaries with file metadata
            
        Raises:
            NetworkError: For GitHub API issues
        """
        log.debug(f"Getting contents for path: {path or 'root'}")
        files_data = []
        
        try:
            contents = repo.get_contents(path, ref=ref)
            
            # Handle case where contents is a single file
            if not isinstance(contents, list):
                contents = [contents]
                
            for content in contents:
                if content.type == "dir":
                    # Recursively process directory
                    dir_content = await self.get_repo_contents(repo, content.path, ref)
                    files_data.extend(dir_content)
                else:
                    # Get file content
                    try:
                        file_data = await self.get_file_content(repo, content.path, ref)
                        if file_data['is_binary'] == False and file_data.get('content'):
                            # It's a text file with content
                            ext = os.path.splitext(content.path)[1]
                            lang = CrawlerUtils.get_language_from_extension(ext)
                            line_count = len(file_data['content'].splitlines())
                            
                            files_data.append({
                                'file_path': content.path,
                                'content': file_data['content'],
                                'language': lang,
                                'extension': ext,
                                'size_bytes': content.size,
                                'line_count': line_count,
                                'last_modified': None,  # API doesn't provide this directly
                                'author': None,  # Would need git history for this
                                'timestamp': datetime.now(UTC).isoformat()
                            })
                    except (ResourceNotFoundError, NetworkError) as e:
                        # Log but don't stop processing other files
                        log.warning(f"Skipping file {content.path}: {str(e)}")
            
            return files_data
            
        except RateLimitExceededException:
            reset_time = self.github.get_rate_limit().core.reset.strftime("%Y-%m-%d %H:%M:%S")
            raise NetworkError(f"GitHub API rate limit exceeded. Resets at {reset_time}")
        except Exception as e:
            raise NetworkError(f"Error accessing repository contents: {str(e)}")

    async def clone_repo(self, repo_url: str, target_dir: Optional[str] = None) -> str:
        """Clone a GitHub repository to the local filesystem.
        
        Args:
            repo_url: GitHub repository URL
            target_dir: Target directory (optional, creates temp dir if not provided)
            
        Returns:
            str: Path to the cloned repository
            
        Raises:
            OperationUnsupportedError: If Git is not available
            ResourceNotFoundError: If repository does not exist
            NetworkError: If connection fails
        """
        if not self._check_git_available():
            log.error("Git is not available on the system - cannot clone repository")
            raise RuntimeError(
                "Git is not available. Install Git or use API-based methods instead."
            )
        
        log.debug(f"Cloning repository: {repo_url}")
        
        # Create target directory if not provided
        if target_dir is None:
            owner, repo_name, _ = self.extract_repo_info_from_url(repo_url)
            target_dir = str(Paths.create_github_temp_dir(owner, repo_name))
            
        log.debug(f"Cloning to directory: {target_dir}")
        
        try:
            git.Repo.clone_from(repo_url, target_dir)
            log.debug(f"Successfully cloned repository to {target_dir}")
            return target_dir
        except git.GitCommandError as e:
            error_msg = str(e).lower()
            if "repository not found" in error_msg or "not found" in error_msg:
                log.error(f"Repository not found: {repo_url}")
                raise ResourceNotFoundError(f"Repository not found: {repo_url}")
            elif "could not resolve host" in error_msg or "network" in error_msg:
                log.error(f"Network error while cloning: {e}")
                raise NetworkError(f"Failed to connect to GitHub: {str(e)}")
            else:
                log.error(f"Git error while cloning: {e}")
                raise DataExtractionError(f"Error cloning repository: {str(e)}")

    async def process_repo_to_dataframe(self, repo: Union[Repository.Repository, str, Path], 
                                      ref: Optional[str] = None) -> pd.DataFrame:
        """Process repository files and convert to DataFrame.
        
        This method can process:
        1. Local repository paths (when cloned with clone_repo)
        2. GitHub repository objects from PyGitHub
        3. GitHub repository URLs/identifiers (API-based, no clone required)
        
        Args:
            repo: Repository object, repository full name "owner/repo", local Path, or URL
            ref: Branch, tag or commit SHA (optional)
            
        Returns:
            DataFrame with repository file data
        """
        # Handle Path objects specially for local repositories
        if isinstance(repo, Path) or (isinstance(repo, str) and os.path.isdir(repo)):
            # This is a local repository path, process files directly
            log.debug(f"Processing local repository at path: {repo}")
            repo_files = []
            
            for root, _, files in os.walk(repo):
                # Skip .git directory
                if ".git" in root:
                    continue
                    
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, repo)
                    
                    # Skip binary files or files that are too large
                    if await self.is_binary_file(file_path):
                        continue
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        ext = os.path.splitext(file_path)[1]
                        lang = CrawlerUtils.get_language_from_extension(ext)
                        line_count = len(content.splitlines())
                        
                        repo_files.append({
                            'file_path': rel_path,
                            'content': content,
                            'language': lang,
                            'extension': ext,
                            'size_bytes': os.path.getsize(file_path),
                            'line_count': line_count,
                            'timestamp': datetime.now(UTC).isoformat()
                        })
                    except (UnicodeDecodeError, PermissionError, OSError) as e:
                        log.warning(f"Could not process file {file_path}: {str(e)}")
                        continue
            
            if not repo_files:
                raise DataExtractionError("No processable files found in repository")
                
            return pd.DataFrame(repo_files)
        
        # Original GitHub API logic
        if isinstance(repo, str):
            # If string, assume it's "owner/repo" format or a URL
            if '/' in repo and 'github.com' not in repo:
                owner, repo_name = repo.split('/')
            else:
                owner, repo_name, branch = self.extract_repo_info_from_url(repo)
                if ref is None and branch:
                    ref = branch
            
            repo_obj = await self.get_repo(owner, repo_name)
        else:
            repo_obj = repo
        
        log.debug(f"Processing repository: {repo_obj.full_name} (ref: {ref or 'default branch'})")
        
        # Get all files recursively
        repo_files = await self.get_repo_contents(repo_obj, "", ref)
        
        if not repo_files:
            raise DataExtractionError(f"No accessible files found in repository {repo_obj.full_name}")
            
        log.debug(f"Found {len(repo_files)} files in repository")
        
        # Convert to DataFrame
        df = pd.DataFrame(repo_files)
        return df

    async def clone_and_store_repo(self, repo_url: str, branch: Optional[str] = None) -> Dict:
        """Access a GitHub repository via API and store its data in Parquet format.
        
        This method first tries to use the GitHub API to process the repository.
        If Git is available, it will clone the repository for more complete access.
        
        Args:
            repo_url: GitHub repository URL
            branch: Specific branch to access (optional)
            
        Returns:
            Dict with repository metadata and storage information
            
        Raises:
            Various exceptions depending on the operation
        """
        owner, repo_name, url_branch = self.extract_repo_info_from_url(repo_url)
        branch = branch or url_branch
        
        log.debug(f"Accessing and storing repository: {owner}/{repo_name} (branch: {branch or 'default'})")
        
        try:
            # First, get repository metadata via API
            repo = await self.get_repo(owner, repo_name)
            
            # Check if Git is available for cloning - if yes, clone the repo for better processing
            use_git = self._check_git_available()
            
            if use_git:
                try:
                    # Clone the repository to a temporary location
                    target_dir = str(Paths.create_github_temp_dir(owner, repo_name))
                    repo_path = await self.clone_repo(repo_url, target_dir)
                    
                    # Process from the cloned repository (local filesystem)
                    df = await self.process_repo_to_dataframe(Path(repo_path))
                    log.debug(f"Processed {len(df)} files from cloned repository")
                except Exception as e:
                    log.warning(f"Error cloning repository, falling back to API: {str(e)}")
                    # Fall back to API if cloning fails
                    df = await self.process_repo_to_dataframe(repo, branch)
            else:
                # Just use the API (without Git)
                log.debug("Git not available, processing repository via API only")
                df = await self.process_repo_to_dataframe(repo, branch)
            
            # Save to parquet
            parquet_path = ParquetStorage.save_github_data(
                data=df,
                owner=owner,
                repo=repo_name,
                base_dir=self.data_dir
            )
            
            # Return repository information
            return {
                "owner": owner,
                "repo": repo_name,
                "branch": branch or repo.default_branch,
                "url": repo_url,
                "num_files": len(df),
                "size_kb": df['size_bytes'].sum() / 1024 if 'size_bytes' in df else 0,
                "data_path": parquet_path,
                "timestamp": datetime.now(UTC).isoformat(),
                "method": "git" if use_git else "api"
            }
            
        except Exception as e:
            log.error(f"Error processing repository {repo_url}: {str(e)}")
            if isinstance(e, (ResourceNotFoundError, NetworkError, AuthenticationError, RuntimeError)):
                raise
            raise DataExtractionError(f"Failed to process repository {repo_url}: {str(e)}")

    async def get_repo_summary(self, repo_url: str) -> str:
        """Get a summary of the repository.
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Markdown formatted summary of the repository
        """
        owner, repo_name, branch = self.extract_repo_info_from_url(repo_url)
        log.debug(f"Creating summary for repository: {owner}/{repo_name}")
        
        # Check if we have local data already
        parquet_path = Paths.github_repo_data_path(self.data_dir, owner, repo_name)
        
        if not os.path.exists(parquet_path):
            log.debug(f"Repository data not found, accessing from GitHub API first")
            result = await self.clone_and_store_repo(repo_url)
            parquet_path = result["data_path"]
        
        # Load the repository data
        df = ParquetStorage.load_from_parquet(parquet_path)
        log.debug(f"Loaded repository data: {len(df)} files")
        
        # Get repository from GitHub API for additional metadata
        repo = await self.get_repo(owner, repo_name)
        
        total_files = len(df)
        total_lines = df['line_count'].sum() if 'line_count' in df.columns else 0
        
        lang_counts = df['language'].value_counts().to_dict() if 'language' in df.columns else {}
        
        summary = f"""# GitHub Repository Summary: {owner}/{repo_name}

## Repository Information
- **Name:** {repo.name}
- **Owner:** {repo.owner.login}
- **Description:** {repo.description or "No description provided"}
- **Stars:** {repo.stargazers_count}
- **Forks:** {repo.forks_count}
- **Created:** {repo.created_at.strftime('%Y-%m-%d')}
- **Last Updated:** {repo.updated_at.strftime('%Y-%m-%d')}
- **Default Branch:** {repo.default_branch}
- **Repository URL:** {repo_url}

## Statistics
- **Total Files:** {total_files}
- **Total Lines of Code:** {total_lines:,}
- **Size:** {df['size_bytes'].sum() / 1024 / 1024:.2f} MB

## Language Distribution
"""
        
        for lang, count in sorted(lang_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_files) * 100
            summary += f"- **{lang}:** {count} files ({percentage:.1f}%)\n"
        
        # Get main directories
        main_dirs = set()
        for path in df['file_path']:
            parts = path.split('/')
            if len(parts) > 1:
                main_dirs.add(parts[0])
                
        summary += "\n## Main Directories\n"
        for directory in sorted(main_dirs):
            file_count = sum(1 for path in df['file_path'] if path.startswith(f"{directory}/"))
            summary += f"- **{directory}/**: {file_count} files\n"
        
        # Try to find and add README content
        readme_row = df[df['file_path'].str.lower().str.contains('readme.md')].head(1)
        if not readme_row.empty:
            readme_content = readme_row.iloc[0]['content']
            summary += "\n## README Preview\n"
            
            if len(readme_content) > 500:
                summary += readme_content[:500] + "...\n"
            else:
                summary += readme_content + "\n"
        
        log.debug("Repository summary created successfully")
        return summary

    async def find_similar_code(self, repo_info: Union[str, Tuple[str, str]], 
                              code_snippet: str, top_n: int = 5) -> List[Dict]:
        """Find similar code in the repository.
        
        Args:
            repo_info: Repository URL or (owner, repo) tuple
            code_snippet: Code snippet to search for
            top_n: Maximum number of results to return
            
        Returns:
            List of dictionaries with matched file paths and content
        """
        log.debug(f"Searching for similar code in repository")
        
        # Parse repository info
        if isinstance(repo_info, str):
            owner, repo_name, _ = self.extract_repo_info_from_url(repo_info)
        else:
            owner, repo_name = repo_info
        
        # Check if we have local data already
        parquet_path = Paths.github_repo_data_path(self.data_dir, owner, repo_name)
        
        if not os.path.exists(parquet_path):
            log.debug(f"Repository data not found, accessing from GitHub API first")
            result = await self.clone_and_store_repo(f"https://github.com/{owner}/{repo_name}")
            parquet_path = result["data_path"]
        
        # Load the repository data
        df = ParquetStorage.load_from_parquet(parquet_path)
        log.debug(f"Loaded repository data: {len(df)} files")
        
        # Detect language of the code snippet
        lang = "Unknown"
        if "def " in code_snippet and ":" in code_snippet:
            lang = "Python"
        elif "function" in code_snippet and "{" in code_snippet:
            lang = "JavaScript"
        elif "class" in code_snippet and "{" in code_snippet:
            lang = "Java"
        
        log.debug(f"Detected language for code snippet: {lang}")
        
        if lang != "Unknown":
            df_filtered = df[df['language'] == lang].copy()
            if len(df_filtered) > 0:
                df = df_filtered
                log.debug(f"Filtered to {len(df)} {lang} files")
        
        # Simple similarity function
        def simple_similarity(content):
            try:
                snippet_lines = set(line.strip() for line in code_snippet.splitlines() if len(line.strip()) > 10)
                if not snippet_lines:
                    return 0
                    
                content_lines = content.splitlines()
                matches = sum(1 for line in snippet_lines if any(line in c_line for c_line in content_lines))
                return matches / len(snippet_lines) if snippet_lines else 0
            except:
                return 0
        
        # Calculate similarity scores
        df['similarity'] = df['content'].apply(simple_similarity)
        
        # Filter and sort results
        similar_files = df[df['similarity'] > 0.1].sort_values('similarity', ascending=False).head(top_n)
        
        # Format results
        results = []
        for _, row in similar_files.iterrows():
            # Find best matching section
            content_lines = row['content'].splitlines()
            best_section = ""
            max_matches = 0
            section_start = 0
            
            for i in range(0, len(content_lines), 10):
                section = '\n'.join(content_lines[i:min(i+20, len(content_lines))])
                snippet_lines = set(line.strip() for line in code_snippet.splitlines() if len(line.strip()) > 10)
                matches = sum(1 for line in snippet_lines if any(line in c_line for c_line in section.splitlines()))
                
                if matches > max_matches:
                    max_matches = matches
                    best_section = section
                    section_start = i
            
            results.append({
                'file_path': row['file_path'],
                'language': row['language'],
                'similarity': round(row['similarity'] * 100, 1),
                'content': best_section,
                'line_start': section_start + 1  # 1-indexed line numbers
            })
        
        return results

    async def search_code(self, repo_info: Union[str, Tuple[str, str]], query: str, 
                        language: Optional[str] = None) -> List[Dict]:
        """Search code in a repository using GitHub's search API.
        
        Args:
            repo_info: Repository URL or (owner, repo) tuple
            query: Search query
            language: Filter by programming language (optional)
            
        Returns:
            List of search results
        """
        # Parse repository info
        if isinstance(repo_info, str):
            owner, repo_name, _ = self.extract_repo_info_from_url(repo_info)
        else:
            owner, repo_name = repo_info
        
        log.debug(f"Searching for '{query}' in {owner}/{repo_name}")
        
        # Construct the search query for GitHub API
        search_query = f"{query} repo:{owner}/{repo_name}"
        if language:
            search_query += f" language:{language}"
        
        try:
            # Use GitHub's code search API
            code_results = self.github.search_code(search_query)
            results = []
            
            for item in code_results[:30]:  # Limit to 30 results to avoid rate limiting
                try:
                    # Get file content
                    file_content = await self.get_file_content(item.repository, item.path)
                    
                    if not file_content.get('is_binary', True) and file_content.get('content'):
                        content = file_content['content']
                        
                        # Find best snippet with query matches
                        lines = content.splitlines()
                        best_snippet = []
                        query_terms = query.lower().split()
                        
                        for i, line in enumerate(lines):
                            line_lower = line.lower()
                            if any(term in line_lower for term in query_terms):
                                start = max(0, i - 3)
                                end = min(len(lines), i + 4)
                                snippet = lines[start:end]
                                best_snippet = snippet
                                break
                        
                        if not best_snippet and lines:
                            best_snippet = lines[:7]  # Just first 7 lines if no match found
                        
                        results.append({
                            'file_path': item.path,
                            'repository': item.repository.full_name,
                            'language': CrawlerUtils.get_language_from_extension(os.path.splitext(item.path)[1]),
                            'url': item.html_url,
                            'content_snippet': '\n'.join(best_snippet),
                            'score': item.score
                        })
                except Exception as e:
                    log.warning(f"Error getting content for {item.path}: {str(e)}")
                    continue
                    
            return results
            
        except RateLimitExceededException:
            reset_time = self.github.get_rate_limit().search.reset.strftime("%Y-%m-%d %H:%M:%S")
            raise NetworkError(f"GitHub API search rate limit exceeded. Resets at {reset_time}")
        except Exception as e:
            raise NetworkError(f"Error searching repository: {str(e)}")


