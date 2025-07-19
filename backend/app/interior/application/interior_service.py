import os
import uuid
import asyncio
from datetime import datetime
from typing import Optional, List
from pathlib import Path
import aiofiles
from fastapi import UploadFile, HTTPException
from PIL import Image as PILImage
import io

from app.interior.domain.interior import (
    InteriorProject,
    ImageUploadResponse,
    InteriorGenerationResponse,
)
from app.interior.domain.repository.interior_repo import InteriorRepository
from app.config import get_settings

settings = get_settings()


class InteriorService:
    def __init__(self, interior_repository: InteriorRepository):
        self.interior_repository = interior_repository
        self.upload_dir = Path("uploads/interior")
        self.processed_dir = Path("uploads/processed")
        self._ensure_directories()

    def _ensure_directories(self):
        """업로드 및 처리된 이미지를 저장할 디렉토리를 생성합니다."""
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    async def upload_interior_image(
        self,
        file: UploadFile,
        user_id: str,
        room_type_id: str,
        interior_type_id: str,
    ) -> ImageUploadResponse:
        """인테리어 이미지를 비동기로 업로드합니다."""
        try:
            # 파일 유효성 검사
            if not file.content_type.startswith("image/"):
                raise HTTPException(
                    status_code=400,
                    detail={
                        "status": "error",
                        "message": "이미지 파일만 업로드 가능합니다.",
                    },
                )

            # 파일 크기 제한 (10MB)
            if file.size and file.size > 10 * 1024 * 1024:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "status": "error",
                        "message": "파일 크기는 10MB를 초과할 수 없습니다.",
                    },
                )

            # 고유한 파일명 생성
            file_extension = Path(file.filename).suffix if file.filename else ".jpg"
            unique_filename = f"{user_id}_{uuid.uuid4()}{file_extension}"
            upload_path = self.upload_dir / unique_filename

            # 파일을 비동기로 저장
            content = await file.read()
            async with aiofiles.open(upload_path, "wb") as f:
                await f.write(content)

            # 이미지 URL 생성 (명세서에 맞는 형식)
            image_url = f"http://localhost:8000/uploads/{unique_filename}"

            # 인테리어 프로젝트 생성
            project = InteriorProject(
                user_id=user_id,
                original_image_url=image_url,
                room_type_id=room_type_id,
                interior_type_id=interior_type_id,
                status="uploaded",
            )

            # 데이터베이스에 저장
            saved_project = await self.interior_repository.save_project(project)

            # 백그라운드에서 AI 처리 시작
            asyncio.create_task(self._process_interior_async(saved_project.id))

            return ImageUploadResponse(
                status="success",
                image_url=image_url,
                filename=unique_filename,
                project_id=saved_project.id,
                message="인테리어 이미지가 성공적으로 업로드되었습니다. AI 처리를 시작합니다.",
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "status": "error",
                    "message": f"이미지 업로드 중 오류가 발생했습니다: {str(e)}",
                },
            )

    async def _process_interior_async(self, project_id: str):
        """백그라운드에서 인테리어를 비동기로 처리합니다."""
        try:
            # 상태를 processing으로 업데이트
            await self.interior_repository.update_project_status(
                project_id, "processing"
            )

            # 프로젝트 정보 가져오기
            project = await self.interior_repository.find_project_by_id(project_id)
            if not project:
                return

            # TODO: AI 인테리어 생성 (RoomGPT, Stable Diffusion 등)
            # generated_image_url = await self._generate_interior_ai(project)

            # TODO: 가구 감지 (YOLO, BLIP)
            # furniture_detected = await self._detect_furniture(project)

            # TODO: AR 씬 생성
            # ar_scene_url = await self._create_ar_scene(project)

            # 임시로 성공 상태로 업데이트
            await self.interior_repository.update_project_status(
                project_id, "completed"
            )

        except Exception as e:
            # 오류 발생 시 상태를 failed로 업데이트
            await self.interior_repository.update_project_status(project_id, "failed")
            print(f"인테리어 처리 중 오류 발생: {str(e)}")

    async def _generate_interior_ai(self, project: InteriorProject) -> str:
        """AI를 사용하여 인테리어 이미지를 생성합니다."""
        # TODO: RoomGPT, Stable Diffusion API 연동
        # 예시: RoomGPT API 호출
        # response = await roomgpt_client.generate(project.original_image_url, project.requirements)
        # return response.generated_image_url
        pass

    async def _detect_furniture(self, project: InteriorProject) -> List[dict]:
        """이미지에서 가구를 감지합니다."""
        # TODO: YOLO, BLIP 모델 연동
        # 예시: YOLO 모델로 가구 감지
        # furniture_list = await yolo_model.detect(project.original_image_url)
        # return furniture_list
        pass

    async def _create_ar_scene(self, project: InteriorProject) -> str:
        """AR 씬을 생성합니다."""
        # TODO: Three.js, AR.js 연동
        # 예시: AR 씬 생성
        # ar_scene = await ar_service.create_scene(project.furniture_detected)
        # return ar_scene.url
        pass

    async def get_project(self, project_id: str) -> Optional[InteriorProject]:
        """프로젝트 정보를 가져옵니다."""
        return await self.interior_repository.find_project_by_id(project_id)

    async def get_user_projects(self, user_id: str) -> List[InteriorProject]:
        """사용자의 모든 프로젝트를 가져옵니다."""
        return await self.interior_repository.find_projects_by_user_id(user_id)

    async def delete_project(self, project_id: str) -> bool:
        """프로젝트를 삭제합니다."""
        project = await self.interior_repository.find_project_by_id(project_id)
        if not project:
            return False

        # 파일 삭제
        try:
            filename = project.original_image_url.split("/")[-1]
            file_path = self.upload_dir / filename
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass

        # 데이터베이스에서 삭제
        return await self.interior_repository.delete_project(project_id)
