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
from pathlib import Path
from datetime import datetime, UTC
from typing import Optional, Tuple

import git
import pandas as pd

from oarc_log import log
from oarc_utils.errors import (
    NetworkError,
    DataExtractionError,
)

from oarc_crawlers.config.config import Config
from oarc_crawlers.core.storage.parquet_storage import ParquetStorage
from oarc_crawlers.utils.paths import Paths
from oarc_crawlers.utils.crawler_utils import CrawlerUtils
from oarc_crawlers.utils.const import (
    GITHUB_BINARY_EXTENSIONS,
    GITHUB_LANGUAGE_EXTENSIONS,
)


class GHCrawler:
    """Class for crawling and extracting content from GitHub repositories."""


    def __init__(self, data_dir: Optional[str] = None):
        """Initialize the GitHub Crawler.
        
        Args:
            data_dir (str, optional): Directory to store data. Defaults to Config's data_dir.
        """

        # Use the global config if no data_dir provided
        if data_dir is None:
            data_dir = str(Config.get_instance().data_dir)
        self.data_dir = data_dir

        # Use the Paths utility for standardized path handling
        self.github_data_dir = Paths.github_repos_dir(self.data_dir)
        log.debug(f"Initialized GitHubCrawler with data directory: {self.data_dir}")


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
        
        # Use Paths utility for managing temporary directories
        if temp_dir is None:
            temp_dir = Paths.create_github_temp_dir(owner, repo_name)
        else:
            temp_dir = Paths.ensure_temp_dir(temp_dir)
        
        log.debug(f"Cloning repository {repo_url} to {temp_dir}")
        
        try:
            repo = git.Repo.clone_from(repo_url, temp_dir)
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
        """Check if a file is binary."""
        return   # Use Paths class instead of CrawlerUtils


    async def process_repo_to_dataframe(self, repo_path: Path, max_file_size_kb: int = 500) -> pd.DataFrame:
        """Process repository files and convert to DataFrame."""
        data = []
        max_file_size = max_file_size_kb * 1024
        log.debug(f"Processing repository at {repo_path} (max file size: {max_file_size_kb} KB)")
        
        try:
            repo = git.Repo(repo_path)
        except git.exc.InvalidGitRepositoryError:
            log.debug("Not a valid git repo, processing without git metadata")
            repo = None
        
        file_count = 0
        binary_count = 0
        error_count = 0
        
        for file_path in glob.glob(str(repo_path / '**' / '*'), recursive=True):
            file_path = Path(file_path)
            
            if file_path.is_dir():
                continue
                
            if Paths.is_binary_file(file_path):
                binary_count += 1
                continue
                
            if file_path.stat().st_size > max_file_size:
                log.debug(f"Skipping large file: {file_path.name} ({file_path.stat().st_size / 1024:.1f} KB)")
                continue
            
            if '.git' in str(file_path):
                continue
                
            try:
                rel_path = str(file_path.relative_to(repo_path))
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                file_ext = file_path.suffix
                language = CrawlerUtils.get_language_from_extension(file_ext)
                
                last_modified = None
                author = None
                
                if repo:
                    try:
                        for commit, lines in repo.git.blame('--incremental', str(rel_path)).items():
                            author = lines.split('author ')[1].split('\n')[0]
                            last_modified = lines.split('author-time ')[1].split('\n')[0]
                            break
                    except git.exc.GitCommandError:
                        last_modified = datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                else:
                    last_modified = datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                
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


    async def clone_and_store_repo(self, repo_url: str) -> str:
        """Clone a GitHub repository and store its data in Parquet format."""
        owner, repo_name, _ = self.extract_repo_info_from_url(repo_url)
        log.debug(f"Cloning and storing repository: {owner}/{repo_name}")
        
        # Use Paths utility for temporary directory creation
        temp_dir = Paths.create_github_temp_dir(owner, repo_name)
        
        try:
            cloned_path = await self.clone_repo(repo_url, temp_dir)
            df = await self.process_repo_to_dataframe(cloned_path)
            
            parquet_path = ParquetStorage.save_github_data(
                data=df,
                owner=owner,
                repo=repo_name,
                base_dir=self.data_dir
            )
            
            log.debug(f"Successfully stored repository {repo_url} to {parquet_path}")
            return parquet_path
            
        finally:
            # Use Paths utility for cleanup
            Paths.cleanup_temp_dir(temp_dir)

    async def query_repo_content(self, repo_url: str, query: str) -> str:
        """Query repository content using natural language."""
        owner, repo_name, _ = self.extract_repo_info_from_url(repo_url)
        log.debug(f"Querying repository: {owner}/{repo_name} with query: {query}")
        
        parquet_path = f"{self.github_data_dir}/{owner}_{repo_name}.parquet"
        
        if not os.path.exists(parquet_path):
            log.debug(f"Repository data not found, cloning first")
            parquet_path = await self.clone_and_store_repo(repo_url)
        
        df = ParquetStorage.load_from_parquet(parquet_path)
        log.debug(f"Loaded repository data: {len(df)} files")
        
        from llama_index.experimental.query_engine import PandasQueryEngine
        log.debug("Using PandasQueryEngine for advanced querying")
        
        result = await PandasQueryEngine.execute_query(df, query)
        
        if result["success"]:
            response = f"""# GitHub Repository Query Results
Repository: {owner}/{repo_name}
Query: `{query}`

{result["result"]}

"""
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
        """Get a summary of the repository."""
        owner, repo_name, _ = self.extract_repo_info_from_url(repo_url)
        log.debug(f"Creating summary for repository: {owner}/{repo_name}")
        
        parquet_path = f"{self.github_data_dir}/{owner}_{repo_name}.parquet"
        
        if not os.path.exists(parquet_path):
            log.debug(f"Repository data not found, cloning first")
            parquet_path = await self.clone_and_store_repo(repo_url)
        
        df = ParquetStorage.load_from_parquet(parquet_path)
        log.debug(f"Loaded repository data: {len(df)} files")
        
        total_files = len(df)
        total_lines = df['line_count'].sum()
        
        lang_counts = df['language'].value_counts().to_dict()
        
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
        
        main_dirs = set()
        for path in df['file_path']:
            parts = path.split('/')
            if len(parts) > 1:
                main_dirs.add(parts[0])
                
        summary += "\n## Main Directories\n"
        for directory in sorted(main_dirs):
            summary += f"- {directory}/\n"
        
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

    async def find_similar_code(self, repo_url: str, code_snippet: str) -> str:
        """Find similar code in the repository."""
        owner, repo_name, _ = self.extract_repo_info_from_url(repo_url)
        log.debug(f"Finding similar code in repository: {owner}/{repo_name}")
        
        parquet_path = f"{self.github_data_dir}/{owner}_{repo_name}.parquet"
        
        if not os.path.exists(parquet_path):
            log.debug(f"Repository data not found, cloning first")
            parquet_path = await self.clone_and_store_repo(repo_url)
        
        df = ParquetStorage.load_from_parquet(parquet_path)
        log.debug(f"Loaded repository data: {len(df)} files")
        
        lang = "Unknown"
        if "def " in code_snippet and ":" in code_snippet:
            lang = "Python"
        elif "function" in code_snippet and "{" in code_snippet:
            lang = "JavaScript"
        elif "class" in code_snippet and "{" in code_snippet:
            lang = "Java"
        
        log.debug(f"Detected language for code snippet: {lang}")
        
        if lang != "Unknown":
            df = df[df['language'] == lang]
            log.debug(f"Filtered to {len(df)} {lang} files")
        
        def simple_similarity(content):
            snippet_lines = set(line.strip() for line in code_snippet.splitlines() if len(line.strip()) > 10)
            if not snippet_lines:
                return 0
                
            content_lines = content.splitlines()
            matches = sum(1 for line in snippet_lines if any(line in c_line for c_line in content_lines))
            return matches / len(snippet_lines) if snippet_lines else 0
        
        df['similarity'] = df['content'].apply(simple_similarity)
        
        similar_files = df[df['similarity'] > 0.1].sort_values('similarity', ascending=False)
        log.debug(f"Found {len(similar_files)} files with similarity > 0.1")
        
        if len(similar_files) == 0:
            return "No similar code found in the repository."
            
        results = f"""# Similar Code Findings

Found {len(similar_files)} files with potentially similar code:

"""
        for idx, row in similar_files.head(5).iterrows():
            similarity_percent = row['similarity'] * 100
            results += f"## {row['file_path']} ({similarity_percent:.1f}% similarity)\n\n"
            
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
            
            if best_section:
                results += f"```{row['language'].lower()}\n{best_section}\n```\n\n"
        
        return results


