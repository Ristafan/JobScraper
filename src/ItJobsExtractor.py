import requests
import re
import json

class ItJobsExtractor:
    def __init__(self):
        self.filtered_jobs = []

    def extract(self, html_content):
        # Define the keys we want to extract from each job dictionary
        job_infos = ["title", "company", "location", "status", "remote", "posted_at", "updated_at", "job_expires_in_days", "apply_to"]

        # target the specific javascript array injection
        pattern = r"window\.jobsList\.concat\(\[(.*?)\]\);"
        
        # search the entire html document for the pattern
        match = re.search(pattern, html_content, re.DOTALL)
        
        if not match:
            # return empty list if the data block is missing
            return []
            
        # reconstruct the json array format
        json_string = f"[{match.group(1)}]"
        
        try:
            # parse the string into python dictionaries
            jobs_data = json.loads(json_string)

            for job in jobs_data:
                # Filter the job dictionary to only include relevant information
                filtered_job = {key: job.get(key, "N/A") for key in job_infos}
                self.filtered_jobs.append(filtered_job)

            return self.filtered_jobs

        except json.JSONDecodeError:
            # handle potential parsing failures gracefully
            return []
        

# example usage
if __name__ == "__main__":
    response = requests.get("https://www.itjobs.ch/jobs?q=&category=&job_type=50075&location=Z%C3%BCrich%2C+Kanton+Z%C3%BCrich%2C+Schweiz&location_id=1040687")

    # convert the response content to string for processing
    html_data = response.text
        
    extractor = ItJobsExtractor()
    jobs = extractor.extract(html_data)

    
    print(f"extracted {len(jobs)} jobs.")
    if jobs:
        print(jobs)