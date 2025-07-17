# app/user/application/user_service.py
from app.user.domain.repository.user_repo import IUserRepository
from datetime import datetime
from typing import Optional
import ulid
import bcrypt
from app.user.schemas.user_schema import CreateUserBody, UserResponse
from app.user.mongo import user_collection

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
