"""Extractor for studentjob.ch ( /stellenangebote ) job-listing HTML."""

from __future__ import annotations

import re
import json
from bs4 import BeautifulSoup
import requests

BASE_URL = "https://www.studentjob.ch/stellenangebote?region_name=&search%5Bregions%5D%5Bid%5D=&search%5Bprovinces%5D%5Bid%5D=&job_guide_name=&search%5Bzipcode_eq%5D=&search%5Bkeywords_scope%5D=&search%5Bjob_types%5D%5Bid%5D%5B%5D=2&search%5Bjob_types%5D%5Bid%5D%5B%5D=4&search%5Bjob_types%5D%5Bid%5D%5B%5D=12&search%5Bjob_types%5D%5Bid%5D%5B%5D=5&search%5Bjob_types%5D%5Bid%5D%5B%5D=3&search%5Bjob_types%5D%5Bid%5D%5B%5D=14&search%5Bjob_types%5D%5Bid%5D%5B%5D=9&search%5Bjob_types%5D%5Bid%5D%5B%5D=6&search%5Bjob_types%5D%5Bid%5D%5B%5D=1&search%5Bfunctions%5D%5Bid%5D%5B%5D=11"


class StudentJobChExtractor:
    def __init__(self) -> None:
        self.filtered_jobs: list[dict] = []

    def extract(self, html) -> list[dict]:
        self.filtered_jobs = []
        soup = BeautifulSoup(html, "html.parser")
        
        # find every job card by class name and target attribute
        cards = soup.select("a.job-opening__item[data-job-opening-id]")
        for card in cards:
            job = self._parse_card(card)
            if job:
                self.filtered_jobs.append(job)
                
        return self.filtered_jobs

    def _parse_card(self, card) -> dict | None:
        job_id = card.get("data-job-opening-id")
        if not job_id:
            return None

        href = card.get("href", "")
        url = href if href.startswith("http") else f"{BASE_URL}{href}"
        title = card.get("data-job-opening-title") or self._text(card.find("h3"))

        company = card.get("data-job-opening-item-brand") or None
        logo = card.find("img", class_="job-opening__customer-logo")
        if logo is not None:
            company = company or logo.get("title") or logo.get("alt")

        location = self._field_after_icon(card, "nyc-icon-location")

        # map data to your standardized job_infos schema format
        return {
            "title": (title or "").strip(),
            "company": company.strip() if company else "N/A",
            "location": location if location else "N/A",
            "status": "active",
            "remote": "N/A",
            "posted_at": "N/A",
            "updated_at": "N/A",
            "job_expires_in_days": "N/A",
            "apply_to": url
        }

    def _field_after_icon(self, card, icon_class: str) -> str | None:
        icon = card.find("span", class_=icon_class)
        if icon is None:
            return None
        value = icon.find_next_sibling("span")
        text = self._text(value)
        return text or None

    @staticmethod
    def _text(node) -> str | None:
        if node is None:
            return None
        return re.sub(r"\s+", " ", node.get_text(strip=True)) or None

    @staticmethod
    def _to_int(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _to_float(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None


if __name__ == "__main__":
    response = requests.get(BASE_URL)
    html_str = response.text

    extractor = StudentJobChExtractor()
    extractor.extract(html_str)
    print(f"Extracted {len(extractor.filtered_jobs)} jobs\n")
    print(json.dumps(extractor.filtered_jobs[:3], indent=2, ensure_ascii=False))