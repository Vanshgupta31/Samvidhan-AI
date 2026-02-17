import argparse
import json
import os
import logging
from scrapers.india_code import IndiaCodeScraper
from scrapers.indian_kanoon import IndianKanoonScraper

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Construct absolute path to data file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "legal_corpus.json")

def load_corpus():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_corpus(corpus):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(corpus, f, indent=2, ensure_ascii=False)

def main():
    parser = argparse.ArgumentParser(description="Ingest legal data from websites.")
    parser.add_argument("--source", type=str, required=True, choices=["india_code", "indian_kanoon"], help="Source website to scrape.")
    parser.add_argument("--url", type=str, required=True, help="URL of the Act or Table of Contents.")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of sections to scrape (0 for all).")
    
    args = parser.parse_args()
    
    scraper = None
    if args.source == "india_code":
        scraper = IndiaCodeScraper()
    elif args.source == "indian_kanoon":
        scraper = IndianKanoonScraper()
        
    if not scraper:
        logger.error("Invalid source.")
        return

    logger.info(f"Starting ingestion from {args.source}...")
    
    # Scrape data
    # We use scrape_act as entry point
    new_data = scraper.scrape_act(args.url, limit=args.limit)
        
    logger.info(f"Scraped {len(new_data)} items.")

    # Load existing corpus
    corpus = load_corpus()
    
    # Append new data, avoiding exact duplicates (based on Act + Section + Text)
    added_count = 0
    existing_sigs = set()
    for item in corpus:
        sig = (item.get('act'), item.get('section'), item.get('text'))
        existing_sigs.add(sig)
        
    for item in new_data:
        sig = (item.get('act'), item.get('section'), item.get('text'))
        if sig not in existing_sigs:
            corpus.append(item)
            existing_sigs.add(sig)
            added_count += 1
            
    # Save back
    save_corpus(corpus)
    logger.info(f"Successfully added {added_count} new entries to corpus.")

if __name__ == "__main__":
    main()
