from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class ReportComment(BaseModel):
    comment_id: str = Field(..., alias="commentId")
    report_id: str = Field(..., alias="reportId")
    user_id: str = Field(..., alias="userId")
    content: str
    created_at: Optional[datetime] = Field(None, alias="createdAt")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )
