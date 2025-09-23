from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from dependency_injector.wiring import inject, Provide
from user.application.user_service import UserService
from user.domain.user import User
from containers import Container
from typing import Optional

from common.logger import logger
from common.context_vars import user_context

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
    id_token: str


class UserResponse(User):
    matched: bool


@router.post("/register", response_model=User)
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
        parent_id=req.parent_id,
        birth_year=req.birth_year,
    )
    logger.info(f"회원가입 성공 uid={user.user_id}")
    return user


@router.post("/login", response_model=User)
@inject
def login_user(
    req: UserLoginRequest,
    service: UserService = Depends(Provide[Container.user_service]),
):
    logger.info("로그인 요청 시작")
    user = service.login(req.id_token)
    if not user:
        logger.warning("로그인 실패")
        raise HTTPException(401, "Invalid credentials")
    logger.info(f"로그인 성공 uid={user.user_id}")
    return user


@router.get("/me", response_model=UserResponse)
@inject
def get_current_user(
    service: UserService = Depends(Provide[Container.user_service]),
):
    current = user_context.get()
    if current.uid == "anonymous":
        logger.warning("인증되지 않은 요청 /me 접근")
        raise HTTPException(status_code=401, detail="Unauthorized")

    user = service.get(current.uid)
    if not user:
        logger.warning(f"유저 정보 없음 uid={current.uid}")
        raise HTTPException(status_code=404, detail="User not found")

    matched = service.has_matching(user.user_id)

    logger.info(f"현재 유저 정보 반환 uid={user.user_id}")
    return UserResponse(**user.dict(by_alias=True), matched=matched)
