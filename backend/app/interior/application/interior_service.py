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
from app.config import get_settings


# Celery 및 Qdrant 연동 import (분리된 태스크)
from app.interior.tasks.qdrant_tasks import qdrant_search_task

import httpx
import uuid
import asyncio
import time

settings = get_settings()

YOLO_CLIP_API_URL = "https://yolo-clip-api-604858116968.asia-northeast3.run.app/process"
QDRANT_SEARCH_URL = settings.QDRANT_SEARCH_URL


# Qdrant 유사도 검색 Celery 태스크
def qdrant_search(embedding, top_k=3):
    import requests

    payload = {"vector": embedding, "top": top_k, "with_payload": True}
    resp = requests.post(QDRANT_SEARCH_URL, json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()


def now(utc=True):
    if utc:
        return datetime.utcnow()
    return datetime.now()


def qdrant_payload_to_danawa_product(payload):
    return DanawaProduct(
        id=payload.get("id", ""),
        label=payload.get("label", ""),
        product_name=payload.get("product_name", ""),
        product_url=payload.get("product_url", ""),
        image_url=payload.get("image_url", ""),
        dimensions=Dimensions(
            width_cm=payload.get("width_cm", 0),
            depth_cm=payload.get("depth_cm", 0),
            height_cm=payload.get("height_cm", 0),
        ),
        created_at=payload.get("created_at"),
        updated_at=payload.get("updated_at"),
    )


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
        인테리어 이미지 생성 및 가구 인식 (YOLO+CLIP → Celery로 Qdrant 병렬 검색, 내부 polling)
        """
        try:
            # 1. 인테리어 이미지 생성 (Replicate 등)
            generated_image_url = await self._generate_interior_image(
                image_url, room_type, style, prompt
            )

            # 2. YOLO+CLIP 서버에 생성된 이미지 URL 전달하여 객체 인식 및 임베딩 추출
            async with httpx.AsyncClient() as client:
                yolo_resp = await client.post(
                    YOLO_CLIP_API_URL,
                    data={"url": generated_image_url},  # form-data로 보냄
                    timeout=60.0,
                )
                yolo_resp.raise_for_status()
                yolo_results = (
                    yolo_resp.json()
                )  # [{label, confidence, bbox, clip_embedding}, ...]

            detected_part_ids = []
            celery_results = []
            for obj in yolo_results:
                part_id = str(uuid.uuid4())
                bbox = obj["bbox"]  # [x, y, width, height]
                label = obj.get("label", "object")
                embedding = obj.get("clip_embedding")
                celery_result = qdrant_search_task.delay(embedding, 5)
                celery_results.append((part_id, celery_result, label, bbox))
                detected_part_ids.append(part_id)

            # 내부 polling: 모든 태스크가 끝날 때까지 주기적으로 체크
            timeout_sec = 30  # 최대 30초 대기
            interval_sec = 0.5  # 0.5초마다 체크
            start = time.time()
            while True:
                if all(r.ready() for _, r, _, _ in celery_results):
                    break
                if time.time() - start > timeout_sec:
                    raise Exception("Qdrant 검색 태스크 timeout")
                await asyncio.sleep(interval_sec)

            # 결과 모으기
            detected_furnitures = []
            for part_id, celery_result, label, bbox in celery_results:
                qdrant_resp = celery_result.get()
                hits = qdrant_resp.get("result", [])
                danawa_products = [
                    qdrant_payload_to_danawa_product(hit.get("payload", {}))
                    for hit in hits
                ]
                furniture = FurnitureDetected(
                    id=part_id,
                    label=label,
                    bounding_box=BoundingBox(
                        x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3]
                    ),
                    danawa_products=danawa_products,
                    created_at=now(),
                )
                detected_furnitures.append(furniture)

            # 4. 상품 정보 조회
            products = await self.interior_repository.get_danawa_products_by_ids(
                [p.id for f in detected_furnitures for p in f.danawa_products]
            )
            products_map = {p.id: p for p in products}

            # 7. 매퍼로 최종 응답 생성 (Qdrant payload의 image_url, product_name 등 반영)
            def enrich_product_with_qdrant_info(product, qdrant_payload):
                return product.__class__(
                    id=product.id,
                    name=qdrant_payload.get("product_name", product.name),
                    product_url=qdrant_payload.get("product_url", product.product_url),
                    image_url=qdrant_payload.get("image_url", product.image_url),
                    dimensions=Dimensions(
                        width_cm=qdrant_payload.get(
                            "width_cm", getattr(product.dimensions, "width_cm", 0)
                        ),
                        depth_cm=qdrant_payload.get(
                            "depth_cm", getattr(product.dimensions, "depth_cm", 0)
                        ),
                        height_cm=qdrant_payload.get(
                            "height_cm", getattr(product.dimensions, "height_cm", 0)
                        ),
                    ),
                    label=qdrant_payload.get("label", product.label),
                )

            # products_map은 DB 기준이므로, Qdrant payload 정보로 enrich
            for part in detected_furnitures:
                for i, pid in enumerate(part.danawa_products_id):
                    # Qdrant payload에서 해당 id의 정보 찾기
                    for hit in hits:
                        payload = hit.get("payload", {})
                        if payload.get("id") == pid and pid in products_map:
                            products_map[pid] = enrich_product_with_qdrant_info(
                                products_map[pid], payload
                            )

            return domain_to_interior_generate_response(detected_furnitures)

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
