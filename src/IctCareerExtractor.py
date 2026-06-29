import math
import re
import json
import requests


class IctCareerExtractor:
    """
    Extractor for ictcareer.ch (Next.js / JobCloud).

    ictcareer.ch embeds job data as JSON inside a
        <script id="__NEXT_DATA__" type="application/json">...</script>
    block – there is no window.jobsList injection like itjobs.ch uses.

    The page returns only `pageSize` jobs at a time (currently 10).
    Pass the portal URL to __init__ so the extractor can fetch the
    remaining pages automatically.
    """

    _NEXT_DATA_PATTERN = re.compile(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        re.DOTALL,
    )

    def __init__(self, url: str = ""):
        self.url = url
        self.filtered_jobs: list[dict] = []

    # ------------------------------------------------------------------
    # Public API (same interface as ItJobsExtractor)
    # ------------------------------------------------------------------

    def extract(self, html_content: str) -> list[dict]:
        """
        Extract all jobs starting from the already-fetched HTML (page 1),
        then paginate through the remaining pages using self.url.
        """
        page_data = self._parse_next_data(html_content)
        if page_data is None:
            return []

        result_count = page_data.get("resultCount", 0)
        page_size = page_data.get("pageSize", 10)
        total_pages = math.ceil(result_count / page_size) if page_size else 1

        # Collect jobs from the first (already-fetched) page
        self._collect_jobs(page_data.get("jobs", []))

        # Fetch any remaining pages (page 2, 3, …)
        if total_pages > 1 and self.url:
            for page_num in range(2, total_pages + 1):
                extra_html = self._fetch_page(page_num)
                if extra_html is None:
                    break
                extra_data = self._parse_next_data(extra_html)
                if extra_data is None:
                    break
                self._collect_jobs(extra_data.get("jobs", []))

        return self.filtered_jobs

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _parse_next_data(self, html_content: str) -> dict | None:
        """
        Locate the __NEXT_DATA__ JSON block and return the SSR jobs object:
            props → initialProps → pageProps → jobsSSR
        Returns None when the block is missing or unparseable.
        """
        match = self._NEXT_DATA_PATTERN.search(html_content)
        if not match:
            return None

        try:
            data = json.loads(match.group(1))
            return data["props"]["initialProps"]["pageProps"]["jobsSSR"]
        except (json.JSONDecodeError, KeyError):
            return None

    def _collect_jobs(self, jobs: list[dict]) -> None:
        """Filter raw job dicts down to the fields we care about."""
        for job in jobs:
            job_id = job.get("jcJobId") or job.get("jobId")
            apply_url = (
                f"https://ictcareer.ch/en/jobs/{job_id}" if job_id else "N/A"
            )

            tags = job.get("tags") or []
            tag_labels = ", ".join(t.get("label", "") for t in tags if isinstance(t, dict))

            self.filtered_jobs.append(
                {
                    "title": job.get("title") or "N/A",
                    "company": job.get("companyName") or "N/A",
                    "location": job.get("location") or "N/A",
                    "workload": job.get("workload") or "N/A",
                    "tags": tag_labels or "N/A",
                    "posted_at": job.get("datePosted") or "N/A",
                    "apply_to": apply_url,
                }
            )

    def _fetch_page(self, page_num: int) -> str | None:
        """GET the portal URL with ?page=<page_num> appended."""
        separator = "&" if "?" in self.url else "?"
        url = f"{self.url}{separator}page={page_num}"
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                return response.text
            print(f"[IctCareerExtractor] page {page_num} returned HTTP {response.status_code}")
        except requests.RequestException as exc:
            print(f"[IctCareerExtractor] failed to fetch page {page_num}: {exc}")
        return None


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    url = "https://ictcareer.ch/en/jobs?l=Zurich&workload=0-60"
    response = requests.get(url)
    html_data = response.text

    extractor = IctCareerExtractor(url=url)
    jobs = extractor.extract(html_data)

    print(f"Extracted {len(jobs)} jobs.")
    if jobs:
        for job in jobs[:3]:
            print(job)