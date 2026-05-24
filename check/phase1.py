import json
from pathlib import Path

from pipeline.phase1_scrape import scrape_and_process_jobs


RESULTS_FILE = Path("results/phase1_results.json")


def run_check():

    results = scrape_and_process_jobs()
    RESULTS_FILE.parent.mkdir(parents=True,exist_ok=True)

    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\nPHASE 1 CHECK COMPLETE")
    print(f"Saved results to: {RESULTS_FILE}")

if __name__ == "__main__":
    run_check()