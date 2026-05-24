import json
from pathlib import Path

from pipeline.phase1_scrape import scrape_and_process_jobs
from pipeline.phase2_deduplicate import deduplicate_jobs # type: ignore
from pipeline.phase3_reddit import fetch_reddit_intelligence  # type: ignore
from pipeline.phase4_mail import send_email # type: ignore


RESULTS_DIR = Path("results")

PHASE1_FILE = "./results/phase1_results.json"
PHASE2_FILE = "./results/phase2_results.json"
PHASE3_FILE = "./results/phase3_results.json"


def save_results(path, data):

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Failed to save results to {path}: {e}")
        return False


def main():
    print("\nPHASE 1: SCRAPING JOBS")
    try:
        phase1_results = scrape_and_process_jobs()
    except Exception as e:
        print("Phase 1 failed:", e)
        return

    if not save_results(PHASE1_FILE, phase1_results):
        return

    print("\nPHASE 2: DEDUPLICATION")
    try:
        phase2_results = deduplicate_jobs(phase1_results)
    except Exception as e:
        print("Phase 2 failed:", e)
        return

    if not save_results(PHASE2_FILE, phase2_results):
        return

    print("\nPHASE 3: REDDIT INTEL")
    try:
        phase3_results = fetch_reddit_intelligence(phase2_results)
    except Exception as e:
        print("Phase 3 failed:", e)
        return

    if not save_results(PHASE3_FILE, phase3_results):
        return

    print("\nPHASE 4: SENDING EMAIL")
    try:
        send_email(phase3_results)
    except Exception as e:
        print("Phase 4 failed:", e)
        return

    print("\nPIPELINE COMPLETE")


if __name__ == "__main__":
    main()