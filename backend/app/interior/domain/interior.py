from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class InteriorProject(BaseModel):
    id: Optional[str] = None
    user_id: str
    original_image_url: str
    generated_image_url: Optional[str] = None
    room_type_id: (
        str  # "room_bedroom", "room_living", "room_study", "room_oneroom", "room_etc"
    )
    interior_type_id: str  # "style_modern", "style_minimal", "style_natural", "style_nordic", "style_industrial", "style_classic", "style_vintage", "style_tribal"
    status: str = "uploaded"  # uploaded, processing, completed, failed
    saved: bool = False
    detected_parts: Optional[List[str]] = None  # 감지된 가구 ID 목록
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    deleted_at: Optional[datetime] = None


class ImageUploadRequest(BaseModel):
    user_id: str
    room_type_id: str
    interior_type_id: str


class ImageUploadResponse(BaseModel):
    status: str
    image_url: str
    filename: str


class InteriorGenerationRequest(BaseModel):
    project_id: str
    style_preference: Optional[str] = None
    furniture_preference: Optional[List[str]] = None


class InteriorGenerationResponse(BaseModel):
    status: str
    generated_image_url: Optional[str] = None
    furniture_recommendations: Optional[List[dict]] = None
    ar_scene_url: Optional[str] = None
    message: str
