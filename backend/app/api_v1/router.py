from fastapi import APIRouter

from app.api_v1.endpoints import user, vetis

api_router = APIRouter()

api_router.include_router(user.router)
api_router.include_router(vetis.router)

