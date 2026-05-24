# AI Job Hunt Pipeline

A small Python pipeline for scraping job listings, filtering relevant roles, extracting job details, searching Reddit for company/role intelligence, and sending a summary email.

## What this repo does

- `run.py` runs the full pipeline in 4 phases
- `pipeline/phase1_scrape.py` scrapes career pages defined in `CAREERS_URL`
- `pipeline/phase2_deduplicate.py` removes duplicate jobs using `data/visited_jobs.json`
- `pipeline/phase3_reddit.py` fetches Reddit intelligence for each job
- `pipeline/phase4_mail.py` sends the final summary email
- `utils/` contains the key customization points for models, queries, and search logic

## Setup on another device

1. Clone or copy the repository.
2. Create and activate a Python virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install the required Python libraries:

   ```bash
   python -m pip install playwright sentence-transformers scikit-learn httpx ollama
   ```

4. Install Playwright browser support:

   ```bash
   python -m playwright install chromium
   ```

5. Install the Ollama model used by the pipeline:

   ```bash
   ollama install gemma3:4b
   ```

6. Create a `.env` file in the repository root and fill in the email values below.

7. Make sure your machine has Ollama available and the Python `ollama` package can call it.

## Run the pipeline

From the repository root:

```bash
python run.py
```

If email values are missing, the pipeline will still run but the final mail step will be skipped safely.

This writes output to:

- `results/phase1_results.json`
- `results/phase2_results.json`
- `results/phase3_results.json`

## Files and where things are located

### Main pipeline

- `run.py` — orchestrates all phases and saves results
- `pipeline/phase1_scrape.py` — company URLs and the first job scraping step
- `pipeline/phase2_deduplicate.py` — job deduplication using `data/visited_jobs.json`
- `pipeline/phase3_reddit.py` — Reddit search + analysis step
- `pipeline/phase4_mail.py` — builds and sends the email

### Utility files

- `utils/job_scraper.py` — fetches jobs from career pages using Playwright
- `utils/job_relevence_finder.py` — filters jobs by similarity to target roles
- `utils/job_details_extractor.py` — extracts job fields from each job page using Ollama
- `utils/reddit_scraper.py` — builds Reddit queries and fetches Reddit posts/comments
- `utils/reddit_gemma.py` — analyzes Reddit snippets with Ollama and returns JSON results

### Debug / stage check scripts

- `check/phase1.py`
- `check/phase2.py`
- `check/phase3.py`
- `check/phase4.py`

These are alternate entry points for running each phase separately if you want to debug or run one stage at a time.

## What you can tweak

### 0. Environment variables and sensitive settings

Create a `.env` file in the repository root with these values:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
EMAIL_SENDER=your-sender@example.com
EMAIL_PASSWORD=your-app-password
EMAIL_RECIPIENT=your-recipient@example.com
```

This file is ignored by Git and keeps your secrets safe from GitHub.


### 1. Add or change companies

Edit `pipeline/phase1_scrape.py`.

- `CAREERS_URL` is the single place to add companies:

```python
CAREERS_URL = {
    "Razorpay": "https://razorpay.com/jobs/jobs-all/",
    "NewCompany": "https://newcompany.com/careers/"
}
```

Add more keys and URLs here. The key becomes the company name used across the pipeline.

### 2. Job relevance model and threshold

Edit `utils/job_relevence_finder.py`.

- Model: `SentenceTransformer("all-MiniLM-L6-v2")`
- Threshold: `0.45`
- Target roles: `TARGET_ROLES`

For example:

```python
model = SentenceTransformer("all-MiniLM-L6-v2")
TARGET_ROLES = ["software engineer", "machine learning engineer", "backend engineer"]
```

Change `0.45` to a higher value for stricter matches or lower it to accept more titles.

### 3. Ollama model for job detail extraction

Edit `utils/job_details_extractor.py`.

- `model="gemma3:4b"`
- Prompt: `PROMPT`

If you want a different LLM, update the model name here and verify it is installed.

### 4. Reddit search queries and subreddits

Edit `utils/reddit_scraper.py`.

- `SUBREDDITS` holds the subreddits searched.
- `queries` contains the exact search strings used for every job.

Current queries:

```python
queries = [
    f"{company} {title} ctc",
    f"{company} {title} salary",
]
```

Add any query patterns you want. You can also add more subreddits:

```python
SUBREDDITS = ["developersIndia", "cscareerquestions", "india", "learnprogramming"]
```

### 5. Reddit analysis model and temperature

Edit `utils/reddit_gemma.py`.

- `model="gemma3:4b"`
- `options={"temperature": 0.1}`

A larger temperature makes output looser, a smaller temperature makes it more deterministic. Example:

```python
options={"temperature": 0.2}
```

### 6. Email configuration

Edit `pipeline/phase4_mail.py`.

- `EMAIL_CONFIG["smtp_host"]`
- `EMAIL_CONFIG["smtp_port"]`
- `EMAIL_CONFIG["sender"]`
- `EMAIL_CONFIG["password"]`
- `EMAIL_CONFIG["recipient"]`

If you want a safer setup, replace this with environment variables and avoid storing passwords in code.

### 7. Deduplication storage

- `data/visited_jobs.json` stores job IDs already processed.
- `pipeline/phase2_deduplicate.py` uses this file to skip jobs already seen.

If you want to reprocess all jobs, either delete this file or clear it.

## How the outputs are structured

- Phase 1 result: raw scraped jobs plus extracted details
- Phase 2 result: same jobs after deduplication
- Phase 3 result: adds `reddit_intel` to each job
- Final email: created by `pipeline/phase4_mail.py`

## Recommended customization flow

1. Add a company URL to `pipeline/phase1_scrape.py`.
2. Update `TARGET_ROLES` or threshold in `utils/job_relevence_finder.py` if your use case is different.
3. Add new Reddit query patterns or subreddits in `utils/reddit_scraper.py`.
4. Modify `utils/reddit_gemma.py` if you want a different output schema or temperature.
5. Update `pipeline/phase4_mail.py` if you want email formatting, subject, or recipients to change.

## Notes for easy setup

- `run.py` is the easiest command to start the full pipeline.
- Use `check/phase*.py` if you want to run a single stage.
- Make sure Ollama is installed and the model `gemma3:4b` is available.
- If Playwright fails, confirm browser install with `python -m playwright install chromium`.

## Summary of locations

- Company list: `pipeline/phase1_scrape.py`
- Job filtering model/threshold: `utils/job_relevence_finder.py`
- Job detail extraction prompt/model: `utils/job_details_extractor.py`
- Reddit queries: `utils/reddit_scraper.py`
- Reddit analysis model/temperature: `utils/reddit_gemma.py`
- Email settings: `pipeline/phase4_mail.py`
- Dedup cache: `data/visited_jobs.json`

---

This README is intentionally minimal and focused on what to change and where to change it.
