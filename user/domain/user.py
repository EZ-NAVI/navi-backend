from dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    user_id: str
    user_type: str     # "parent" | "child"
    name: str
    email: str
    parent_id: str | None
    birth_year: int | None
    created_at: datetime | None
    updated_at: datetime | None
