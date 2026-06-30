import requests
import re
import json
from urllib.parse import urlparse

class ItBoardPraktikumExtractor:
    def __init__(self):
        self.filtered_jobs = []

    def extract(self, html_content):
        """
        Extract internship positions from itboard.ch HTML content.
        Saves filtered jobs to self.filtered_jobs without returning.
        
        Args:
            html_content: HTML string from itboard.ch/praktikumsstellen
        """
        # Define the keys we want to extract from each job dictionary
        job_infos = [
            "id", 
            "title", 
            "company", 
            "location", 
            "jobType",
            "remote", 
            "postedAt", 
            "expiresAt",
            "description",
            "applicationsCount",
            "url"
        ]

        jobs_data = []
        
        # Primary method: Extract from Schema.org ItemList format (most reliable)
        jobs_data = self._extract_from_schema_org(html_content)
        
        # Fallback: Try other patterns if Schema.org doesn't work
        if not jobs_data:
            jobs_data = self._extract_from_other_formats(html_content)
        
        # Filter and process the jobs
        self.filtered_jobs = []
        
        if jobs_data:
            for job in jobs_data:
                if isinstance(job, dict):
                    # Normalize field names (handle both camelCase and snake_case)
                    normalized_job = self._normalize_job_data(job)
                    
                    # Filter the job dictionary to only include relevant information
                    filtered_job = {
                        key: normalized_job.get(key, "N/A") 
                        for key in job_infos
                    }
                    self.filtered_jobs.append(filtered_job)
        
        # Return filtered jobs for compatibility with scraper
        return self.filtered_jobs

    def _extract_from_schema_org(self, html_content):
        """
        Extract job data from Schema.org ItemList format.
        This is the primary data source on itboard.ch.
        """
        jobs = []
        
        # Find all Schema.org scripts
        script_pattern = r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>'
        scripts = re.findall(script_pattern, html_content, re.DOTALL)
        
        for script_content in scripts:
            try:
                data = json.loads(script_content)
                
                # Look for ItemList with job entries
                if data.get('@type') == 'ItemList' and 'itemListElement' in data:
                    items = data.get('itemListElement', [])
                    
                    # Check if items contain job URLs (contain /job/)
                    if items and any('/job/' in str(item.get('url', '')) for item in items):
                        for item in items:
                            job = {
                                'position': item.get('position'),
                                'url': item.get('url'),
                                'name': item.get('name')
                            }
                            
                            # Extract structured info from URL
                            url = item.get('url', '')
                            if url:
                                # Parse job title and company from URL
                                # URL format: .../job/[title]-at-[company]-[id]
                                url_parts = url.split('/job/')[-1]  # Get everything after /job/
                                
                                # Extract company (between 'at-' and the UUID)
                                company_match = re.search(r'-at-(.+?)-[a-f0-9\-]{36}$', url_parts)
                                if company_match:
                                    company = company_match.group(1).replace('-', ' ').title()
                                    job['company'] = company
                                
                                # Extract title (everything before ' at ')
                                title_part = url_parts.split('-at-')[0] if '-at-' in url_parts else url_parts
                                title = title_part.replace('-', ' ').title()
                                job['title'] = title
                                
                                # Extract ID from URL
                                id_match = re.search(r'([a-f0-9\-]{36})$', url_parts)
                                if id_match:
                                    job['id'] = id_match.group(1)
                            
                            jobs.append(job)
                        
                        # Found job listings, no need to check other scripts
                        break
                        
            except json.JSONDecodeError:
                pass
        
        return jobs

    def _extract_from_other_formats(self, html_content):
        """
        Fallback method to extract job data from other formats or HTML elements.
        """
        jobs = []
        
        # Try multiple patterns to find job data in the HTML
        patterns = [
            r'window\.__NEXT_DATA__\s*=\s*({.*?});',
            r'<script[^>]*type="application/json"[^>]*>(.*?)</script>',
            r'"jobs":\s*\[(.*?)\](?:,|$|\})',
            r'window\.praktikumsList\s*=\s*(\[.*?\]);',
            r'"praktikumsstellen":\s*(\[.*?\])',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html_content, re.DOTALL)
            if match:
                json_string = match.group(1)
                try:
                    data = json.loads(json_string)
                    
                    if isinstance(data, dict):
                        # Look for jobs array in the dict
                        for key in ['jobs', 'praktikumsstellen', 'positions', 'internships', 'listings']:
                            if key in data and isinstance(data[key], list):
                                return data[key]
                    elif isinstance(data, list):
                        return data
                        
                except json.JSONDecodeError:
                    continue
        
        # Last resort: try HTML element parsing
        return self._extract_from_html_elements(html_content)

    def _normalize_job_data(self, job):
        """
        Normalize job data by handling different field name conventions.
        """
        normalized = {}
        
        # Map potential field names to standard names
        field_mapping = {
            'title': ['title', 'jobTitle', 'position', 'positionName'],
            'company': ['company', 'employer', 'companyName', 'organization'],
            'location': ['location', 'city', 'place', 'workLocation'],
            'jobType': ['jobType', 'type', 'employment_type', 'employmentType'],
            'remote': ['remote', 'isRemote', 'remoteWork', 'workFromHome'],
            'postedAt': ['postedAt', 'posted_at', 'createdAt', 'created_at', 'publishedAt'],
            'expiresAt': ['expiresAt', 'expires_at', 'deadline', 'applicationDeadline'],
            'description': ['description', 'jobDescription', 'summary', 'details'],
            'applicationsCount': ['applicationsCount', 'applications_count', 'applicationCount'],
            'url': ['url', 'link', 'jobUrl', 'apply_to', 'applyTo'],
            'id': ['id', 'jobId', 'job_id', 'postId'],
        }
        
        for standard_key, alternative_keys in field_mapping.items():
            for alt_key in alternative_keys:
                if alt_key in job:
                    normalized[standard_key] = job[alt_key]
                    break
            # If not found in alternatives, use original if it exists
            if standard_key not in normalized and standard_key in job:
                normalized[standard_key] = job[standard_key]
        
        return normalized

    def _extract_from_html_elements(self, html_content):
        """
        Fallback method to extract job data from HTML elements if JSON is not found.
        Looks for common HTML patterns used in job listings.
        """
        jobs = []
        
        # Look for job containers with common class patterns
        job_patterns = [
            r'<article[^>]*class="[^"]*job[^"]*"[^>]*>(.*?)</article>',
            r'<div[^>]*class="[^"]*job-item[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*data-job-id="[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*class="[^"]*position[^"]*"[^>]*>(.*?)</div>',
        ]
        
        for pattern in job_patterns:
            containers = re.findall(pattern, html_content, re.DOTALL)
            if containers:
                for container in containers:
                    job = {}
                    
                    # Extract title from various heading tags
                    title_match = re.search(r'<h[1-6][^>]*>([^<]*)</h[1-6]>', container)
                    if title_match:
                        job['title'] = title_match.group(1).strip()
                    
                    # Extract company
                    company_match = re.search(
                        r'<(?:div|span)[^>]*class="[^"]*(?:company|employer)[^"]*"[^>]*>([^<]*)<',
                        container
                    )
                    if company_match:
                        job['company'] = company_match.group(1).strip()
                    
                    # Extract location
                    location_match = re.search(
                        r'<(?:div|span)[^>]*class="[^"]*location[^"]*"[^>]*>([^<]*)<',
                        container
                    )
                    if location_match:
                        job['location'] = location_match.group(1).strip()
                    
                    # Extract URL
                    url_match = re.search(r'href="([^"]*)"', container)
                    if url_match:
                        url = url_match.group(1)
                        if '/job/' in url:
                            job['url'] = url
                    
                    if job:
                        jobs.append(job)
                
                if jobs:
                    break
        
        return jobs


# Example usage
if __name__ == "__main__":
    # Example: Fetch from itboard.ch
    try:
        response = requests.get("https://www.itboard.ch/praktikumsstellen")
        html_data = response.text
        
        extractor = ItBoardPraktikumExtractor()
        extractor.extract(html_data)
        
        print(f"Extracted {len(extractor.filtered_jobs)} internship positions.")
        if extractor.filtered_jobs:
            print("\nFirst 3 positions:")
            for job in extractor.filtered_jobs[:3]:
                print(f"  - {job.get('title', 'N/A')} at {job.get('company', 'N/A')} ({job.get('location', 'N/A')})")
    except Exception as e:
        print(f"Error: {e}")