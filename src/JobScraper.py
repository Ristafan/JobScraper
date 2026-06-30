import html
import tempfile
import webbrowser
from datetime import datetime

from ConfigLoader import ConfigLoader
from SimpleJobScraper import SimpleJobScraper

from extractors.IctCareerExtractor import IctCareerExtractor
from extractors.ItJobsExtractor import ItJobsExtractor
from extractors.StudentJobChExtractor import StudentJobChExtractor


class JobScraper:
    def __init__(self, num_priorities=1):
        self.config_loader = ConfigLoader(num_priorities)
        self.config_loader.import_jobPortal_configs()
        self.job_portal_configs = self.config_loader.job_portal_configs
        self.config_loader.import_job_configs()
        self.job_configs = self.config_loader.job_configs

        self.extractors = {
            "itjobs.ch": ItJobsExtractor,
            "ictcareer.ch": IctCareerExtractor,
            "studentjob.ch": StudentJobChExtractor
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
        sections = []
        total = 0

        for portal_name, jobs in parsed_jobs.items():
            total += len(jobs)

            # Columns = union of all keys across this portal's jobs,
            # preserving first-seen order. Handles renamed/extra fields.
            columns = []
            for job in jobs:
                for key in job.keys():
                    if key not in columns:
                        columns.append(key)

            header_cells = "".join(
                f"<th>{html.escape(self._prettify_header(c))}</th>" for c in columns
            )

            body_rows = []
            for job in jobs:
                cells = "".join(
                    f"<td>{self._format_value(job.get(c))}</td>" for c in columns
                )
                body_rows.append(f"<tr>{cells}</tr>")

            rows_html = "".join(body_rows) or (
                f'<tr><td colspan="{len(columns) or 1}" class="muted">No jobs found.</td></tr>'
            )

            sections.append(f"""
            <section class="portal">
              <h2>{html.escape(portal_name)} <span class="count">{len(jobs)}</span></h2>
              <div class="table-wrap">
                <table>
                  <thead><tr>{header_cells}</tr></thead>
                  <tbody>{rows_html}</tbody>
                </table>
              </div>
            </section>
            """)

        document = self._build_html_document(sections, total)

        with tempfile.NamedTemporaryFile(
            "w", suffix=".html", delete=False, encoding="utf-8"
        ) as f:
            f.write(document)
            path = f.name

        webbrowser.open(f"file://{path}")
        print(f"Opened {total} jobs in your browser: {path}")

    def _prettify_header(self, key):
        # posted_at -> "Posted At"
        return key.replace("_", " ").title()

    def _format_value(self, value):
        # Empty-ish values -> muted dash
        if value is None or value == "" or value == "N/A":
            return '<span class="muted">—</span>'

        # Booleans -> coloured pill (check before str, bool is an int subclass)
        if isinstance(value, bool):
            cls, text = ("yes", "Yes") if value else ("no", "No")
            return f'<span class="pill {cls}">{text}</span>'

        text = str(value)

        # URLs -> clickable link (keeps long apply links from bloating the table)
        if text.startswith(("http://", "https://")):
            safe = html.escape(text, quote=True)
            return f'<a href="{safe}" target="_blank" rel="noopener">Open ↗</a>'

        # ISO timestamps -> friendlier format, otherwise raw text
        pretty = self._try_format_datetime(text)
        return html.escape(pretty if pretty else text)

    def _try_format_datetime(self, text):
        try:
            dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
            return dt.strftime("%d %b %Y, %H:%M")
        except (ValueError, TypeError):
            return None

    def _build_html_document(self, sections, total):
        body = "\n".join(sections) if sections else '<p class="muted">No jobs parsed.</p>'
        generated = datetime.now().strftime("%d %b %Y, %H:%M")

        # CSS kept in a plain string (not an f-string) so its { } braces
        # don't clash with Python formatting.
        head = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Scraped Jobs</title>
<style>
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background: #f4f5f7;
    color: #1f2430;
    line-height: 1.45;
  }
  .topbar {
    position: sticky; top: 0; z-index: 10;
    display: flex; align-items: baseline; gap: 16px;
    padding: 16px 28px;
    background: #ffffff;
    border-bottom: 1px solid #e5e7eb;
    box-shadow: 0 1px 3px rgba(0,0,0,.04);
  }
  .topbar h1 { font-size: 20px; margin: 0; font-weight: 650; }
  .topbar .meta { color: #6b7280; font-size: 13px; }
  main { padding: 28px; max-width: 1400px; margin: 0 auto; }
  .portal {
    background: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,.05);
    margin-bottom: 28px;
    overflow: hidden;
  }
  .portal h2 {
    margin: 0; padding: 14px 18px;
    font-size: 15px; font-weight: 600;
    border-bottom: 1px solid #eef0f3;
    display: flex; align-items: center; gap: 10px;
  }
  .portal h2 .count {
    background: #eef2ff; color: #4338ca;
    font-size: 12px; font-weight: 600;
    padding: 2px 9px; border-radius: 999px;
  }
  .table-wrap { max-height: 70vh; overflow: auto; }
  table { border-collapse: collapse; width: 100%; font-size: 13.5px; }
  thead th {
    position: sticky; top: 0;
    background: #fafbfc;
    text-align: left;
    text-transform: uppercase;
    letter-spacing: .04em;
    font-size: 11px; font-weight: 600;
    color: #6b7280;
    padding: 10px 14px;
    border-bottom: 1px solid #e5e7eb;
    white-space: nowrap;
  }
  tbody td {
    padding: 11px 14px;
    border-bottom: 1px solid #f1f2f4;
    vertical-align: top;
  }
  tbody tr:last-child td { border-bottom: none; }
  tbody tr:hover { background: #f7f9ff; }
  a { color: #2563eb; text-decoration: none; font-weight: 500; }
  a:hover { text-decoration: underline; }
  .muted { color: #9aa0aa; }
  .pill {
    display: inline-block;
    font-size: 11px; font-weight: 600;
    padding: 2px 9px; border-radius: 999px;
  }
  .pill.yes { background: #dcfce7; color: #15803d; }
  .pill.no  { background: #f1f2f4; color: #6b7280; }
</style>
</head>
<body>
"""
        topbar = (
            '<header class="topbar">'
            "<h1>Scraped Jobs</h1>"
            f'<div class="meta">{total} jobs · generated {generated}</div>'
            "</header><main>"
        )
        return head + topbar + body + "</main></body></html>"

    

if __name__ == "__main__":
    job_scraper = JobScraper()
    parsed_jobs = job_scraper.run_scraper()