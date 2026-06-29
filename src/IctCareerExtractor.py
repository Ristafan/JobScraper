import re
import json

class IctCareerExtractor:
    def __init__(self):
        self.filtered_jobs = []

    def extract(self, html_content):
        # Target the Next.js specific JSON injection
        pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
        match = re.search(pattern, html_content, re.DOTALL)
        
        if not match:
            # Return empty list if the Next.js data block is missing
            return []
            
        try:
            # Parse the JSON state object
            json_data = json.loads(match.group(1))
            
            # Navigate the deeply nested Next.js state tree to find the jobs array
            # We use .get() chaining to avoid KeyError if the site structure changes slightly
            jobs_list = (json_data.get("props", {})
                                  .get("initialState", {})
                                  .get("jobs", {})
                                  .get("jobs", {})
                                  .get("jobs", []))
            
            for job in jobs_list:
                # Map the site-specific keys to your unified schema
                filtered_job = {
                    "title": job.get("title", "N/A"),
                    "company": job.get("companyName", "N/A"),  # Mapped from companyName
                    "location": job.get("location", "N/A"),
                    "status": "active",  # Assumed active if present in payload
                    "remote": "N/A",     # Not provided in this payload
                    "posted_at": job.get("datePosted", "N/A"), # Mapped from datePosted
                    "updated_at": "N/A", # Not provided in this payload
                    "job_expires_in_days": "N/A", # Not provided in this payload
                    # Construct the application URL using the unique jobId
                    "apply_to": f"https://ictcareer.ch/en/job/{job.get('jobId')}" if job.get("jobId") else "N/A"
                }
                self.filtered_jobs.append(filtered_job)

            return self.filtered_jobs

        except json.JSONDecodeError:
            return []

# Example usage
if __name__ == "__main__":
    # Ensure you load the HTML file you provided
    with open("view-source_https___ictcareer.ch_en_jobs_l=Zurich.html", "r", encoding="utf-8") as file:
        html_data = file.read()
        
    extractor = IctCareerExtractor()
    jobs = extractor.extract(html_data)

    print(f"Extracted {len(jobs)} jobs.")
    if jobs:
        print(json.dumps(jobs[0], indent=4))