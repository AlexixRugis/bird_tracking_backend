import httpx
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class SensorDataResponse(BaseModel):
    latitude: float
    longitude: float
    timestamp: datetime
    light: Optional[float] = None


async def fetch_sensor_data(
    base_url: str,
    internal_id: str,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    limit: Optional[int] = None,
    order: Optional[str] = None,
) -> List[SensorDataResponse]:
    """Запрос данных к удалённому сервису."""

    params = {
        "internal_id": internal_id
    }

    if date_from is not None:
        params["date_from"] = date_from.isoformat()

    if date_to is not None:
        params["date_to"] = date_to.isoformat()

    if limit is not None:
        params["limit"] = limit

    if order is not None:
        params["order"] = order

    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{base_url}/api/v1/sensors/data", params=params)
        resp.raise_for_status()

    return [SensorDataResponse(**item) for item in resp.json()]