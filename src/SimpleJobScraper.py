import requests
from ConfigLoader import ConfigLoader


# The jobscraper has one jobs:
# Scrape the jobs from the specified urls and returning the results as an html string (only if the url contains the filterquery) 
class SimpleJobScraper:
    def __init__(self, jobPortalConfigs):
        self.jobPortal_configs = jobPortalConfigs
        self.jobs_html = {}

    def scrape_jobs(self):
        for jobs in self.jobPortal_configs:
            portal_name = jobs.get('name', 'Unknown Portal')
            url = jobs.get('url', '')
            request_method = jobs.get('requestMethod', 'GET')
            needs_special_instructions = jobs.get('needsSpecialInstructions', False)

            if needs_special_instructions:
                raise NotImplementedError(f"Special instructions are required for {url}. Please implement the necessary logic.")

            self.get_web_content(portal_name, url, request_method=request_method)

    
    def get_web_content(self, portal_name, url, request_method='GET', headers=None, params=None):
        
        if request_method.upper() == 'GET':
            response = requests.get(url)
        elif request_method.upper() == 'POST':
            response = requests.post(url, headers=headers, data=params)

        if response.status_code == 200:
            html_content = response.text
            self.jobs_html[portal_name] = html_content
        else:
            print(f"Failed to fetch content from {url}. Status code: {response.status_code}")


if __name__ == "__main__":
    # Example usage: Import configs
    config_loader = ConfigLoader()
    config_loader.import_jobPortal_configs()

    scraper = SimpleJobScraper(config_loader.job_portal_configs)
    scraper.scrape_jobs()
    
    print(f"Found jobs: {scraper.jobs_html.keys()}")