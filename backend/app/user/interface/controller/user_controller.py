from fastapi import APIRouter, HTTPException, Depends, Response, Cookie, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from app.user.application.user_service import UserService
from app.user.schemas.user_schema import (
    CreateUserBody,
    UserResponse,
    LoginUserBody,
    TokenResponse,
    ProfileResponse,
)
from app.utils.jwt_utils import decode_token, create_access_token, create_refresh_token
from app.user.dependencies import (
    get_current_user_id,
    get_user_service,
    get_current_user_id_bearer,
)
import logging
from app.interior.dependencies import get_interior_service
from app.interior.application.interior_service import InteriorService
from app.utils.logger import get_logger

router = APIRouter(prefix="/users", tags=["User Api"])
logger = get_logger("user_controller")

# OAuth2 스키마 정의
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


class Profile(BaseModel):
    name: str
    email: str


@router.post("/signup", status_code=201)
async def create_user(
    user: CreateUserBody,
    user_service: UserService = Depends(get_user_service),
):
    """사용자 회원가입"""
    try:
        logger.info(f"회원가입 요청 - 이메일: {user.email}, 이름: {user.name}")

        await user_service.create_user(
            name=user.name,
            email=user.email,
            password=user.password,
        )

        logger.info(f"회원가입 성공 - 이메일: {user.email}")
        return {"status": "success", "message": "회원가입이 완료되었습니다."}
    except ValueError as e:
        logger.warning(
            f"회원가입 실패 (검증 오류) - 이메일: {user.email}, 오류: {str(e)}"
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            f"회원가입 실패 (서버 오류) - 이메일: {user.email}, 오류: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=f"서버 내부 오류: {str(e)}")


# @router.post("/login")
# async def login_user(
#     user: LoginUserBody,
#     response: Response,
#     user_service: UserService = Depends(get_user_service),
# ):
#     """사용자 로그인 (쿠키 기반)"""
#     try:
#         access_token, refresh_token = await user_service.login_user(
#             user.email, user.password
#         )
#         # 쿠키에 토큰 저장
#         response.set_cookie(
#             key="access_token", value=access_token, httponly=True, secure=False
#         )
#         response.set_cookie(
#             key="refresh_token", value=refresh_token, httponly=True, secure=False
#         )
#         return {
#             "status": "success",
#             "message": "로그인 성공",
#             "access_token": access_token,
#             "refresh_token": refresh_token,
#         }
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"서버 내부 오류: {str(e)}")


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service),
):
    """OAuth2 표준 토큰 발급 (Bearer 토큰)"""
    try:
        logger.info(f"로그인 요청 - 사용자: {form_data.username}")

        access_token, refresh_token = await user_service.login_user(
            form_data.username, form_data.password
        )

        logger.info(f"로그인 성공 - 사용자: {form_data.username}")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 3600,  # 1시간
        }
    except ValueError as e:
        logger.warning(
            f"로그인 실패 (인증 오류) - 사용자: {form_data.username}, 오류: {str(e)}"
        )
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 내부 오류: {str(e)}")


@router.post("/logout")
async def logout_user(response: Response):
    """사용자 로그아웃"""
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return {"message": "로그아웃되었습니다."}


# @router.post("/token/verify")
# async def verify_token(
#     user_id: str = Depends(get_current_user_id_bearer),
# ):  # Bearer 토큰 기반으로 변경
#     """토큰 검증 (Bearer 토큰 기반)"""
#     return {"valid": True, "user_id": user_id}


class RefreshTokenBody(BaseModel):
    refresh_token: str


# @router.post("/token/refresh")
# async def refresh_access_token(
#     body: RefreshTokenBody,
# ):
#     """액세스 토큰 갱신 (Bearer 토큰 기반, request body로 받음)"""
#     refresh_token = body.refresh_token
#     if not refresh_token:
#         raise HTTPException(status_code=401, detail="리프레시 토큰이 필요합니다.")

#     try:
#         payload = decode_token(refresh_token)
#         if payload and payload.get("type") == "refresh":
#             new_access_token = create_access_token(payload["user_id"])
#             return {"access_token": new_access_token}
#         else:
#             raise HTTPException(
#                 status_code=401, detail="유효하지 않은 refresh 토큰입니다."
#             )
#     except Exception as e:
#         raise HTTPException(status_code=401, detail=f"토큰 갱신 실패: {str(e)}")


# @router.post("/token/refresh-bearer")
# async def refresh_access_token_bearer(
#     refresh_token: str, user_service: UserService = Depends(get_user_service)
# ):
#     """액세스 토큰 갱신 (Bearer 토큰 기반)"""
#     try:
#         payload = decode_token(refresh_token)
#         if payload and payload.get("type") == "refresh":
#             user_id = payload["user_id"]
#             new_access_token = create_access_token(user_id)
#             new_refresh_token = create_refresh_token(user_id)
#             # 사용자 정보 조회 (더 이상 반환하지 않음)
#             user = await user_service.get_user_by_id(user_id)
#             if not user:
#                 raise HTTPException(
#                     status_code=404, detail="사용자를 찾을 수 없습니다."
#                 )
#             return {
#                 "access_token": new_access_token,
#                 "refresh_token": new_refresh_token,
#                 "token_type": "bearer",
#                 "expires_in": 3600,
#             }
#         else:
#             raise HTTPException(
#                 status_code=401, detail="유효하지 않은 refresh 토큰입니다."
#             )
#     except Exception as e:
#         raise HTTPException(status_code=401, detail=f"토큰 갱신 실패: {str(e)}")


@router.get("/mypage")
async def get_mypage(
    user_id: str = Depends(get_current_user_id_bearer),  # Bearer 토큰 기반 인증
    user_service: UserService = Depends(get_user_service),
    interior_service: InteriorService = Depends(get_interior_service),
):
    """마이페이지 조회"""
    try:
        # 사용자 정보 조회
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

        user_info = {
            "name": user.name,
            "email": user.email,
            "profile_image_url": user.profile_image_url,
        }

        # 저장된 인테리어 리스트 조회 (최대 6개)
        interiors = await interior_service.get_user_interiors(user_id, limit=6)

        # 저장된 인테리어만 필터링
        saved_interiors = [
            {
                "id": interior.id,
                "generated_image_url": interior.generated_image_url,
                "room_type_id": interior.room_type_id,
                "interior_type_id": interior.interior_type_id,
                "saved": interior.saved,
                "created_at": (
                    interior.created_at.isoformat() if interior.created_at else None
                ),
            }
            for interior in interiors
            if interior.saved
        ]

        return {"status": "success", "user": user_info, "interiors": saved_interiors}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 내부 오류: {str(e)}")


@router.get("/profile")
async def get_user_profile(
    user_id: str = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service),
):
    """사용자 프로필 조회"""
    try:
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
        return {
            "status": "success",
            "user": user.dict(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 내부 오류: {str(e)}")


@router.put("/profile")
async def update_user_profile(
    profile: Profile,
    user_id: str = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service),
):
    """사용자 프로필 수정"""
    try:
        updated_user = await user_service.update_user_profile(
            user_id=user_id,
            name=profile.name,
            email=profile.email,
        )
        return {
            "status": "success",
            "message": "프로필이 수정되었습니다.",
            "user": updated_user,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 내부 오류: {str(e)}")
