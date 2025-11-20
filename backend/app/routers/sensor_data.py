from datetime import datetime
from typing import List, Optional

from app.database import get_db
from app.models import Sensor, SensorData
from app.schemas import CoordinateResponse, SensorDataCreate, SensorDataBatchCreate
from app.utils import calculate_avg_distance, calculate_avg_speed
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_
from sqlalchemy.orm import Session
from app.sensor_data import fetch_sensor_data

SENSOR_ADAPTER_URL = "http://sensor-adapter:8002"

router = APIRouter(prefix="/sensor-data", tags=["Sensor Data"])

@router.post("/")
def add_sensor_data(data: SensorDataCreate, db: Session = Depends(get_db)):
    sensor = db.query(Sensor).filter_by(internal_id=data.internal_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")

    record = SensorData(
        timestamp=data.timestamp,
        is_light=data.is_light,
        latitude=data.latitude,
        longitude=data.longitude,
        sensor=sensor
    )
    db.add(record)
    db.commit()
    return {"status": "Sensor data added"}

@router.post("/batch/")
def add_sensor_data_batch(data: SensorDataBatchCreate, db: Session = Depends(get_db)):
    sensor = db.query(Sensor).filter_by(internal_id=data.internal_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    for entry in data.entries:
        record = SensorData(
            timestamp=entry.timestamp,
            is_light=entry.is_light,
            latitude=entry.latitude,
            longitude=entry.longitude,
            sensor=sensor
        )
        db.add(record)
        
    db.commit()
    
    return {"status": "Sensor data added"}

@router.get("/avg-speed/")
async def get_avg_speed(
    internal_id: str,
    date_from: datetime,
    date_to: datetime,
    times_of_day: Optional[bool] = False
):
    records = await fetch_sensor_data(
        SENSOR_ADAPTER_URL,
        internal_id,
        date_from,
        date_to,
        order="asc"
    )
    
    if times_of_day:
        records = list(filter(lambda x: x.light is not None and x.light > 0.8, records))
        
    avg_speed = calculate_avg_speed(records)
    return {"average_speed_kmh": avg_speed}

@router.get("/avg-distance/")
async def get_avg_distance(
    internal_id: str,
    date_from: datetime,
    date_to: datetime,
    times_of_day: Optional[bool] = False
):    
    records = await fetch_sensor_data(
        SENSOR_ADAPTER_URL,
        internal_id,
        date_from,
        date_to,
        order="asc"
    )
    
    if times_of_day:
        records = list(filter(lambda x: x.light is not None and x.light > 0.8, records))
        
    avg_distance = calculate_avg_distance(records)
    return {"average_distance_km": avg_distance}

@router.get("/coordinates/by-sensor/", response_model=List[CoordinateResponse])
async def get_coordinates_by_sensor(
    internal_id: str,
    date_from: datetime,
    date_to: datetime
):
    records = await fetch_sensor_data(
        SENSOR_ADAPTER_URL,
        internal_id,
        date_from,
        date_to
    )

    return [
        CoordinateResponse(
            latitude=r.latitude,
            longitude=r.longitude,
            timestamp=r.timestamp
        ) for r in records
    ]


@router.get("/get_data")
async def get_sensor_data(limit: int = 10, db: Session = Depends(get_db)):
    sensor_data = db.query(SensorData).limit(limit).all()
    return sensor_data
