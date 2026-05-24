from sentence_transformers import SentenceTransformer # type: ignore
from sklearn.metrics.pairwise import cosine_similarity # type: ignore


model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

TARGET_ROLES = [
    "software engineer",
    "machine learning engineer",
    "backend engineer",
    "ai engineer",
    "data scientist",
]

target_embeddings = model.encode(TARGET_ROLES)


def filter_jobs(job_list):
    filtered = []
    for job in job_list:
        title = job["title"]
        embedding = model.encode([title])
        scores = cosine_similarity(embedding, target_embeddings)[0] # type: ignore
        score = max(scores)
        if score > 0.45:
            job["similarity"] = float(score)
            filtered.append(job)
    return filtered