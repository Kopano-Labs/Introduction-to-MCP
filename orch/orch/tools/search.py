import httpx
import os

async def perform_search(query: str, search_depth: str = "basic") -> str:
    """Performs a web search using RapidAPI Real-Time Web Search."""
    import os
    
    # Check for rapidapi keys, fallback to tavily if rapidapi isn't configured
    api_key = os.getenv("RAPIDAPI_KEY")
    rapidapi_host = os.getenv("RAPIDAPI_GOOGLE_SEARCH_HOST", "real-time-web-search.p.rapidapi.com")
    
    if not api_key:
        # Check fallback
        tavily_key = os.getenv("TAVILY_API_KEY")
        if not tavily_key:
            return f"Mock search results for: '{query}'. (RAPIDAPI_KEY not set)"
            
    url = f"https://{rapidapi_host}/search"
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": rapidapi_host
    }
    params = {"q": query, "limit": 5 if search_depth == "advanced" else 3}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            # RapidAPI real-time-web-search shape contains 'data' array
            results = data.get("data", [])
            
            if not results:
                return "No results found."
            
            summary = []
            for res in results:
                summary.append(f"Title: {res.get('title', 'N/A')}\nURL: {res.get('url', 'N/A')}\nContent: {res.get('snippet', 'N/A')}\n")
            return "\n".join(summary)
    except Exception as e:
        return f"Error performing search: {e}"

def search(query: str, search_depth: str = "basic") -> str:
    """Synchronous wrapper for search."""
    import asyncio
    try:
        return asyncio.run(perform_search(query, search_depth=search_depth))
    except Exception as e:
        return f"Error in search: {e}"
