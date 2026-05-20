import atexit
import logging
import logging.config
from contextlib import asynccontextmanager
from typing import AsyncContextManager

import uvicorn
from fastapi import FastAPI

from api import api_router
from core.config import uvicorn_options, app_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncContextManager[None]:
    logging.config.dictConfig(app_settings.logging_config)
    queue_handler = logging.getHandlerByName("queue_handler")
    try:
        if queue_handler is not None:
            queue_handler.listener.start()
            atexit.register(queue_handler.listener.stop)
        yield
    finally:
        if queue_handler is not None:
            queue_handler.listener.stop()


app = FastAPI(
    lifespan=lifespan,
    docs_url='/api/openapi'
)
app.include_router(api_router)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        **uvicorn_options
    )
