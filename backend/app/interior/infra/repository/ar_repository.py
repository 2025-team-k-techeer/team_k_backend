from app.mongo import db
from typing import List, Optional


class ARRepository:
    def __init__(self):
        self.danawa_collection = db["danawa_products"]

    async def get_ar_documents_by_label(
        self, label: str, limit: int = 10
    ) -> List[dict]:
        # label에 따라 컬렉션명을 동적으로 선택
        ar_collection_name = f"ar_{label}_documents"
        ar_collection = db[ar_collection_name]
        return await ar_collection.find({"label": label}).to_list(length=limit)

    async def get_danawa_products_by_label(
        self, label: str, limit: int = 20
    ) -> List[dict]:
        return await self.danawa_collection.find({"label": label}).to_list(length=limit)
