import asyncio
from logging import getLogger
from app.adapters import adapter

logger = getLogger(__name__)

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    data = await reader.read()  # читаем весь пакет
    addr = writer.get_extra_info("peername")
    
    logger.info(f"Processing request from TCP client {addr}")
    
    response = b""

    try:
        result = await adapter.process_packet(data)
        response = f"OK {result['saved_messages']}\n".encode()
    except Exception as e:
        response = f"ERR {e}\n".encode()

    writer.write(response)
    await writer.drain()
    writer.close()
    await writer.wait_closed()
    
    logger.info(f"TCP client {addr} disconnected")


async def run_tcp_server(host: str, port: int, stop_event: asyncio.Event):
    logger.info(f"Starting tcp server on host={host}, port={port}")
    
    server = await asyncio.start_server(handle_client, host, port)
    async with server:
        await stop_event.wait()
        server.close()
        await server.wait_closed()
