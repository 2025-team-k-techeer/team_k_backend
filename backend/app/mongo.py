# app/mongo.py
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import get_settings  # 설정에서 MONGO_URI 가져오기

settings = get_settings()
client = AsyncIOMotorClient(settings.MONGO_URI)
db = client["interior_db"]  # 원하는 DB 이름

# User 관련 컬렉션
user_collection = db["users"]

# Interior 관련 컬렉션
interior_collection = db["interiors"]  # 인테리어 메인 컬렉션
interior_type_collection = db["interior_types"]  # 인테리어 스타일 타입 컬렉션
furniture_detected_collection = db["furniture_detected"]  # 가구 인식 결과 컬렉션
danawa_products_collection = db["danawa_products"]  # 다나와 제품 컬렉션
