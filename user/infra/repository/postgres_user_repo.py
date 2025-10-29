from sqlalchemy.orm import Session
from fastapi import HTTPException

from user.domain.repository.user_repo import UserRepository
from user.domain.user import User as UserVO
from user.infra.db_models.user import User as UserDB
from database import SessionLocal


class PostgresUserRepository(UserRepository):
    def save(self, user: UserVO) -> UserVO:
        with SessionLocal() as db:
            db_user = db.query(UserDB).filter(UserDB.user_id == user.user_id).first()
            if db_user:
                # 이미 존재하면 업데이트
                db_user.name = user.name
                db_user.email = user.email
                db_user.phone = user.phone
                db_user.password = user.password
                db_user.parent_id = user.parent_id
                db_user.birth_year = user.birth_year
                db_user.fcm_token = user.fcm_token
                db_user.updated_at = user.updated_at
            else:
                # 신규 생성
                db_user = UserDB(
                    user_id=user.user_id,
                    user_type=user.user_type,
                    name=user.name,
                    email=user.email,
                    phone=user.phone,
                    password=user.password,
                    parent_id=user.parent_id,
                    birth_year=user.birth_year,
                    fcm_token=user.fcm_token,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                )
                db.add(db_user)

            db.commit()
            db.refresh(db_user)
            return UserVO.model_validate(db_user)

    def get(self, user_id: str) -> UserVO | None:
        with SessionLocal() as db:
            user = db.query(UserDB).filter(UserDB.user_id == user_id).first()
            if not user:
                return None
            return UserVO.model_validate(user)

    def find_by_email(self, email: str) -> UserVO | None:
        with SessionLocal() as db:
            user = db.query(UserDB).filter(UserDB.email == email).first()
            if not user:
                return None
            return UserVO.model_validate(user)

    def find_children_by_parent_id(self, parent_id: str) -> list[UserVO]:
        with SessionLocal() as db:
            users = db.query(UserDB).filter(UserDB.parent_id == parent_id).all()
            return [UserVO.model_validate(u) for u in users]
