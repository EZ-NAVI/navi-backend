from datetime import datetime
from typing import Optional
from user.domain.user import User
from user.domain.repository.user_repo import UserRepository
from user.infra.auth.firebase_auth_service import FirebaseAuthService


class UserService:
    def __init__(self, repo: UserRepository, auth_service: FirebaseAuthService):
        self.repo = repo
        self.auth_service = auth_service

    def register(
        self,
        user_type: str,
        name: str,
        email: str,
        password: str,
        parent_id: Optional[str] = None,
        birth_year: Optional[int] = None,
    ) -> User:

        firebase_uid = self.auth_service.create_user(
            email=email,
            password=password,
            display_name=name,
        )

        now = datetime.utcnow()
        user = User(
            user_id=firebase_uid,  # Firebase UID 사용
            user_type=user_type,
            name=name,
            email=email,
            parent_id=parent_id,
            birth_year=birth_year,
            created_at=now,
            updated_at=now,
        )
        return self.repo.save(user)

    def login(self, id_token: str) -> Optional[User]:
        # 프론트에서 넘긴 Firebase ID 토큰 검증
        uid = self.auth_service.verify_token(id_token)
        return self.repo.get(uid)

    def get(self, user_id: str) -> Optional[User]:
        if not self.repo:
            return None
        return self.repo.get(user_id)

    def has_matching(self, user_id: str) -> bool:
        user = self.repo.get(user_id)
        if not user:
            return False

        if user.user_type == "child":
            # 자녀 → parent_id가 있으면 매칭된 것
            return user.parent_id is not None

        elif user.user_type == "parent":
            # 부모 → 자신을 parent_id로 가진 자녀가 있는지 확인
            children = self.repo.find_children_by_parent_id(user.user_id)
            return len(children) > 0

        return False
