import logging
from app.config.settings import settings

def init_logging() -> None:
    stream_handler = logging.StreamHandler()
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(formatter)
    logging.basicConfig(
        level=logging.INFO,
        handlers=[stream_handler, ]
    )