import requests
from typing import List
from urllib.parse import urlencode
from scrapers.base_scraper import BaseScraper

class AmazonScraper(BaseScraper):
    def __init__(self, config):
        super().__init__(config)
        self.base_url = config["url"]

    def scrape(self) -> List[dict]:
        print("Scraping Amazon jobs...")
        all_jobs = []

        for keyword in self.keywords:
            for location in self.locations:
                params = {
                    "base_query": keyword,
                    "loc_query": location,
                    "job_type": "Full-Time",
                    "offset": 0,
                    "limit": 100
                }
                url = f"{self.base_url}?{urlencode(params)}"
                response = requests.get(url)

                if response.status_code != 200:
                    print(f"Failed to fetch for {keyword} in {location}: {response.status_code}")
                    continue

                try:
                    data = response.json()
                    for job in data.get("jobs", []):
                        job_title = job.get("title", "").lower()
                        #if not is_job_active()
                        if not self.check_title_ok(job_title):
                            continue

                        if not self.is_recent(job.get("posted_date"), self.max_post_day):
                            continue

                        if not self.get_required_experience_from_qualifications(job.get("description", ""), self.year_of_exp):
                            continue

                        all_jobs.append({
                            "company": self.company_name,
                            "title": job.get("title", "N/A"),
                            "id": job.get("id", "N/A"),
                            "location": job.get("location", "N/A"),
                            "url": f"https://www.amazon.jobs{job['job_path']}",
                            "date_posted": job.get("posted_date", "N/A")
                        })
                except Exception as e:
                    print(f"Failed to parse Amazon jobs: {e}")

        return all_jobs
