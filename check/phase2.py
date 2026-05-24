import json
from pathlib import Path
from pipeline.phase2_deduplicator import deduplicate_jobs # type: ignore

PHASE1_FILE = Path("results/phase1_results.json")
PHASE2_FILE = Path("results/phase2_results.json")

def run_check():
    with open(PHASE1_FILE, "r", encoding="utf-8") as f:
        phase1_results = json.load(f)

    phase2_results = deduplicate_jobs(phase1_results)

    PHASE2_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(PHASE2_FILE, "w", encoding="utf-8") as f:
        json.dump(phase2_results, f, indent=2, ensure_ascii=False)

    print("\nPHASE 2 CHECK COMPLETE")
    print(f"Saved results to: {PHASE2_FILE}")

if __name__ == "__main__":
    run_check()