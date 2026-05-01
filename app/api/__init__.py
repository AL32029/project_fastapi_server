from fastapi import APIRouter

from api.v1.user import auth_router

api_router = APIRouter()

api_router.include_router(auth_router)