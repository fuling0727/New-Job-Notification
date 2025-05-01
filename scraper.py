import requests
import json
from urllib.parse import urlencode
from pathlib import Path
import re
from bs4 import BeautifulSoup
from datetime import datetime, timezone


def load_config(config_path="config.json"):
    with open(config_path, "r") as f:
        return json.load(f)

def fetch_google_jobs(company_config):
    base_url = company_config["url"]
    keywords = company_config.get("keywords", [])
    locations = company_config.get("locations", [])
    all_jobs = []

    for keyword in keywords:
        for location in locations:
            query = urlencode({"q": keyword, "location": location})
            url = f"{base_url}?{query}"

            response = requests.get(url)
            if response.status_code != 200:
                print(f"❌ Failed to fetch for {keyword} in {location}")
                continue

            data = response.json()
            max_years = company_config.get("max_years_experience", 99)
            max_days_post = company_config.get("post_day", 30)
            #print(json.dumps(data.get("jobs", []), indent=2))
            
            for job in data.get("jobs", []):
                
                job_id = job.get("id", "").split("/")[-1]
                job_url = job.get("apply_url", "N/A")
                

                qual_html = job.get("qualifications", "")
                if not get_required_experience_from_qualifications(qual_html, max_years):
                    continue

                if not is_recent(job.get("created"), max_days_post):
                    continue

                all_jobs.append({
                    "company": company_config["name"],
                    "title": job.get("title", "N/A"),
                    "location": job.get("locations", ["N/A"])[0]['display'],
                    "url": job_url,
                    "date_posted": job.get("created", "N/A")
                })

    return all_jobs

def get_required_experience_from_qualifications(qual_html, max_years=2):
    if not qual_html:
        return True  # No info = keep it

    # Strip HTML tags
    soup = BeautifulSoup(qual_html, "html.parser")
    plain_text = soup.get_text()

    # Find all "X years of experience" phrases
    matches = re.findall(r"(\d+)\+? years? of experience", plain_text, flags=re.IGNORECASE)
    for match in matches:
        if int(match) > max_years:
            return False  # Too senior
    return True

def is_recent(publish_date_str, max_days_old):
    if not publish_date_str:
        return False
    publish_date = datetime.fromisoformat(publish_date_str.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    return (now - publish_date).days <= max_days_old

def main():
    config = load_config()
    all_results = []

    for company in config["companies"]:
        if "google.com" in company["url"]:
            print(f"🔍 Scraping jobs for {company['name']} using API...")
            jobs = fetch_google_jobs(company)
            all_results.extend(jobs)
        else:
            print(f"⚠️ No handler implemented for {company['name']}")

    output_path = Path("results.json")
    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"✅ {len(all_results)} jobs saved to {output_path.resolve()}")

if __name__ == "__main__":
    main()
