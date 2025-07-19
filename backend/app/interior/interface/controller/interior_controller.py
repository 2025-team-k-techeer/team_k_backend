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

router = APIRouter(prefix="/api/interior", tags=["interior"])


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


@router.post("/upload-image", response_model=ImageUploadResponse)
async def upload_interior_image(
    image: UploadFile = File(..., alias="image"),
    user_id: str = Form(...),
    room_type_id: str = Form(...),
    interior_type_id: str = Form(...),
    interior_service: InteriorService = Depends(get_interior_service),
):
    """
    인테리어 이미지를 업로드합니다.

    - **image**: 업로드할 이미지 파일 (JPEG, PNG 등) - API 명세서 준수
    - **user_id**: 사용자 ID
    - **room_type_id**: 공간 유형 ID ("room_bedroom", "room_living", "room_study", "room_oneroom", "room_etc")
    - **interior_type_id**: 인테리어 스타일 ID ("style_modern", "style_minimal", "style_natural", "style_nordic", "style_industrial", "style_classic", "style_vintage", "style_tribal")

    명세서에 맞는 응답 형식으로 반환합니다.
    """
    try:
        result = await interior_service.upload_interior_image(
            file=image,
            user_id=user_id,
            room_type_id=room_type_id,
            interior_type_id=interior_type_id,
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": f"업로드 중 오류가 발생했습니다: {str(e)}",
            },
        )


@router.get("/projects/{project_id}", response_model=InteriorProject)
async def get_interior_project(
    project_id: str, interior_service: InteriorService = Depends(get_interior_service)
):
    """
    인테리어 프로젝트 정보를 가져옵니다.

    - **project_id**: 프로젝트 ID
    """
    project = await interior_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다")
    return project


@router.get("/projects/user/{user_id}", response_model=List[InteriorProject])
async def get_user_interior_projects(
    user_id: str, interior_service: InteriorService = Depends(get_interior_service)
):
    """
    사용자의 모든 인테리어 프로젝트를 가져옵니다.

    - **user_id**: 사용자 ID
    """
    projects = await interior_service.get_user_projects(user_id)
    return projects


@router.get("/projects/{project_id}/status")
async def get_project_status(
    project_id: str, interior_service: InteriorService = Depends(get_interior_service)
):
    """
    프로젝트 처리 상태를 확인합니다.

    - **project_id**: 프로젝트 ID
    """
    project = await interior_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다")

    return {
        "project_id": project.id,
        "status": project.status,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
    }


@router.delete("/projects/{project_id}")
async def delete_interior_project(
    project_id: str, interior_service: InteriorService = Depends(get_interior_service)
):
    """
    인테리어 프로젝트를 삭제합니다.

    - **project_id**: 프로젝트 ID
    """
    success = await interior_service.delete_project(project_id)
    if not success:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다")

    return {"message": "프로젝트가 성공적으로 삭제되었습니다"}


@router.get("/health")
async def interior_health_check():
    """
    인테리어 서비스 상태 확인
    """
    return {
        "status": "healthy",
        "service": "interior",
        "message": "인테리어 서비스가 정상적으로 실행 중입니다",
    }
