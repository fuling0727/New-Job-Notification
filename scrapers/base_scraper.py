from abc import ABC, abstractmethod
from typing import List
from datetime import datetime, timezone
from bs4 import BeautifulSoup
import re
from utils.config_loader import load_config_for_filter

class BaseScraper(ABC):
    def __init__(self, config: dict):
        self.company_config = config
        self.filter_config = load_config_for_filter()

    @abstractmethod
    def scrape(self, max_days_old: int) -> List[dict]:
        pass

    def is_recent(self, publish_date_str: str, max_days_old: int) -> bool:
        if not publish_date_str:
            return False
        try:
            publish_date = datetime.fromisoformat(publish_date_str.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            return (now - publish_date).days <= max_days_old
        except Exception as e:
            print(f"Date parsing error: {e}")
            return False

    def is_entry_level(self, qual_html: str, max_years: int) -> bool:
        if not qual_html:
            return True  # No info = keep it

        soup = BeautifulSoup(qual_html, "html.parser")
        plain_text = soup.get_text()

        # Match patterns like: "2+ years", "2 years", "3 years of experience"
        matches = re.findall(r"(\d+)\+?\s+years?\s+of\s+experience", plain_text, flags=re.IGNORECASE)
        for match in matches:
            if int(match) > max_years:
                return False
        return True
    
    def get_required_experience_from_qualifications(self, qual_html, max_years):
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
