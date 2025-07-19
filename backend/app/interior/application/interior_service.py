from app.user.mongo import client, db
from app.config import get_settings


class InteriorService:

    def __init__(self):
        self.settings = get_settings()
        self.client = client
        self.db = db  # 원하는 DB 이름
        self.interior_type_collection = self.db["interior_type"]

    async def search_furniture(self, style_name: str):
        # Search for furniture in mongodb
        result = await self.interior_type_collection.find_one({"name": style_name})

        return result if result else None
