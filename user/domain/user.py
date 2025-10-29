from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class User(BaseModel):
    user_id: str = Field(..., alias="userId")
    user_type: str = Field(..., alias="userType")
    name: str
    email: str
    phone: str
    parent_id: Optional[str] = Field(None, alias="parentId")
    birth_year: Optional[int] = Field(None, alias="birthYear")
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")
    password: Optional[str] = None
    fcm_token: Optional[str] = None
    model_config = ConfigDict(
        populate_by_name=True,  # snake_case로도 값 넣을 수 있음
        from_attributes=True,
    )
