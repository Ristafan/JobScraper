import os
import json


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




if __name__ == "__main__":
    # Example usage: Import the first 3 job configurations
    job_configs = import_job_configs(1)
    print(job_configs)