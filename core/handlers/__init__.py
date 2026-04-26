from aiogram import Router

from .general_handler import router as general_router
from .voices_handler import router as voices_router


def setup() -> Router:
    router = Router()
    router.include_router(general_router)
    router.include_router(voices_router)
    return router
