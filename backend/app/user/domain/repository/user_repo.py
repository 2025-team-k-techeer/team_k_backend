from abc import ABCMeta, abstractmethod

# ✅ 올바른 경로
from app.user.domain.user import User


class IUserRepository(metaclass=ABCMeta):
    @abstractmethod
    def save(self, user: User):
        raise NotImplementedError

    @abstractmethod
    def find_by_email(self, email: str) -> User:
        """
        이메일로 유저를 검색한다.
        검색한 유저가 없을 경우 422 에러를 발생시킨다.
        """
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, id: str) -> User:
        """
        아이디로 사용자를 검색한다.
        """
        raise NotImplementedError

    @abstractmethod
    def update(self, user: User):
        raise NotImplementedError

    @abstractmethod
    def get_users(self, page: int, items_per_page: int) -> tuple[int, list[User]]:
        raise NotImplementedError

    @abstractmethod
    def delete_user(self, id: str):
        raise NotImplementedError
