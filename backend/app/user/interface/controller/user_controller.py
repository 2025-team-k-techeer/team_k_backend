from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from app.user.application.user_service import UserService  # 클래스형으로 정의된 경우
from app.user.schemas.user_schema import CreateUserBody, UserResponse

# ⛳ 정확한 경로로 바꿔주세요!
from app.user.infra.repository.user_repo import UserRepository


router = APIRouter(prefix="/users", tags=["User Api"])


class Proflle(BaseModel):
    name: str
    email: str


# @router.post("/signup")
# async def signup(user: UserCreate):
#     print("📌 signup 요청 도착")  # ← 또는 여기에 중단점
#     await user_collection.insert_one(user.dict())  # ← 여기에 중단점 찍기
#     return {"message": "회원가입 완료"}


@router.post("/signup", status_code=201, response_model=UserResponse)
async def create_user(
    user: CreateUserBody,  # class CreateUserBody의 객체가 user
    # background_tasks: BackgroundTasks,
    # user_service: UserService = Depends(
    #     UserService
    # ),  # 일단 의존성없이가자 리팩토링 필요
):
    # user_service: Annotated[UserService, Depends(UserService)]):
    user_repo = UserRepository()  # ✅ 직접 생성
    user_service = UserService(user_repo)  # ✅ 직접 주입
    created_user = await user_service.create_user(
        # background_tasks=background_tasks,
        name=user.name,
        email=user.email,
        password=user.password,
    )
    return created_user
