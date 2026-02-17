import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict, Optional
from .base import BaseScraper
import re

logger = logging.getLogger(__name__)

class IndianKanoonScraper(BaseScraper):
    """
    Scraper for Indian Kanoon (indiankanoon.org).
    """
    
    BASE_URL = "https://indiankanoon.org"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def scrape_act(self, url: str, limit: int = 0) -> List[Dict]:
        """
        Scrapes an entire act from its main TOC URL.
        Example URL: https://indiankanoon.org/doc/1569253/ (Indian Penal Code)
        """
        logger.info(f"Starting scrape for Act TOC: {url}")
        sections_data = []
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find Act Name
            # Try h2 first, then div
            act_title_tag = soup.find('h2', class_='doc_title')
            if not act_title_tag:
                act_title_tag = soup.find('div', class_='doc_title')

            act_name = act_title_tag.get_text(strip=True) if act_title_tag else "Unknown Act"
            logger.info(f"Identified Act: {act_name}")

            # Find all links to sections
            links = soup.find_all('a', href=True)
            section_links = []
            
            for link in links:
                href = link['href']
                text = link.get_text(strip=True)
                
                # Check if it looks like a section link
                if href.startswith('/doc/') or href.startswith('http://indiankanoon.org/doc/'):
                    full_url = self.BASE_URL + href if href.startswith('/') else href
                    if full_url not in section_links and url not in full_url: 
                         section_links.append((full_url, text))

            logger.info(f"Found {len(section_links)} potential section links.")
            
            for i, (sec_url, sec_text) in enumerate(section_links):
                if limit > 0 and len(sections_data) >= limit:
                    break

                time.sleep(1) 
                
                section_data = self.scrape_section(sec_url)
                if section_data:
                    # Enrich with Act Name if missing
                    if not section_data.get('act') or section_data.get('act') == "Unknown Act":
                        section_data['act'] = act_name
                    
                    # If section number wasn't found in the page text, try to infer from link text
                    if not section_data.get('section'):
                        match = re.search(r'Section\s+(\w+)', sec_text, re.IGNORECASE)
                        if match:
                            section_data['section'] = match.group(1)
                        elif sec_text.strip().replace('.', '').isdigit():
                             section_data['section'] = sec_text.strip().replace('.', '')
                        else:
                            section_data['section'] = "Unknown"

                    sections_data.append(section_data)
                    logger.info(f"Scraped Section {section_data.get('section')}")

        except Exception as e:
            logger.error(f"Error scraping Act TOC {url}: {e}")
            
        return sections_data

    def scrape_section(self, url: str) -> Optional[Dict]:
        """
        Scrapes a single section.
        """
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Title
            title_tag = soup.find('h2', class_='doc_title')
            if not title_tag:
                 title_tag = soup.find('div', class_='doc_title')
                 
            title = title_tag.get_text(strip=True) if title_tag else ""
            
            # Content
            # Priority: akoma-ntoso (formal acts), judgments (case law), or maindoc
            text = ""
            content_div = soup.find('div', class_='akoma-ntoso')
            if not content_div:
                content_div = soup.find('div', class_='judgments')
            
            if content_div:
                text = content_div.get_text(separator="\n", strip=True)
            else:
                # Fallback to main content area logic or just body text
                main_doc = soup.find('div', class_='maindoc')
                if main_doc:
                     text = main_doc.get_text(separator="\n", strip=True)

            # Attempt to extract Act and Section from title
            # e.g. "Section 302 in The Indian Penal Code"
            act_name = None
            section_num = None
            
            if " in " in title:
                parts = title.split(" in ")
                section_part = parts[0]
                act_name = parts[1].strip()
                if "," in act_name: # Remove year if present? No, keep it.
                    pass
                
                sec_match = re.search(r'Section\s+(\w+)', section_part, re.IGNORECASE)
                if sec_match:
                    section_num = sec_match.group(1)
            
            return {
                "act": act_name,
                "section": section_num,
                "text": text,
                "link": url,
                "source": "Indian Kanoon"
            }

        except Exception as e:
            logger.error(f"Error scraping section {url}: {e}")
            return None
