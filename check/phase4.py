import json
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
from pipeline.phase4_mail import send_email # type: ignore

PHASE3_FILE = Path("results/phase3_results.json")

def run_check():
    with open(PHASE3_FILE, "r", encoding="utf-8") as f:
        phase3_results = json.load(f)
    send_email(phase3_results)
    print("\nPHASE 4 CHECK COMPLETE")

if __name__ == "__main__":
    run_check()