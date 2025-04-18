import asyncio
import os
from pathlib import Path
from oarc_crawlers import GHCrawler

async def github_examples():
    """Examples for using the GitHub Crawler module."""
    
    # Initialize the crawler
    data_dir = Path("./data")
    crawler = GHCrawler(data_dir=data_dir)
    
    print("=== GitHub Crawler Examples ===")
    
    # Example 1: Clone and analyze a repository
    print("\n1. Clone and analyze a repository")
    repo_url = "https://github.com/pandas-dev/pandas"  # Use a smaller repo in practice
    result = await crawler.clone_and_store_repo(repo_url)
    print(f"Repository data saved to: {result}")
    
    # Example 2: Get a repository summary
    print("\n2. Get repository summary")
    summary = await crawler.get_repo_summary("https://github.com/numpy/numpy")
    print(summary[:500] + "...\n(Summary truncated)")
    
    # Example 3: Find similar code in a repository
    print("\n3. Find similar code in a repository")
    code_snippet = """
    def calculate_mean(values):
        return sum(values) / len(values)
    """
    similar_code = await crawler.find_similar_code(
        repo_url="https://github.com/numpy/numpy",
        code_snippet=code_snippet
    )
    print(similar_code[:300] + "...\n(Results truncated)")
    
    # Example 4: Using the URL extraction utility
    print("\n4. Extract repository information from different URL formats")
    urls = [
        "https://github.com/username/repo",
        "https://github.com/username/repo/tree/dev",
        "git@github.com:username/repo.git"
    ]
    for url in urls:
        owner, repo, branch = GHCrawler.extract_repo_info_from_url(url)
        print(f"URL: {url}")
        print(f"  Owner: {owner}")
        print(f"  Repo: {repo}")
        print(f"  Branch: {branch}")

if __name__ == "__main__":
    asyncio.run(github_examples())