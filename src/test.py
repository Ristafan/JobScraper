import requests
import re
import json

class ItJobsExtractor:
    def __init__(self, html_content):
        self.html_content = html_content

    def extract(self):
        # target the specific javascript array injection
        pattern = r"window\.jobsList\.concat\(\[(.*?)\]\);"
        
        # search the entire html document for the pattern
        match = re.search(pattern, self.html_content, re.DOTALL)
        
        if not match:
            # return empty list if the data block is missing
            return []
            
        # reconstruct the json array format
        json_string = f"[{match.group(1)}]"
        
        try:
            # parse the string into python dictionaries
            jobs_data = json.loads(json_string)
            return jobs_data
        except json.JSONDecodeError:
            # handle potential parsing failures gracefully
            return []

# example usage
if __name__ == "__main__":
    response = requests.get("https://www.itjobs.ch/jobs?q=&category=&job_type=50075&location=Z%C3%BCrich%2C+Kanton+Z%C3%BCrich%2C+Schweiz&location_id=1040687")
    print(response.status_code)

    # convert the response content to string for processing
    html_data = response.text
        
    extractor = ItJobsExtractor(html_data)
    jobs = extractor.extract()

    jobInfosToPrint = ["title", "company", "location", "status", "remote", "posted_at", "updated_at", "job_expires_in_days", "url"]
    
    print(f"extracted {len(jobs)} jobs.")
    if jobs:
        for job in jobs:
            job_info = {key: job.get(key, "N/A") for key in jobInfosToPrint}
            print(job_info)
