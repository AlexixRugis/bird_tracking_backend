from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.http_endpoints import router as http_router
from app.core.database import start_database
from app.config.settings import settings
from app.core.logs import init_logging
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_logging()
    await start_database()
    
    # --- TCP server -----------------------------------------------------------
    stop_event = None
    tcp_task = None
    if settings.ENABLE_TCP_SERVER:
        from app.api.tcp_server import run_tcp_server

        loop = asyncio.get_event_loop()
        stop_event = asyncio.Event()
        tcp_task = loop.create_task(run_tcp_server(settings.APP_HOST, settings.APP_TCP_PORT, stop_event))
    
    yield

    if settings.ENABLE_TCP_SERVER:    
        stop_event.set()
        await tcp_task

app = FastAPI(title="Sensor Adapter Service", lifespan=lifespan)
app.include_router(http_router, prefix="/api/v1")
