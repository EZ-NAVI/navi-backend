from user.domain.user import User
from user.domain.repository.user_repo import UserRepository
from uuid import uuid4
from typing import Optional

class UserService:
    def __init__(self, repo: Optional[UserRepository] = None):
        self.repo = repo

    def create(self, user_type: str, name: str, email: str,
               parent_id: Optional[str] = None,
               birth_year: Optional[int] = None) -> User:
        user = User(
            user_id=str(uuid4()),
            user_type=user_type,
            name=name,
            email=email,
            parent_id=parent_id,
            birth_year=birth_year,
            created_at=None,
            updated_at=None,
        )
        # 지금은 DB 저장 안 하고 그냥 객체만 리턴
        if self.repo:
            return self.repo.save(user)
        return user

    def get(self, user_id: str) -> Optional[User]:
        if not self.repo:
            return None
        return self.repo.get(user_id)

    def find_by_email(self, email: str) -> Optional[User]:
        if not self.repo:
            return None
        return self.repo.find_by_email(email)
