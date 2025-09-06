from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from dependency_injector.wiring import inject, Provide
from user.application.user_service import UserService
from containers import Container
from typing import Optional

# 추가
from common.logger import logger

router = APIRouter(prefix="/users", tags=["users"])


class UserRegisterRequest(BaseModel):
    user_type: str
    name: str
    email: EmailStr
    password: str
    parent_id: Optional[str] = None
    birth_year: Optional[int] = None


class UserLoginRequest(BaseModel):
    id_token: str


@router.post("/register")
@inject
def register_user(
    req: UserRegisterRequest,
    service: UserService = Depends(Provide[Container.user_service]),
):
    logger.info("회원가입 요청 시작")  # ← 로그 추가
    user = service.register(
        user_type=req.user_type,
        name=req.name,
        email=req.email,
        password=req.password,
        parent_id=req.parent_id,
        birth_year=req.birth_year,
    )
    logger.info(f"회원가입 성공 uid={user.user_id}")  # ← 로그 추가
    return user.__dict__


@router.post("/login")
@inject
def login_user(
    req: UserLoginRequest,
    service: UserService = Depends(Provide[Container.user_service]),
):
    logger.info("로그인 요청 시작")  # ← 로그 추가
    user = service.login(req.id_token)
    if not user:
        logger.warning("로그인 실패")  # ← 실패 로그
        raise HTTPException(401, "Invalid credentials")
    logger.info(f"로그인 성공 uid={user.user_id}")  # ← 성공 로그
    return user.__dict__
