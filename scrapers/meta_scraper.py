from scrapers.base_scraper import BaseScraper
from typing import List
import requests

class MetaScraper(BaseScraper):
    def scrape(self) -> List[dict]:
        print("Scraping Meta jobs...")
        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        # Sample GraphQL payload for Meta
        payload = {
            "query": """
            query Jobs($limit: Int!) {
                jobs(first: $limit) {
                    edges {
                        node {
                            id
                            title
                            listedLocation
                            postedDate
                            jobFunction
                            description
                        }
                    }
                }
            }
            """,
            "variables": {"limit": 100}
        }
        # payload = {
        #     "q": "software engineer",
        #     "locale": "en_us",
        #     "limit": 25
        # }
        print(self.base_url)
        res = requests.post("https://www.metacareers.com/graphql", json=payload, headers=headers)
        print(res)
        jobs = []
        try:
            data = res.json()
            i = 0
            for edge in data["data"]["jobs"]["edges"]:
                # if i == 0:
                #     print(edge)
                #     i += 1
                job = edge["node"]
                if not self.is_recent(job["postedDate"], self.max_post_day):
                    continue
                if not self.get_required_experience_from_qualifications(job.get("description", ""), self.year_of_exp):
                    continue
                job_title = job["title"].lower()
                if not self.check_title_ok(job_title):
                        continue

                jobs.append({
                    "title": job["title"],
                    "location": job["listedLocation"],
                    "url": f"https://www.metacareers.com/jobs/{job['id']}",
                    "description": job.get("description", "")
                })
        except Exception as e:
            print(f"Failed to parse Meta jobs: {e}")
        return jobs
