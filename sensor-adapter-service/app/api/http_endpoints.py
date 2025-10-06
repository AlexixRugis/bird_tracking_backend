from logging import getLogger
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from app.adapters import adapter

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
