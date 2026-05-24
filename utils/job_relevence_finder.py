from sentence_transformers import SentenceTransformer # type: ignore
from sklearn.metrics.pairwise import cosine_similarity # type: ignore


TARGET_ROLES = [
    "software engineer",
    "machine learning engineer",
    "backend engineer",
    "ai engineer",
    "data scientist",
]

try:
    model = SentenceTransformer(
        "all-MiniLM-L6-v2"
    )
    target_embeddings = model.encode(TARGET_ROLES)
except Exception as e:
    print(f"Embedding model initialization failed: {e}")
    model = None
    target_embeddings = []


def filter_jobs(job_list):
    if model is None or not target_embeddings:
        print("Embedding model unavailable, returning unfiltered job list.")
        return list(job_list)

    filtered = []
    for job in job_list:
        try:
            title = job.get("title", "")
            embedding = model.encode([title])
            scores = cosine_similarity(embedding, target_embeddings)[0] # type: ignore
            score = max(scores)
            if score > 0.45:
                job["similarity"] = float(score)
                filtered.append(job)
        except Exception as e:
            print(f"Job filtering failed for '{job.get('title', '')}': {e}")
            continue
    return filtered