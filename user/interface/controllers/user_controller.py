from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from dependency_injector.wiring import inject, Provide
from user.application.user_service import UserService
from user.domain.user import User
from typing import Optional

from common.logger import logger
from common.context_vars import user_context
from common.auth import get_current_user, CurrentUser

router = APIRouter(prefix="/users", tags=["users"])


class UserRegisterRequest(BaseModel):
    user_type: str
    name: str
    email: EmailStr
    phone: str
    password: str
    parent_id: Optional[str] = None
    birth_year: Optional[int] = None


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class MessageResponse(BaseModel):
    message: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(User):
    matched: bool


@router.post("/register", response_model=MessageResponse, dependencies=[])
@inject
def register_user(
    req: UserRegisterRequest,
    service: UserService = Depends(Provide["container.user_service"]),
):
    logger.info("회원가입 요청 시작")
    user = service.register(
        user_type=req.user_type,
        name=req.name,
        email=req.email,
        phone=req.phone,
        password=req.password,
        parent_id=req.parent_id,
        birth_year=req.birth_year,
    )
    logger.info(f"회원가입 성공 uid={user.user_id}")
    return {"message": "User registered successfully"}


@router.post("/login", response_model=TokenResponse, dependencies=[])
@inject
def login_user(
    req: UserLoginRequest,
    service: UserService = Depends(Provide["container.user_service"]),
):
    logger.info("로그인 요청 시작")

    access_token = service.login(req.email, req.password)

    logger.info("로그인 성공")
    return TokenResponse(access_token=access_token)


@router.get(
    "/me", response_model=UserResponse, dependencies=[Depends(get_current_user)]
)
@inject
def get_current_user_info(
    service: UserService = Depends(Provide["container.user_service"]),
    current: CurrentUser = Depends(get_current_user),  # JWT 인증 사용
):
    user = service.get(current.user_id)
    if not user:
        logger.warning(f"유저 정보 없음 uid={current.user_id}")
        raise HTTPException(status_code=404, detail="User not found")

    matched = service.has_matching(user.user_id)

    logger.info(f"현재 유저 정보 반환 uid={user.user_id}")
    return UserResponse(**user.dict(by_alias=True), matched=matched)
