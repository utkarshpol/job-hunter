import json
import re
import time
from pathlib import Path
from typing import Any

import httpx # type: ignore
import ollama # type: ignore


REDDIT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,image/avif,image/webp,"
        "image/apng,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

SUBREDDITS = [
    "developersIndia",
    "cscareerquestions",
    "india"
]


def fetch_reddit_intelligence(companies_data):

    output_data = []

    company_cache = {}

    for company_entry in companies_data:

        company = company_entry.get(
            "company",
            ""
        ).strip()

        if not company:
            continue

        print(f"\nFetching Reddit data for {company}")

        if company not in company_cache:

            company_cache[company] = fetch_raw_reddit_pool(
                company
            )

        raw_pool = company_cache[company]

        updated_jobs = []

        for job in company_entry.get("jobs", []):

            title = job.get("title", "")

            snippets = extract_relevant_snippets(
                raw_pool,
                company
            )

            print(
                f"Found {len(snippets)} snippets for {company} - {title}"
            )

            if snippets:

                reddit_intel = analyze_with_gemma(
                    snippets,
                    company,
                    title
                )

            else:

                reddit_intel = default_intel()

            updated_jobs.append({
                **job,
                "reddit_intel": reddit_intel,
                "reddit_sources": list(set([
                    item["source"]
                    for item in snippets
                    if item["source"]
                ]))
            })

        output_data.append({
            "company": company,
            "jobs": updated_jobs
        })

    return output_data


def analyze_with_gemma(
    snippets,
    company,
    job_title
):

    context = "\n---\n".join([
        item["text"]
        for item in snippets[:10]
    ])

    prompt = f"""
You are an expert career intelligence analyst.

Analyze these Reddit discussions.

Company: {company}
Role: {job_title}

Return STRICT JSON ONLY:

{{
  "estimated_ctc": "",
  "legitimacy": "",
  "interview_difficulty": "",
  "work_culture": "",
  "important_notes": []
}}

If information is missing,
return "Unknown".

REDDIT DATA:
{context}
"""

    try:

        response = ollama.chat(
            model="gemma3:4b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": 0.1
            }
        )

        content = response[
            "message"
        ][
            "content"
        ].strip()

        match = re.search(
            r"\{.*\}",
            content,
            re.DOTALL
        )

        if match:
            return json.loads(match.group())

    except Exception as e:

        print("Gemma parse error:", e)

    return default_intel()


def fetch_raw_reddit_pool(company):

    pool = []

    for subreddit in SUBREDDITS:

        url = (
            f"https://www.reddit.com/"
            f"r/{subreddit}/search.json"
        )

        params = {
            "q": company,
            "sort": "relevance",
            "limit": 3,
            "restrict_sr": "on"
        }

        try:

            time.sleep(2)

            response = httpx.get(
                url,
                params=params,
                headers=REDDIT_HEADERS,
                timeout=10
            )

            if response.status_code == 429:

                print(
                    f"Rate limited on r/{subreddit}"
                )

                time.sleep(5)

                response = httpx.get(
                    url,
                    params=params,
                    headers=REDDIT_HEADERS,
                    timeout=10
                )

            if response.status_code != 200:

                print(
                    f"Reddit error {response.status_code}"
                )

                continue

            posts = response.json().get(
                "data",
                {}
            ).get(
                "children",
                []
            )

            for post in posts:

                post_data = post.get(
                    "data",
                    {}
                )

                title = clean_text(
                    post_data.get(
                        "title",
                        ""
                    )
                )

                selftext = clean_text(
                    post_data.get(
                        "selftext",
                        ""
                    )
                )

                permalink = post_data.get(
                    "permalink",
                    ""
                )

                source_url = ""

                if permalink:

                    source_url = (
                        "https://www.reddit.com"
                        f"{permalink}"
                    )

                combined = (
                    f"{title} - {selftext}"
                    if title and selftext
                    else title or selftext
                )

                if combined:

                    pool.append({
                        "text": combined,
                        "source": source_url
                    })

                if source_url:

                    comments = fetch_thread_comments(
                        f"{source_url}.json",
                        source_url
                    )

                    pool.extend(comments)

        except Exception as e:

            print(
                f"Network error on r/{subreddit}: {e}"
            )

    return pool


def fetch_thread_comments(
    thread_json_url,
    source_url
):

    comments = []

    try:

        response = httpx.get(
            thread_json_url,
            headers=REDDIT_HEADERS,
            timeout=10
        )

        if (
            response.status_code == 200
            and len(response.json()) > 1
        ):

            children = response.json()[1].get(
                "data",
                {}
            ).get(
                "children",
                []
            )

            for child in children[:10]:

                comment_data = child.get(
                    "data",
                    {}
                )

                body = clean_text(
                    comment_data.get(
                        "body",
                        ""
                    )
                )

                score = comment_data.get(
                    "score",
                    0
                )

                if (
                    body
                    and score >= 2
                    and body not in [
                        "[deleted]",
                        "[removed]"
                    ]
                ):

                    comments.append({
                        "text": body,
                        "source": source_url
                    })

    except Exception:

        pass

    return comments


def extract_relevant_snippets(
    pool,
    company
):

    snippets = []

    pattern = re.compile(
        r"\b"
        + re.escape(company.lower())
        + r"\b"
    )

    for item in pool:

        text = item["text"]

        if pattern.search(text.lower()):

            snippets.append({
                "text": text[:600],
                "source": item["source"]
            })

    unique = {}

    for item in snippets:

        key = item["text"][:120]

        if key not in unique:
            unique[key] = item

    return list(unique.values())


def clean_text(value: Any):

    text = str(value or "")

    text = re.sub(
        r"https?://\S+",
        "",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def default_intel():

    return {
        "estimated_ctc": "Unknown",
        "legitimacy": "Unknown",
        "interview_difficulty": "Unknown",
        "work_culture": "Unknown",
        "important_notes": []
    }


import sys
import json

from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)



PHASE2_FILE = Path(
    "results/phase2_results.json"
)

PHASE3_FILE = Path(
    "results/phase3_results.json"
)


def main():

    with open(
        PHASE2_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        phase2_results = json.load(f)

    results = fetch_reddit_intelligence(
        phase2_results
    )

    with open(
        PHASE3_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            results,
            f,
            indent=2,
            ensure_ascii=False
        )

    print("\nPHASE 3 COMPLETE")
    print(
        f"Saved to {PHASE3_FILE}"
    )


if __name__ == "__main__":
    main()