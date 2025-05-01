from utils.config_loader import load_config_for_company
from scrapers.google_scraper import GoogleScraper
from scrapers.meta_scraper import MetaScraper
from scrapers.amazon_scraper import AmazonScraper
from scrapers.greenhouse_scraper import GreenhouseScraper
import sys
import os
import json
from pathlib import Path
from datetime import datetime
from utils.email_notifier import send_email 

from dotenv import load_dotenv

load_dotenv()

sender_email = os.getenv("EMAIL_SENDER")
sender_password = os.getenv("EMAIL_PASSWORD")
recipient_email = os.getenv("EMAIL_RECIPIENT")


# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

SCRAPER_MAP = {
    "google": GoogleScraper,
    #"meta": MetaScraper
    "amazon": AmazonScraper,
    "greenhouse": GreenhouseScraper
}

def main():
    summary_lines = []
    for company in SCRAPER_MAP:
        print(f"\nScraping jobs from {company.capitalize()}...")
        company_config = load_config_for_company(company)
        
        if not company_config:
            print(f"⚠️  No config found for company: {company}")
            continue

        scraper_class = SCRAPER_MAP[company]
        scraper = scraper_class(company_config)
        jobs = scraper.scrape()

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(f"results/{company}_{timestamp}.json")

        # Ensure results folder exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(jobs, f, indent=2)
        print(f"{len(jobs)} jobs saved to {output_path.resolve()}")
        summary_lines.append(f"{company.capitalize()}: {len(jobs)} jobs")

    subject = "Job Scraper Notification"
    body = "Here is the summary of today's scraping:\n\n" + "\n".join(summary_lines)
    send_email(
        subject,
        body,
        recipient_email=recipient_email,
        sender_email=sender_email,
        sender_password=sender_password
    )

if __name__ == "__main__":
    main()
