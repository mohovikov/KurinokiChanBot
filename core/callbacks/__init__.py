from aiogram import Router

from .general import router as general_router
from .marry import router as marry_router


def setup() -> Router:
    router = Router()
    router.include_router(general_router)
    router.include_router(marry_router)
    return router
