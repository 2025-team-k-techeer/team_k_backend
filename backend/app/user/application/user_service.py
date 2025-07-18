# app/user/application/user_service.py
from app.user.domain.repository.user_repo import IUserRepository
from datetime import datetime
from typing import Optional
import ulid
import bcrypt
from app.user.schemas.user_schema import CreateUserBody, UserResponse, LoginUserBody
from app.user.mongo import user_collection
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

        # 비밀번호 제거 후 반환
        user.pop("password", None)
        user_response = UserResponse(**user)

        # JWT 토큰 발급
        user_id = user["_id"]
        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)
        return user_response, access_token, refresh_token
