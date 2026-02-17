from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class BaseScraper(ABC):
    """
    Abstract base class for legal text scrapers.
    """
    
    @abstractmethod
    def scrape_act(self, url: str, limit: int = 0) -> List[Dict]:
        """
        Scrapes an entire act from its main URL/Table of Contents.
        
        Args:
            url: The URL of the Act's main page or Table of Contents.
            limit: Maximum number of sections to scrape (0 for no limit).
            
        Returns:
            A list of dictionaries, where each dictionary represents a section
            and contains keys like 'act', 'section', 'text', 'link'.
        """
        pass

    @abstractmethod
    def scrape_section(self, url: str) -> Optional[Dict]:
        """
        Scrapes a single section from its URL.
        
        Args:
            url: The URL of the specific section.
            
        Returns:
            A dictionary with section details, or None if scraping failed.
        """
        pass
