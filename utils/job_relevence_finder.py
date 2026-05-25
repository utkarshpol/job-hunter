from sentence_transformers import SentenceTransformer # type: ignore
from sklearn.metrics.pairwise import cosine_similarity # type: ignore
import re

TARGET_ROLES = ["software engineer", "machine learning engineer", "backend engineer", "ai engineer", "data scientist"]

BAD_KEYWORDS = ["career", "careers", "country", "language", "english", "spanish", "thai", "china", "mainland", "privacy", "cookie", "accessibility", "saved jobs", "search", "sign in", "login", "home", "location", "region", "global", "content", "policy", "terms", "legal", "help", "about", "contact"]

GOOD_KEYWORDS = ["engineer", "developer", "scientist", "analyst", "intern", "software", "backend", "frontend", "full stack", "machine learning", "ai", "data", "cloud", "security"]

try:
    model = SentenceTransformer(
        "all-MiniLM-L6-v2"
    )
    target_embeddings = model.encode(TARGET_ROLES)
except Exception as e:
    print(f"Embedding model initialization failed: {e}")
    model = None
    target_embeddings = []

MAX_EXPERIENCE = 2

def filter_jobs(job_list):
    if model is None or len(target_embeddings) == 0:
        print("Embedding model unavailable, returning unfiltered job list.")
        return list(job_list)

    filtered = []
    for job in job_list:
        try:
            title = job.get("title", "")
            title_lower = title.lower()
            if any(bad in title_lower for bad in BAD_KEYWORDS):
                continue
            keyword_match = any(good in title_lower for good in GOOD_KEYWORDS)
            url = job.get("url", "")
            experience_text = (title.lower() + " " + url.lower())
            embedding = model.encode([title])
            scores = cosine_similarity(embedding, target_embeddings)[0] # type: ignore
            score = max(scores)
            if score > 0.5 or keyword_match:
                job["similarity"] = float(score)
                filtered.append(job)
        except Exception as e:
            print(f"Job filtering failed for '{job.get('title', '')}': {e}")
            continue
    return filtered