import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from utils.job_scraper import scrape_careers_page
from utils.job_relevence_finder import filter_jobs
from utils.job_details_extractor import extract_job_details
import json


CAREERS_URL = {
    "Airbus": "https://ag.wd3.myworkdayjobs.com/Airbus",
    "Apollo.io": "https://www.apollo.io/careers#open-roles",
    "Cisco": "https://jobs.cisco.com/jobs/SearchJobs",
    "Disney+ Hotstar": "https://careers.hotstar.com/jobs",
    "Magicpin": "https://magicpin.darwinbox.in/ms/candidate/careers",
    "Mercedes-Benz Research and Development India": "https://jobs.mercedes-benz.com/en_US/jobs",
    "Qualcomm": "https://careers.qualcomm.com/careers",
    "ServiceNow": "https://jobs.smartrecruiters.com/ServiceNow",
    "Accenture": "https://www.accenture.com/in-en/careers/jobsearch",
    "Adobe": "https://careers.adobe.com/us/en/search-results",
    "Amazon": "https://www.amazon.jobs/en/search",
    "AMD": "https://careers.amd.com/careers-home/jobs",
    "American Express": "https://aexp.eightfold.ai/careers",
    "Amex": "https://aexp.eightfold.ai/careers",
    "Apple": "https://jobs.apple.com/en-in/search",
    "Autodesk": "https://autodesk.wd1.myworkdayjobs.com/Ext",
    "Axis Bank": "https://www.axisbank.com/careers/current-openings",
    "Azure Power": "https://www.azurepower.com/careers/#current-openings",
    "Barclays": "https://search.jobs.barclays/search-jobs",
    "BCG": "https://careers.bcg.com/global/en/search-results",
    "BlackRock": "https://careers.blackrock.com/job-search",
    "Blinkit": "https://blinkit.com/careers/current-openings",
    "BNY Mellon": "https://bnymellon.eightfold.ai/careers",
    "Cerner": "https://careers.oracle.com/jobs/#en/sites/jobsearch",
    "Chubb": "https://careers.chubb.com/global/en/search-results",
    "CoinDCX": "https://careers.coindcx.com/jobs",
    "Coinbase": "https://www.coinbase.com/careers/positions",
    "D.E.Shaw": "https://www.deshaw.com/careers",
    "D. E. Shaw India Private Limited": "https://www.deshaw.com/careers",
    "Deutsche Bank Operations International (DBOI)": "https://careers.db.com/search-jobs",
    "Flipkart": "https://www.flipkartcareers.com/#!/joblist",
    "Gemini": "https://www.gemini.com/careers/open-roles",
    "Goldman Sachs": "https://higher.gs.com/careers/search-jobs",
    "Google": "https://www.google.com/about/careers/applications/jobs/results",
    "HCL Tech": "https://www.hcltech.com/careers/open-positions",
    "InfoEdge": "https://careers.infoedge.com/jobs",
    "InMobi": "https://www.inmobi.com/company/careers/open-roles",
    "Intel": "https://jobs.intel.com/en/search-jobs",
    "Jaguar Land Rover India": "https://jlr.wd3.myworkdayjobs.com/en-US/jlrcareers",
    "Jane Street": "https://www.janestreet.com/join-jane-street/open-roles/",
    "JP Morgan Chase": "https://careers.jpmorgan.com/us/en/students/programs",
    "Mastercard": "https://careers.mastercard.com/us/en/search-results",
    "McKinsey & Company": "https://www.mckinsey.com/careers/search-jobs",
    "Databricks": "https://www.databricks.com/company/careers/open-positions",
    "Netflix": "https://jobs.netflix.com/search",
    "Netradyne": "https://jobs.lever.co/netradyne",
    "NPCI": "https://career.npci.org.in/currentOpenings.htm",
    "Oracle": "https://careers.oracle.com/jobs/#en/sites/jobsearch",
    "Palo Alto Networks": "https://jobs.smartrecruiters.com/PaloAltoNetworks2",
    "JP Morgan Experienced": "https://careers.jpmorgan.com/us/en/students/programs",
    "JP Morgan All Jobs": "https://careers.jpmorgan.com/global/en/search",
    "Google Student Careers": "https://www.google.com/about/careers/applications/students/",
    "Netflix Teams": "https://jobs.netflix.com/teams",
    "Amazon Student Programs": "https://www.amazon.jobs/en/teams/internships-for-students"
}


def scrape_and_process_jobs():
    print("Scraping careers page...")
    uni_results = []
    for company, url in CAREERS_URL.items():
        print(f"\nProcessing {company} - {url}")
        try:
            jobs = scrape_careers_page(url)
        except Exception as e:
            print(f"Skipping {company} due to scrape error: {e}")
            continue
        print("Total links:", len(jobs))

        print("Filtering relevant jobs...")
        filtered_jobs = filter_jobs(jobs)
        print("Relevant jobs:", len(filtered_jobs))

        results = []
        for job in filtered_jobs[:5]:
            title = job.get("title", "Unknown")
            print("\nProcessing:", title)
            job_url = job.get("url", "")
            if not job_url:
                print(f"Skipping job '{title}' because no URL was found.")
                continue
            try:
                details = extract_job_details(job_url)
            except Exception as e:
                print(f"Failed to extract details for {title}: {e}")
                details = {
                    "error": "extraction_failed",
                    "title": title,
                    "job_url": job_url
                }
            details["job_url"] = job_url
            results.append(details)

        uni_results.append({"company": company, "jobs": results})
        print("\nDONE WITH SCRAPING AND PROCESSING CAREER SITES")

    return uni_results