"""Main command-line interface for OARC Crawlers."""
import argparse
import asyncio
import sys
import subprocess
from pathlib import Path

def setup_environment():
    """Setup the development environment."""
    try:
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
        subprocess.run([sys.executable, "-m", "build"], check=True)
        print("Package built successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error building package: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error building package: {e}")
        sys.exit(1)

async def publish_package(test=False):
    """Publish the package to PyPI."""
    try:
        cmd = ["twine", "upload"]
        if test:
            cmd.extend(["--repository", "testpypi"])
        cmd.extend(["dist/*"])
        
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        
        if proc.returncode == 0:
            print("Package published successfully!")
        else:
            print(f"Error publishing package: {stderr.decode()}")
            sys.exit(1)
    except Exception as e:
        print(f"Error publishing package: {e}")
        sys.exit(1)

async def _handle_command(args):
    """Handle the different crawler commands."""
    try:
        if args.command == 'setup':
            setup_environment()
        elif args.command == 'build':
            build_package()
        elif args.command == 'publish':
            await publish_package(test=args.test)
        else:
            from .. import (YouTubeDownloader, GitHubCrawler, ArxivFetcher,
                        BSWebCrawler, DuckDuckGoSearcher)
            
            if args.command == 'youtube':
                downloader = YouTubeDownloader()
                if args.action == 'download' and args.url:
                    result = await downloader.download_video(args.url)
                elif args.action == 'playlist' and args.url:
                    result = await downloader.download_playlist(args.url)
                elif args.action == 'captions' and args.url:
                    result = await downloader.extract_captions(args.url)
                elif args.action == 'search' and args.query:
                    result = await downloader.search_videos(args.query)
                else:
                    print("Error: Missing required arguments")
                    sys.exit(1)
                print(result)
                
            elif args.command == 'github':
                crawler = GitHubCrawler()
                if args.action == 'clone' and args.url:
                    result = await crawler.clone_and_store_repo(args.url)
                elif args.action == 'analyze' and args.url:
                    result = await crawler.get_repo_summary(args.url)
                else:
                    print("Error: Missing required arguments")
                    sys.exit(1)
                print(result)
                
            elif args.command == 'arxiv':
                fetcher = ArxivFetcher()
                if args.action == 'download' and args.id:
                    result = await fetcher.download_source(args.id)
                elif args.action == 'search' and args.query:
                    # TODO: Implement arxiv search
                    pass
                elif args.action == 'latex' and args.id:
                    result = await fetcher.fetch_paper_with_latex(args.id)
                else:
                    print("Error: Missing required arguments")
                    sys.exit(1)
                print(result)
                
            elif args.command == 'bs':
                crawler = BSWebCrawler()
                if args.action == 'crawl' and args.url:
                    result = await crawler.crawl_documentation_site(args.url)
                elif args.action == 'pypi' and args.package:
                    html = await BSWebCrawler.fetch_url_content(f"https://pypi.org/project/{args.package}/")
                    result = await BSWebCrawler.extract_pypi_content(html, args.package)
                else:
                    print("Error: Missing required arguments")
                    sys.exit(1)
                print(result)
                
            elif args.command == 'ddg':
                searcher = DuckDuckGoSearcher()
                if args.action == 'text' and args.query:
                    result = await searcher.text_search(args.query, max_results=args.max_results)
                elif args.action == 'images' and args.query:
                    result = await searcher.image_search(args.query, max_results=args.max_results)
                elif args.action == 'news' and args.query:
                    result = await searcher.news_search(args.query, max_results=args.max_results)
                else:
                    print("Error: Missing required arguments")
                    sys.exit(1)
                print(result)
                
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

async def async_main():
    """Async main entry point for the CLI."""
    parser = argparse.ArgumentParser(description='OARC Crawlers CLI')
    
    # Add subparsers for each command
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Setup the environment')
    
    # Build command
    build_parser = subparsers.add_parser('build', help='Build the package')
    
    # Publish command
    publish_parser = subparsers.add_parser('publish', help='Publish to PyPI')
    publish_parser.add_argument('--test', action='store_true', help='Publish to TestPyPI')
    
    # YouTube command
    youtube = subparsers.add_parser('youtube')
    youtube.add_argument('action', choices=['download', 'playlist', 'captions', 'search'])
    youtube.add_argument('--url', help='Video or playlist URL')
    youtube.add_argument('--query', help='Search query')
    
    # GitHub command
    github = subparsers.add_parser('github')
    github.add_argument('action', choices=['clone', 'analyze'])
    github.add_argument('--url', help='Repository URL')
    
    # ArXiv command
    arxiv = subparsers.add_parser('arxiv')
    arxiv.add_argument('action', choices=['download', 'search', 'latex'])
    arxiv.add_argument('--id', help='ArXiv paper ID')
    arxiv.add_argument('--query', help='Search query')
    
    # BeautifulSoup command
    bs = subparsers.add_parser('bs')
    bs.add_argument('action', choices=['crawl', 'docs', 'pypi'])
    bs.add_argument('--url', help='URL to crawl')
    bs.add_argument('--package', help='PyPI package name')
    
    # DuckDuckGo command
    ddg = subparsers.add_parser('ddg')
    ddg.add_argument('action', choices=['text', 'images', 'news'])
    ddg.add_argument('--query', help='Search query')
    ddg.add_argument('--max-results', type=int, default=5, help='Maximum number of results')
    
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
        
    await _handle_command(args)

def main():
    """Synchronous entry point for the CLI."""
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()