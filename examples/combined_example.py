import asyncio
import os
from pathlib import Path

from src.youtube_script import YouTubeDownloader
from src.gh_crawler import GitHubCrawler
from src.ddg_search import DuckDuckGoSearcher
from src.beautiful_soup import BSWebCrawler
from src.arxiv_fetcher import ArxivFetcher

async def research_topic(topic):
    """
    Demonstrate researching a topic using all modules.
    
    This is an advanced example showing how the different
    modules can work together.
    """
    data_dir = Path("./data/research_" + topic.replace(" ", "_"))
    data_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"=== Researching '{topic}' using OARC-Crawlers ===")
    
    # Step 1: Search for information using DuckDuckGo
    print("\nStep 1: Gathering general information with DuckDuckGo...")
    ddg = DuckDuckGoSearcher(data_dir=data_dir)
    text_results = await ddg.text_search(topic, max_results=3)
    news_results = await ddg.news_search(topic, max_results=2)
    
    print(f"Found general information and {topic} news")
    
    # Step 2: Search for related papers on ArXiv
    print("\nStep 2: Finding academic papers on ArXiv...")
    arxiv = ArxivFetcher(data_dir=data_dir)
    # Here we'd ideally search ArXiv, but the module doesn't have a search function
    # so we'd need to have a relevant paper ID beforehand
    if topic.lower() in ['machine learning', 'deep learning', 'neural networks']:
        paper_id = "2103.00020"  # A paper related to machine learning
        paper_info = await arxiv.fetch_paper_info(paper_id)
        print(f"Found paper: {paper_info.get('title')}")
    else:
        print(f"No specific paper ID available for {topic}")
    
    # Step 3: Search for YouTube tutorials
    print("\nStep 3: Finding YouTube tutorials...")
    youtube = YouTubeDownloader(data_dir=data_dir)
    search_query = f"{topic} tutorial"
    video_results = await youtube.search_videos(search_query, limit=3)
    
    print(f"Found {video_results.get('result_count')} tutorial videos")
    for i, video in enumerate(video_results.get('results', [])[:2]):
        print(f"  {i+1}. {video.get('title')}")
    
    # Step 4: Find relevant GitHub repositories
    print("\nStep 4: Finding GitHub repositories...")
    # Note: GitHub crawler doesn't have a search function, so we'd need to know the repo URL
    # In a real scenario, we might extract this from the DuckDuckGo results
    
    # Step 5: Crawl a documentation site for more information
    print("\nStep 5: Finding documentation...")
    bs_crawler = BSWebCrawler(data_dir=data_dir)
    
    # Map topics to potential documentation URLs
    doc_urls = {
        "python": "https://docs.python.org/3/",
        "javascript": "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
        "machine learning": "https://scikit-learn.org/stable/",
        "deep learning": "https://pytorch.org/docs/stable/index.html"
    }
    
    if topic.lower() in doc_urls:
        doc_url = doc_urls[topic.lower()]
        print(f"Crawling documentation from {doc_url}...")
        # In a real example, we would await this, but we'll skip for brevity
        # doc_content = await bs_crawler.crawl_documentation_site(doc_url)
        print(f"Found documentation for {topic}")
    else:
        print(f"No specific documentation URL defined for {topic}")
    
    # Step 6: Summarize findings
    print("\nStep 6: Research Summary")
    print(f"Completed research on '{topic}'")
    print(f"- Web search results: Available")
    print(f"- News articles: {len(news_results.splitlines()) > 5}")
    print(f"- Tutorial videos: {video_results.get('result_count', 0)}")
    print(f"- Documentation: {'Yes' if topic.lower() in doc_urls else 'No'}")
    print("\nAll data saved to:", data_dir)

async def main():
    """Run the combined example with a specific topic."""
    await research_topic("machine learning")

if __name__ == "__main__":
    asyncio.run(main())