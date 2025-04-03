import requests
from datetime import datetime, timedelta
from scrapers.base_scraper import BaseScraper
from urllib.parse import urlencode

class GoogleScraper(BaseScraper):
    def __init__(self, config):
        super().__init__(config)
        self.base_url = config["url"]
        self.keywords = config["keywords"]
        self.company_name = config["name"]
        
        self.year_of_exp = self.filter_config.get("max_years_experience", 5)
        self.max_post_day = self.filter_config.get("post_day", 30)
        self.locations = self.filter_config["locations"]


    def scrape(self):
        # base_url = company_config["url"]
        # keywords = company_config.get("keywords", [])
        # locations = company_config.get("locations", [])
        all_jobs = []

        for keyword in self.keywords:
            for location in self.locations:
                query = urlencode({"q": keyword, "location": location})
                url = f"{self.base_url}?{query}"

                response = requests.get(url)
                if response.status_code != 200:
                    print(f"❌ Failed to fetch for {keyword} in {location}")
                    continue

                data = response.json()
                # max_years = company_config.get("max_years_experience", 99)
                # max_days_post = company_config.get("post_day", 30)
                #print(json.dumps(data.get("jobs", []), indent=2))
                
                for job in data.get("jobs", []):
                    
                    job_id = job.get("id", "").split("/")[-1]
                    job_url = job.get("apply_url", "N/A")
                    

                    qual_html = job.get("qualifications", "")
                    if not self.get_required_experience_from_qualifications(qual_html, self.year_of_exp):
                        continue

                    if not self.is_recent(job.get("created"), self.max_post_day):
                        continue

                    all_jobs.append({
                        "company": self.company_name,
                        "title": job.get("title", "N/A"),
                        "id": job_id,
                        "location": job.get("locations", ["N/A"])[0]['display'],
                        "url": job_url,
                        "date_posted": job.get("created", "N/A")
                    })

        return all_jobs