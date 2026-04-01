import httpx
import xml.etree.ElementTree as ET

def search_arxiv(query: str, max_results: int = 3) -> str:
    """
    Searches arXiv for the latest papers on a given topic.
    
    Args:
        query: The search query (topic or paper ID).
        max_results: Number of results to return.
    """
    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}"
    
    try:
        response = httpx.get(url)
        response.raise_for_status()
        
        # Parse XML response
        root = ET.fromstring(response.text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall("atom:entry", ns)
        
        if not entries:
            return f"No arXiv papers found for: '{query}'."
        
        results = []
        for entry in entries:
            title = entry.find("atom:title", ns).text.strip()
            # ArXiv links can have multiple rels, find the one without 'pdf' in it or with rel='alternate'
            link = entry.find("atom:link[@rel='alternate']", ns)
            if link is None:
                link = entry.find("atom:link", ns)
            url_paper = link.get("href") if link is not None else "No URL"
            
            summary = entry.find("atom:summary", ns).text.strip()
            author_names = [author.find("atom:name", ns).text.strip() for author in entry.findall("atom:author", ns)]
            authors = ", ".join(author_names)
            
            results.append(f"Title: {title}\nAuthors: {authors}\nURL: {url_paper}\nAbstract: {summary}\n")
        
        return "\n".join(results)
    except Exception as e:
        return f"Error performing arXiv search: {e}"
