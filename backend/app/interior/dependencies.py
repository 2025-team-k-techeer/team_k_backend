from fastapi import Depends
from app.interior.application.interior_service import InteriorService
from app.interior.infra.repository.interior_repository_impl import (
    InteriorRepositoryImpl,
)
from app.integrations.gcs import GCSService


def get_interior_repository() -> InteriorRepositoryImpl:
    return InteriorRepositoryImpl()


def get_interior_service() -> InteriorService:
    repository = get_interior_repository()
    return InteriorService(repository)


def get_gcs_service() -> GCSService:
    return GCSService()
