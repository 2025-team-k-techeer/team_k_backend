from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.interior.domain.interior import (
    Interior,
    InteriorType,
    FurnitureDetected,
    DanawaProduct,
    BoundingBox,
    Dimensions,
)
from app.interior.domain.repository.interior_repository import InteriorRepository
from app.mongo import (
    interior_collection,
    interior_type_collection,
    furniture_detected_collection,
    danawa_products_collection,
)


class InteriorRepositoryImpl(InteriorRepository):
    def __init__(self):
        self.interior_collection = interior_collection
        self.interior_type_collection = interior_type_collection
        self.furniture_detected_collection = furniture_detected_collection
        self.danawa_products_collection = danawa_products_collection

    def _interior_to_dict(self, interior: Interior) -> dict:
        """Interior 객체를 MongoDB 문서로 변환"""
        return {
            "_id": interior.id,
            "user_id": interior.user_id,
            "original_image_url": interior.original_image_url,
            "interior_type_id": interior.interior_type_id,
            "room_type_id": interior.room_type_id,
            "status": interior.status,
            "saved": interior.saved,
            "generated_image_url": interior.generated_image_url,
            "detected_parts": interior.detected_parts or [],
            "created_at": interior.created_at,
            "updated_at": interior.updated_at,
            "deleted_at": interior.deleted_at,
        }

    def _dict_to_interior(self, doc: dict) -> Interior:
        """MongoDB 문서를 Interior 객체로 변환"""
        return Interior(
            id=doc["_id"],
            user_id=doc["user_id"],
            original_image_url=doc["original_image_url"],
            interior_type_id=doc["interior_type_id"],
            room_type_id=doc["room_type_id"],
            status=doc["status"],
            saved=doc["saved"],
            generated_image_url=doc.get("generated_image_url"),
            detected_parts=doc.get("detected_parts"),
            created_at=doc.get("created_at"),
            updated_at=doc.get("updated_at"),
            deleted_at=doc.get("deleted_at"),
        )

    def _interior_type_to_dict(self, interior_type: InteriorType) -> dict:
        """InteriorType 객체를 MongoDB 문서로 변환"""
        return {
            "_id": interior_type.id,
            "name": interior_type.name,
            "description": interior_type.description,
            "image_url": interior_type.image_url,
        }

    def _dict_to_interior_type(self, doc: dict) -> InteriorType:
        """MongoDB 문서를 InteriorType 객체로 변환"""
        return InteriorType(
            id=doc["_id"],
            name=doc["name"],
            description=doc["description"],
            image_url=doc["image_url"],
        )

    def _furniture_detected_to_dict(self, furniture: FurnitureDetected) -> dict:
        """FurnitureDetected 객체를 MongoDB 문서로 변환"""
        return {
            "_id": furniture.id,
            "interior_id": furniture.interior_id,
            "label": furniture.label,
            "bounding_box": {
                "x": furniture.bounding_box.x,
                "y": furniture.bounding_box.y,
                "width": furniture.bounding_box.width,
                "height": furniture.bounding_box.height,
            },
            "danawa_products_id": furniture.danawa_products_id,
            "danawa_products_image_index": furniture.danawa_products_image_index,
            "created_at": furniture.created_at,
        }

    def _dict_to_furniture_detected(self, doc: dict) -> FurnitureDetected:
        """MongoDB 문서를 FurnitureDetected 객체로 변환"""
        return FurnitureDetected(
            id=doc["_id"],
            interior_id=doc["interior_id"],
            label=doc["label"],
            bounding_box=BoundingBox(
                x=doc["bounding_box"]["x"],
                y=doc["bounding_box"]["y"],
                width=doc["bounding_box"]["width"],
                height=doc["bounding_box"]["height"],
            ),
            danawa_products_id=doc["danawa_products_id"],
            danawa_products_image_index=doc.get("danawa_products_image_index"),
            created_at=doc.get("created_at"),
        )

    def _danawa_product_to_dict(self, product: DanawaProduct) -> dict:
        """DanawaProduct 객체를 MongoDB 문서로 변환"""
        return {
            "_id": product.id,
            "label": product.label,
            "product_name": product.product_name,
            "product_url": product.product_url,
            "image_url": product.image_url,
            "dimensions": {
                "width_cm": product.dimensions.width_cm,
                "depth_cm": product.dimensions.depth_cm,
                "height_cm": product.dimensions.height_cm,
            },
            "created_at": product.created_at,
            "updated_at": product.updated_at,
        }

    def _dict_to_danawa_product(self, doc: dict) -> DanawaProduct:
        """MongoDB 문서를 DanawaProduct 객체로 변환"""
        return DanawaProduct(
            id=doc["_id"],
            label=doc["label"],
            product_name=doc["product_name"],
            product_url=doc["product_url"],
            image_url=doc["image_url"],
            dimensions=Dimensions(
                width_cm=doc["dimensions"]["width_cm"],
                depth_cm=doc["dimensions"]["depth_cm"],
                height_cm=doc["dimensions"]["height_cm"],
            ),
            created_at=doc.get("created_at"),
            updated_at=doc.get("updated_at"),
        )

    async def create(self, interior: Interior) -> Interior:
        """인테리어 생성"""
        interior_dict = self._interior_to_dict(interior)
        await self.interior_collection.insert_one(interior_dict)
        return interior

    async def get_by_id(self, interior_id: str) -> Optional[Interior]:
        """ID로 인테리어 조회"""
        doc = await self.interior_collection.find_one({"_id": interior_id})
        if doc:
            return self._dict_to_interior(doc)
        return None

    async def get_by_user_id(self, user_id: str, limit: int = 10) -> List[Interior]:
        """사용자 ID로 인테리어 목록 조회"""
        cursor = (
            self.interior_collection.find({"user_id": user_id, "deleted_at": None})
            .sort("created_at", -1)
            .limit(limit)
        )

        interiors = []
        async for doc in cursor:
            interiors.append(self._dict_to_interior(doc))

        return interiors

    async def update(self, interior: Interior) -> Interior:
        """인테리어 업데이트"""
        interior_dict = self._interior_to_dict(interior)
        interior_dict["updated_at"] = datetime.utcnow()

        await self.interior_collection.update_one(
            {"_id": interior.id}, {"$set": interior_dict}
        )
        return interior

    async def delete(self, interior_id: str) -> bool:
        """인테리어 삭제 (소프트 삭제)"""
        result = await self.interior_collection.update_one(
            {"_id": interior_id}, {"$set": {"deleted_at": datetime.utcnow()}}
        )
        return result.modified_count > 0

    async def save_interior(self, interior_id: str, user_id: str) -> bool:
        """인테리어 저장 상태 변경"""
        result = await self.interior_collection.update_one(
            {"_id": interior_id, "user_id": user_id},
            {"$set": {"saved": True, "updated_at": datetime.utcnow()}},
        )
        return result.modified_count > 0

    async def get_all_interior_types(self) -> List[InteriorType]:
        """모든 인테리어 스타일 타입 조회"""
        cursor = self.interior_type_collection.find({})
        interior_types = []
        async for doc in cursor:
            interior_types.append(self._dict_to_interior_type(doc))
        return interior_types

    async def get_by_interior_types_id(
        self, interior_type_id: str
    ) -> Optional[Interior]:
        """ID로 인테리어 조회"""
        doc = await self.interior_type_collection.find_one({"_id": interior_type_id})
        if doc:
            return self._dict_to_interior(doc)
        return None

    async def get_interior_type_by_id(
        self, interior_type_id: str
    ) -> Optional[InteriorType]:
        """ID로 인테리어 스타일 타입 조회"""
        doc = await self.interior_type_collection.find_one({"_id": interior_type_id})
        if doc:
            return self._dict_to_interior_type(doc)
        return None

    async def create_furniture_detected(
        self, furniture: FurnitureDetected
    ) -> FurnitureDetected:
        """가구 인식 결과 생성"""
        furniture_dict = self._furniture_detected_to_dict(furniture)
        await self.furniture_detected_collection.insert_one(furniture_dict)
        return furniture

    async def get_furniture_detected_by_interior_id(
        self, interior_id: str
    ) -> List[FurnitureDetected]:
        """인테리어 ID로 가구 인식 결과 조회"""
        cursor = self.furniture_detected_collection.find({"interior_id": interior_id})
        furnitures = []
        async for doc in cursor:
            furnitures.append(self._dict_to_furniture_detected(doc))
        return furnitures

    async def get_furniture_detected_by_ids(
        self, ids: list[str]
    ) -> list[FurnitureDetected]:
        cursor = self.furniture_detected_collection.find({"_id": {"$in": ids}})
        result = []
        async for doc in cursor:
            result.append(self._dict_to_furniture_detected(doc))
        return result

    async def get_danawa_products_by_ids(
        self, product_ids: List[str]
    ) -> List[DanawaProduct]:
        """제품 ID 리스트로 다나와 제품 조회"""
        cursor = self.danawa_products_collection.find({"_id": {"$in": product_ids}})
        products = []
        async for doc in cursor:
            products.append(self._dict_to_danawa_product(doc))
        return products
