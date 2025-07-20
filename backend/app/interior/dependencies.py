from fastapi import Depends
from app.interior.application.interior_service import InteriorService
from app.interior.infra.repository.interior_repository_impl import (
    InteriorRepositoryImpl,
)
from app.integrations.replicate import ReplicateService


def get_interior_repository() -> InteriorRepositoryImpl:
    """InteriorRepository 의존성 함수"""
    return InteriorRepositoryImpl()


def get_replicate_service() -> ReplicateService:
    """ReplicateService 의존성 함수"""
    return ReplicateService()


def get_interior_service(
    interior_repo: InteriorRepositoryImpl = Depends(get_interior_repository),
    replicate_service: ReplicateService = Depends(get_replicate_service),
) -> InteriorService:
    """InteriorService 의존성 함수"""
    return InteriorService(
        interior_repository=interior_repo, replicate_service=replicate_service
    )
