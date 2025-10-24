from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class Report(BaseModel):
    report_id: str = Field(..., alias="reportId")
    reporter_id: str = Field(..., alias="reporterId")
    reporter_type: str = Field(..., alias="reporterType")

    # 위치 정보: 위도/경도 분리
    location_lat: Optional[float] = Field(None, alias="locationLat")
    location_lng: Optional[float] = Field(None, alias="locationLng")

    cluster_id: Optional[str] = Field(None, alias="clusterId")

    image_url: Optional[str] = Field(None, alias="imageUrl")
    category: Optional[str] = None
    description: Optional[str] = None
    status: str = "pending"

    good_count: Optional[int] = Field(0, alias="goodCount")  # 이모지는 '아쉬움'
    normal_count: Optional[int] = Field(0, alias="normalCount") # 이모지는 '보통'
    bad_count: Optional[int] = Field(0, alias="badCount") # 이모지는 '좋음'
    total_feedbacks: Optional[int] = Field(0, alias="totalFeedbacks")

    not_there: Optional[int] = Field(None, alias="notThere")
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")

    model_config = ConfigDict(
        populate_by_name=True,  # snake_case로도 값 넣기 가능
        from_attributes=True,  # ORM 객체 -> Pydantic 변환 허용
    )
