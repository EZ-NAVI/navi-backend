from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Dict, Optional


class Route(BaseModel):
    route_id: str
    user_id: str
    origin_lat: float
    origin_lng: float
    dest_lat: float
    dest_lng: float
    path_data: List[Dict[str, float]]
    duration: int
    evaluation: Optional[float] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )
