from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserInDB(BaseModel):
    _id: str
    email: EmailStr
    password: str
    name: str
    profile_image_url: Optional[str]
    created_at: datetime
    last_login_at: Optional[datetime]
    deleted_at: Optional[datetime]
    updated_at: datetime
