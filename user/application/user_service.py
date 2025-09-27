from datetime import datetime
from typing import Optional
from fastapi import HTTPException, status
import ulid

from user.domain.user import User
from user.domain.repository.user_repo import UserRepository
from utils.crypto import Crypto
from common.auth import create_access_token, Role


class UserService:
    def __init__(self, repo: UserRepository, crypto: Crypto):
        self.repo = repo
        self.crypto = crypto

    def register(
        self,
        user_type: str,
        name: str,
        email: str,
        phone: str,
        password: str,
        parent_id: Optional[str] = None,
        birth_year: Optional[int] = None,
    ) -> User:
        # 이메일 중복 체크
        existing = self.repo.find_by_email(email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        now = datetime.utcnow()
        user = User(
            user_id=str(ulid.new()),
            user_type=user_type,
            name=name,
            email=email,
            phone=phone,
            parent_id=parent_id,
            birth_year=birth_year,
            password=self.crypto.encrypt(password),
            created_at=now,
            updated_at=now,
        )
        return self.repo.save(user)

    def login(self, email: str, password: str) -> str:
        user = self.repo.find_by_email(email)
        if not user or not self.crypto.verify(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # JWT 발급
        return create_access_token(payload={"user_id": user.user_id}, role=Role.USER)

    def get(self, user_id: str) -> Optional[User]:
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
