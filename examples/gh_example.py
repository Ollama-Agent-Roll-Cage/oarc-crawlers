import asyncio
from pathlib import Path
from oarc_crawlers import GHCrawler

async def github_examples():
    """Examples for using the GitHub Crawler module."""

    # Initialize the crawler
    data_dir = Path("./data")
    crawler = GHCrawler(data_dir=data_dir)

    print("=== GitHub Crawler Examples ===")

    # Example 1: Clone and store a repository (Parquet)
    print("\n1. Clone and store a repository (Parquet)")
    repo_url = "https://github.com/pandas-dev/pandas"
    try:
        result = await crawler.clone_and_store_repo(repo_url)
        print(f"Repository data saved to: {result['data_path']}")
    except Exception as e:
        print(f"Error cloning repository: {e}")

    # Example 2: Get a repository summary (Markdown)
    print("\n2. Get repository summary")
    try:
        summary = await crawler.get_repo_summary("https://github.com/numpy/numpy")
        print(summary[:500] + "...\n(Summary truncated)")
    except Exception as e:
        print(f"Error getting summary: {e}")

    # Example 3: Find similar code in a repository
    print("\n3. Find similar code in a repository")
    code_snippet = """
    def calculate_mean(values):
        return sum(values) / len(values)
    """
    try:
        similar_code = await crawler.find_similar_code(
            repo_info="https://github.com/numpy/numpy",
            code_snippet=code_snippet,
            top_n=3
        )
        for i, match in enumerate(similar_code, 1):
            print(f"\nMatch {i}:")
            print(f"File: {match['file_path']}")
            print(f"Language: {match['language']}")
            print(f"Similarity: {match['similarity']}%")
            print(f"Snippet (lines {match['line_start']}+):\n{match['content'][:200]}...\n")
    except Exception as e:
        print(f"Error finding similar code: {e}")

    # Example 4: Extract repository information from different URL formats
    print("\n4. Extract repository information from different URL formats")
    urls = [
        "https://github.com/username/repo",
        "https://github.com/username/repo/tree/dev",
        "git@github.com:username/repo.git"
    ]
    for url in urls:
        try:
            owner, repo, branch = GHCrawler.extract_repo_info_from_url(url)
            print(f"URL: {url}")
            print(f"  Owner: {owner}")
            print(f"  Repo: {repo}")
            print(f"  Branch: {branch}")
        except Exception as e:
            print(f"Error parsing URL '{url}': {e}")

if __name__ == "__main__":
    asyncio.run(github_examples())