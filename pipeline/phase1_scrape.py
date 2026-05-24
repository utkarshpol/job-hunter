import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from utils.job_scraper import scrape_careers_page
from utils.job_relevence_finder import filter_jobs
from utils.job_details_extractor import extract_job_details
import json


CAREERS_URL = {"Razorpay":"https://razorpay.com/jobs/jobs-all/"}


def scrape_and_process_jobs():
    print("Scraping careers page...")
    uni_results = []
    for company, url in CAREERS_URL.items():
        jobs = scrape_careers_page(url)
        print("Total links:", len(jobs))

        print("Filtering relevant jobs...")
        filtered_jobs = filter_jobs(jobs)
        print("Relevant jobs:", len(filtered_jobs))

        results = []
        for job in filtered_jobs[:5]:
            print("\nProcessing:", job["title"])
            details = extract_job_details(job["url"])
            details["job_url"] = job["url"]
            results.append(details)
        
        uni_results.append({"company": company, "jobs": results})
        print("\nDONE WITH SCRAPING AND PROCESSING CAREER SITES")
    
    return uni_results