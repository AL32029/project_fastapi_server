import uvicorn
from fastapi import FastAPI

from api import api_router
from core.config import uvicorn_options

app = FastAPI(
    docs_url='/api/openapi'
)
app.include_router(api_router)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        **uvicorn_options
    )
