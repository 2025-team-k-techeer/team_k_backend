from celery import Celery, shared_task
import qdrant_client

# Celery 인스턴스 생성 (보통 별도의 worker.py 등에서 관리)
celery_app = Celery(
    "worker",
    broker="redis://redis:6379/0",  # 브로커 주소는 환경에 맞게 수정
    backend="redis://redis:6379/0",
)


@celery_app.task
def match_product_with_qdrant(furniture_id, clip_embedding):
    client = qdrant_client.QdrantClient(host="qdrant", port=6333)
    # Qdrant에서 유사 벡터 검색
    hits = client.search(
        collection_name="products", query_vector=clip_embedding, limit=5
    )
    product_ids = [hit.payload["product_id"] for hit in hits]
    # DB에 furniture_id에 해당하는 danawa_products_id 업데이트
    from pymongo import MongoClient

    mongo = MongoClient("mongodb://mongo:27017")
    db = mongo["your_db_name"]
    collection = db["furnitures"]

    collection.update_one(
        {"_id": furniture_id}, {"$set": {"danawa_products_id": product_ids}}
    )
    return product_ids
