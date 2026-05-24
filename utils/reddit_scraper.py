import re
import time
import httpx # type: ignore

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

SUBREDDITS = ["developersIndia", "cscareerquestions", "india", ]

def clean_text(text):
    text = str(text or "")
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"\s+"," ",text)
    return text.strip()
def search_reddit_data(company, title):
    queries = [
        f"{company} {title} ctc",
        f"{company} {title} salary",
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