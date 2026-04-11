import asyncio
from typing import List
from .search import perform_search

def monitor_brand(brand_name: str, platform: str = "all") -> str:
    """
    Monitors social media platforms (Reddit, X, forums) for brand mentions.
    
    Args:
        brand_name: The brand or keyword to monitor.
        platform: The specific platform ('reddit', 'x', 'forum', or 'all').
    """
    queries = []
    if platform == "reddit":
        queries.append(f'site:reddit.com "{brand_name}"')
    elif platform == "x" or platform == "twitter":
        queries.append(f'site:x.com OR site:twitter.com "{brand_name}"')
    elif platform == "forum":
        queries.append(f'site:forums.com OR site:community.com "{brand_name}"')
    elif platform == "all":
        queries.append(f'site:reddit.com OR site:x.com OR site:twitter.com "{brand_name}"')
    else:
        return f"Error: Invalid platform '{platform}'. Choose from 'reddit', 'x', 'forum', or 'all'."

    results = []
    for query in queries:
        try:
             # Using asyncio.run to call the async perform_search
             res = asyncio.run(perform_search(query))
             results.append(f"--- Results for {query} ---\n{res}")
        except Exception as e:
             results.append(f"Error searching for {query}: {e}")

    return "\n\n".join(results)
