# app/user/domain/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class Profile(BaseModel):
    name: str
    email: EmailStr


class User(BaseModel):
    id: str
    profile: Profile
    password: str
    memo: Optional[str] = None
    created_at: datetime
    updated_at: datetime
