from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from dependency_injector.wiring import inject, Provide
from containers import Container
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
    birth_year: Optional[int] = None

    # 매칭용 정보 (DB에는 저장되지 않음)
    parent_info: Optional[dict] = None
    child_info: Optional[dict] = None


class RegisterResponse(BaseModel):
    message: str
    matched: bool


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


class FcmTokenRequest(BaseModel):
    fcm_token: str


@router.post("/register", response_model=RegisterResponse, dependencies=[])
@inject
def register_user(
    req: UserRegisterRequest,
    service: UserService = Depends(Provide[Container.user_service]),
):
    logger.info("회원가입 요청 시작")
    user = service.register(
        user_type=req.user_type,
        name=req.name,
        email=req.email,
        phone=req.phone,
        password=req.password,
        birth_year=req.birth_year,
        parent_info=req.parent_info,
        child_info=req.child_info,
    )
    logger.info(f"회원가입 성공 uid={user.user_id}")

    matched = service.has_matching(user.user_id)

    return {"message": "User registered successfully", "matched": matched}


@router.post("/login", response_model=TokenResponse, dependencies=[])
@inject
def login_user(
    req: UserLoginRequest,
    service: UserService = Depends(Provide[Container.user_service]),
):
    logger.info("로그인 요청 시작")

    access_token = service.login(req.email, req.password)

    logger.info("로그인 성공")
    return TokenResponse(access_token=access_token)


@router.post("/fcm-token", response_model=MessageResponse)
@inject
def register_fcm_token(
    req: FcmTokenRequest,
    current: CurrentUser = Depends(get_current_user),
    service: UserService = Depends(Provide[Container.user_service]),
):
    fcm_token = req.fcm_token.strip()
    if not fcm_token:
        raise HTTPException(status_code=400, detail="fcm_token is required")

    updated_user = service.register_fcm_token(current.user_id, fcm_token)

    logger.info(f"FCM 토큰 등록 완료 uid={current.user_id}")
    return {"message": "FCM token registered"}


@router.get("/me", response_model=UserResponse)
@inject
def get_current_user_info(
    current: CurrentUser = Depends(get_current_user),  # JWT 인증 사용
    service: UserService = Depends(Provide[Container.user_service]),
):
    user = service.get(current.user_id)
    if not user:
        logger.warning(f"유저 정보 없음 uid={current.user_id}")
        raise HTTPException(status_code=404, detail="User not found")

    matched = service.has_matching(user.user_id)

    logger.info(f"현재 유저 정보 반환 uid={user.user_id}")
    return UserResponse(**user.dict(by_alias=True), matched=matched)


@router.delete("/", response_model=MessageResponse)
@inject
def delete_current_user(
    current: CurrentUser = Depends(get_current_user),
    service: UserService = Depends(Provide[Container.user_service]),
):
    service.delete_user(current.user_id)
    return {"message": "User deleted successfully"}
