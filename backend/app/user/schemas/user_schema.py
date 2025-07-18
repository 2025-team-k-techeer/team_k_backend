from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# 회원가입 요청 바디 사용자가 이 정보를 입력
class CreateUserBody(BaseModel):
    email: EmailStr
    password: str
    name: str
    profile_image_url: Optional[str] = None


# 응답 형식 사용자에게 이 정보를 보여줌
class UserResponse(BaseModel):
    _id: str
    email: EmailStr
    name: str
    profile_image_url: Optional[str]
    created_at: datetime
    last_login_at: Optional[datetime]
    deleted_at: Optional[datetime]
    updated_at: datetime


class LoginUserBody(BaseModel):
    email: str
    password: str
