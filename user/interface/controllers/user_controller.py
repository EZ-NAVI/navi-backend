from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from dependency_injector.wiring import inject, Provide
from user.application.user_service import UserService
from containers import Container
from typing import Optional

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
    user = service.register(
        user_type=req.user_type,
        name=req.name,
        email=req.email,
        password=req.password,
        parent_id=req.parent_id,
        birth_year=req.birth_year,
    )
    return user.__dict__


@router.post("/login")
@inject
def login_user(
    req: UserLoginRequest,
    service: UserService = Depends(Provide[Container.user_service]),
):
    user = service.login(req.id_token)
    if not user:
        raise HTTPException(401, "Invalid credentials")
    return user.__dict__
