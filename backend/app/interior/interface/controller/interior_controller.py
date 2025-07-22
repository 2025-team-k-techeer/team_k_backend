from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from app.user.dependencies import get_current_user_id_bearer
from app.interior.dependencies import get_interior_service, get_gcs_service
from app.interior.application.interior_service import InteriorService
from app.integrations.gcs import GCSService
from app.interior.schemas.interior_schema import (
    InteriorGenerateRequest,
    InteriorGenerateResponse,
    StyleInfoRequest,
    StyleInfoResponse,
    StyleInfoListResponse,
    SaveInteriorRequest,
    SaveInteriorResponse,
    UserLibraryResponse,
    ImageUploadResponse,
    ErrorResponse,  # 추가
)
from app.interior.schemas.mappers import (
    interior_type_to_style_info_item,
    interior_type_to_style_info_response,
    domain_to_user_library_interior,
)

router = APIRouter(prefix="/interiors", tags=["Interior Api"])


# JWT 토큰 검증은 user 모듈의 의존성 함수를 사용합니다
# 쿠키 기반: get_current_user_id
# Bearer 토큰 기반: get_current_user_id_bearer


@router.post("/image", response_model=ImageUploadResponse)
async def upload_image(
    image: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id_bearer),
    gcs_service: GCSService = Depends(get_gcs_service),
):
    """
    이미지 파일을 GCS에 업로드하고 공개 URL 반환

    - 이미지는 항상 JPG로 변환되어 저장됩니다
    - 파일명은 SHA256 기반으로 암호화되어 URL이 유추되지 않습니다
    - 업로드된 이미지의 공개 URL과 실제 저장된 파일명을 반환합니다
    """
    try:
        # 파일 타입 검증
        if not image.content_type or not image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400, detail="이미지 파일만 업로드 가능합니다."
            )

        # 파일 크기 검증 (10MB 제한)
        if image.size and image.size > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400, detail="파일 크기는 10MB를 초과할 수 없습니다."
            )

        # 파일 내용 읽기
        image_data = await image.read()

        # GCS에 업로드
        upload_result = await gcs_service.upload_image(
            image_data=image_data,
            original_filename=image.filename or "unknown.jpg",
            user_id=user_id,
        )

        return ImageUploadResponse(
            status="success",
            message="이미지가 성공적으로 업로드되었습니다.",
            data=upload_result,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"이미지 업로드 중 오류가 발생했습니다: {str(e)}"
        )


@router.post(
    "/generate",
    response_model=InteriorGenerateResponse,
    responses={
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def generate_interior(
    request: InteriorGenerateRequest,
    user_id: str = Depends(get_current_user_id_bearer),
    interior_service: InteriorService = Depends(get_interior_service),
):
    """
    인테리어 이미지를 생성하고 가구를 인식하는 엔드포인트 (명세서 기반)
    """
    try:
        # 필수 필드 검증
        if not request.room_type or not request.style or not request.prompt:
            return (
                ErrorResponse(
                    status="failed",
                    message="room_type, style, prompt 중 하나 이상이 누락되었습니다.",
                    code="MISSING_FIELD",
                ),
                422,
            )
        if not request.image_url:
            return (
                ErrorResponse(
                    status="failed",
                    message="이미지 URL이 필요합니다.",
                    code="MISSING_FIELD",
                ),
                422,
            )

        # 서비스 호출
        response = await interior_service.generate_interior(
            user_id=user_id,
            image_url=request.image_url,
            room_type=request.room_type,
            style=request.style,
            prompt=request.prompt,
        )
        return response

    except Exception as e:
        return (
            ErrorResponse(
                status="error",
                message="Unexpected server error occurred.",
                code="INTERNAL_ERROR",
                detail=str(e),
            ),
            500,
        )


@router.post("/style-info", response_model=StyleInfoResponse)
async def get_style_info(
    request: StyleInfoRequest,
    interior_service: InteriorService = Depends(get_interior_service),
):
    """
    스타일 name을 기반으로 인테리어 스타일 정보를 조회합니다.
    """
    try:
        style_info = await interior_service.get_style_info_by_name(request.style_name)
        if not style_info:
            raise HTTPException(
                status_code=404, detail="해당 스타일을 찾을 수 없습니다."
            )
        return interior_type_to_style_info_response(style_info)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"서버 내부 오류가 발생했습니다: {str(e)}"
        )


@router.get("/style-info/all", response_model=StyleInfoListResponse)
async def get_all_style_info(
    interior_service: InteriorService = Depends(get_interior_service),
):
    """
    전체 인테리어 스타일 정보를 조회합니다.
    """
    try:
        styles = await interior_service.get_all_interior_types()
        data = [interior_type_to_style_info_item(style) for style in styles]
        return StyleInfoListResponse(status="success", data=data)
    except Exception:
        return {
            "status": "error",
            "message": "스타일 정보를 조회하는 도중 오류가 발생했습니다.",
        }


@router.post("/my-interior", response_model=SaveInteriorResponse)
async def save_interior(
    request: SaveInteriorRequest,
    user_id: str = Depends(get_current_user_id_bearer),
    interior_service: InteriorService = Depends(get_interior_service),
):
    """
    생성된 인테리어를 사용자 라이브러리에 저장합니다.
    """
    if not request.interior_id:
        return {"status": "error", "message": "interior_id가 누락되었습니다."}
    try:
        result = await interior_service.save_interior(request.interior_id, user_id)
        if not result:
            return {"status": "error", "message": "저장에 실패했습니다."}
        return SaveInteriorResponse(
            status="success",
            message="인테리어 정보가 라이브러리에 저장되었습니다.",
            saved_id=request.interior_id,
        )
    except Exception as e:
        return {"status": "error", "message": f"저장 중 오류 발생: {str(e)}"}


@router.get("/user-library", response_model=UserLibraryResponse)
async def get_user_library(
    user_id: str = Depends(get_current_user_id_bearer),
    interior_service: InteriorService = Depends(get_interior_service),
):
    """
    사용자가 저장한 인테리어 이미지 목록을 조회합니다.
    """
    try:
        interiors, furniture_map = await interior_service.get_user_library(user_id)
        result = [domain_to_user_library_interior(i, furniture_map) for i in interiors]
        return UserLibraryResponse(status="success", interiors=result)
    except Exception as e:
        return {"status": "error", "message": "인증되지 않은 사용자입니다."}
