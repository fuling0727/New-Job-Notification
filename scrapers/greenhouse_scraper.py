import requests
from scrapers.base_scraper import BaseScraper

class GreenhouseScraper(BaseScraper):
    def __init__(self, config):
        super().__init__(config)

    def scrape(self):
        all_jobs = []

        for slug in self.company_config.get("slugs", []):
            url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
            try:
                response = requests.get(url)
                if response.status_code != 200:
                    print(f"❌ Failed to fetch jobs from {slug}")
                    continue

                jobs = response.json().get("jobs", [])
                i = 0
                for job in jobs:
                    title = job.get("title", "").lower()
                    location = job.get("location", {}).get("name", "")
                    if i == 0:
                        print(job)
                        i += 1

                    if not self.check_title_ok(title):
                        continue

                    if not any(loc.lower() in location.lower() for loc in self.locations):
                        continue

                    if not any(kw.lower() in title for kw in self.keywords):
                        continue

                    if not self.get_required_experience_from_qualifications(job.get("description", ""), self.year_of_exp):
                        continue

                    all_jobs.append({
                        "company": slug.capitalize(),
                        "title": job.get("title"),
                        "id": job.get("id"),
                        "location": location,
                        "url": job.get("absolute_url"),
                        "date_posted": ""  # Greenhouse doesn't provide it
                    })
            except Exception as e:
                print(f"❌ Error parsing jobs from {slug}: {e}")

        return all_jobs
