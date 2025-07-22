import os
from app.interior.tasks.celery_app import celery_app
import requests

QDRANT_SEARCH_URL = os.getenv(
    "QDRANT_SEARCH_URL", "http://qdrant:6333/collections/danawa_products/points/search"
)


@celery_app.task
def qdrant_search_task(embedding, top_k=3):
    payload = {"vector": embedding, "top": top_k, "with_payload": True}
    resp = requests.post(QDRANT_SEARCH_URL, json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()
