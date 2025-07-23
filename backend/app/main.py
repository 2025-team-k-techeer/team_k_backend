# import os
# from fastapi import FastAPI
# import redis
# from pymongo import MongoClient
# import httpx
# import pika
# from app.config import get_settings

# settings = get_settings()

# app = FastAPI()

# # # main.py
# # if os.getenv("DEBUG", "false").lower() == "true":
# #     import debugpy

# #     try:
# #         debugpy.listen(("0.0.0.0", 5678))
# #         print("✅ VSCode 디버거 대기 중 (5678 포트)...")
# #         debugpy.wait_for_client()  # 필요시
# #     except RuntimeError as e:
# #         if "Address already in use" in str(e):
# #             print("⚠️ debugpy 포트 5678 이미 사용 중. 중복 listen 시도 무시.")
# #         else:
# #             raise


# @app.get("/test/redis")
# def test_redis():
#     try:
#         r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
#         r.set("test_key", "test_value")
#         value = r.get("test_key")
#         return {"redis_alive": True, "value": value.decode()}
#     except Exception as e:
#         return {"redis_alive": False, "error": str(e)}


# @app.get("/test/mongo")
# def test_mongo():
#     try:
#         client = MongoClient(settings.MONGO_URI)
#         db = client.test_db
#         result = db.test_col.insert_one({"name": "sample", "value": 123})
#         return {"mongo_alive": True, "inserted_id": str(result.inserted_id)}
#     except Exception as e:
#         return {"mongo_alive": False, "error": str(e)}


# @app.get("/test/qdrant")
# def test_qdrant():
#     try:
#         response = httpx.get(
#             f"http://{settings.QDRANT_HOST}:{settings.QDRANT_PORT}/collections"
#         )
#         return {"qdrant_alive": response.status_code == 200, "data": response.json()}
#     except Exception as e:
#         return {"qdrant_alive": False, "error": str(e)}


# @app.get("/test/rabbitmq")
# def test_rabbitmq():
#     try:
#         connection = pika.BlockingConnection(
#             pika.ConnectionParameters(host=settings.RABBITMQ_HOST)
#         )
#         channel = connection.channel()
#         channel.queue_declare(queue=settings.RABBITMQ_QUEUE)
#         channel.basic_publish(
#             exchange="", routing_key="test_queue", body="Hello RabbitMQ!"
#         )
#         connection.close()
#         return {"rabbitmq_alive": True}
#     except Exception as e:
#         return {"rabbitmq_alive": False, "error": str(e)}

# app/main.py

# app/main.py
from fastapi import FastAPI
from app.user.interface.controller import user_controller
from app.interior.interface.controller import interior_controller
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# 👉 Prometheus metrics 등록
Instrumentator().instrument(app).expose(app)

# 라우터 등록
app.include_router(user_controller.router)
app.include_router(interior_controller.router)
