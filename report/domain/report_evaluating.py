from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class ReportEvaluating(BaseModel):
    id: str
    report_id: str = Field(..., alias="reportId")
    user_id: str = Field(..., alias="userId")
    evaluation: str  # "good" | "normal" | "bad"
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )
