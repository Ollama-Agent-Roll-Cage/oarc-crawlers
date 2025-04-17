import asyncio
import sys

async def main():
    if len(sys.argv) < 2:
        print("Please specify which example to run:")
        print("  youtube - YouTube Downloader examples")
        print("  github - GitHub Crawler examples")
        print("  ddg - DuckDuckGo Searcher examples")
        print("  bs - BeautifulSoup Web Crawler examples")
        print("  arxiv - ArXiv Fetcher examples")
        print("  combined - Combined multi-module example")
        print("  all - Run all examples")
        return
    
    example = sys.argv[1].lower()
    
    if example == "youtube" or example == "all":
        from oarc_crawlers import youtube_examples
        await youtube_examples()
        print("\n" + "="*50 + "\n")
    
    if example == "github" or example == "all":
        from oarc_crawlers import github_examples
        await github_examples()
        print("\n" + "="*50 + "\n")
    
    if example == "ddg" or example == "all":
        from oarc_crawlers import ddg_examples
        await ddg_examples()
        print("\n" + "="*50 + "\n")
    
    if example == "bs" or example == "all":
        from oarc_crawlers import bs_examples
        await bs_examples()
        print("\n" + "="*50 + "\n")
    
    if example == "arxiv" or example == "all":
        from oarc_crawlers import arxiv_examples
        await arxiv_examples()
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(main())