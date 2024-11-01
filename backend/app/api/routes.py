from fastapi import FastAPI

from app.config import settings
from app.api.users import router as api_router
from app.api.websocket import router as ws_router


def init_routers(app: FastAPI) -> None:
    app.include_router(api_router, prefix=settings.api_v1_str, tags=["Users"])
    app.include_router(ws_router, prefix=settings.api_v1_str, tags=["Websockers"])
