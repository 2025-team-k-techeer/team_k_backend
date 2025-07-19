import os
import uuid
from datetime import datetime
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

from app.interior.domain.interior import InteriorProject
from app.interior.domain.repository.interior_repo import InteriorRepository
from app.interior.infra.db_models.interior import InteriorProjectModel
from app.config import get_settings

settings = get_settings()


class MongoInteriorRepository(InteriorRepository):
    def __init__(self, client: AsyncIOMotorClient):
        self.client = client
        self.db = client.interior_db
        self.collection = self.db.interior_projects

    async def save_project(self, project: InteriorProject) -> InteriorProject:
        # MongoDB에 저장할 모델로 변환
        project_dict = project.dict()
        if project.id:
            project_dict["_id"] = ObjectId(project.id)
        else:
            project_dict["_id"] = ObjectId()

        project_dict["created_at"] = datetime.now()
        project_dict["updated_at"] = datetime.now()

        result = await self.collection.insert_one(project_dict)
        project.id = str(result.inserted_id)
        return project

    async def find_project_by_id(self, project_id: str) -> Optional[InteriorProject]:
        try:
            doc = await self.collection.find_one({"_id": ObjectId(project_id)})
            if doc:
                doc["id"] = str(doc["_id"])
                return InteriorProject(**doc)
            return None
        except Exception:
            return None

    async def find_projects_by_user_id(self, user_id: str) -> List[InteriorProject]:
        cursor = self.collection.find({"user_id": user_id})
        projects = []
        async for doc in cursor:
            doc["id"] = str(doc["_id"])
            projects.append(InteriorProject(**doc))
        return projects

    async def update_project_status(
        self, project_id: str, status: str
    ) -> Optional[InteriorProject]:
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(project_id)},
                {"$set": {"status": status, "updated_at": datetime.now()}},
            )
            if result.modified_count > 0:
                return await self.find_project_by_id(project_id)
            return None
        except Exception:
            return None

    async def update_generated_image(
        self, project_id: str, generated_image_url: str
    ) -> Optional[InteriorProject]:
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(project_id)},
                {
                    "$set": {
                        "generated_image_url": generated_image_url,
                        "updated_at": datetime.now(),
                    }
                },
            )
            if result.modified_count > 0:
                return await self.find_project_by_id(project_id)
            return None
        except Exception:
            return None

    async def delete_project(self, project_id: str) -> bool:
        try:
            result = await self.collection.delete_one({"_id": ObjectId(project_id)})
            return result.deleted_count > 0
        except Exception:
            return False
