# app/user/application/user_service.py
from app.user.domain.repository.user_repo import IUserRepository
from datetime import datetime
from typing import Optional
import ulid
import bcrypt
from app.user.schemas.user_schema import (
    UserResponse,
    ProfileResponse,
)
from app.mongo import user_collection
from app.utils.jwt_utils import create_access_token, create_refresh_token

# from app.user.schemas.user_schema import UserResponse


class UserService:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def create_user(
        self,
        name: str,
        email: str,
        password: str,
        profile_image_url: Optional[str] = None,
    ) -> UserResponse:
        # 1. 이메일 중복 확인 나중에 구현하자
        existing_user = await user_collection.find_one({"email": email})
        if existing_user:
            raise ValueError("이미 사용 중인 이메일입니다.")

        # 2. 비밀번호 암호화
        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
            "utf-8"
        )

        # 3. 사용자 딕셔너리 생성
        now = datetime.now()
        user_dict = {
            "_id": str(ulid.new()),
            "email": email,
            "password": hashed_pw,
            "name": name,
            "profile_image_url": profile_image_url,
            "created_at": now,
            "last_login_at": None,
            "deleted_at": None,
            "updated_at": now,
        }

        # 4. MongoDB에 삽입
        await user_collection.insert_one(user_dict)

        # 5. 비밀번호 제거 후 응답용 데이터 반환
        del user_dict["password"]
        # MongoDB의 _id를 id로 변환
        user_dict["id"] = user_dict.pop("_id")
        return UserResponse(**user_dict)

    async def login_user(self, email: str, password: str):
        user = await user_collection.find_one({"email": email})
        if not user:
            raise ValueError("존재하지 않는 이메일입니다.")

        if not bcrypt.checkpw(
            password.encode("utf-8"), user["password"].encode("utf-8")
        ):
            raise ValueError("비밀번호가 일치하지 않습니다.")

        # 로그인 성공 시 last_login_at 업데이트
        from datetime import datetime

        await user_collection.update_one(
            {"_id": user["_id"]}, {"$set": {"last_login_at": datetime.now()}}
        )

        # JWT 토큰 발급
        user_id = user["_id"]
        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)
        return access_token, refresh_token

    async def get_user_by_id(self, user_id: str) -> Optional[ProfileResponse]:
        """사용자 ID로 사용자 프로필 정보 조회 (최소 정보만)"""
        user = await user_collection.find_one({"_id": user_id, "deleted_at": None})
        if not user:
            return None
        return ProfileResponse(
            id=str(user["_id"]),
            name=user["name"],
            email=user["email"],
            profile_image_url=user.get("profile_image_url"),
        )

    async def update_user_profile(
        self,
        user_id: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        profile_image_url: Optional[str] = None,
    ) -> ProfileResponse:
        """사용자 프로필 수정"""
        # 사용자 존재 확인
        existing_user = await user_collection.find_one(
            {"_id": user_id, "deleted_at": None}
        )
        if not existing_user:
            raise ValueError("사용자를 찾을 수 없습니다.")

        # 이메일 중복 확인 (이메일이 변경되는 경우)
        if email and email != existing_user.get("email"):
            email_exists = await user_collection.find_one(
                {"email": email, "deleted_at": None}
            )
            if email_exists:
                raise ValueError("이미 사용 중인 이메일입니다.")

        # 업데이트할 필드 구성
        update_fields: dict[str, object] = {"updated_at": datetime.now()}
        if name is not None:
            update_fields["name"] = name
        if email is not None:
            update_fields["email"] = email
        if profile_image_url is not None:
            update_fields["profile_image_url"] = profile_image_url

        # MongoDB 업데이트
        await user_collection.update_one({"_id": user_id}, {"$set": update_fields})

        # 업데이트된 사용자 정보 반환
        updated_user = await user_collection.find_one({"_id": user_id})
        if updated_user:
            return ProfileResponse(
                id=str(updated_user["_id"]),
                name=updated_user["name"],
                email=updated_user["email"],
                profile_image_url=updated_user.get("profile_image_url"),
            )
        else:
            raise ValueError("사용자 정보 업데이트 후 조회에 실패했습니다.")

    async def delete_user(self, user_id: str) -> bool:
        """사용자 삭제 (소프트 삭제)"""
        result = await user_collection.update_one(
            {"_id": user_id}, {"$set": {"deleted_at": datetime.now()}}
        )
        return result.modified_count > 0
