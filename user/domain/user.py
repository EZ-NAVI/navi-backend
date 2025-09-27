from pydantic import BaseModel
from datetime import datetime


# snake_case → camelCase 변환 함수
def to_camel(string: str) -> str:
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class User(BaseModel):
    user_id: str
    user_type: str  # "parent" | "child"
    name: str
    email: str
    phone: str
    parent_id: str | None
    birth_year: int | None
    created_at: datetime | None
    updated_at: datetime | None
    password: str | None = None  # 사실상 안 쓰지만 Auth 동기화용

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True
