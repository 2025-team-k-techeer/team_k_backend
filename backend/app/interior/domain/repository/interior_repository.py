from abc import ABC, abstractmethod
from typing import List, Optional
from app.interior.domain.interior import (
    Interior,
    InteriorType,
    FurnitureDetected,
    DanawaProduct,
)


class InteriorRepository(ABC):
    @abstractmethod
    async def create(self, interior: Interior) -> Interior:
        """인테리어 생성"""
        pass

    @abstractmethod
    async def get_by_id(self, interior_id: str) -> Optional[Interior]:
        """ID로 인테리어 조회"""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: str, limit: int = 10) -> List[Interior]:
        """사용자 ID로 인테리어 목록 조회"""
        pass

    @abstractmethod
    async def update(self, interior: Interior) -> Interior:
        """인테리어 업데이트"""
        pass

    @abstractmethod
    async def delete(self, interior_id: str) -> bool:
        """인테리어 삭제 (소프트 삭제)"""
        pass

    @abstractmethod
    async def save_interior(self, interior_id: str, user_id: str) -> bool:
        """인테리어 저장 상태 변경"""
        pass

    @abstractmethod
    async def get_all_interior_types(self) -> List[InteriorType]:
        """모든 인테리어 스타일 타입 조회"""
        pass

    @abstractmethod
    async def get_by_interior_types_id(self) -> Optional[InteriorType]:
        """인테리어 스타일 타입 조회"""
        pass

    @abstractmethod
    async def get_interior_type_by_id(
        self, interior_type_id: str
    ) -> Optional[InteriorType]:
        """ID로 인테리어 스타일 타입 조회"""
        pass

    @abstractmethod
    async def create_furniture_detected(
        self, furniture: FurnitureDetected
    ) -> FurnitureDetected:
        """가구 인식 결과 생성"""
        pass

    @abstractmethod
    async def get_furniture_detected_by_interior_id(
        self, interior_id: str
    ) -> List[FurnitureDetected]:
        """인테리어 ID로 가구 인식 결과 조회"""
        pass

    @abstractmethod
    async def get_danawa_products_by_ids(
        self, product_ids: List[str]
    ) -> List[DanawaProduct]:
        """제품 ID 리스트로 다나와 제품 조회"""
        pass
