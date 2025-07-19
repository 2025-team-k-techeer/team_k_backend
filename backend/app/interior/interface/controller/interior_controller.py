import os
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import FileResponse
from motor.motor_asyncio import AsyncIOMotorClient

from app.interior.application.interior_service import InteriorService
from app.interior.domain.interior import InteriorProject, ImageUploadResponse
from app.interior.infra.repository.interior_repo import MongoInteriorRepository
from app.config import get_settings

settings = get_settings()

router = APIRouter(prefix="/api/interiors", tags=["interior"])


# MongoDB 클라이언트 의존성
async def get_mongo_client() -> AsyncIOMotorClient:
    client = AsyncIOMotorClient(settings.MONGO_URI)
    try:
        yield client
    finally:
        client.close()


# 인테리어 서비스 의존성
async def get_interior_service(
    client: AsyncIOMotorClient = Depends(get_mongo_client),
) -> InteriorService:
    repository = MongoInteriorRepository(client)
    return InteriorService(repository)


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
):
    """
    인테리어 이미지를 업로드합니다. (명세서 준수)
    - file: 업로드할 이미지 파일 (JPEG, PNG 등)
    """
    # 파일 유효성 검사
    if not file.content_type or not file.content_type.startswith("image/"):
        return {"status": "error", "message": "이미지 파일이 없습니다."}, 400

    from app.interior.application.interior_service import save_uploaded_image_only

    try:
        result = await save_uploaded_image_only(file)
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": f"이미지 업로드 중 오류가 발생했습니다: {str(e)}",
        }, 400
