from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional, Literal
from dependency_injector.wiring import inject, Provide
from containers import Container
from user.application.user_service import UserService
from uuid import UUID

router = APIRouter(prefix="/users", tags=["users"])

# 요청/응답 스키마
class CreateUser(BaseModel):
    name: str
    email: EmailStr
    user_type: Literal["parent", "child"]
    parent_id: Optional[str] = None
    birth_year: Optional[int] = None

class ReadUser(BaseModel):
    user_id: str
    user_type: str
    name: str
    email: str
    parent_id: Optional[str] = None
    birth_year: Optional[int] = None

@router.post("", response_model=ReadUser)
@inject
def create_user(
    body: CreateUser,
    svc: UserService = Depends(Provide[Container.user_service]),
):
    u = svc.create(**body.model_dump())
    return ReadUser(**u.__dict__)

@router.get("/{user_id}", response_model=ReadUser)
@inject
def get_user(
    user_id: str,
    svc: UserService = Depends(Provide[Container.user_service]),
):
    u = svc.get(user_id)
    if not u:
        raise HTTPException(404, "User not found")
    return ReadUser(**u.__dict__)
