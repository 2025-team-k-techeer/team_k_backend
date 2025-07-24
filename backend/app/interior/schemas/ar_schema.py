from pydantic import BaseModel
from typing import List, Optional


class ARSimilarObjectRequest(BaseModel):
    label: str


class ARPosition(BaseModel):
    x: float
    y: float
    z: float


class ARObject(BaseModel):
    id: str
    label: str
    model_url: str
    image_url: str
    position: ARPosition
    rotation: float
    scale: float
    width: Optional[float] = None
    depth: Optional[float] = None
    height: Optional[float] = None


class ARSimilarObjectResponse(BaseModel):
    status: str
    message: str
    objects: List[ARObject]
