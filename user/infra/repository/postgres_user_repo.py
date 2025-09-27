from sqlalchemy.orm import Session
from fastapi import HTTPException

from user.domain.repository.user_repo import UserRepository
from user.domain.user import User as UserVO
from user.infra.db_models.user import User as UserDB
from database import SessionLocal


class PostgresUserRepository(UserRepository):
    def save(self, user: UserVO) -> UserVO:
        with SessionLocal() as db:
            db_user = UserDB(
                user_id=user.user_id,
                user_type=user.user_type,
                name=user.name,
                email=user.email,
                phone=user.phone,
                password=user.password,
                parent_id=user.parent_id,
                birth_year=user.birth_year,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return user

    def get(self, user_id: str) -> UserVO | None:
        with SessionLocal() as db:
            user = db.query(UserDB).filter(UserDB.user_id == user_id).first()
            if not user:
                return None
            return UserVO.from_orm(user)

    def find_by_email(self, email: str) -> UserVO | None:
        with SessionLocal() as db:
            user = db.query(UserDB).filter(UserDB.email == email).first()
            if not user:
                return None
            return UserVO.from_orm(user)

    def find_children_by_parent_id(self, parent_id: str) -> list[UserVO]:
        with SessionLocal() as db:
            users = db.query(UserDB).filter(UserDB.parent_id == parent_id).all()
            return [UserVO.from_orm(u) for u in users]
