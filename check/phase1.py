import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import json
from pipeline.phase1_scrape import scrape_and_process_jobs
import traceback

RESULTS_FILE = Path("results/phase1_results.json")


def run_check():
    try:
        print("try started")
        results = scrape_and_process_jobs()
        print("process of results complete")
        RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        print("result file ok")
        with open(RESULTS_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print("open and wrote file")
        print("\nPHASE 1 CHECK COMPLETE")
        print(f"Saved results to: {RESULTS_FILE}")
    except Exception as e:
        print("PHASE 1 CHECK FAILED: ", e)
        traceback.print_exc()

if __name__ == "__main__":
    run_check()