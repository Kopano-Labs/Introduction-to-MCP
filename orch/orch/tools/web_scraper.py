import httpx
from bs4 import BeautifulSoup

def scrape_page(url: str, selector: str = "body") -> str:
    """
    Scrapes the text content of a web page using a CSS selector.
    
    Args:
        url: The URL of the page to scrape.
        selector: CSS selector to target specific content (defaults to 'body').
    """
    try:
        response = httpx.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        title = soup.title.string if soup.title else "No Title"
        
        element = soup.select_one(selector)
        if not element:
            return f"Error: No content found for selector '{selector}' on {url}."
            
        # Extract text and clean up whitespace
        text = element.get_text(separator="\n")
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = "\n".join(chunk for chunk in chunks if chunk)
        
        return f"Title: {title}\nURL: {url}\n\nContent Preview:\n{clean_text[:2000]}..."
    except Exception as e:
        return f"Error scraping '{url}': {e}"
