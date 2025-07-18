# app/user/mongo.py
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import get_settings  # 설정에서 MONGO_URI 가져오기

settings = get_settings()
client = AsyncIOMotorClient(settings.MONGO_URI)
db = client["test_db"]  # 원하는 DB 이름
user_collection = db["users"]
