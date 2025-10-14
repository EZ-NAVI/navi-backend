from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List, Dict, Optional


class Route(BaseModel):
    route_id: str = Field(..., alias="routeId")
    user_id: str = Field(..., alias="userId")
    origin_lat: float = Field(..., alias="originLat")
    origin_lng: float = Field(..., alias="originLng")
    dest_lat: float = Field(..., alias="destLat")
    dest_lng: float = Field(..., alias="destLng")
    path_data: List[Dict[str, float]] = Field(..., alias="pathData")
    duration: int
    score: Optional[float] = None
    created_at: Optional[datetime] = Field(None, alias="createdAt")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )
