from utils.config_loader import load_config_for_company
from scrapers import GoogleScraper
import sys
import os
import json
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

SCRAPER_MAP = {
    "google": GoogleScraper,
    # Add more companies here
}

def main():
    company = "google"
    company_config = load_config_for_company(company)
    
    if not company_config:
        raise ValueError(f"No config found for company: {company}")

    scraper_class = SCRAPER_MAP[company]
    scraper = scraper_class(company_config)
    jobs = scraper.scrape()

    #print(f"\n{len(jobs)} jobs found for {company}:")
    output_path = Path("results.json")
    with open(output_path, "w") as f:
        json.dump(jobs, f, indent=2)
    print(f"✅ {len(jobs)} jobs saved to {output_path.resolve()}")

if __name__ == "__main__":
    main()
