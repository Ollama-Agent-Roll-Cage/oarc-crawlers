"""
Example usage of OARC-Crawlers MCP API
This example demonstrates how to use the MCP API to interact with various crawlers.
"""
import asyncio
from oarc_crawlers.mcp_api import OARCCrawlersMCP

async def main():
    # Initialize with custom data directory
    mcp = OARCCrawlersMCP(data_dir="./data", name="CrawlerDemo")
    
    # Example 1: Download YouTube video and its captions
    video_result = await mcp.youtube.download_video(
        "https://www.youtube.com/watch?v=example",
        resolution="720p"
    )
    captions = await mcp.youtube.extract_captions(
        "https://www.youtube.com/watch?v=example",
        languages=["en", "es"]
    )
    
    # Example 2: Search and analyze GitHub repositories
    search_results = await mcp.ddg.text_search(
        "github advanced python repositories",
        max_results=3
    )
    for result in search_results:
        if "github.com" in result["url"]:
            repo_summary = await mcp.github.analyze_github_repo(result["url"])
            print(f"Repository Analysis:\n{repo_summary}\n")
    
    # Example 3: Research workflow combining multiple crawlers
    # Search for papers about a topic
    papers = await mcp.ddg.text_search("arxiv machine learning breakthroughs 2024")
    for paper in papers:
        if "arxiv.org" in paper["url"]:
            # Extract arxiv ID and fetch paper info
            arxiv_id = paper["url"].split("/")[-1]
            paper_info = await mcp.arxiv.fetch_paper_info(arxiv_id)
            print(f"Paper: {paper_info['title']}")
            
            # Search for related GitHub implementations
            code_results = await mcp.ddg.text_search(
                f"github implementation {paper_info['title']}"
            )
            for code in code_results:
                if "github.com" in code["url"]:
                    await mcp.github.clone_github_repo(code["url"])

if __name__ == "__main__":
    # Option 1: Run as MCP server
    mcp = OARCCrawlersMCP(data_dir="./data")
    mcp.run()
    
    # Option 2: Run example workflow
    # asyncio.run(main())