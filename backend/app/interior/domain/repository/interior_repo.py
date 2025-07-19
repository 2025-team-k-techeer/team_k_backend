from abc import ABC, abstractmethod
from typing import List, Optional
from app.interior.domain.interior import InteriorProject


class InteriorRepository(ABC):
    @abstractmethod
    async def save_project(self, project: InteriorProject) -> InteriorProject:
        pass

    @abstractmethod
    async def find_project_by_id(self, project_id: str) -> Optional[InteriorProject]:
        pass

    @abstractmethod
    async def find_projects_by_user_id(self, user_id: str) -> List[InteriorProject]:
        pass

    @abstractmethod
    async def update_project_status(
        self, project_id: str, status: str
    ) -> Optional[InteriorProject]:
        pass

    @abstractmethod
    async def update_generated_image(
        self, project_id: str, generated_image_url: str
    ) -> Optional[InteriorProject]:
        pass

    @abstractmethod
    async def delete_project(self, project_id: str) -> bool:
        pass
