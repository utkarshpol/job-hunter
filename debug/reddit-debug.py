import json
import re
import time

import httpx # type: ignore
import ollama # type: ignore


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

SUBREDDITS = ["developersIndia", "cscareerquestions", "india"]


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


def search_reddit_data(company, title):
    queries = [
        f"{company} {title} ctc",
        f"{company} {title} salary",
        f"{company} {title} interview experience",
        f"{company} {title} legitimacy",
        f"{company} {title} work culture",
        f"{company} ctc",
        f"{company} interview experience",
        f"{company} work culture"
    ]

    snippets = []
    for subreddit in SUBREDDITS:
        for query in queries:
            url = (f"https://www.reddit.com/"f"r/{subreddit}/search.json")
            params = {"q": query, "sort": "relevance", "limit": 3, "restrict_sr": "on"}
            try:
                time.sleep(2)
                response = httpx.get(url, params=params, headers=HEADERS, timeout=10)
                if response.status_code != 200:
                    continue

                posts = response.json().get("data",{}).get("children",[])
                for post in posts:
                    post_data = post.get("data",{})
                    title_text = clean_text(post_data.get("title", ""))
                    body_text = clean_text(post_data.get("selftext", ""))

                    permalink = post_data.get("permalink", "")
                    source_url = ""

                    if permalink:
                        source_url = ("https://www.reddit.com"f"{permalink}")

                    combined = (f"{title_text} - {body_text}")
                    if combined.strip():
                        snippets.append({
                            "text": combined[:600],
                            "source": source_url
                        })

                    if source_url:
                        comments = fetch_thread_comments(f"{source_url}.json", source_url)
                        snippets.extend(comments)
            except Exception as e:
                print("Reddit error:", e)

    unique = {}
    for item in snippets:
        key = item["text"][:120]
        if key not in unique:
            unique[key] = item
    return list(unique.values())


def fetch_thread_comments(thread_json_url, source_url):
    comments = []
    try:
        response = httpx.get(thread_json_url, headers=HEADERS, timeout=10)
        if (response.status_code == 200 and len(response.json()) > 1):
            children = response.json()[1].get("data",{}).get("children",[])
            for child in children[:10]:
                comment_data = child.get("data",{})
                body = clean_text(comment_data.get("body", ""))
                score = comment_data.get("score", 0)
                if (body and score >= 2 and body not in ["[deleted]", "[removed]"]):
                    comments.append({
                        "text": body[:600],
                        "source": source_url
                    })
    except Exception:
        pass
    return comments


def analyze_with_gemma(company, title, snippets):
    if not snippets:
        return default_output()
    context = "\n---\n".join([item["text"] for item in snippets[:15]])
    prompt = f"""
You are an expert career intelligence analyst.
Analyze these Reddit discussions.
Company: {company}
Role: {title}
Return STRICT JSON ONLY:
{{
  "estimated_ctc": "",
  "legitimacy": "",
  "interview_difficulty": "",
  "work_culture": "",
  "important_notes": [],
  "sources": []
}}
If information is missing,
return "Unknown".
REDDIT DATA:
{context}
"""
    try:
        response = ollama.chat(
            model="gemma3:4b",
            messages=[{
                    "role": "user",
                    "content": prompt
                }],
            options={"temperature": 0.1})
        content = response["message"]["content"].strip()
        return parse_gemma_output(content, snippets)
    except Exception as e:
        print("Gemma error:", e)
        return default_output()


def parse_gemma_output(raw_output,snippets):
    try:
        match = re.search(r"\{.*\}", raw_output, re.DOTALL)
        if not match:
            return default_output()
        parsed = json.loads(match.group())
        parsed["sources"] = list(set([item["source"] for item in snippets if item["source"]]))
        return parsed
    except Exception:
        return default_output()


def clean_text(text):
    text = str(text or "")
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"\s+"," ",text)
    return text.strip()


def default_output():
    return {
        "estimated_ctc": "Unknown",
        "legitimacy": "Unknown",
        "interview_difficulty": "Unknown",
        "work_culture": "Unknown",
        "important_notes": [],
        "sources": []
    }

def main():
    try:
        with open(
            "results/phase2_results.json",
            "r",
            encoding="utf-8"
        ) as f:
            phase2_results = json.load(f)

        results = fetch_reddit_intelligence(
            phase2_results
        )

        with open(
            "results/phase3_results.json",
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
            f"Saved to {'results/phase3_results.json'}"
        )
    except Exception as e:
        print("PHASE 3 DEBUG FAILED:", e)


if __name__ == "__main__":
    main()