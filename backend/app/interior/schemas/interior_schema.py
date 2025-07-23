from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# Request
class InteriorGenerateRequest(BaseModel):
    image_url: str
    room_type: str
    style: str
    prompt: str


# Response
class Dimensions(BaseModel):
    """제품 크기 정보 스키마"""

    width_cm: int
    depth_cm: int
    height_cm: int


class DanawaProduct(BaseModel):
    """다나와 제품 정보 스키마 (명세서 기반)"""

    id: str
    name: str
    product_url: str
    image_url: str
    dimensions: Dimensions
    label: Optional[str] = (
        None  # 명세서에는 label 필드가 있으나, 실제 DB에는 없을 수 있어 optional 처리
    )


class BoundingBox(BaseModel):
    """가구 위치 정보 스키마 (명세서 기반)"""

    x: float  # YOLO+CLIP에서 float으로 반환됨
    y: float
    width: float
    height: float


class DetectedPart(BaseModel):
    id: str
    bounding_box: BoundingBox
    danawa_products: Optional[List[DanawaProduct]] = None
    created_at: datetime
    label: Optional[str] = None  # 객체 인식 label (YOLO+CLIP)


class InteriorGenerateResponse(BaseModel):
    """인테리어 생성 응답 스키마 (명세서 기반)"""

    id: str
    status: str
    original_image_url: str
    generated_image_url: str
    saved: bool
    detected_parts: List[DetectedPart]


class StyleInfo(BaseModel):
    style_id: str
    name: str
    description: str


class StyleInfoRequest(BaseModel):
    """스타일 정보 조회 요청 스키마"""

    style_name: str


class StyleInfoResponse(StyleInfo):
    status: str


class StyleInfoListResponse(BaseModel):
    status: str
    data: list[StyleInfo]


# 오류 응답 스키마 (명세서 기반)
class ErrorResponse(BaseModel):
    """에러 응답 스키마"""

    status: str
    message: str
    code: str
    detail: Optional[str] = None


class SaveInteriorRequest(BaseModel):
    interior_id: str


class SaveInteriorResponse(BaseModel):
    status: str
    message: str
    saved_id: str


class UserLibraryBoundingBox(BaseModel):
    x: float
    y: float
    width: float
    height: float


class UserLibraryDetectedPart(BaseModel):
    furniture_id: str
    label: str
    bounding_box: UserLibraryBoundingBox
    danawa_products: List[DanawaProduct]  # 실제 상품 정보 리스트 추가


class UserLibraryInterior(BaseModel):
    interior_id: str
    original_image_url: str
    generated_image_url: Optional[str]
    interior_type_id: str
    room_type_id: str
    status: str
    created_at: datetime
    detected_parts: List[UserLibraryDetectedPart]


class UserLibraryResponse(BaseModel):
    status: str
    interiors: List[UserLibraryInterior]


# 이미지 업로드 관련 스키마
class ImageUploadResponse(BaseModel):
    """이미지 업로드 응답 스키마"""

    status: str
    message: str
    data: dict

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "이미지가 성공적으로 업로드되었습니다.",
                "data": {
                    "public_url": "https://storage.googleapis.com/team-k-interior-images/interior/abc123def456.jpg",
                    "filename": "abc123def456.jpg",
                    "size": 1024000,
                },
            }
        }
