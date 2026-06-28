import os
import json
import requests


# Import desired job configurations from the jobs.json file
def import_job_configs(num_priorities: int) -> list:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load the jobs.json file
    with open(os.path.join(current_dir, 'config\\jobs.json'), 'r') as file:
        job_configs = json.load(file)

    # Unpack the job configurations into a list of dictionaries
    job_configs = [job_configs[job] for job in job_configs]

    # Make sure that the number of priorities requested does not exceed the available configurations
    if num_priorities > len(job_configs):
        raise ValueError(f"Requested {num_priorities} priorities, but only {len(job_configs)} are available.")

    # Return the specified number of priority levels
    return job_configs[:num_priorities]


class Scraper:
    def __init__(self, job_configs: list):
        self.job_configs = job_configs
        self.found_jobs = []

    def scrape_jobs(self):
        for job in self.job_configs:
            url = job['url']
            api_endpoint = job.get('apiEndpoint', '')
            needs_special_instructions = job.get('needsSpecialInstructions', False)
            special_instructions = job.get('specialInstructions', '')

            if needs_special_instructions:
                self.prepare_special_instructions(special_instructions)

            # Fetch web content (this is a placeholder for actual scraping logic)
            self.get_web_content(url + api_endpoint)

    
    def get_job_names(self):
        job_names = [job['name'] for job in self.job_configs]
        return job_names
    
    def get_web_content(self):
        # Placeholder for fetching web content
        print(f"Fetching content from {url}")
        # Here you would implement the actual logic to fetch web content

    def prepare_special_instructions(self):
        pass



if __name__ == "__main__":
    # Example usage: Import the first 3 job configurations
    job_configs = import_job_configs(1)
    print(job_configs)