import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict, Optional
from .base import BaseScraper
import re

logger = logging.getLogger(__name__)

class IndiaCodeScraper(BaseScraper):
    """
    Scraper for India Code (indiacode.nic.in).
    """
    
    BASE_URL = "https://www.indiacode.nic.in"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def scrape_act(self, url: str, limit: int = 0) -> List[Dict]:
        """
        Scrapes an entire act from its India Code handle URL.
        Example: https://indiacode.nic.in/handle/123456789/2347?locale=en
        """
        logger.info(f"Starting scrape for Act: {url}")
        sections_data = []
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find Act Name
            # Typically in a breadcrumb or a heading
            # <h2 class="alert alert-info">The Indian Penal Code, 1860</h2>
            act_header = soup.find('h2', class_='alert alert-info')
            if act_header:
                act_name = act_header.get_text(strip=True)
            else:
                 # Fallback
                 act_name = "Unknown Act"

            logger.info(f"Identified Act: {act_name}")

            # India Code lists sections in a table or list
            # We look for links that point to 'view_section' or similar
            
            links = soup.find_all('a', href=True)
            section_links = []
            
            for link in links:
                href = link['href']
                text = link.get_text(strip=True)
                
                # Check for section links
                # Usually contain 'view_file' or specific easy to identify patterns?
                # Actually, India Code structure is complex. 
                # Sections are often listed in a table with links to individual section text.
                
                # Let's try to find links that seem to be sections.
                # Often they are just relative links in the TOC table.
                
                if 'handle' in href and href != url:
                     full_url = href if href.startswith('http') else self.BASE_URL + href
                     # Avoid adding the main page itself or other non-section pages
                     if full_url not in section_links:
                         section_links.append((full_url, text))

            logger.info(f"Found {len(section_links)} potential section links.")

            for i, (sec_url, sec_text) in enumerate(section_links):
                if limit > 0 and len(sections_data) >= limit:
                    break
                
                # Scrape section
                time.sleep(1) # Polite delay
                
                section_data = self.scrape_section(sec_url)
                if section_data:
                    if not section_data.get('act'):
                        section_data['act'] = act_name
                    
                    # Infer section number if missing
                    if not section_data.get('section'):
                        # Heuristic: check if link text starts with "Section"
                        match = re.search(r'Section\s+(\w+)', sec_text, re.IGNORECASE)
                        if match:
                             section_data['section'] = match.group(1)
                        else:
                             # Try to parse from the scraped text, first line often has it
                             pass
                    
                    sections_data.append(section_data)
                    logger.info(f"Scraped Section {section_data.get('section')}")

        except Exception as e:
            logger.error(f"Error scraping Act {url}: {e}")

        return sections_data

    def scrape_section(self, url: str) -> Optional[Dict]:
        """
        Scrapes a single section page from India Code.
        """
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Content extraction
            # Needs to be adjusted based on actual page structure of India Code section view
            # Assuming there's a main content area
            
            # Often India Code displays the PDF plugin or a text box.
            # If it's just a PDF viewer, scraping text is hard without OCR/PDF tools.
            # However, many acts have HTML text available.
            
            # Let's look for a content container.
            # <div id="main_content"> or similar.
            
            content_div = soup.find('div', id='main_content') # Hypothetical ID
            if not content_div:
                content_div = soup.find('div', class_='content') # Another common class
            
            if content_div:
                text = content_div.get_text(separator="\n", strip=True)
            else:
                # Fallback: get all paragraph text
                text = "\n".join([p.get_text(strip=True) for p in soup.find_all('p')])

            # Try to identify Section Number from the page
            # Usually bolded "Section 123"
            section_num = None
            act_name = None
            
            # Very basic extraction
            match = re.search(r'Section\s+(\w+)', text, re.IGNORECASE)
            if match:
                section_num = match.group(1)

            return {
                "act": act_name, # Will be filled by parent if None
                "section": section_num,
                "text": text,
                "link": url,
                "source": "India Code"
            }

        except Exception as e:
            logger.error(f"Error scraping section {url}: {e}")
            return None
