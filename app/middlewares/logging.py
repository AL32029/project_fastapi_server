# [MISC][DONE][HIGH] Реализовать логирование
import logging

from fastapi import HTTPException
from fastapi.requests import Request
from starlette.responses import JSONResponse

from main import app

logger = logging.getLogger()


@app.exception_handler(Exception)
async def exception(request: Request, exc: Exception):
    logger.error(f"{request.url} | Error in application: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": exc}
    )


@app.exception_handler(HTTPException)
async def exception(request: Request, exc: HTTPException):
    logger.error(f"{request.url} | Error in application: {exc}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )
