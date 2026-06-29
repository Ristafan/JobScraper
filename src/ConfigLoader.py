import os
import json

class ConfigLoader:
    def __init__(self, num_priorities=1):
        self.job_configs = []
        self.job_portal_configs = []
        self.num_priorities = num_priorities

    # Import desired job configurations from the jobs.json file
    def import_job_configs(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Load the jobs.json file
        with open(os.path.join(current_dir, 'config/jobs.json'), 'r') as file:
            job_configs = json.load(file)

        # Unpack the job configurations into a list of dictionaries
        job_configs = [job_configs[job] for job in job_configs]

        # Make sure that the number of priorities requested does not exceed the available configurations
        if self.num_priorities > len(job_configs):
            raise ValueError(f"Requested {self.num_priorities} priorities, but only {len(job_configs)} are available.")

        # Save the specified number of priority levels
        self.job_configs = job_configs[:self.num_priorities]

    def import_jobPortal_configs(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Load the jobs.json file
        with open(os.path.join(current_dir, 'config\\jobPortals.json'), 'r') as file:
            job_portal_configs = json.load(file)

        # Unpack the job configurations into a list of dictionaries
        job_portal_configs = [job_portal_configs[job] for job in job_portal_configs]

        # Make sure that the number of priorities requested does not exceed the available configurations
        if self.num_priorities > len(job_portal_configs):
            raise ValueError(f"Requested {self.num_priorities} priorities, but only {len(job_portal_configs)} are available.")

        # Save the specified number of priority levels
        self.job_portal_configs = job_portal_configs[:self.num_priorities]