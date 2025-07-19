# app/user/infra/repository/user_repository.py

from app.user.domain.repository.user_repo import IUserRepository
from app.user.domain.user import User, Profile
from fastapi import HTTPException
from app.mongo import user_collection
from datetime import datetime


class UserRepository(IUserRepository):
    async def save(self, user: User):
        doc = {
            "_id": user.id,
            "email": user.profile.email,
            "name": user.profile.name,
            "password": user.password,
            "memo": user.memo,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }
        await user_collection.insert_one(doc)

    async def find_by_email(self, email: str) -> User:
        doc = await user_collection.find_one({"email": email})
        if not doc:
            raise HTTPException(status_code=422)

        return self._map_user(doc)

    async def find_by_id(self, id: str) -> User:
        doc = await user_collection.find_one({"_id": id})
        if not doc:
            raise HTTPException(status_code=422)

        return self._map_user(doc)

    async def update(self, user: User):
        await user_collection.update_one(
            {"_id": user.id},
            {
                "$set": {
                    "name": user.profile.name,
                    "password": user.password,
                    "updated_at": datetime.now(),
                }
            },
        )

    async def delete_user(self, id: str):
        result = await user_collection.delete_one({"_id": id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=422)

    async def get_users(self) -> list[User]:
        cursor = user_collection.find({})
        users = []
        async for doc in cursor:
            users.append(self._map_user(doc))
        return users

    def _map_user(self, doc: dict) -> User:
        return User(
            id=doc["_id"],
            profile=Profile(name=doc["name"], email=doc["email"]),
            password=doc["password"],
            memo=doc.get("memo"),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
        )
