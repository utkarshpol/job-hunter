from utils.reddit_scraper import search_reddit_data 
from utils.reddit_gemma import analyze_with_gemma

def fetch_reddit_intelligence(companies_data):

    final_results = []
    for company_data in companies_data:
        company = company_data["company"]
        updated_jobs = []
        for job in company_data["jobs"]:
            title = job.get("title", "")
            print(f"\nSearching Reddit for {company} - {title}")
            snippets = search_reddit_data(company, title)
            reddit_intel = analyze_with_gemma(company, title, snippets)
            updated_jobs.append({
                **job,
                "reddit_intel": reddit_intel
            })
        final_results.append({
            "company": company,
            "jobs": updated_jobs
        })
    return final_results