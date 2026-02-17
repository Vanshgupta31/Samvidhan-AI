import requests
from bs4 import BeautifulSoup
from googlesearch import search
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def search_indian_kanoon(query, num_results=3):
    """
    Searches Indian Kanoon via Google Search and returns top results.
    """
    results = []
    search_query = f"site:indiankanoon.org {query}"
    
    try:
        # Perform Google search
        urls = list(search(search_query, num_results=num_results, advanced=True))
        
        for result in urls:
            try:
                url = result.url
                title = result.title
                description = result.description
                
                # Basic scraping of the content
                # Note: Indian Kanoon structure varies, we'll try to get the main document text
                # Asking for permission or using an API is better, but for this demo we scrap lightly.
                # To be respectful, we will just use the snippet from Google if possible, 
                # or fetch the page and get the first few paragraphs.
                
                page_content = ""
                try:
                    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        # Indian Kanoon content is usually in <div class="judgments"> or similar
                        # We will try to extract text from the main body
                        doc_source = soup.find('div', {'class': 'judgments'})
                        if doc_source:
                            page_content = doc_source.get_text()[:1000] + "..." # Limit content
                        else:
                            # Fallback
                            page_content = soup.get_text()[:1000] + "..."
                except Exception as e:
                    logger.error(f"Failed to scrape {url}: {e}")
                    page_content = description # Fallback to google description

                results.append({
                    "title": title,
                    "url": url,
                    "summary": page_content,
                    "source": "Indian Kanoon"
                })
                
            except Exception as e:
                logger.error(f"Error processing result: {e}")
                continue

    except Exception as e:
        logger.error(f"Search failed: {e}")
        return []

    return results

if __name__ == "__main__":
    # Test
    q = "murder punishment section 302"
    res = search_indian_kanoon(q)
    for r in res:
        print(f"Title: {r['title']}")
        print(f"URL: {r['url']}")
        summary = str(r.get('summary', ''))
        print(f"Summary: {summary[:200] if len(summary) > 200 else summary}...")
        print("-" * 20)
