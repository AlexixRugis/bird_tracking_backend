from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class CoordinateResponse(BaseModel):
    latitude: float
    longitude: float
    timestamp: datetime
    light: float | None = None
