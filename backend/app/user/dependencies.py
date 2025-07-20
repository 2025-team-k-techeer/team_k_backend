from fastapi import HTTPException, Depends, Cookie, Request
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from app.utils.jwt_utils import decode_token
from app.user.application.user_service import UserService
from app.user.infra.repository.user_repo import UserRepository


def get_user_repository() -> UserRepository:
    """UserRepository 의존성 함수"""
    return UserRepository()


def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
) -> UserService:
    """UserService 의존성 함수"""
    return UserService(user_repo)


# OAuth2 Bearer 토큰 스키마
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")


def get_current_user_id_bearer(token: str = Depends(oauth2_scheme)) -> str:
    """
    Bearer 토큰을 검증하고 사용자 ID를 반환하는 의존성 함수
    """
    try:
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            raise HTTPException(
                status_code=401,
                detail="유효하지 않은 토큰입니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="토큰에 사용자 정보가 없습니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user_id
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"토큰 검증 실패: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user_id_bearer_optional(
    token: str = Depends(oauth2_scheme),
) -> Optional[str]:
    """
    Bearer 토큰을 검증하고 사용자 ID를 반환하는 의존성 함수 (선택적)
    토큰이 없거나 유효하지 않아도 None을 반환
    """
    try:
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            return None

        user_id = payload.get("user_id")
        return user_id if user_id else None
    except Exception:
        return None


def get_current_user_id(access_token: str = Cookie(None)) -> str:
    """
    JWT 토큰을 검증하고 사용자 ID를 반환하는 의존성 함수 (쿠키 기반)
    """
    if not access_token:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")

    try:
        payload = decode_token(access_token)
        if not payload or payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")

        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=401, detail="토큰에 사용자 정보가 없습니다."
            )

        return user_id
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"토큰 검증 실패: {str(e)}")


def get_current_user_id_optional(access_token: str = Cookie(None)) -> Optional[str]:
    """
    JWT 토큰을 검증하고 사용자 ID를 반환하는 의존성 함수 (선택적)
    토큰이 없거나 유효하지 않아도 None을 반환
    """
    if not access_token:
        return None

    try:
        payload = decode_token(access_token)
        if not payload or payload.get("type") != "access":
            return None

        user_id = payload.get("user_id")
        return user_id if user_id else None
    except Exception:
        return None


def verify_token_from_request(request: Request) -> str:
    """
    Request 객체에서 토큰을 추출하고 검증하는 함수
    """
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")

    try:
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")

        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=401, detail="토큰에 사용자 정보가 없습니다."
            )

        return user_id
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"토큰 검증 실패: {str(e)}")
