import json
from pathlib import Path


VISITED_DB = Path("data/visited_jobs.json")


def normalize_text(text):
    if not text:
        return ""
    return text.strip().lower()


def create_job_id(company, title):
    company = normalize_text(company)
    title = normalize_text(title)
    return f"{company}::{title}"


def load_visited_jobs():
    if not VISITED_DB.exists():
        return set()
    try:
        with open(VISITED_DB, "r", encoding="utf-8") as f:
            data = json.load(f)
        return set(data)
    except Exception as e:
        print(f"Failed to load visited jobs: {e}")
        return set()


def save_visited_jobs(visited_jobs):
    try:
        VISITED_DB.parent.mkdir(parents=True, exist_ok=True)
        with open(VISITED_DB, "w", encoding="utf-8") as f:
            json.dump(list(visited_jobs), f, indent=2)
        return True
    except Exception as e:
        print(f"Failed to save visited jobs: {e}")
        return False


def deduplicate_jobs(all_company_jobs):
    visited_jobs = load_visited_jobs()
    new_company_jobs = []
    for company_data in all_company_jobs:
        try:
            company = company_data["company"]
            jobs = company_data["jobs"]

            print(f"\nDeduplicating jobs for {company}...")

            unique_jobs = []
            for job in jobs:
                title = job.get("title", "")
                print("Checking job:", title)
                job_id = create_job_id(company, title)
                if job_id in visited_jobs:
                    print("Skipping duplicate: ", company, title)
                    continue
                print("Adding new job:", company, title)
                unique_jobs.append(job)
                visited_jobs.add(job_id)
            if unique_jobs:
                new_company_jobs.append({
                    "company": company,
                    "jobs": unique_jobs
                })
        except Exception as e:
            print(f"Deduplication failed for company entry: {e}")
            continue
    if not save_visited_jobs(visited_jobs):
        print("Warning: visited jobs could not be persisted.")
    return new_company_jobs