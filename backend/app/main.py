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
import os
from fastapi import FastAPI, Request
from app.user.interface.controller import user_controller
from app.interior.interface.controller import interior_controller
import json
import logging
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.middleware.cors import CORSMiddleware


class CustomJsonFormatter(logging.Formatter):

    # CustomJsonFormatter는 로그 메시지를 JSON 형식으로 포맷팅하는 사용자 정의 로거 포맷터입니다.

    # Methods:
    # 	format(record):
    # 		주어진 로그 레코드를 JSON 형식으로 변환합니다.
    # 		- record: 로그 레코드 객체로, 로그 메시지와 관련된 모든 정보를 포함합니다.

    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "name": record.name,
        }
        return json.dumps(log_record)


# programmatically create logs directory if it doesn't exist
if not os.path.exists("./app/logs"):
    os.makedirs("./app/logs", exist_ok=True)
    os.chmod("./app/logs", 0o755)
app = FastAPI()
logger = logging.getLogger("uvicorn.access")
logger.setLevel(logging.INFO)
handler = logging.FileHandler("./app/logs/fastapi.log")
handler.setFormatter(CustomJsonFormatter())
logger.addHandler(handler)


@app.middleware("http")
async def add_logging_middleware(request: Request, call_next):
    """
    HTTP 요청에 대한 로깅 미들웨어를 추가합니다.

    이 미들웨어는 다음 작업을 수행합니다:
    1. "uvicorn.access" 로거를 가져오고 INFO 레벨로 설정합니다.
    2. 로그를 기록할 파일 핸들러를 추가하고, 사용자 정의 JSON 포맷터를 설정합니다.
    3. 요청 메서드, URL, 상태 코드, 클라이언트 IP 주소와 같은 요청 및 응답 데이터를 JSON 형식으로 로깅합니다.

    매개변수:
    - request (Request): FastAPI 요청 객체.
    - call_next (Callable): 다음 미들웨어 또는 엔드포인트를 호출하는 함수.

    반환값:
    - response: FastAPI 응답 객체.
    """
    logger = logging.getLogger("uvicorn.access")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler("./app/logs/fastapi.log")
    handler.setFormatter(CustomJsonFormatter())
    logger.addHandler(handler)
    response = await call_next(request)
    log_data = {
        "method": request.method,
        "url": str(request.url),
        "status_code": response.status_code,
        "client": request.client.host,
    }
    logger.info(json.dumps(log_data))
    return response


# CORS 설정 for metrics and logging
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Instrumentator().instrument(app).expose(app)
# 라우터 등록
app.include_router(user_controller.router)
app.include_router(interior_controller.router)
