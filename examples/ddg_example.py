import asyncio
from pathlib import Path
from oarc_crawlers import DDGCrawler

async def ddg_examples():
    """Examples for using the DuckDuckGo Search module."""

    # Initialize the searcher
    data_dir = Path("./data")
    searcher = DDGCrawler(data_dir=data_dir)

    print("=== DuckDuckGo Searcher Examples ===")

    # Example 1: Basic text search
    print("\n1. Basic text search")
    query = "quantum computing"
    try:
        text_results = await searcher.text_search(query, max_results=3)
        print(text_results)
    except Exception as e:
        print(f"Error during text search: {e}")

    # Example 2: Image search
    print("\n2. Image search")
    image_query = "mountain landscape"
    try:
        image_results = await searcher.image_search(image_query, max_results=2)
        print(image_results)
    except Exception as e:
        print(f"Error during image search: {e}")

    # Example 3: News search
    print("\n3. News search")
    news_query = "artificial intelligence"
    try:
        news_results = await searcher.news_search(news_query, max_results=3)
        print(news_results)
    except Exception as e:
        print(f"Error during news search: {e}")

    # Example 4: Error handling demonstration
    print("\n4. Error handling demonstration")
    try:
        # Pass an invalid query to force an error
        invalid_result = await searcher.text_search("", max_results=-1)
        print(invalid_result)
    except Exception as e:
        print(f"Caught exception: {e}")

if __name__ == "__main__":
    asyncio.run(ddg_examples())