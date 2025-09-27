import os
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt

SECRET_KEY = os.getenv("JWT_SECRET", "dev-secret")
ALGORITHM = "HS256"


class Role(StrEnum):
    ADMIN = "ADMIN"
    USER = "USER"


def create_access_token(
    payload: dict,
    role: Role,
    expires_delta: timedelta = timedelta(
        hours=6
    ),  # expires_delta: timedelta = timedelta(hours=6) ← 기본 만료시간이 6시간으로 설정
):

    expire = datetime.utcnow() + expires_delta
    payload.update({"role": role, "exp": expire})
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


class CurrentUser:
    def __init__(self, id: str, role: Role):
        self.id = id
        self.role = role

    def __str__(self):
        return f"{self.id}({self.role})"


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    payload = decode_access_token(token)
    user_id = payload.get("user_id")
    role = payload.get("role")
    if not user_id or not role or role != Role.USER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return CurrentUser(user_id, Role(role))


def get_admin_user(token: Annotated[str, Depends(oauth2_scheme)]):
    payload = decode_access_token(token)
    role = payload.get("role")
    if not role or role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return CurrentUser("ADMIN_USER_ID", Role(role))
