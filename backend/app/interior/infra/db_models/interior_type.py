# 응답 형식 사용자에게 이 정보를 보여줌
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# mongodb schema for interior type
class InteriorType(BaseModel):
    _id: str
    name: str
    description: str
    example_image_url: Optional[str]
    created_at: datetime
    updated_at: datetime


class Interior(BaseModel):

    _id: str
    user_id: str
    original_image_url: str
    interior_type_id: str  # style 고정 문자열
    room_type_id: str  # room 고정 문자열
    status: str  # "failed" 등 가능
    saved: bool
    generated_image_url: Optional[str]
    detected_parts: list[str]
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]
