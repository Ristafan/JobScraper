

from ConfigLoader import ConfigLoader
from SimpleJobScraper import SimpleJobScraper

from ItJobsExtractor import ItJobsExtractor


class JobScraper:
    def __init__(self, num_priorities=1):
        self.config_loader = ConfigLoader(num_priorities)
        self.config_loader.import_jobPortal_configs()
        self.job_portal_configs = self.config_loader.job_portal_configs
        self.config_loader.import_job_configs()
        self.job_configs = self.config_loader.job_configs

        self.extractors = {
            "itjobs.ch": ItJobsExtractor,
        }

    def run_scraper(self):
        jobs_html = self.scrape_jobs()
        parsed_jobs = self.parse_jobs_html(jobs_html)
        self.print_parsed_jobs(parsed_jobs)
        return parsed_jobs

    def scrape_jobs(self):
        simple_scraper = SimpleJobScraper(self.config_loader.job_portal_configs)
        simple_scraper.scrape_jobs()
        return simple_scraper.jobs_html
    
    def parse_jobs_html(self, jobs_html):
        parsed_jobs = {}

        for portal_name, html_content in jobs_html.items():
            if portal_name in self.extractors:
                extractor = self.extractors[portal_name]()
                parsed_jobs[portal_name] = extractor.extract(html_content)
            else:
                print(f"No extractor defined for {portal_name}. Skipping parsing.")

        return parsed_jobs
    
    def print_parsed_jobs(self, parsed_jobs):
        for portal_name, jobs in parsed_jobs.items():
            print(f"Parsed {len(jobs)} jobs from {portal_name}.")
            for job in jobs:
                print(job)

    

if __name__ == "__main__":
    job_scraper = JobScraper()
    parsed_jobs = job_scraper.run_scraper()