from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class ReportNotThere(BaseModel):
    id: str
    report_id: str = Field(..., alias="reportId")
    user_id: str = Field(..., alias="userId")
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="createdAt")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
