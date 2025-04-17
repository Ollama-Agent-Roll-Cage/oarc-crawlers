"""Main command-line interface for OARC Crawlers."""
import argparse
import asyncio
import sys
from pathlib import Path

def main():
    """Main entry point for the OARC Crawlers CLI."""
    parser = argparse.ArgumentParser(description="OARC Crawlers - Web crawling and data extraction tools")
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Setup the environment')
    
    # Build command
    build_parser = subparsers.add_parser('build', help='Build the package')
    
    # Publish command
    publish_parser = subparsers.add_parser('publish', help='Publish to PyPI')
    publish_parser.add_argument('--test', action='store_true', help='Publish to TestPyPI')
    
    # YouTube command
    youtube_parser = subparsers.add_parser('youtube', help='YouTube operations')
    youtube_parser.add_argument('action', choices=['download', 'playlist', 'captions', 'search'])
    youtube_parser.add_argument('--url', help='YouTube URL')
    youtube_parser.add_argument('--query', help='Search query')
    
    # GitHub command
    github_parser = subparsers.add_parser('github', help='GitHub operations')
    github_parser.add_argument('action', choices=['clone', 'analyze', 'search'])
    github_parser.add_argument('--url', help='Repository URL')
    
    # ArXiv command
    arxiv_parser = subparsers.add_parser('arxiv', help='ArXiv operations')
    arxiv_parser.add_argument('action', choices=['download', 'search', 'latex'])
    arxiv_parser.add_argument('--id', help='ArXiv paper ID')
    arxiv_parser.add_argument('--query', help='Search query')
    
    # BeautifulSoup command
    bs_parser = subparsers.add_parser('bs', help='Web crawling operations')
    bs_parser.add_argument('action', choices=['crawl', 'docs', 'pypi'])
    bs_parser.add_argument('--url', help='URL to crawl')
    bs_parser.add_argument('--package', help='PyPI package name')
    
    # DuckDuckGo command
    ddg_parser = subparsers.add_parser('ddg', help='DuckDuckGo search operations')
    ddg_parser.add_argument('action', choices=['text', 'images', 'news'])
    ddg_parser.add_argument('--query', required=True, help='Search query')
    ddg_parser.add_argument('--max-results', type=int, default=10, help='Maximum number of results')
    
    args = parser.parse_args()
    
    if args.command == 'setup':
        setup_environment()
    elif args.command == 'build':
        build_package()
    elif args.command == 'publish':
        publish_package(test=args.test)
    elif args.command == 'youtube':
        asyncio.run(_handle_youtube(args))
    elif args.command == 'github':
        asyncio.run(_handle_github(args))
    elif args.command == 'arxiv':
        asyncio.run(_handle_arxiv(args))
    elif args.command == 'bs':
        asyncio.run(_handle_bs(args))
    elif args.command == 'ddg':
        asyncio.run(_handle_ddg(args))
    else:
        parser.print_help()
        sys.exit(1)

def setup_environment():
    """Setup the development environment."""
    try:
        import subprocess
        subprocess.run(["uv", "venv", "--python", "3.11"], check=True)
        subprocess.run([".venv/Scripts/activate"], check=True)
        subprocess.run(["uv", "pip", "install", "-e", ".[dev]"], check=True)
        print("Environment setup complete!")
    except Exception as e:
        print(f"Error setting up environment: {e}")
        sys.exit(1)

def build_package():
    """Build the package."""
    try:
        import subprocess
        subprocess.run(["python", "-m", "build"], check=True)
        print("Package built successfully!")
    except Exception as e:
        print(f"Error building package: {e}")
        sys.exit(1)

def publish_package(test=False):
    """Publish the package to PyPI."""
    try:
        import subprocess
        cmd = ["twine", "upload"]
        if test:
            cmd.extend(["--repository", "testpypi"])
        cmd.extend(["dist/*"])
        subprocess.run(cmd, check=True)
        print("Package published successfully!")
    except Exception as e:
        print(f"Error publishing package: {e}")
        sys.exit(1)

async def _handle_youtube(args):
    """Handle YouTube commands."""
    from .youtube_cli import (download_video, download_playlist, 
                            extract_captions, search_videos)
    
    if args.action == 'download':
        await download_video(args.url)
    elif args.action == 'playlist':
        await download_playlist(args.url)
    elif args.action == 'captions':
        await extract_captions(args.url)
    elif args.action == 'search':
        await search_videos(args.query)

async def _handle_github(args):
    """Handle GitHub commands."""
    from .github_cli import clone_repo, analyze_repo, search_repos
    
    if args.action == 'clone':
        await clone_repo(args.url)
    elif args.action == 'analyze':
        await analyze_repo(args.url)
    elif args.action == 'search':
        await search_repos(args.query)

async def _handle_arxiv(args):
    """Handle ArXiv commands."""
    from .arxiv_cli import download_paper, search_papers, get_latex
    
    if args.action == 'download':
        await download_paper(args.id)
    elif args.action == 'search':
        await search_papers(args.query)
    elif args.action == 'latex':
        await get_latex(args.id)

async def _handle_bs(args):
    """Handle BeautifulSoup commands."""
    from .beautiful_soup_cli import crawl_url, crawl_docs, crawl_pypi
    
    if args.action == 'crawl':
        await crawl_url(args.url)
    elif args.action == 'docs':
        await crawl_docs(args.url)
    elif args.action == 'pypi':
        await crawl_pypi(args.package)

async def _handle_ddg(args):
    """Handle DuckDuckGo commands."""
    from .ddg_cli import text_search, image_search, news_search
    
    if args.action == 'text':
        await text_search(args.query, args.max_results)
    elif args.action == 'images':
        await image_search(args.query, args.max_results)
    elif args.action == 'news':
        await news_search(args.query, args.max_results)

if __name__ == "__main__":
    main()