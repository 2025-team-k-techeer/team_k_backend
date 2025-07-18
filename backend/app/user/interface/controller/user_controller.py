from fastapi import APIRouter, HTTPException, Depends, Response, Cookie, Request
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from app.user.application.user_service import UserService  # 클래스형으로 정의된 경우
from app.user.schemas.user_schema import CreateUserBody, UserResponse, LoginUserBody
from app.utils.jwt_utils import decode_token, create_access_token, get_current_user_id

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


@router.post("/login", response_model=UserResponse)
async def login_user(user: LoginUserBody, response: Response):
    user_repo = UserRepository()
    user_service = UserService(user_repo)
    try:
        user_obj, access_token, refresh_token = await user_service.login_user(
            user.email, user.password
        )
        # 쿠키에 토큰 저장
        response.set_cookie(
            key="access_token", value=access_token, httponly=True, secure=False
        )
        response.set_cookie(
            key="refresh_token", value=refresh_token, httponly=True, secure=False
        )
        return user_obj
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/token/verify")
async def verify_token(access_token: str = Cookie(None)):
    payload = decode_token(access_token)
    if payload and payload.get("type") == "access":
        return {"valid": True, "user_id": payload["user_id"]}
    return {"valid": False}


@router.post("/token/refresh")
async def refresh_access_token(refresh_token: str = Cookie(None)):
    payload = decode_token(refresh_token)
    if payload and payload.get("type") == "refresh":
        new_access_token = create_access_token(payload["user_id"])
        response = Response()
        response.set_cookie(
            key="access_token", value=new_access_token, httponly=True, secure=False
        )
        return {"access_token": new_access_token}
    raise HTTPException(status_code=401, detail="유효하지 않은 refresh 토큰입니다.")


@router.get("/mypage", tags=["User Api"])
async def get_mypage(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return {"status": "error", "message": "로그인이 필요합니다."}, 401
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        return {"status": "error", "message": "로그인이 필요합니다."}, 401
    user_id = payload["user_id"]

    # 사용자 정보 조회
    from app.user.mongo import user_collection

    user = await user_collection.find_one({"_id": user_id})
    if not user:
        return {"status": "error", "message": "사용자를 찾을 수 없습니다."}, 404
    user_info = {
        "name": user.get("name"),
        "email": user.get("email"),
        "profile_image_url": user.get("profile_image_url"),
    }

    # 인테리어 리스트 조회
    from app.user.mongo import user_collection
    from motor.motor_asyncio import AsyncIOMotorClient

    db = user_collection.database
    interior_collection = db.get_collection("interior")
    interiors_cursor = (
        interior_collection.find(
            {"user_id": user_id, "saved": True, "deleted_at": None}
        )
        .sort("created_at", -1)
        .limit(6)
    )
    interiors = []
    async for doc in interiors_cursor:
        interiors.append(
            {
                "_id": str(doc.get("_id")),
                "generated_image_url": doc.get("generated_image_url"),
                "interior_type_id": doc.get("interior_type_id"),
                "saved": doc.get("saved", False),
                "created_at": (
                    doc.get("created_at").isoformat() if doc.get("created_at") else None
                ),
            }
        )

    return {"status": "success", "user": user_info, "interiors": interiors}
