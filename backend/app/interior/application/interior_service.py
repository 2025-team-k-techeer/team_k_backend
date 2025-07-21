from typing import List, Optional
from datetime import datetime
from uuid import uuid4
from app.interior.domain.interior import (
    Interior,
    InteriorType,
    FurnitureDetected,
    BoundingBox,
    DanawaProduct,
    Dimensions,
)
from app.interior.domain.repository.interior_repository import InteriorRepository
from app.integrations.replicate import ReplicateService
from app.interior.schemas.mappers import domain_to_interior_generate_response


def now(utc=True):
    if utc:
        return datetime.utcnow()
    return datetime.now()


class InteriorService:
    def __init__(
        self,
        interior_repository: InteriorRepository,
        replicate_service: Optional[ReplicateService] = None,
    ):
        self.interior_repository = interior_repository
        self.replicate_service = replicate_service or ReplicateService()

    async def generate_interior(
        self,
        user_id: str,
        image_url: str,
        room_type: str,
        style: str,
        prompt: str,
    ):
        """
        인테리어 이미지 생성 및 가구 인식
        """
        try:
            # 1. AI 서비스를 통한 이미지 생성
            generated_image_url = await self._generate_interior_image(
                image_url, room_type, style, prompt
            )

            # 2. 가구 인식 (YOLO 모델 사용)
            furniture_id = str(uuid4())
            furniture = FurnitureDetected(
                id=furniture_id,
                interior_id="",  # 나중에 설정
                label="desk",
                bounding_box=BoundingBox(x=120, y=200, width=280, height=160),
                danawa_products_id=["danawa_desk_001", "danawa_desk_002"],
                created_at=now(),
            )
            furnitures = [furniture]

            # 3. 상품 정보 조회
            products = await self.interior_repository.get_danawa_products_by_ids(
                furniture.danawa_products_id
            )
            products_map = {p.id: p for p in products}

            # 4. 인테리어 객체 생성
            interior = Interior(
                id=str(uuid4()),
                user_id=user_id,
                original_image_url=image_url,
                interior_type_id=style,
                room_type_id=room_type,
                status="success",
                saved=False,
                generated_image_url=generated_image_url,
                detected_parts=[furniture_id],
                created_at=now(),
                updated_at=now(),
            )

            # 5. DB 저장
            await self.interior_repository.create(interior)

            # 6. 매퍼로 최종 응답 생성
            return domain_to_interior_generate_response(
                interior, furnitures, products_map
            )

        except Exception as e:
            raise Exception(f"인테리어 생성 중 오류 발생: {str(e)}")

    async def _generate_interior_image(
        self,
        image_url: str,
        room_type: str,
        style: str,
        prompt: str,
    ) -> str:
        try:
            generated_image_url = await self.replicate_service.generate_interior_image(
                image_url, room_type, style, prompt
            )
            if generated_image_url:
                return generated_image_url
            else:
                return f"https://example.com/generated/{uuid4()}.jpg"
        except Exception as e:
            raise Exception(f"이미지 생성 실패: {str(e)}")

    async def get_interior_types_by_id(
        self, interior_types_id: str
    ) -> Optional[Interior]:
        return await self.interior_repository.get_by_interior_types_id(
            interior_types_id
        )

    async def get_user_interiors(self, user_id: str, limit: int = 10) -> List[Interior]:
        return await self.interior_repository.get_by_user_id(user_id, limit)

    async def save_interior(self, interior_id: str, user_id: str) -> bool:
        return await self.interior_repository.save_interior(interior_id, user_id)

    async def delete_interior(self, interior_id: str) -> bool:
        return await self.interior_repository.delete(interior_id)

    async def get_style_info_by_name(self, style_name: str) -> Optional[InteriorType]:
        """스타일 이름으로 스타일 정보 조회"""
        style_id = f"style_{style_name}"
        return await self.interior_repository.get_interior_type_by_id(style_id)

    async def get_all_interior_types(self):
        return await self.interior_repository.get_all_interior_types()

    async def get_user_library(self, user_id: str) -> list:
        # saved=True인 인테리어만 조회
        interiors = await self.interior_repository.get_by_user_id(user_id, limit=100)
        interiors = [i for i in interiors if i.saved]
        # 모든 detected_parts id 수집
        furniture_ids = set()
        for interior in interiors:
            if interior.detected_parts:
                furniture_ids.update(interior.detected_parts)
        # 가구 정보 조회
        furniture_map = {}
        for fid in furniture_ids:
            furniture = (
                await self.interior_repository.get_furniture_detected_by_interior_id(
                    fid
                )
            )
            if furniture:
                # get_furniture_detected_by_interior_id는 리스트 반환이므로 첫번째만 사용
                furniture_map[fid] = (
                    furniture[0] if isinstance(furniture, list) else furniture
                )
        return interiors, furniture_map
