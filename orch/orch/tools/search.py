import httpx
import os

async def perform_search(query: str) -> str:
    """Performs a web search using Tavily API (if available) or a mock fallback."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return f"Mock search results for: '{query}'. (TAVILY_API_KEY not set)"
    
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "basic",
        "max_results": 3
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            results = response.json().get("results", [])
            if not results:
                return "No results found."
            
            summary = []
            for res in results:
                summary.append(f"Title: {res['title']}\nURL: {res['url']}\nContent: {res['content']}\n")
            return "\n".join(summary)
    except Exception as e:
        return f"Error performing search: {e}"

def search(query: str) -> str:
    """Synchronous wrapper for search."""
    import asyncio
    try:
        return asyncio.run(perform_search(query))
    except Exception as e:
        return f"Error in search: {e}"
