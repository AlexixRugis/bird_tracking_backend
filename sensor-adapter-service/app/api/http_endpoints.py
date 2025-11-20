from typing import List, Optional
from logging import getLogger
from datetime import datetime
from fastapi import APIRouter, Depends, Request, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.adapters import adapter
from app.core.models import SensorMessage
from app.core.database import get_db
from app.core.schemas import CoordinateResponse

logger = getLogger(__name__)
router = APIRouter()

@router.post("/sensors/binary", status_code=201)
async def receive_binary(request: Request):
    logger.info(f"Processing request from {request.client.host}")
    raw = await request.body()
    try:
        processed = await adapter.process_packet(raw)
    except Exception as exc:
        raise HTTPException(400, detail=str(exc))
    return JSONResponse(content=processed)

@router.get("/sensors/data", response_model=List[CoordinateResponse])
async def get_coordinates_by_sensor(
    internal_id: str,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    limit: Optional[int] = None,
    order: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(SensorMessage).where(
        SensorMessage.device_id == internal_id
    )

    if date_from is not None:
        stmt = stmt.where(
            SensorMessage.timestamp >= int(date_from.timestamp())
        )

    if date_to is not None:
        stmt = stmt.where(
            SensorMessage.timestamp <= int(date_to.timestamp())
        )
        
    if order == "asc":
        stmt = stmt.order_by(SensorMessage.timestamp.asc())
    elif order == "desc":
        stmt = stmt.order_by(SensorMessage.timestamp.desc())

    if limit is not None:
        stmt = stmt.limit(limit)

    result = await db.execute(stmt)

    records = result.scalars().all()

    return [
        CoordinateResponse(
            latitude=r.latitude,
            longitude=r.longitude,
            timestamp=r.timestamp,
            light=(r.data.get("light") if r.data else None),
        ) for r in records
    ]