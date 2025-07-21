from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class Dimensions:
    width_cm: int
    depth_cm: int
    height_cm: int


@dataclass
class DanawaProduct:
    id: str
    label: str
    product_name: str
    product_url: str
    image_url: str
    dimensions: Dimensions
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class BoundingBox:
    x: int
    y: int
    width: int
    height: int


@dataclass
class FurnitureDetected:
    id: str
    interior_id: str
    label: str
    bounding_box: BoundingBox
    danawa_products_id: List[str]
    created_at: Optional[datetime] = None


@dataclass
class InteriorType:
    id: str
    name: str
    description: str
    image_url: str


@dataclass
class Interior:
    id: str
    user_id: str
    original_image_url: str
    interior_type_id: str  # style 고정 문자열
    room_type_id: str  # room 고정 문자열
    status: str  # "done", "failed" 등
    saved: bool
    generated_image_url: Optional[str] = None
    detected_parts: Optional[List[str]] = None  # furniture_001, furniture_002 등
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
