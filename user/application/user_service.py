from datetime import datetime, timezone
from typing import Optional
from fastapi import HTTPException, status
import ulid

from user.domain.user import User
from user.domain.repository.user_repo import UserRepository
from utils.crypto import Crypto
from common.auth import create_access_token, Role
from common.logger import logger


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
        birth_year: Optional[int] = None,
        parent_info: Optional[dict] = None,
        child_info: Optional[dict] = None,
    ) -> User:
        # 이메일 중복 체크
        existing = self.repo.find_by_email(email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        now = datetime.now(timezone.utc)
        user = User(
            user_id=str(ulid.new()),
            user_type=user_type,
            name=name,
            email=email,
            phone=phone,
            birth_year=birth_year,
            password=self.crypto.encrypt(password),
            created_at=now,
            updated_at=now,
        )

        saved = self.repo.save(user)

        # 자녀 → 부모 매칭
        if user_type == "child" and parent_info:
            parent = self.repo.find_parent_candidate(
                name=parent_info.get("name"),
                email=parent_info.get("email"),
                phone=parent_info.get("phone"),
                birth_year=parent_info.get("birth_year"),
            )
            if parent:
                saved.parent_id = parent.user_id
                saved.updated_at = datetime.now(timezone.utc)
                saved = self.repo.save(saved)

        # 부모 → 자녀 매칭
        elif user_type == "parent" and child_info:
            child = self.repo.find_child_candidate(
                name=child_info.get("name"),
                email=child_info.get("email"),
                phone=child_info.get("phone"),
                birth_year=child_info.get("birth_year"),
            )
            if child:
                child.parent_id = saved.user_id
                child.updated_at = datetime.now(timezone.utc)
                self.repo.save(child)

        return saved

    def login(self, email: str, password: str) -> str:
        user = self.repo.find_by_email(email)
        if not user or not self.crypto.verify(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # JWT 발급
        return create_access_token(
            payload={"user_id": user.user_id, "user_type": user.user_type},
            role=Role.USER,
        )

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

    def register_fcm_token(self, user_id: str, fcm_token: str) -> User:
        """유저의 FCM 토큰을 등록하거나 갱신"""
        user = self.repo.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # 같은 토큰이면 굳이 DB 업데이트 안함 (불필요한 커밋 방지)
        if user.fcm_token == fcm_token:
            logger.info(f"FCM 토큰 이미 최신 상태 uid={user_id}")
            return user

        user.fcm_token = fcm_token
        user.updated_at = datetime.now(timezone.utc)

        updated = self.repo.save(user)
        logger.info(f"FCM 토큰 등록 완료 uid={user_id}")
        return updated
