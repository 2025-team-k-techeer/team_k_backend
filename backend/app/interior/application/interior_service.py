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
import asyncio
import time
from dataclasses import dataclass

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
        인테리어 이미지 생성 → 객체 인식 및 임베딩 추출 → Qdrant 검색 → 결과 가공 및 응답 생성
        """
        try:
            # 1. 인테리어 이미지 생성
            generated_image_url = await self._generate_interior_image(
                image_url, room_type, style, prompt
            )

            # 2. YOLO+CLIP 서버로 객체 인식 및 임베딩 추출
            yolo_results = await self._detect_furniture_with_yolo_clip(
                generated_image_url
            )

            # 3. Qdrant 검색 태스크 실행 및 polling
            detected_furnitures = await self._search_qdrant_for_furnitures(yolo_results)

            # 4. DB에서 상품 정보 조회 및 Qdrant 결과로 enrich
            await self._enrich_furnitures_with_db_and_qdrant(detected_furnitures)

            # 5. 각 가구(FurnitureDetected) 객체를 DB에 저장하고, id만 리스트로 추출
            detected_furniture_ids = []
            for furniture in detected_furnitures:
                # danawa_products_id 필드에 id 리스트 할당
                furniture.danawa_products_id = [
                    p.id for p in (furniture.danawa_products or [])
                ]
                await self.interior_repository.create_furniture_detected(furniture)
                detected_furniture_ids.append(furniture.id)

            # 6. Interior 객체 생성 시 detected_parts에 id 리스트만 넣기
            interior = Interior(
                id=str(uuid4()),
                user_id=user_id,
                original_image_url=image_url,
                generated_image_url=generated_image_url,
                interior_type_id=style,
                room_type_id=room_type,
                status="done",
                saved=False,
                detected_parts=detected_furniture_ids,
                created_at=now(),
                updated_at=now(),
            )
            await self.interior_repository.create(interior)

            # 7. 최종 응답 생성 (interior와 실제 가구 객체 리스트를 함께 반환)
            return domain_to_interior_generate_response(interior, detected_furnitures)

        except Exception as e:
            raise Exception(f"인테리어 생성 중 오류 발생: {str(e)}")

    async def _detect_furniture_with_yolo_clip(self, image_url: str):
        """YOLO+CLIP 서버에 이미지 URL을 전달하여 객체 인식 및 임베딩 추출"""
        async with httpx.AsyncClient() as client:
            yolo_resp = await client.post(
                YOLO_CLIP_API_URL,
                data={"url": image_url},
                timeout=60.0,
            )
            yolo_resp.raise_for_status()
            return yolo_resp.json()  # [{label, confidence, bbox, clip_embedding}, ...]

    async def _search_qdrant_for_furnitures(self, yolo_results):
        import uuid

        detected_furnitures = []
        celery_results = []
        # 1. 각 객체별로 Qdrant 검색 태스크 실행
        for obj in yolo_results:
            part_id = str(uuid.uuid4())
            bbox = obj["bbox"]
            label = obj.get("label", "object")
            embedding = obj.get("clip_embedding")
            celery_result = qdrant_search_task.delay(label, embedding, 5)
            celery_results.append((part_id, celery_result, label, bbox))

        # 2. polling: 모든 태스크가 끝날 때까지 대기
        timeout_sec = 30
        interval_sec = 0.5
        start = time.time()
        while True:
            if all(r.ready() for _, r, _, _ in celery_results):
                break
            if time.time() - start > timeout_sec:
                raise Exception("Qdrant 검색 태스크 timeout")
            await asyncio.sleep(interval_sec)

        # 3. 결과 가공 (DB 상품정보 미리 조회)
        all_product_ids = []
        all_hits = []
        for _, celery_result, _, _ in celery_results:
            qdrant_resp = celery_result.get()
            hits = qdrant_resp.get("result", [])
            points = (
                hits["points"] if isinstance(hits, dict) and "points" in hits else hits
            )
            for point in points:
                payload = point.get("payload", {})
                pid = payload.get("id")
                if pid:
                    all_product_ids.append(pid)
            all_hits.append(points)
        # DB에서 DanawaProduct 미리 조회
        products = await self.interior_repository.get_danawa_products_by_ids(
            list(set(all_product_ids))
        )
        products_map = {p.id: p for p in products}

        # 4. 각 가구별로 DanawaProduct, image_url 인덱스 매칭
        for idx, (part_id, _, label, bbox) in enumerate(celery_results):
            points = all_hits[idx]
            danawa_products = []
            danawa_products_image_index = []
            for point in points:
                payload = point.get("payload", {})
                qdrant_image_urls = payload.get("image_url", [])
                db_product = products_map.get(payload.get("id"))
                db_image_url = db_product.image_url if db_product else ""
                try:
                    img_idx = db_image_url.index(qdrant_image_urls)
                except ValueError:
                    img_idx = 0
                danawa_products_image_index.append(img_idx)
                danawa_products.append(qdrant_payload_to_danawa_product(payload))
            furniture = FurnitureDetected(
                id=part_id,
                label=label,
                bounding_box=BoundingBox(
                    x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3]
                ),
                danawa_products=danawa_products,
                danawa_products_image_index=danawa_products_image_index,
                created_at=now(),
            )
            # Qdrant hits도 함께 저장 (enrich용)
            furniture._qdrant_hits = points
            detected_furnitures.append(furniture)
        return detected_furnitures

    async def _enrich_furnitures_with_db_and_qdrant(self, detected_furnitures):
        all_product_ids = [p.id for f in detected_furnitures for p in f.danawa_products]
        products = await self.interior_repository.get_danawa_products_by_ids(
            all_product_ids
        )
        products_map = {p.id: p for p in products}

        def enrich_product_with_qdrant_info(product, qdrant_payload):
            return product.__class__(
                id=product.id,
                label=qdrant_payload.get("label", getattr(product, "label", "")),
                product_name=qdrant_payload.get(
                    "product_name", getattr(product, "product_name", "")
                ),
                product_url=qdrant_payload.get(
                    "product_url", getattr(product, "product_url", "")
                ),
                image_url=qdrant_payload.get(
                    "image_url", getattr(product, "image_url", "")
                ),
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
                created_at=qdrant_payload.get(
                    "created_at", getattr(product, "created_at", None)
                ),
                updated_at=qdrant_payload.get(
                    "updated_at", getattr(product, "updated_at", None)
                ),
            )

        for furniture in detected_furnitures:
            enriched_products = []
            for i, product in enumerate(furniture.danawa_products):
                # Qdrant hits에서 image_url 리스트 추출
                points = getattr(furniture, "_qdrant_hits", [])
                payload = None
                qdrant_image_urls = []
                for point in points:
                    if point.get("payload", {}).get("id") == product.id:
                        payload = point.get("payload", {})
                        qdrant_image_urls = payload.get("image_url", [])
                        if isinstance(qdrant_image_urls, str):
                            qdrant_image_urls = [qdrant_image_urls]
                        break
                idx = (
                    furniture.danawa_products_image_index[i]
                    if furniture.danawa_products_image_index
                    and len(furniture.danawa_products_image_index) > i
                    else 0
                )
                image_url = (
                    qdrant_image_urls[idx]
                    if qdrant_image_urls and len(qdrant_image_urls) > idx
                    else (qdrant_image_urls[0] if qdrant_image_urls else "")
                )
                db_product = products_map.get(product.id, product)
                enriched = enrich_product_with_qdrant_info(db_product, payload or {})
                enriched.image_url = image_url  # 대표 이미지로 덮어쓰기
                enriched_products.append(enriched)
            furniture.danawa_products = enriched_products

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

    async def get_user_library(self, user_id: str) -> tuple[list, dict, dict]:
        # saved=True인 인테리어만 조회
        interiors = await self.interior_repository.get_by_user_id(user_id, limit=100)
        interiors = [i for i in interiors if i.saved]
        # 모든 detected_parts id 수집
        furniture_ids = set()
        for interior in interiors:
            if interior.detected_parts:
                furniture_ids.update(interior.detected_parts)
        # 가구 정보 조회 (id 리스트로 한 번에)
        furniture_map = {}
        if furniture_ids:
            furnitures = await self.interior_repository.get_furniture_detected_by_ids(
                list(furniture_ids)
            )
            for f in furnitures:
                furniture_map[f.id] = f
        # 모든 danawa_products_id 수집
        product_ids = set()
        for f in furniture_map.values():
            if f.danawa_products_id:
                product_ids.update(f.danawa_products_id)
        products_map = {}
        if product_ids:
            products = await self.interior_repository.get_danawa_products_by_ids(
                list(product_ids)
            )
            for p in products:
                products_map[p.id] = p
        return interiors, furniture_map, products_map
